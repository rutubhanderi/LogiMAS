from fastapi import FastAPI
from pydantic import BaseModel
from .agents.coordinator import rag_chain

# --- API Definition ---
app = FastAPI(
    title="LogiMAS Agent Server",
    description="An API for interacting with the LogiMAS multi-agent system.",
    version="1.0.0",
)

# Pydantic model for the request body to ensure type safety
class QueryRequest(BaseModel):
    query: str

# --- API Endpoints ---
@app.get("/", tags=["Health"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "LogiMAS Agent Server is running."}


@app.post("/query/rag", tags=["Queries"])
async def query_rag_endpoint(request: QueryRequest):
    """
    Receives a user query, processes it through the RAG chain,
    and returns the model's generated answer.
    """
    try:
        # The .invoke() method runs the LangChain chain
        result = rag_chain.invoke(request.query)
        return {"answer": result}
    except Exception as e:
        # Basic error handling
        return {"error": str(e)}, 500