from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .shared import llm
from ..tools.database import get_shipment_status

# 1. Define the list of tools this agent can use
tools = [get_shipment_status]

# 2. Create the Agent Prompt
# This special prompt tells the agent it has tools and how to use them.
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful tracking assistant for the LogiMAS system. You have access to a tool that can look up shipment information. Only use the tool if a valid shipment ID is provided in the user's query."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), # This is where the agent thinks about which tool to use.
])

# 3. Create the Agent
# This binds the LLM, tools, and prompt together into a runnable agent.
tool_calling_agent = create_tool_calling_agent(llm, tools, prompt)

# 4. Create the Agent Executor
# This is the runtime for the agent. It's what actually invokes the tools.
tracking_agent_executor = AgentExecutor(
    agent=tool_calling_agent, 
    tools=tools, 
    verbose=True # Set to True to see the agent's thought process
)