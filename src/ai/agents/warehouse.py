"""
Warehouse agent factory with lazy imports and fallback.

Provides get_warehouse_agent_executor() which returns a LangChain AgentExecutor.
"""
from typing import Any, Dict

# Use the project's shared LLM instance
from .shared import llm
# Import the specific tools for this agent
from ..tools.database import get_inventory_level, find_best_packaging

# The list of tools this agent can use
tools = [get_inventory_level, find_best_packaging]


class _FallbackExecutor:
    """A minimal executor used when LangChain agent creation fails."""
    def __init__(self, llm):
        self.llm = llm

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_input = payload.get("input") or ""
        # A simple pass-through to the LLM if agent fails
        response = self.llm.invoke(user_input)
        return {"output": response.content}


def get_warehouse_agent_executor():
    """
    Factory function to create and return the warehouse agent executor.
    """
    try:
        # Modern, direct imports
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents import create_tool_calling_agent, AgentExecutor

        # Your existing prompt for this agent is excellent because it gives clear examples.
        # We will keep it.
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a highly efficient warehouse logistics bot for LogiMAS.
- Your goal is to provide concise, accurate answers by using your available tools.
- Do not make up information. If a tool fails or returns an error, state that you cannot retrieve the data.
- **For inventory queries:** Use the 'inventory-level-lookup' tool. State the total quantity and the per-warehouse breakdown.
  Example: "We have 350 units of PROD0001 in stock: 150 in warehouse 1, and 200 in warehouse 2."
- **For packaging queries:** Use the 'packaging-optimizer' tool. State ONLY the recommended box name and its packing efficiency.
  Example: "The recommended packaging is the 'Medium Box', with a packing efficiency of 85%."
""",
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
        print(f"[ERROR] Failed to import LangChain dependencies for Warehouse Agent: {ie}")
        print("[WARNING] Warehouse Agent is using a fallback LLM. Tool-calling will not work.")
        return _FallbackExecutor(llm)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while building Warehouse Agent: {e}")
        print("[WARNING] Warehouse Agent is using a fallback LLM. Tool-calling will not work.")
        return _FallbackExecutor(llm)

# The global instance is no longer needed, as the graph will call the factory function.
# This prevents import-time errors from crashing the application.
warehouse_agent_executor = None
try:
    # We can still try to create it here for other potential uses,
    # but the graph should rely on the factory function.
    warehouse_agent_executor = get_warehouse_agent_executor()
except Exception:
    # The error is already printed inside the factory, so we can pass here.
    pass