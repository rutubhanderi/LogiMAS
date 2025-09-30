import re
from langgraph.graph import StateGraph, END
from ..schemas.graph_state import AgentState
from ..agents.coordinator import rag_chain as coordinator_chain
from ..agents.mobility import mobility_rag_chain
from ..agents.tracking import tracking_agent_executor
from ..agents.warehouse import warehouse_agent_executor
# --- Agent Nodes Definition ---

def coordinator_node(state: AgentState) -> AgentState:
    """Invokes the general-purpose RAG coordinator agent."""
    print("--- Calling Coordinator Agent ---")
    # Use dot notation to access attributes of the Pydantic model
    query = state.initial_query
    response = coordinator_chain.invoke(query)
    state.intermediate_steps.append(f"Coordinator response: {response}")
    return state

def mobility_node(state: AgentState) -> AgentState:
    """Invokes the mobility-focused RAG agent."""
    print("--- Calling Mobility Agent ---")
    query = state.initial_query
    response = mobility_rag_chain.invoke(query)
    state.intermediate_steps.append(f"Mobility response: {response}")
    return state

def tracking_node(state: AgentState) -> AgentState:
    """Invokes the tool-equipped tracking agent."""
    print("--- Calling Tracking Agent ---")
    query = state.initial_query
    response = tracking_agent_executor.invoke({"input": query})
    agent_output = response.get('output', "The tracking agent did not provide a response.")
    state.intermediate_steps.append(f"Tracking response: {agent_output}")
    return state

def warehouse_node(state: AgentState) -> AgentState:
    """Invokes the tool-equipped warehouse agent."""
    print("--- Calling Warehouse Agent ---")
    query = state.initial_query
    response = warehouse_agent_executor.invoke({"input": query})
    agent_output = response.get('output', "The warehouse agent did not provide a response.")
    state.intermediate_steps.append(f"Warehouse response: {agent_output}")
    return state

def final_responder_node(state: AgentState) -> AgentState:
    """Generates the final response to the user."""
    print("--- Generating Final Response ---")
    final_response = state.intermediate_steps[-1]
    state.final_response = final_response
    return state


# --- Router Logic Definition ---

def route_logic(state: AgentState) -> AgentState:
    """
    Router that inspects the user query to determine the correct agent.
    """
    print("--- Routing Query ---")
    query = state.initial_query.lower()
    
    # Define keywords for each agent's specialty
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    
    warehouse_keywords = ["inventory", "stock", "how many", "quantity", "sku", "pack", "box", "package", "packaging"]
    
    mobility_keywords = ["route", "traffic", "mobility", "highway", "i-405", "congestion", "road"]

    # Check in a specific order of priority
    if re.search(uuid_pattern, query):
        print("--- Decision: Route to Tracking Agent (UUID detected) ---")
        state.next_agent = "tracking"
    elif any(keyword in query for keyword in warehouse_keywords):
        print("--- Decision: Route to Warehouse Agent (Keyword match) ---")
        state.next_agent = "warehouse"
    elif any(keyword in query for keyword in mobility_keywords):
        print("--- Decision: Route to Mobility Agent (Keyword match) ---")
        state.next_agent = "mobility"
    else:
        # Default to the general-purpose coordinator
        print("--- Decision: Route to Coordinator Agent (Default) ---")
        state.next_agent = "coordinator"
    return state

def get_next_agent(state: AgentState) -> str:
    """Helper function to read the router's decision from the state."""
    return state.next_agent

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("router", route_logic)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("mobility", mobility_node)
workflow.add_node("tracking", tracking_node)
workflow.add_node("warehouse", warehouse_node) 
workflow.add_node("final_responder", final_responder_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    get_next_agent,
    {
        "coordinator": "coordinator",
        "mobility": "mobility",
        "tracking": "tracking",

        "warehouse": "warehouse", 
    }
)

workflow.add_edge("coordinator", "final_responder")
workflow.add_edge("mobility", "final_responder")
workflow.add_edge("tracking", "final_responder")
workflow.add_edge("warehouse", "final_responder") 

workflow.add_edge("final_responder", END)

agent_graph = workflow.compile()   