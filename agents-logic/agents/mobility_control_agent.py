# mobility_control_agent.py (Corrected with full execution loop)

import os
from dotenv import load_dotenv
from typing import Dict, Callable

# LangChain Imports
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# Make sure to import HumanMessage AND ToolMessage
from langchain_core.messages import HumanMessage, ToolMessage

# --- Step 1: Initial Sanity Check ---
print("✅ Script Started: mobility_control_agent.py is running.")

# --- Environment and LLM Setup ---
print("... Loading environment variables from .env file...")
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("❌ ERROR: GROQ_API_KEY not found! Check your .env file.")
    exit()

print("... API Key found. Initializing ChatGroq model...")
try:
    agent_llm = ChatGroq(
        model="llama3-70b-8192", temperature=0.2, groq_api_key=groq_api_key
    )
    print("✅ ChatGroq model initialized successfully.")
except Exception as e:
    print(f"❌ ERROR: Failed to initialize ChatGroq model: {e}")
    exit()

# ==============================================================================
# 1. TOOL DEFINITIONS (No changes here)
# ==============================================================================


@tool
def get_live_traffic_data(location: str) -> str:
    """
    Gets real-time traffic data for a specified city or location.
    Use this to identify congestion, accidents, or road closures that affect travel time.
    """
    print(f"--- TOOL CALLED: get_live_traffic_data(location='{location}') ---")
    location_lower = location.lower()
    traffic_conditions = {
        "bangalore": "Heavy congestion on Outer Ring Road near Marathahalli. An accident is reported near Silk Board junction. Recommend avoiding these routes.",
        "chennai": "Moderate traffic on Anna Salai. Waterlogging reported on several coastal roads due to rain.",
        "mumbai": "Western Express Highway is heavily congested. Sea Link has moderate traffic flow.",
    }
    return traffic_conditions.get(
        location_lower, f"No specific traffic data available for {location}."
    )


@tool
def get_weather_forecast(location: str) -> str:
    """
    Gets the current and near-term weather forecast for a specified city or location.
    Use this to check for conditions like rain, storms, or fog that could impact delivery safety and times.
    """
    print(f"--- TOOL CALLED: get_weather_forecast(location='{location}') ---")
    location_lower = location.lower()
    weather_conditions = {
        "bangalore": "Clear skies, visibility is good. No weather-related disruptions expected.",
        "chennai": "Heavy rain and thunderstorms expected in the afternoon. High chance of localized flooding. Visibility will be poor.",
        "mumbai": "Cloudy with a chance of light showers. No major disruptions expected.",
    }
    return weather_conditions.get(
        location_lower, f"No specific weather data available for {location}."
    )


# ==============================================================================
# 2. AGENT DEFINITION (No changes here)
# ==============================================================================


def create_mobility_agent():
    # A more descriptive system prompt for better performance
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Mobility Agent, a specialized AI for logistics and route optimization. "
                "Your primary function is to find the most efficient and fastest delivery routes. "
                "You MUST use the provided tools to get real-time traffic and weather data to inform your decisions. "
                "First, gather all necessary information using the tools. Then, combine the information to provide a clear, actionable route suggestion. "
                "Explain your reasoning based on the data from the tools.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    tools = [get_live_traffic_data, get_weather_forecast]
    llm_with_tools = agent_llm.bind_tools(tools)
    return prompt | llm_with_tools


def get_available_tools() -> Dict[str, Callable]:
    return {
        "get_live_traffic_data": get_live_traffic_data,
        "get_weather_forecast": get_weather_forecast,
    }


# ==============================================================================
# 3. TEST EXECUTION BLOCK (THIS IS THE CORRECTED PART)
# ==============================================================================
if __name__ == "__main__":
    print("\n--- Starting Test Execution Block ---")

    mobility_agent = create_mobility_agent()
    available_tools = get_available_tools()

    query = "Given the current weather disruptions, what is the best route for an urgent delivery to Chennai?"
    print(f'User Query: "{query}"')

    chat_history = [HumanMessage(content=query)]

    # This loop continues until the agent gives a final answer instead of calling a tool.
    while True:
        print("\n[1. Invoking agent with current history...]")

        try:
            response = mobility_agent.invoke({"messages": chat_history})
            print("✅ API call successful! Agent responded.")
        except Exception as e:
            print(f"\n❌ An error occurred during the API call: {e}")
            break

        chat_history.append(response)

        # If there are no tool calls, the agent has its final answer. We print it and exit.
        if not response.tool_calls:
            print("\n[FINAL ANSWER RECEIVED]")
            print("=" * 40)
            print(response.content)
            print("=" * 40)
            break

        # If we are here, the agent wants to use one or more tools.
        print(
            f"\n[2. Agent requested tool calls: {[tc['name'] for tc in response.tool_calls]}]"
        )

        tool_messages = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_to_call = available_tools.get(tool_name)

            if tool_to_call:
                # Execute the tool function with the arguments provided by the LLM
                tool_output = tool_to_call.invoke(tool_call["args"])
                # Create a ToolMessage with the result to send back to the agent
                tool_messages.append(
                    ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                )

        # Add the tool results to the chat history
        chat_history.extend(tool_messages)
        print(
            "[3. Added tool results to history. Looping back to agent for next step...]"
        )
