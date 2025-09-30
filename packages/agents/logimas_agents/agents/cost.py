from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .shared import llm
from ..tools.database import calculate_route_fuel_cost

tools = [calculate_route_fuel_cost]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a cost optimization analyst for LogiMAS. Your primary function is to calculate the fuel cost for shipments using your available tool. When asked about cost, provide a clear summary including the distance, fuel type, and the final estimated cost."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

cost_agent = create_tool_calling_agent(llm, tools, prompt)

cost_agent_executor = AgentExecutor(
    agent=cost_agent, 
    tools=tools, 
    verbose=True
)