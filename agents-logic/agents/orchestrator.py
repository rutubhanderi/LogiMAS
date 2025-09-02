import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Callable, Dict

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from operator import itemgetter

# Import your agent creation functions and tools
from mobility_control_agent import (
    create_mobility_agent,
    get_available_tools as get_mobility_tools,
)
from inventory_supply_agent import (
    create_inventory_supply_agent,
    get_available_tools as get_inventory_tools,
)
from cost_optimization_agent import (
    create_cost_optimization_agent,
    get_available_tools as get_cost_tools,
)

# --- Central Coordinator Setup ---
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
coordinator_llm = ChatGroq(
    model="llama-3.3-70b-versatile", temperature=0, groq_api_key=groq_api_key
)

routing_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are a coordinator agent in a logistics system. Your task is to read the user's query and decide which specialized agent should handle it.
The query may require a combination of agents, but you must choose only the *best* primary agent to start the task.

Specialized agents:
- 'Mobility Agent': Optimizes delivery routes using live traffic and weather data. Handles questions about "fastest route", "safest path", "traffic", or "weather disruptions".
- 'Inventory & Supply Agent': Monitors stock levels, predicts demand, and schedules restocking. Handles questions about "stock levels", "inventory", "demand forecast", or "restocking".
- 'Cost Optimization Agent': Minimizes transportation and handling costs. Handles questions about "costs", "cheapest way", "profitability", or "batching shipments".
- 'End User': For when the query is a greeting, a thank you, or a general question not related to logistics.

Rules:
- Output only the agent name from the list above, nothing else.

User Query: {query}
Answer:""",
)
routing_chain = routing_prompt | coordinator_llm


# ==============================================================================
# 1. Define the State for the Graph
# ==============================================================================

class AgentState(TypedDict):
    messages: List[BaseMessage]
    next_agent: str


# ==============================================================================
# 2. Define the Nodes of the Graph
# ==============================================================================



def coordinator_node(state: AgentState) -> AgentState:
    """
    This node runs the routing logic to decide which agent should act next.
    """
    print("---NODE: COORDINATOR---")
    
    last_message = state["messages"][-1]

    
    result = routing_chain.invoke({"query": last_message.content})
    agent_name = result.content.strip()

    print(f"Coordinator decision: Route to '{agent_name}'")
    return {"next_agent": agent_name}


def agent_node(
    state: AgentState, agent_creator: Callable, tool_getter: Callable
) -> AgentState:
    """
    This is a generic node that executes any of our specialized agents.
    It handles the complete tool-calling loop for the agent.
    """
    agent_name = state["next_agent"]
    print(f"---NODE: {agent_name.upper()}---")

    
    agent = agent_creator()
    available_tools = tool_getter()

    
    while True:
        response = agent.invoke({"messages": state["messages"]})

       
        if not response.tool_calls:
            print(f"---FINAL ANSWER from {agent_name}---")
            return {"messages": [response]}

      
        print(
            f"Agent requested tool calls: {[tc['name'] for tc in response.tool_calls]}"
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

        
        state["messages"].append(response)
        state["messages"].extend(tool_messages)
        


# ==============================================================================
# 3. Define the Edges and Build the Graph
# ==============================================================================

mobility_node = lambda state: agent_node(
    state, create_mobility_agent, get_mobility_tools
)
inventory_node = lambda state: agent_node(
    state, create_inventory_supply_agent, get_inventory_tools
)
cost_node = lambda state: agent_node(
    state, create_cost_optimization_agent, get_cost_tools
)


def router(state: AgentState) -> str:
    """
    This function directs the graph to the correct specialized agent node
    based on the coordinator's decision.
    """
    if "Mobility Agent" in state["next_agent"]:
        return "mobility_agent"
    elif "Inventory & Supply Agent" in state["next_agent"]:
        return "inventory_agent"
    elif "Cost Optimization Agent" in state["next_agent"]:
        return "cost_agent"
    else:
        return "end"  



workflow = StateGraph(AgentState)


workflow.add_node("coordinator", coordinator_node)
workflow.add_node("mobility_agent", mobility_node)
workflow.add_node("inventory_agent", inventory_node)
workflow.add_node("cost_agent", cost_node)


workflow.set_entry_point("coordinator")

workflow.add_conditional_edges(
    "coordinator",
    router,
    {
        "mobility_agent": "mobility_agent",
        "inventory_agent": "inventory_agent",
        "cost_agent": "cost_agent",
        "end": END,
    },
)

workflow.add_edge("mobility_agent", END)
workflow.add_edge("inventory_agent", END)
workflow.add_edge("cost_agent", END)

app = workflow.compile()


# ==============================================================================
# 4. Run the Orchestrator
# ==============================================================================
if __name__ == "__main__":
    queries = [
        "Given the heavy rains, what is the fastest and safest delivery route to Chennai?",
        "Do we have enough stock of PROD-456 at the Bangalore warehouse for the next 30 days?",
        "Find me the absolute cheapest way to ship a 200kg package from Mumbai to Delhi, and tell me if I can save more by waiting.",
        "A sudden spike in demand for PROD-123 in Delhi means we need 500 units urgently. Check the Mumbai warehouse and schedule a transfer if possible.",
        "Hello there!",
    ]

    for i, q in enumerate(queries):
        print(f"\n{'='*60}\n🚀 EXECUTING QUERY {i+1}: {q}\n{'='*60}")


        initial_state = {"messages": [HumanMessage(content=q)]}

        final_state = app.invoke(
            initial_state, {"recursion_limit": 10}
        )  
        final_answer = final_state["messages"][-1].content
        print(f"\n✅ FINAL RESPONSE:\n{final_answer}")
