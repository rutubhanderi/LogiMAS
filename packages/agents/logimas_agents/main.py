from fastapi import FastAPI
from pydantic import BaseModel

# Import the specific chains from the agent files
from .agents.coordinator import rag_chain
from .agents.mobility import mobility_rag_chain
from .chains.graph import agent_graph
from .schemas.graph_state import AgentState
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:3000"], # The origin of your frontend app
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
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
    Invokes the LangGraph workflow.
    """
    try:
        # The input to the graph is a dictionary matching the state
        inputs = {"initial_query": request.query}
        
        # .stream() can also be used here for streaming output
        final_state = agent_graph.invoke(inputs)
        
        return {"response": final_state.get('final_response', "No response generated.")}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"error": str(e)})