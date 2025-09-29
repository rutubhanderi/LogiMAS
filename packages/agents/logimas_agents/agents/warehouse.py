from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .shared import llm
from ..tools.database import get_inventory_level # Import our new tool

# 1. Define the list of tools this agent can use
tools = [get_inventory_level]

# 2. Create the Agent Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a warehouse operations assistant for LogiMAS. Your specialty is checking inventory levels. Use your tool to answer questions about product stock quantities. When asked about stock, always provide the total quantity and a breakdown by warehouse if available."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3. Create the Agent
warehouse_agent = create_tool_calling_agent(llm, tools, prompt)

# 4. Create the Agent Executor
warehouse_agent_executor = AgentExecutor(
    agent=warehouse_agent, 
    tools=tools, 
    verbose=True # Keep verbose=True for debugging
)