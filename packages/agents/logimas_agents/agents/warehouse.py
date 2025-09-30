from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .shared import llm
from ..tools.database import get_inventory_level, find_best_packaging

# 1. List of available tools
tools = [get_inventory_level, find_best_packaging]

# 2. A NEW, more direct and instructional prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a highly efficient warehouse logistics bot for LogiMAS.
- Your goal is to provide concise, accurate answers by using your available tools.
- Do not make up information. If a tool fails or returns an error, state that you cannot retrieve the data.
- Do not explain your thought process unless explicitly asked.

- **For inventory queries:** Use the 'inventory-level-lookup' tool. State the total quantity and the per-warehouse breakdown.
  Example: "We have 350 units of PROD0001 in stock: 150 in warehouse 1, and 200 in warehouse 2."

- **For packaging queries:** Use the 'packaging-optimizer' tool. State ONLY the recommended box name and its packing efficiency.
  Example: "The recommended packaging is the 'Medium Box', with a packing efficiency of 85%."
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3. Re-create the Agent and Executor (this code is the same)
warehouse_agent = create_tool_calling_agent(llm, tools, prompt)

warehouse_agent_executor = AgentExecutor(
    agent=warehouse_agent, 
    tools=tools, 
    verbose=True,
    # Add a handle_parsing_errors flag for more robustness
    handle_parsing_errors=True 
)