import traceback
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query


# from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

# --- Local Imports ---
# from .auth import get_current_user, require_roles, User
from .chains.graph import agent_graph
from .tools.database import supabase_client

# --- API Definition ---
app = FastAPI(
    title="LogiMAS Agent Server",
    description="The single, consolidated backend for the LogiMAS application with JWT authentication.",
    version="1.1.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models for Payloads ---
class QueryRequest(BaseModel):
    query: str


class IncidentReport(BaseModel):
    shipment_id: Optional[str] = None
    route_description: str
    details: str


# --- API Endpoints ---


# === Health Check ===
@app.get("/", tags=["Health"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LogiMAS Agent Server is running."}


# # === Authentication ===
# @app.post("/auth/token", tags=["Authentication"])
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     """
#     Handles user login via email and password. On success, it returns a JWT access token.
#     """
#     try:
#         res = supabase_client.auth.sign_in_with_password(
#             {"email": form_data.username, "password": form_data.password}
#         )
#         if res.session and res.session.access_token:
#             return {"access_token": res.session.access_token, "token_type": "bearer"}
#         else:
#             raise HTTPException(status_code=401, detail="Incorrect email or password")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


# === Agent Graph ===
@app.post("/agent/invoke", tags=["Agent Graph"])
async def agent_invoke_endpoint(request: QueryRequest):
    """Main entry point for the agent system. Protected: All authenticated users."""
    try:
        inputs = {"initial_query": request.query}
        final_state = agent_graph.invoke(inputs)
        return {
            "response": final_state.get(
                "final_response", "Agent did not provide a response."
            )
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# # === Data Fetching ===
# @app.get("/shipments/{shipment_id}", tags=["Data Fetching"])
# async def get_shipment_details(shipment_id: str):
#     """Fetches details for a single shipment. Protected: All roles."""
#     try:
#         res = (
#             supabase_client.from_("shipments")
#             .select("*, orders(*), vehicles(*)")
#             .eq("shipment_id", shipment_id)
#             .single()
#             .execute()
#         )
#         if res.data:
#             return res.data
#         else:
#             raise HTTPException(status_code=404, detail="Shipment not found")
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error fetching shipment details: {str(e)}"
#         )

@app.get("/shipments/{shipment_id}", tags=["Data Fetching"])
async def get_shipment_details(shipment_id: str):
    """
    Fetches details for a single shipment using the correct foreign key joins.
    """
    try:
        # --- THIS IS THE CORRECTED QUERY ---
        # We explicitly tell Supabase how to join the tables based on our schema.
        query = """
            *,
            orders ( * ),
            vehicles ( * )
        """
        res = supabase_client.from_("shipments").select(query).eq("shipment_id", shipment_id).single().execute()

        if res.data:
            return res.data
        else:
            raise HTTPException(status_code=404, detail="Shipment not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shipment details: {str(e)}")

@app.get("/admin/kpis", tags=["Data Fetching"])
async def get_admin_kpis():
    try:
        response = supabase_client.from_("daily_on_time_rate").select("*").execute()

        if hasattr(response, "data") and isinstance(response.data, list):
            # Sort in Python if data exists
            sorted_data = sorted(
                response.data, key=lambda item: item["ship_date"], reverse=True
            )
            return sorted_data[:30]
        else:
            # If there's an actual error, log it and raise
            error_details = getattr(response, "error", "An unknown error occurred.")
            print(f"!!! KPI Fetch Error: {error_details}")
            raise Exception(f"Failed to fetch KPI data: {error_details}")

    except Exception as e:
        print(f"An exception occurred in get_admin_kpis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Knowledge Base ===
@app.get("/knowledge/documents", tags=["Knowledge Base"])
async def list_available_documents():
    """Fetches a list of source documents. Protected: Manager role required."""
    try:
        response = (
            supabase_client.from_("documents")
            .select("source_id, source_type, region_id, ts")
            .execute()
        )
        if response.data:
            unique_documents = {doc["source_id"]: doc for doc in response.data}.values()
            return list(unique_documents)
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch documents list.")


@app.get("/knowledge/schemas", tags=["Knowledge Base"])
async def list_table_schemas():
    """Returns a predefined list of key table schemas. Protected: Manager role required."""
    schemas = {
        "shipments": ["shipment_id", "status", "current_eta"],
        "orders": ["order_id", "status"],
        "inventory": ["sku", "product_name", "qty_on_hand"],
        "vehicles": ["vehicle_id", "vehicle_type"],
        "profiles": ["id", "name", "role"],
    }
    return schemas


# # === Role-Specific Actions ===
# @app.post("/incidents", tags=["Role Actions"], status_code=201)
# async def create_incident_report(
#     report: IncidentReport,
#     current_user: User = Depends(require_roles(["delivery_guy"])),
# ):
#     """Endpoint for delivery partners to submit incident reports. Protected: Delivery Guy role required."""
#     print(
#         f"User {current_user.id} ({current_user.role}) reported an incident for route: {report.route_description}"
#     )
#     try:
#         # This is a simplified insertion. A real pipeline would handle embedding.
#         full_report_text = f"LIVE REPORT from {current_user.id}\nROUTE: {report.route_description}\nDETAILS: {report.details}"
#         supabase_client.from_("documents").insert(
#             {
#                 "source_type": "incident_report_live",
#                 "source_id": f"live_report_{current_user.id}_{traceback.extract_stack()[-1].lineno}",
#                 "text_snippet": full_report_text,
#                 "region_id": "SoCal",  # Placeholder
#             }
#         ).execute()
#         return {"message": "Incident report received and logged successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to log incident: {str(e)}")

ALLOWED_TABLES = [
    "profiles",
    "orders",
    "shipments",
    "vehicles",
    "warehouses",
    "inventory",
    "packaging_types",
    "fuel_prices",
    "agent_audit_logs",
    "documents",
]


@app.get("/browser/{table_name}", tags=["Data Browser"])
async def browse_table_data(
    table_name: str,
    limit: int = Query(25, ge=1, le=100),  # Default limit 25, min 1, max 100
    offset: int = Query(0, ge=0),  # Default offset 0, min 0
):
    """
    Fetches a paginated list of rows from a specified table.
    """
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(
            status_code=403, detail=f"Access to table '{table_name}' is forbidden."
        )

    try:
        # First, get the total count of rows in the table for pagination info
        count_response = (
            supabase_client.from_(table_name)
            .select("*", count="exact")
            .limit(0)
            .execute()
        )
        total_count = count_response.count if count_response.count is not None else 0

        # Then, fetch the paginated data
        data_response = (
            supabase_client.from_(table_name)
            .select("*")
            .range(offset, offset + limit - 1)
            .execute()
        )

        if data_response.data:
            return {"total": total_count, "data": data_response.data}
        elif data_response.error:
            raise HTTPException(status_code=500, detail=data_response.error.message)
        else:
            return {"total": 0, "data": []}  # Return empty if table has no data

    except Exception as e:
        print(f"Error browsing table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
