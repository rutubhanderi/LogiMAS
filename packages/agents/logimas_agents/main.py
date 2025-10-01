from fastapi import FastAPI
from pydantic import BaseModel

# Import the specific chains from the agent files
from .agents.coordinator import rag_chain
from .agents.mobility import mobility_rag_chain
from .chains.graph import agent_graph
from .schemas.graph_state import AgentState
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from .tools.database import supabase_client

# --- API Definition ---
app = FastAPI(
    title="LogiMAS Agent Server",
    description="An API for interacting with the LogiMAS multi-agent system.",
    version="1.0.0",
)

# --- CORS Middleware ---
# This is important to allow your Next.js app (running on localhost:3000)
# to make requests to this server (running on localhost:8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The origin of your frontend app
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Pydantic model for the request body to ensure type safety
class QueryRequest(BaseModel):
    query: str


# --- API Endpoints ---
@app.get("/", tags=["Health"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LogiMAS Agent Server is running."}


@app.post("/query/rag", tags=["Agents"])
async def query_rag_endpoint(request: QueryRequest):
    """
    Receives a user query, processes it through the RAG chain,
    and returns the model's generated answer.
    """
    try:
        result = rag_chain.invoke(request.query)
        return {"answer": result}
    except Exception as e:
        # Return a proper FastAPI response for errors
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/query/mobility", tags=["Agents"])
async def query_mobility_endpoint(request: QueryRequest):
    """
    Receives a query about a specific route, processes it through the Mobility Agent,
    and returns an analysis.
    """
    try:
        result = mobility_rag_chain.invoke(request.query)
        return {"analysis": result}
    except Exception as e:
        # Return a proper FastAPI response for errors
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/agent/invoke", tags=["Agent Graph"])
async def agent_invoke_endpoint(request: QueryRequest):
    """
    The main entry point for the multi-agent system.
    Invokes the LangGraph workflow and returns a single, clean JSON response.
    """
    try:
        inputs = {"initial_query": request.query}

        # Use .invoke() to run the entire graph and get only the final state.
        # This is guaranteed to run only once.
        final_state = agent_graph.invoke(inputs)

        # Get the clean response from the 'final_responder' node's output
        clean_response = final_state.get(
            "final_response", "Agent did not provide a response."
        )

        return {"response": clean_response}

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/shipments/{shipment_id}", tags=["Data Fetching"])
async def get_shipment_details(shipment_id: str):
    """
    Fetches detailed information for a single shipment, including related
    order and vehicle data. Replaces the Next.js BFF functionality.
    """
    try:
        response = (
            supabase_client.from_("shipments")
            .select(
                "shipment_id, status, current_eta, expected_arrival, orders(order_id, items), vehicles(vehicle_id, vehicle_type)"
            )
            .eq("shipment_id", shipment_id)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Shipment not found")

        return response.data
    except Exception as e:
        print(f"Error fetching shipment {shipment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/kpis", tags=["Data Fetching"])
async def get_admin_kpis():
    """
    Fetches KPI data from the daily_on_time_rate materialized view.
    Replaces the Next.js BFF functionality.
    """
    try:
        # Materialized views are read-only, so we can call them like tables
        response = (
            supabase_client.from_("daily_on_time_rate")
            .select("*")
            .order("ship_date", desc=True)
            .limit(30)
            .execute()
        )

        if hasattr(response, "data"):
            return response.data
        else:
            error_message = "Failed to fetch KPI data."

            if hasattr(response, "message"):
                error_message = response.message
            raise Exception(error_message)

    except Exception as e:
        print(f"Error fetching KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
