import os
from dotenv import load_dotenv
from typing import Dict, Callable, Literal
import json
import random

# LangChain Imports
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

# --- Environment and LLM Setup ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

agent_llm = ChatGroq(
    model="llama3-70b-8192", temperature=0.2, groq_api_key=groq_api_key
)

# ==============================================================================
# 1. TOOL DEFINITIONS
# ==============================================================================
# These tools simulate querying cost databases and analysis services.


@tool
def get_transportation_costs(
    origin: str,
    destination: str,
    weight_kg: float,
    delivery_speed: Literal["standard", "express", "overnight"],
) -> str:
    """
    Calculates the transportation cost for a shipment based on origin, destination, weight, and delivery speed.
    Use this to compare the costs of different shipping options.
    """
    print(f"--- TOOL CALLED: get_transportation_costs(...) ---")

    # Mock cost calculation
    speed_multipliers = {"standard": 1.0, "express": 1.5, "overnight": 2.5}
    base_rate_per_kg = 0.5  # Base cost per kg for a standard distance

    if delivery_speed not in speed_multipliers:
        return f"Error: Invalid delivery speed '{delivery_speed}'. Must be 'standard', 'express', or 'overnight'."

    cost = 50 + (weight_kg * base_rate_per_kg * speed_multipliers[delivery_speed])

    return json.dumps(
        {
            "origin": origin,
            "destination": destination,
            "weight_kg": weight_kg,
            "delivery_speed": delivery_speed,
            "estimated_cost": round(cost, 2),
        }
    )


@tool
def get_handling_costs(
    warehouse_id: str,
    item_count: int,
    packaging_type: Literal["standard_box", "eco_mailer", "protective_crate"],
) -> str:
    """
    Calculates the warehouse handling and packaging costs for a set of items.
    Use this to determine costs incurred before transportation.
    """
    print(f"--- TOOL CALLED: get_handling_costs(...) ---")

    packaging_costs = {
        "standard_box": 0.50,
        "eco_mailer": 0.25,
        "protective_crate": 5.00,
    }
    labor_cost_per_item = 0.10

    if packaging_type not in packaging_costs:
        return f"Error: Invalid packaging type '{packaging_type}'."

    total_cost = (item_count * labor_cost_per_item) + (
        item_count * packaging_costs[packaging_type]
    )

    return json.dumps(
        {
            "warehouse_id": warehouse_id,
            "item_count": item_count,
            "packaging_type": packaging_type,
            "estimated_handling_cost": round(total_cost, 2),
        }
    )


@tool
def analyze_batching_options(destination: str, total_weight_kg: float) -> str:
    """
    Analyzes potential cost savings by waiting to batch the current shipment with other pending orders going to the same destination.
    Use this to find opportunities to reduce per-unit shipping costs.
    """
    print(f"--- TOOL CALLED: analyze_batching_options(...) ---")

    # Mock analysis: batching is more effective for smaller shipments
    if total_weight_kg > 500:
        return "Batching savings are minimal for shipments over 500kg as they already achieve good freight rates."

    # Simulate finding other orders to batch with
    potential_saving_percent = random.randint(15, 30)
    wait_time_hours = 24

    return (
        f"Potential cost savings of {potential_saving_percent}% on transportation "
        f"if you wait approximately {wait_time_hours} hours to batch this shipment with other orders "
        f"headed to {destination}."
    )


# ==============================================================================
# 2. AGENT DEFINITION
# ==============================================================================


def create_cost_optimization_agent():
    """
    Creates and returns the Cost Optimization Agent chain.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Cost Optimization Agent. Your primary objective is to find the most cost-effective strategies for logistics operations. "
                "You MUST use your tools to gather all necessary cost data before making a recommendation. "
                "Your process should be: "
                "1. Identify all cost components mentioned in the query (transport, handling, etc.). "
                "2. Use your tools to calculate these costs. Often, you will need to compare options (e.g., check standard vs. express shipping costs). "
                "3. Use the `analyze_batching_options` tool to see if waiting can reduce costs. "
                "4. Synthesize all findings into a clear recommendation. Present trade-offs to the user (e.g., 'You can save X dollars by choosing standard shipping, but it will take 2 days longer'). "
                "Break down the final cost estimate clearly.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    tools = [get_transportation_costs, get_handling_costs, analyze_batching_options]
    llm_with_tools = agent_llm.bind_tools(tools)
    return prompt | llm_with_tools


def get_available_tools() -> Dict[str, Callable]:
    """
    Returns a dictionary mapping tool names to their callable functions.
    """
    return {
        "get_transportation_costs": get_transportation_costs,
        "get_handling_costs": get_handling_costs,
        "analyze_batching_options": analyze_batching_options,
    }


# ==============================================================================
# 3. TEST EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("\n--- Testing Cost Optimization Agent ---")

    cost_agent = create_cost_optimization_agent()
    available_tools = get_available_tools()

    # A query designed to make the agent use multiple tools to form a strategy
    query = "I need to ship 150 items (400kg total) from Mumbai to Delhi. They will be packed in standard boxes at warehouse MUM-WH-01. Find me the most cost-effective shipping strategy."
    print(f'User Query: "{query}"')

    chat_history = [HumanMessage(content=query)]

    while True:
        print("\n[1. Invoking agent with current history...]")
        response = cost_agent.invoke({"messages": chat_history})
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
