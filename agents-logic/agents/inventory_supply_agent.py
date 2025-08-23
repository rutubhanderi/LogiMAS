import os
from dotenv import load_dotenv
from typing import Dict, Callable, Optional
import json
import random

# LangChain Imports
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

# --- Environment and LLM Setup ---
# Ensures the agent can run independently for testing.
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# A capable model is needed for reasoning about tools and data.
agent_llm = ChatGroq(
    model="llama3-70b-8192", temperature=0.2, groq_api_key=groq_api_key
)

# ==============================================================================
# 1. MOCK DATABASE & TOOL DEFINITIONS
# ==============================================================================
# This simulates a real inventory database for our tools to interact with.
mock_inventory_db = {
    "MUM-WH-01": {  # Mumbai Warehouse
        "PROD-123": 800,  # Standard Electronics Kit
        "PROD-456": 250,  # Premium Gadget Pack
    },
    "BLR-WH-02": {  # Bangalore Warehouse
        "PROD-123": 150,
        "PROD-456": 300,
    },
    "DEL-WH-03": {  # Delhi Warehouse
        "PROD-123": 600,
        "PROD-789": 1200,  # Basic Supply Crate
    },
}


@tool
def get_current_stock_levels(item_id: str, warehouse_id: Optional[str] = None) -> str:
    """
    Checks the current stock quantity for a specific item across one or all warehouses.
    Use this to get real-time inventory data.
    - item_id: The unique product identifier (e.g., 'PROD-123').
    - warehouse_id (optional): The specific warehouse ID (e.g., 'BLR-WH-02'). If not provided, returns stock for all warehouses.
    """
    print(
        f"--- TOOL CALLED: get_current_stock_levels(item_id='{item_id}', warehouse_id='{warehouse_id}') ---"
    )
    if warehouse_id:
        stock = mock_inventory_db.get(warehouse_id, {}).get(item_id)
        if stock is not None:
            return json.dumps({warehouse_id: {item_id: stock}})
        else:
            return f"Error: Item '{item_id}' not found in warehouse '{warehouse_id}'."
    else:
        results = {}
        for wh_id, inventory in mock_inventory_db.items():
            if item_id in inventory:
                results[wh_id] = {item_id: inventory[item_id]}
        if not results:
            return f"Error: Item '{item_id}' not found in any warehouse."
        return json.dumps(results)


@tool
def forecast_demand(item_id: str, time_period_days: int) -> str:
    """
    Forecasts the expected sales demand for a given item over a specific time period.
    Use this to predict future inventory needs and prevent stockouts.
    - item_id: The unique product identifier (e.g., 'PROD-456').
    - time_period_days: The number of days to forecast (e.g., 30 for one month).
    """
    print(
        f"--- TOOL CALLED: forecast_demand(item_id='{item_id}', time_period_days={time_period_days}) ---"
    )
    # Simple mock forecast: base demand + some randomness
    base_demand = 10 if "123" in item_id else 15
    forecast = int((base_demand * time_period_days) * (random.uniform(0.8, 1.2)))
    return f"Forecasted demand for item '{item_id}' over the next {time_period_days} days is approximately {forecast} units."


@tool
def schedule_restock_delivery(
    item_id: str, quantity: int, source_warehouse: str, destination_warehouse: str
) -> str:
    """
    Schedules a transfer of stock from a source warehouse to a destination warehouse.
    Use this tool only after confirming a stock shortage and identifying a source with sufficient inventory.
    This is an action that creates a shipment order.
    - item_id: The unique product identifier.
    - quantity: The number of units to transfer.
    - source_warehouse: The ID of the warehouse to ship from.
    - destination_warehouse: The ID of the warehouse to ship to.
    """
    print(f"--- TOOL CALLED: schedule_restock_delivery(...) ---")
    if (
        source_warehouse not in mock_inventory_db
        or destination_warehouse not in mock_inventory_db
    ):
        return "Error: Invalid source or destination warehouse ID."

    if mock_inventory_db.get(source_warehouse, {}).get(item_id, 0) < quantity:
        return f"Error: Insufficient stock for item '{item_id}' at source warehouse '{source_warehouse}'."

    confirmation_id = f"RSTK-{random.randint(10000, 99999)}"
    return f"Success! Restock delivery scheduled. Confirmation ID: {confirmation_id}. {quantity} units of '{item_id}' will be transferred from {source_warehouse} to {destination_warehouse}."


# ==============================================================================
# 2. AGENT DEFINITION
# ==============================================================================


def create_inventory_supply_agent():
    """
    Creates and returns the Inventory & Supply Agent chain.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Inventory & Supply Agent. Your purpose is to manage logistics by monitoring stock, forecasting demand, and scheduling restocking. "
                "You must use your tools to gather all necessary data before making a recommendation or taking an action. "
                "When a user reports a potential shortage, your process is: "
                "1. Use `get_current_stock_levels` to verify the current inventory at the relevant warehouse. "
                "2. Use `forecast_demand` to understand the future need. "
                "3. If a shortage is confirmed, check other warehouses for surplus stock. "
                "4. If a surplus is found elsewhere, use `schedule_restock_delivery` to resolve the shortage. "
                "Provide clear, step-by-step responses to the user, explaining your actions and findings.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    tools = [get_current_stock_levels, forecast_demand, schedule_restock_delivery]
    llm_with_tools = agent_llm.bind_tools(tools)
    return prompt | llm_with_tools


def get_available_tools() -> Dict[str, Callable]:
    """
    Returns a dictionary mapping tool names to their callable functions.
    """
    return {
        "get_current_stock_levels": get_current_stock_levels,
        "forecast_demand": forecast_demand,
        "schedule_restock_delivery": schedule_restock_delivery,
    }


# ==============================================================================
# 3. TEST EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("\n--- Testing Inventory & Supply Agent ---")

    inventory_agent = create_inventory_supply_agent()
    available_tools = get_available_tools()

    # A complex query that requires multiple tool calls in sequence
    query = "We are seeing a spike in demand for 'PROD-123' at the Bangalore warehouse (BLR-WH-02). Is a shortage likely within the next 30 days? If so, schedule a restock of 500 units from the Mumbai warehouse (MUM-WH-01)."
    print(f'User Query: "{query}"')

    chat_history = [HumanMessage(content=query)]

    while True:
        print("\n[1. Invoking agent with current history...]")
        response = inventory_agent.invoke({"messages": chat_history})
        print("✅ API call successful! Agent responded.")
        chat_history.append(response)

        if not response.tool_calls:
            print("\n[FINAL ANSWER RECEIVED]")
            print("=" * 40)
            print(response.content)
            print("=" * 40)
            break

        print(
            f"\n[2. Agent requested tool calls: {[tc['name'] for tc in response.tool_calls]}]"
        )

        tool_messages = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_to_call = available_tools.get(tool_name)
            if tool_to_call:
                tool_output = tool_to_call.invoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                )

        chat_history.extend(tool_messages)
        print("[3. Added tool results to history. Looping back to agent...]")
