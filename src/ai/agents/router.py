from enum import Enum
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from .shared import llm

# 1. Define the possible routes as an Enum for type safety
class Agent(str, Enum):
    COORDINATOR = "coordinator"
    TRACKING = "tracking"
    WAREHOUSE = "warehouse"
    COST = "cost"
    MOBILITY = "mobility"
    SUPPLIER = "supplier"

# 2. Create a Pydantic model for the LLM's output
# This forces the LLM to give us a clean, predictable response.
class RouterChoice(BaseModel):
    """The choice of the next agent to route the user's query to."""
    agent_name: Agent = Field(
        ...,
        description="The name of the agent that is best suited to handle the user's query."
    )

# 3. Create the prompt template
# This is where we describe the agents to the LLM so it can make an informed choice.
prompt_template = """
You are an expert dispatcher for a logistics AI system called LogiMAS. Your job is to analyze a user's query and route it to the most appropriate specialized agent.

Here are the available agents and their capabilities:

- **coordinator**: A generalist agent. Use this for complex questions that might require information from multiple sources, for questions about incidents (e.g., "what is the issue with..."), or if no other agent seems suitable.
- **tracking**: Use this for specific questions about the real-time status or location of a known shipment or vehicle. It is best when the query contains a shipment ID or vehicle ID.
- **warehouse**: Use this for questions about inventory, stock levels, product quantities (e.g., "how many..."), SKUs, or finding the best packaging for items.
- **cost**: Use this for questions specifically about the price, cost, or fuel expenses of a shipment.
- **mobility**: Use this for questions about traffic conditions, road closures, congestion, or route optimization.
- **supplier**: Use this for questions about suppliers, vendors, contracts, or material lead times.

Based on the user's query below, choose the single best agent to handle the request.

Query:
{query}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# 4. Create the LLM router chain
# We chain the prompt to the LLM and tell the LLM to structure its output
# according to our RouterChoice model.
llm_router_chain = prompt | llm.with_structured_output(RouterChoice)