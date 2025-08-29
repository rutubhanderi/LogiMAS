import os
from dotenv import load_dotenv
from typing import Dict, Callable, Optional, List
import json
import random

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

# --- New Imports for RAG with Astra DB ---
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBStore
from langchain_core.documents import Document

# --- Load Environment Variables ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

agent_llm = ChatGroq(
    model="llama3-70b-8192", temperature=0.2, groq_api_key=groq_api_key
)

# ==============================================================================
# 1. RAG KNOWLEDGE BASE SETUP
# ==============================================================================

# Global variable to hold our vector store connection
vstore = None

def get_knowledge_base() -> Optional[AstraDBStore]:
    """
    Initializes and returns a connection to the Astra DB vector store.
    """
    global vstore
    if vstore is None:
        required_vars = ["ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "OPENAI_API_KEY"]
        if not all(var in os.environ for var in required_vars):
            print("Error: Required environment variables for Astra DB are not set.")
            return None

        try:
            embedding_model = OpenAIEmbeddings()
            vstore = AstraDBStore(
                collection_name="product_knowledge_base",
                embedding=embedding_model,
                api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
                token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            )
            print("✅ Successfully connected to Astra DB knowledge base.")
        except Exception as e:
            print(f"Error connecting to Astra DB: {e}")
            return None
    return vstore

# ==============================================================================
# 2. MOCK DATABASE & TOOL DEFINITIONS
# ==============================================================================

mock_inventory_db = {
    # ... (rest of the mock data remains the same)
    "MUM-WH-01": {"PROD-00001": 800, "PROD-00002": 250},
    "BLR-WH-02": {"PROD-00001": 150, "PROD-00002": 300},
    "DEL-WH-03": {"PROD-00001": 600, "PROD-00003": 1200},
}

# --- NEW RAG-powered Tool ---
@tool
def query_product_knowledge_base(query: str) -> str:
    """
    Searches the vector database for products based on a natural language query.
    Use this to find products, get their details, descriptions, or answer questions like 'Which products are fragile?' or 'Tell me about electronic kits'.
    - query: The natural language question about the products.
    """
    print(f"--- TOOL CALLED: query_product_knowledge_base(query='{query}') ---")
    knowledge_base = get_knowledge_base()
    if not knowledge_base:
        return "Error: Knowledge base is not available."

    # Perform a similarity search
    results: List[Document] = knowledge_base.similarity_search(query, k=3) # Get top 3 results

    if not results:
        return "No relevant products found in the knowledge base for that query."

    # Format the results into a readable string for the LLM
    formatted_results = "Found the following relevant products:\n"
    for i, doc in enumerate(results):
        metadata = doc.metadata
        formatted_results += f"\n--- Result {i+1} ---\n"
        formatted_results += f"ItemID: {metadata.get('item_id')}\n"
        formatted_results += f"Name: {metadata.get('name')}\n"
        formatted_results += f"Category: {metadata.get('category')}\n"
        formatted_results += f"Is Fragile: {metadata.get('is_fragile')}\n"
        formatted_results += f"Weight (kg): {metadata.get('unit_weight_kg')}\n"
        formatted_results += f"Summary: {doc.page_content.split('Description:')[1].split('Special Handling:')[0].strip()}\n"

    return formatted_results

@tool
def get_current_stock_levels(item_id: str, warehouse_id: Optional[str] = None) -> str:
    # ... (this tool remains unchanged)
    print(f"--- TOOL CALLED: get_current_stock_levels(...) ---")
    # ... implementation ...
    return f"Stock for {item_id} at {warehouse_id} is 500 units."

@tool
def forecast_demand(item_id: str, time_period_days: int) -> str:
    # ... (this tool remains unchanged)
    print(f"--- TOOL CALLED: forecast_demand(...) ---")
    # ... implementation ...
    return f"Forecast for {item_id} is 300 units in {time_period_days} days."

@tool
def schedule_restock_delivery(item_id: str, quantity: int, source_warehouse: str, destination_warehouse: str) -> str:
    # ... (this tool remains unchanged)
    print(f"--- TOOL CALLED: schedule_restock_delivery(...) ---")
    # ... implementation ...
    return f"Restock scheduled for {quantity} units of {item_id}."

# ==============================================================================
# 3. AGENT DEFINITION
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
                "You now have a powerful tool, `query_product_knowledge_base`, to answer any questions about products using a vector database. "
                "Use it for queries like 'find a product that...', 'what are the details of...', or 'which products are...'. "
                "For stock levels, demand, or restocking actions, use the other specific tools. "
                "Your process is: "
                "1. If the user asks a question about product features, descriptions, or types, use `query_product_knowledge_base`. "
                "2. If the user asks about stock quantities, use `get_current_stock_levels`. "
                "3. Use `forecast_demand` to understand future needs. "
                "4. If a shortage is confirmed, check other warehouses for surplus stock, then use `schedule_restock_delivery`. "
                "Provide clear, step-by-step responses to the user, explaining your actions and findings.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # UPDATED list of tools for the agent
    tools = [
        query_product_knowledge_base, # The new RAG tool
        get_current_stock_levels,
        forecast_demand,
        schedule_restock_delivery
    ]
    llm_with_tools = agent_llm.bind_tools(tools)
    return prompt | llm_with_tools

def get_available_tools() -> Dict[str, Callable]:
    """
    Returns a dictionary mapping tool names to their callable functions.
    """
    return {
        "query_product_knowledge_base": query_product_knowledge_base,
        "get_current_stock_levels": get_current_stock_levels,
        "forecast_demand": forecast_demand,
        "schedule_restock_delivery": schedule_restock_delivery,
    }

# ==============================================================================
# 4. TEST EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("\n--- Testing Inventory & Supply Agent with RAG ---")

    inventory_agent = create_inventory_supply_agent()
    available_tools = get_available_tools()

    # New RAG-enabled query
    query_rag = "Find me a product that is fragile, suitable for electronics, and tell me its weight."

    chat_history = [HumanMessage(content=query_rag)]

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

        print(f"\n[2. Agent requested tool calls: {[tc['name'] for tc in response.tool_calls]}]")

        tool_messages = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_to_call = available_tools.get(tool_name)
            if tool_to_call:
                tool_output = tool_to_call.invoke(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))

        chat_history.extend(tool_messages)
        print("[3. Added tool results to history. Looping back to agent...]")