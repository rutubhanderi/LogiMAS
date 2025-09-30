import re
from langgraph.graph import StateGraph, END
from ..schemas.graph_state import AgentState
from ..agents.coordinator import rag_chain as coordinator_chain
from ..agents.mobility import mobility_rag_chain
from ..agents.tracking import tracking_agent_executor
from ..agents.warehouse import warehouse_agent_executor
from ..agents.cost import cost_agent_executor
from ..agents.supplier import supplier_rag_chain

# --- Import the new logging utility ---
from ..tools.database import log_agent_decision

# --- Agent Nodes Definition with Integrated Logging ---

def coordinator_node(state: AgentState) -> AgentState:
    print("--- Calling Coordinator Agent ---")
    query = state.initial_query
    response = coordinator_chain.invoke(query)
    log_agent_decision(agent_name="coordinator", query=query, decision=response)
    state.intermediate_steps.append(f"Coordinator response: {response}")
    return state

def mobility_node(state: AgentState) -> AgentState:
    print("--- Calling Mobility Agent ---")
    query = state.initial_query
    response = mobility_rag_chain.invoke(query)
    log_agent_decision(agent_name="mobility", query=query, decision=response)
    state.intermediate_steps.append(f"Mobility response: {response}")
    return state

def tracking_node(state: AgentState) -> AgentState:
    print("--- Calling Tracking Agent ---")
    query = state.initial_query
    response = tracking_agent_executor.invoke({"input": query})
    log_agent_decision(agent_name="tracking", query=query, decision=response)
    agent_output = response.get('output', "The tracking agent did not provide a response.")
    state.intermediate_steps.append(f"Tracking response: {agent_output}")
    return state

def warehouse_node(state: AgentState) -> AgentState:
    print("--- Calling Warehouse Agent ---")
    query = state.initial_query
    response = warehouse_agent_executor.invoke({"input": query})
    log_agent_decision(agent_name="warehouse", query=query, decision=response)
    agent_output = response.get('output', "The warehouse agent did not provide a response.")
    state.intermediate_steps.append(f"Warehouse response: {agent_output}")
    return state

def cost_node(state: AgentState) -> AgentState:
    print("--- Calling Cost Agent ---")
    query = state.initial_query
    response = cost_agent_executor.invoke({"input": query})
    log_agent_decision(agent_name="cost", query=query, decision=response)
    agent_output = response.get('output', "The cost agent did not provide a response.")
    state.intermediate_steps.append(f"Cost response: {agent_output}")
    return state

def supplier_node(state: AgentState) -> AgentState:
    print("--- Calling Supplier Agent ---")
    query = state.initial_query
    response = supplier_rag_chain.invoke(query)
    log_agent_decision(agent_name="supplier", query=query, decision=response)
    state.intermediate_steps.append(f"Supplier response: {response}")
    return state

def final_responder_node(state: AgentState) -> AgentState:
    """Generates the final response to the user."""
    print("--- Generating Final Response ---")
    final_response = state.intermediate_steps[-1]
    state.final_response = final_response
    return state

# --- Router Logic Definition (No Changes Needed Here) ---
def route_logic(state: AgentState) -> AgentState:
    print("--- Routing Query ---")
    query = state.initial_query.lower()
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    warehouse_keywords = ["inventory", "stock", "how many", "quantity", "sku", "pack", "box", "package", "packaging"]
    mobility_keywords = ["route", "traffic", "mobility", "highway", "congestion", "road"]
    cost_keywords = ["cost", "price", "expensive", "cheap", "fuel"]
    supplier_keywords = ["supplier", "vendor", "contract", "lead time"]
    if re.search(uuid_pattern, query) and any(keyword in query for keyword in cost_keywords):
        state.next_agent = "cost"
    elif re.search(uuid_pattern, query):
        state.next_agent = "tracking"
    elif any(keyword in query for keyword in warehouse_keywords):
        state.next_agent = "warehouse"
    elif any(keyword in query for keyword in mobility_keywords):
        state.next_agent = "mobility"
    elif any(keyword in query for keyword in cost_keywords):
        state.next_agent = "cost"
    elif any(keyword in query for keyword in supplier_keywords):
        state.next_agent = "supplier"
    else:
        state.next_agent = "coordinator"
    return state

def get_next_agent(state: AgentState) -> str:
    return state.next_agent

# --- Graph Construction (No Changes Needed Here) ---
workflow = StateGraph(AgentState)
workflow.add_node("router", route_logic)
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("mobility", mobility_node)
workflow.add_node("tracking", tracking_node)
workflow.add_node("warehouse", warehouse_node)
workflow.add_node("cost", cost_node)
workflow.add_node("supplier", supplier_node)
workflow.add_node("final_responder", final_responder_node)
workflow.set_entry_point("router")
workflow.add_conditional_edges("router", get_next_agent, {"coordinator": "coordinator", "mobility": "mobility", "tracking": "tracking", "warehouse": "warehouse", "cost": "cost", "supplier": "supplier"})
workflow.add_edge("coordinator", "final_responder")
workflow.add_edge("mobility", "final_responder")
workflow.add_edge("tracking", "final_responder")
workflow.add_edge("warehouse", "final_responder")
workflow.add_edge("cost", "final_responder")
workflow.add_edge("supplier", "final_responder")
workflow.add_edge("final_responder", END)
agent_graph = workflow.compile()