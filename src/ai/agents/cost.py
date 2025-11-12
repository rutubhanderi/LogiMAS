"""
Cost agent factory with lazy imports and fallback.

Provides get_cost_agent_executor() which returns a LangChain AgentExecutor.
"""
from typing import Any, Dict

# Use the project's shared LLM instance
from .shared import llm
# Import the specific tools for this agent
from ..tools.database import calculate_route_fuel_cost

# The list of tools this agent can use
tools = [calculate_route_fuel_cost]


class _FallbackExecutor:
    """A minimal executor used when LangChain agent creation fails."""
    def __init__(self, llm):
        self.llm = llm

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_input = payload.get("input") or ""
        # A simple pass-through to the LLM if agent fails
        response = self.llm.invoke(user_input)
        return {"output": response.content}


def get_cost_agent_executor():
    """
    Factory function to create and return the cost agent executor.
    """
    try:
        # Modern, direct imports
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents import create_tool_calling_agent, AgentExecutor

        # A clear, directive prompt for the cost agent
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a cost optimization analyst for LogiMAS. Your primary function is to calculate the fuel cost for shipments using the 'route-fuel-cost-calculator' tool. When asked about cost, provide a clear summary including the distance, fuel type, and the final estimated cost."
            ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent runnable
        agent = create_tool_calling_agent(llm, tools, prompt)

        # Create the executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
        )
        return executor

    except ImportError as ie:
        print(f"[ERROR] Failed to import LangChain dependencies for Cost Agent: {ie}")
        print("[WARNING] Cost Agent is using a fallback LLM. Tool-calling will not work.")
        return _FallbackExecutor(llm)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while building Cost Agent: {e}")
        print("[WARNING] Cost Agent is using a fallback LLM. Tool-calling will not work.")
        return _FallbackExecutor(llm)