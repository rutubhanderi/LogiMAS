from typing import Any, Dict
from .shared import llm
# Import the specific tools for this agent, including the new one
from ..tools.database import get_shipment_status, get_vehicle_location

# The list of tools this agent can use is now expanded
tools = [get_shipment_status, get_vehicle_location]


class _FallbackExecutor:
    """A minimal executor used when LangChain agent creation fails."""
    def __init__(self, llm):
        self.llm = llm

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_input = payload.get("input") or ""
        response = self.llm.invoke(user_input)
        return {"output": response.content}


def get_tracking_agent_executor():
    """
    Factory function to create and return the tracking agent executor.
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents import create_tool_calling_agent, AgentExecutor

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a helpful tracking assistant for the LogiMAS system.
- Your job is to provide shipment status and vehicle location updates.
- Use the 'shipment-status-lookup' tool to find the status and vehicle ID for a shipment.
- Use the 'vehicle-location-lookup' tool to find the current GPS coordinates of a vehicle."""
            ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)

        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
        )
        return executor

    except ImportError as ie:
        print(f"[ERROR] Failed to import LangChain dependencies for Tracking Agent: {ie}")
        return _FallbackExecutor(llm)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while building Tracking Agent: {e}")
        return _FallbackExecutor(llm)