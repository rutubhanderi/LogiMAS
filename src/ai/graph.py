import importlib
from langgraph.graph import StateGraph, END
from .schemas.graph_state import AgentState
from .tools.database import log_agent_decision

# --- Import the new LLM-powered router ---
# This replaces the old keyword-based logic.
from .agents.router import llm_router_chain

# Caches for lazily-built agent executors
_cached_executors = {
    "tracking": None,
    "warehouse": None,
    "cost": None,
}

# --- Agent Node Definitions ---
# These nodes are the destinations for our router. Their internal logic is unchanged.

def coordinator_node(state: AgentState) -> AgentState:
    print("--- Calling Coordinator Agent ---")
    query = state.initial_query
    # Lazily import the chain to avoid circular dependencies
    from .agents.coordinator import rag_chain as coordinator_chain
    response = coordinator_chain.invoke(query)
    log_agent_decision(agent_name="coordinator", query=query, decision=response)
    state.intermediate_steps.append(f"Coordinator response: {response}")
    return state


def mobility_node(state: AgentState) -> AgentState:
    print("--- Calling Mobility Agent ---")
    query = state.initial_query
    # Lazily import the chain
    from .agents.mobility import mobility_rag_chain
    response = mobility_rag_chain.invoke(query)
    log_agent_decision(agent_name="mobility", query=query, decision=response)
    state.intermediate_steps.append(f"Mobility response: {response}")
    return state


def tracking_node(state: AgentState) -> AgentState:
    print("--- Calling Tracking Agent ---")
    query = state.initial_query
    if _cached_executors["tracking"] is None:
        try:
            mod = importlib.import_module(".agents.tracking", package=__package__)
            _cached_executors["tracking"] = mod.get_tracking_agent_executor()
        except Exception as exc:
            print(f"[warning] could not import tracking agent module: {exc}")
    
    executor = _cached_executors["tracking"]
    response = executor.invoke({"input": query}) if executor else {"output": "Tracking agent unavailable."}
    
    log_agent_decision(agent_name="tracking", query=query, decision=response)
    agent_output = response.get("output", "The tracking agent did not provide a response.")
    state.intermediate_steps.append(f"Tracking response: {agent_output}")
    return state


def warehouse_node(state: AgentState) -> AgentState:
    print("--- Calling Warehouse Agent ---")
    query = state.initial_query
    if _cached_executors["warehouse"] is None:
        try:
            mod = importlib.import_module(".agents.warehouse", package=__package__)
            _cached_executors["warehouse"] = mod.get_warehouse_agent_executor()
        except Exception as exc:
            print(f"[warning] could not import warehouse agent module: {exc}")
    
    executor = _cached_executors["warehouse"]
    response = executor.invoke({"input": query}) if executor else {"output": "Warehouse agent unavailable."}

    log_agent_decision(agent_name="warehouse", query=query, decision=response)
    agent_output = response.get("output", "The warehouse agent did not provide a response.")
    state.intermediate_steps.append(f"Warehouse response: {agent_output}")
    return state


def cost_node(state: AgentState) -> AgentState:
    print("--- Calling Cost Agent ---")
    query = state.initial_query
    if _cached_executors["cost"] is None:
        try:
            mod = importlib.import_module(".agents.cost", package=__package__)
            _cached_executors["cost"] = mod.get_cost_agent_executor()
        except Exception as exc:
            print(f"[warning] could not import cost agent module: {exc}")

    executor = _cached_executors["cost"]
    response = executor.invoke({"input": query}) if executor else {"output": "Cost agent unavailable."}
    
    log_agent_decision(agent_name="cost", query=query, decision=response)
    agent_output = response.get("output", "The cost agent did not provide a response.")
    state.intermediate_steps.append(f"Cost response: {agent_output}")
    return state


def supplier_node(state: AgentState) -> AgentState:
    print("--- Calling Supplier Agent ---")
    query = state.initial_query
    # Lazily import the chain
    from .agents.supplier import supplier_rag_chain
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


# --- Intelligent Router Node ---
def route_logic(state: AgentState) -> AgentState:
    """
    Routes the query to the appropriate agent by asking an LLM for its recommendation.
    This is more robust than keyword-based routing.
    """
    print("--- Routing Query with LLM Router ---")
    query = state.initial_query

    # Call the intelligent router chain, which returns a structured Pydantic object
    router_choice = llm_router_chain.invoke({"query": query})
    
    # Get the chosen agent name from the structured output
    chosen_agent = router_choice.agent_name.value
    print(f"LLM Router chose: {chosen_agent}")
    
    state.next_agent = chosen_agent
    return state


def get_next_agent(state: AgentState) -> str:
    # This helper function reads the decision from the state and returns it
    return state.next_agent


# --- Graph Construction ---
# This defines the structure and flow of the agentic system.
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

# Based on the router's decision, conditionally call the chosen agent.
workflow.add_conditional_edges(
    "router",
    get_next_agent,
    {
        "coordinator": "coordinator",
        "mobility": "mobility",
        "tracking": "tracking",
        "warehouse": "warehouse",
        "cost": "cost",
        "supplier": "supplier",
    },
)

# After any agent runs, its output goes to the final responder.
workflow.add_edge("coordinator", "final_responder")
workflow.add_edge("mobility", "final_responder")
workflow.add_edge("tracking", "final_responder")
workflow.add_edge("warehouse", "final_responder")
workflow.add_edge("cost", "final_responder")
workflow.add_edge("supplier", "final_responder")

# The final responder marks the end of the process.
workflow.add_edge("final_responder", END)

# Compile the workflow into a runnable graph.
agent_graph = workflow.compile()