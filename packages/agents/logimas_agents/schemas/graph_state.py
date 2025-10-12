from typing import List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """
    Represents the shared state of the agent graph.
    """
    initial_query: str = Field(description="The original user query.")
    
    # The agent router will populate this field
    next_agent: Optional[str] = Field(
        default=None, 
        description="The name of the next agent to be called."
    )
    
    # Each agent will append its output to this list
    intermediate_steps: List[str] = Field(
        default_factory=list, 
        description="A log of all agent outputs."
    )
    
    # Final response for the user
    final_response: str = Field(
        default="", 
        description="The final, aggregated response for the user."
    )