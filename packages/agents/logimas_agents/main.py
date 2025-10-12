import os
import traceback
import random
import json
from typing import Optional, Annotated
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt

# --- Local Imports ---
from .chains.graph import agent_graph
from .tools.database import supabase_client, get_user_permissions, user_has_permission
# Correctly import the reusable embedding function
from .tools.vector_store import create_embedding

# --- API Definition ---
app = FastAPI(
    title="LogiMAS Agent Server",
    description="The single, consolidated backend for the LogiMAS application.",
    version="1.2.0", # Version bump for new feature
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- JWT Configuration ---
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# --- Pydantic Models for Payloads ---
class QueryRequest(BaseModel):
    query: str

class IncidentReport(BaseModel):
    shipment_id: Optional[str] = None
    route_description: str
    details: str

class NewOrder(BaseModel):
    customer_id: str 
    items: list[dict]
    destination: dict

class CurrentUser(BaseModel):
    user_id: str
    role: str
    permissions: list[str]

# --- Authentication Dependency ---
async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> CurrentUser:
    """
    Extracts and validates JWT token from Authorization header.
    Returns the current user with their role and permissions.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Fetch user permissions from database
        permissions = get_user_permissions(user_id)
        
        return CurrentUser(user_id=user_id, role=role, permissions=permissions)
    
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

# --- Optional Authentication (for endpoints that can work with or without auth) ---
async def get_optional_user(authorization: Annotated[str | None, Header()] = None) -> CurrentUser | None:
    """Optional authentication - returns None if no token provided."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

# --- Permission Checker ---
def require_permission(permission: str):
    """Dependency factory to check if user has a specific permission."""
    async def permission_checker(current_user: CurrentUser = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required permission: {permission}"
            )
        return current_user
    return permission_checker

# --- API Endpoints ---

@app.get("/", tags=["Health"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LogiMAS Agent Server is running."}

@app.post("/agent/invoke", tags=["Agent Graph"])
async def agent_invoke_endpoint(
    request: QueryRequest,
    current_user: CurrentUser = Depends(require_permission("access_chat"))
):
    """Main entry point for the agent system. Requires 'access_chat' permission."""
    try:
        inputs = {
            "initial_query": request.query,
            "user_id": current_user.user_id,
            "user_role": current_user.role,
            "user_permissions": current_user.permissions
        }
        final_state = agent_graph.invoke(inputs)
        return {"response": final_state.get("final_response", "Agent did not provide a response.")}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/incidents", tags=["Incidents"], status_code=201)
async def create_incident_report(
    report: IncidentReport,
    current_user: CurrentUser = Depends(require_permission("report_incident"))
):
    """Report an incident. Requires 'report_incident' permission (Admin only)."""
    print(f"New incident reported for route: {report.route_description}")
    try:
        timestamp = datetime.now(timezone.utc)
        source_id = f"live_report_{int(timestamp.timestamp())}.txt"
        full_report_text = f"LIVE REPORT\nDate: {timestamp.isoformat()}\nRoute: {report.route_description}\nDetails: {report.details}"
        embedding = create_embedding(full_report_text)
        
        response = supabase_client.from_('documents').insert({
            "source_type": "live_incident_report", "source_id": source_id,
            "text_snippet": full_report_text, "region_id": "SoCal",
            "ts": timestamp.isoformat(), "embedding": embedding,
            "embedding_model": os.getenv("EMBEDDING_MODEL_NAME")
        }).execute()
        
        # --- THIS IS THE CORRECTED CHECK ---
        if not response.data:
            # If the insert fails, the error details might be in a different attribute
            error_details = getattr(response, 'error', 'Unknown database error')
            raise Exception(f"Database insertion failed: {error_details}")

        return {"message": "Incident report has been successfully embedded and logged."}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to log incident: {str(e)}")

@app.get("/shipments/{shipment_id}", tags=["Data Fetching"])
async def get_shipment_details(shipment_id: str):
    """Fetches details for a single shipment using correct foreign key joins."""
    try:
        query = "*, orders(*), vehicles(*)"
        res = supabase_client.from_("shipments").select(query).eq("shipment_id", shipment_id).single().execute()
        if res.data:
            return res.data
        else:
            raise HTTPException(status_code=404, detail="Shipment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shipment details: {str(e)}")

@app.get("/admin/kpis", tags=["Data Fetching"])
async def get_admin_kpis():
    """Fetches KPI data - calculates daily on-time performance from shipments."""
    try:
        # Try to fetch from materialized view first
        try:
            response = supabase_client.from_("daily_on_time_rate").select("*").execute()
            if response.data and isinstance(response.data, list):
                sorted_data = sorted(response.data, key=lambda item: item["ship_date"], reverse=True)
                return sorted_data[:30]
        except:
            # If view doesn't exist, calculate directly from shipments
            pass
        
        # Fallback: Calculate KPIs directly from shipments table
        response = supabase_client.from_("shipments").select(
            "shipment_id, shipped_at, expected_arrival, status, orders(actual_delivery_date)"
        ).not_.is_("shipped_at", "null").execute()
        
        if not response.data:
            return []
        
        # Group by date and calculate metrics
        from collections import defaultdict
        from datetime import datetime
        
        daily_stats = defaultdict(lambda: {"total": 0, "on_time": 0})
        
        for shipment in response.data:
            if not shipment.get("shipped_at"):
                continue
                
            ship_date = datetime.fromisoformat(shipment["shipped_at"].replace('Z', '+00:00')).date()
            daily_stats[ship_date]["total"] += 1
            
            # Check if delivered on time
            if shipment["status"] == "delivered":
                expected = datetime.fromisoformat(shipment["expected_arrival"].replace('Z', '+00:00'))
                actual = None
                
                if shipment.get("orders") and shipment["orders"].get("actual_delivery_date"):
                    actual = datetime.fromisoformat(shipment["orders"]["actual_delivery_date"].replace('Z', '+00:00'))
                
                if actual and actual <= expected:
                    daily_stats[ship_date]["on_time"] += 1
        
        # Format results
        kpi_data = []
        for date, stats in sorted(daily_stats.items(), reverse=True)[:30]:
            on_time_pct = round((stats["on_time"] / stats["total"] * 100), 2) if stats["total"] > 0 else 0
            kpi_data.append({
                "ship_date": date.isoformat(),
                "total_shipments": stats["total"],
                "on_time_shipments": stats["on_time"],
                "on_time_percentage": on_time_pct
            })
        
        return kpi_data
        
    except Exception as e:
        print(f"Error in get_admin_kpis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

ALLOWED_TABLES = ["profiles", "orders", "shipments", "vehicles", "warehouses", "inventory", "packaging_types", "fuel_prices", "agent_audit_logs", "documents"]
@app.get("/browser/{table_name}", tags=["Data Browser"])
async def browse_table_data(table_name: str, limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Fetches a paginated list of rows from a specified table."""
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=403, detail=f"Access to table '{table_name}' is forbidden.")
    try:
        count_response = supabase_client.from_(table_name).select("*", count="exact").limit(0).execute()
        total_count = count_response.count if count_response.count is not None else 0
        data_response = supabase_client.from_(table_name).select("*").range(offset, offset + limit - 1).execute()
        if data_response.data is not None:
            return {"total": total_count, "data": data_response.data}
        elif data_response.error:
            raise HTTPException(status_code=500, detail=data_response.error.message)
        else:
            return {"total": 0, "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/documents", tags=["Knowledge Base"])
async def list_available_documents(
    current_user: CurrentUser = Depends(require_permission("access_knowledge_base"))
):
    """Fetches a list of source documents. Requires 'access_knowledge_base' permission (Admin only)."""
    try:
        response = supabase_client.from_("documents").select("source_id, source_type, region_id, ts").execute()
        if response.data:
            unique_documents = {doc["source_id"]: doc for doc in response.data}.values()
            return list(unique_documents)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch documents list.")

@app.get("/knowledge/schemas", tags=["Knowledge Base"])
async def list_table_schemas(
    current_user: CurrentUser = Depends(require_permission("access_knowledge_base"))
):
    """Returns a predefined list of key table schemas. Requires 'access_knowledge_base' permission (Admin only)."""
    schemas = {
        "shipments": ["shipment_id", "status", "current_eta"],
        "orders": ["order_id", "customer_id", "status"],
        "profiles": ["customer_id", "name", "loyalty_tier"],
        "inventory": ["sku", "product_name", "qty_on_hand"],
    }
    return schemas

@app.post("/orders", tags=["Role Actions"], status_code=201)
async def place_new_order(
    order: NewOrder,
    current_user: CurrentUser = Depends(require_permission("place_order"))
):
    """
    Endpoint to place a new order. Requires 'place_order' permission (Delivery Person and Customer only).
    Admin cannot place orders.
    """
    print(f"Received new order for customer: {order.customer_id}")
    try:
        # Simple price calculation
        order_total = sum(item.get('price', 50.0) for item in order.items)

        new_order_data = {
            "customer_id": order.customer_id,
            "items": json.dumps(order.items), # Supabase expects JSON as a string
            "destination": json.dumps(order.destination),
            "order_date": datetime.now(timezone.utc).isoformat(),
            "order_total": order_total,
            "status": "processing" # New orders always start as 'processing'
        }

        response = supabase_client.from_('orders').insert(new_order_data).execute()

        if response.error:
            raise Exception(f"Database insertion failed: {response.error.message}")

        return {"message": "Order placed successfully!", "order": response.data[0]}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")
    

