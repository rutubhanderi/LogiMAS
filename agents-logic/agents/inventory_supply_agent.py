import os
from dotenv import load_dotenv
from typing import Dict, Callable, Optional, List

# Core LangChain and LLM imports
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.documents import Document

# --- Imports for Astra DB (Vector RAG) ---
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBStore

# --- Imports for Supabase PostgreSQL (Text-to-SQL) ---
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

agent_llm = ChatGroq(
    model="llama3-70b-8192", 
    temperature=0,  
    groq_api_key=groq_api_key
)

# ==============================================================================
# 1. DATABASE & KNOWLEDGE BASE SETUP
# ==============================================================================

vstore = None
db_connection = None

def get_knowledge_base() -> Optional[AstraDBStore]:
    """
    Initializes and returns a connection to the Astra DB vector store for RAG.
    """
    global vstore
    if vstore is None:
        required_vars = ["ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "OPENAI_API_KEY"]
        if not all(var in os.environ for var in required_vars):
            print("❌ Error: Required environment variables for Astra DB are not set.")
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
            print(f"❌ Error connecting to Astra DB: {e}")
            return None
    return vstore

def get_sql_database_connection() -> Optional[SQLDatabase]:
    """
    Initializes and returns a connection to the Supabase PostgreSQL database.
    """
    global db_connection
    if db_connection is None:
        required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
        if not all(var in os.environ for var in required_vars):
            print("❌ Error: Required Postgres connection variables not set in .env file.")
            return None
        
        try:
            db_uri = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
            db_connection = SQLDatabase.from_uri(db_uri)
            print("✅ Successfully connected to Supabase PostgreSQL database.")
        except Exception as e:
            print(f"❌ Error connecting to Supabase PostgreSQL: {e}")
            return None
    return db_connection

# ==============================================================================
# 2. AGENT TOOL DEFINITIONS
# ==============================================================================

@tool
def query_product_knowledge_base(query: str) -> str:
    """
    Searches the vector database for products based on a natural language query about their features, descriptions, or categories.
    Use this for SEMANTIC questions like 'Which products are fragile?' or 'Tell me about electronic kits for beginners'.
    - query: The natural language question about the products.
    """
    print(f"--- TOOL CALLED: query_product_knowledge_base(query='{query}') ---")
    knowledge_base = get_knowledge_base()
    if not knowledge_base:
        return "Error: Knowledge base (Astra DB) connection is not available."

    try:
        results: List[Document] = knowledge_base.similarity_search(query, k=3)
        if not results:
            return "No relevant products found in the knowledge base for that query."

        formatted_results = "Found the following relevant products:\n"
        for i, doc in enumerate(results):
            metadata = doc.metadata
            formatted_results += f"\n--- Result {i+1} ---\n"
            formatted_results += f"ItemID: {metadata.get('item_id')}\n"
            formatted_results += f"Name: {metadata.get('name')}\n"
            formatted_results += f"Category: {metadata.get('category')}\n"
            formatted_results += f"Summary: {doc.page_content.split('Description:')[1].split('Special Handling:')[0].strip()}\n"
        return formatted_results
    except Exception as e:
        return f"Error during similarity search: {e}"


@tool
def query_logistics_database(question: str) -> str:
    """
    Use this tool to answer precise, analytical questions about logistics data using SQL.
    This includes stock levels, sales history, warehouse details, transport routes, and delivery statuses.
    Input MUST be a clear, natural language question.
    Example questions:
    - 'What is the total quantity of PROD-00001 sold in the last 90 days?'
    - 'Which warehouse has the most stock of PROD-00002?'
    - 'What is the status of restock delivery with confirmation_id RSTK-000001?'
    """
    print(f"--- TOOL CALLED: query_logistics_database(question='{question}') ---")
    db = get_sql_database_connection()
    if not db:
        return "Error: SQL Database (Supabase) connection not available."
        
    try:
        query_chain = create_sql_query_chain(agent_llm, db)
        sql_query = query_chain.invoke({"question": question})

        if any(keyword in sql_query.upper() for keyword in ["UPDATE", "DELETE", "INSERT", "DROP", "ALTER"]):
            return "Error: Read-only access. Cannot execute mutating statements."

        print(f"Generated SQL Query: {sql_query}")
        result = db.run(sql_query)
        
        # Check for empty or unusual results that might indicate an error or no data
        if not result or result == "[]":
            return "Query executed successfully, but no data was found for your question."
            
        return f"Query executed successfully. Result: {result}"
    except Exception as e:
        return f"Error executing query: {e}. Please rephrase your question or check table/column names."

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
                "You are the Inventory & Supply Agent, a logistics expert. You have two powerful data tools:\n"
                "1. `query_product_knowledge_base`: Use this for SEMANTIC SEARCH on product features, descriptions, and types (e.g., 'find a fragile product', 'what are some clothing items?'). This is for finding *what kind* of product exists.\n"
                "2. `query_logistics_database`: Use this for PRECISE, ANALYTICAL queries on structured data like stock counts, sales figures, warehouse capacity, and delivery statuses (e.g., 'how many of X are in warehouse Y?', 'what is the total sales for last month?'). This is for getting specific *numbers, lists, and statuses*.\n\n"
                "You must choose the correct tool for the user's question. If the user asks for a specific count, number, or status, use the SQL database. If they ask for a description or a 'type of' product, use the knowledge base. Do not make up information; always use your tools."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    tools = [query_product_knowledge_base, query_logistics_database]
    llm_with_tools = agent_llm.bind_tools(tools)
    return prompt | llm_with_tools

def get_available_tools() -> Dict[str, Callable]:
    """
    Returns a dictionary mapping tool names to their callable functions,
    which is used by the orchestrator to execute the tool calls.
    """
    return {
        "query_product_knowledge_base": query_product_knowledge_base,
        "query_logistics_database": query_logistics_database,
    }

# ==============================================================================
# 4. TEST EXECUTION BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("\n--- Testing Inventory & Supply Agent with Supabase SQL and AstraDB RAG ---")

    inventory_agent = create_inventory_supply_agent()
    available_tools = get_available_tools()

    # --- CHOOSE A QUERY TO TEST ---

    # 1. Test Query for SQL Database (Analytical Question)
    query = "What is the total sales quantity for item PROD-00001 in the last year?"
    
    # 2. Test Query for Vector Database (Semantic Question)
    # query = "I need to ship something for a household that is not hazardous, what can you find?"

    print(f'User Query: "{query}"')
    chat_history = [HumanMessage(content=query)]

    while True:
        print("\n[1. Invoking agent with current history...]")
        response = inventory_agent.invoke({"messages": chat_history})
        print("✅ API call successful! Agent responded.")
        chat_history.append(response)

        if not response.tool_calls:
            print("\n[FINAL ANSWER RECEIVED]")
            print("=" * 50)
            print(response.content)
            print("=" * 50)
            break

        print(f"\n[2. Agent requested tool calls: {[tc['name'] for tc in response.tool_calls]}]")

        tool_messages = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_to_call = available_tools.get(tool_name)
            if tool_to_call:
                tool_output = tool_to_call.invoke(tool_call["args"])
                print(f"Tool Output ({tool_name}): {tool_output}")
                tool_messages.append(
                    ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
                )

        chat_history.extend(tool_messages)
        print("[3. Added tool results to history. Looping back to agent...]")