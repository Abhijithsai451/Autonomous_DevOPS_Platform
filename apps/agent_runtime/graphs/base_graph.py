from apps.agent_runtime.graphs.nodes import analyze_node, format_node
from apps.agent_runtime.graphs.state import AgentState
from langgraph.graph import StateGraph, START, END

def build_agent_graph():
    builder = StateGraph(AgentState)

    builder.add_node("analyze", analyze_node)
    builder.add_node("format", format_node)

    builder.add_edge(START,"analyze")
    builder.add_edge("analyze", "format")
    builder.add_edge("format", END)

    return builder.compile()

base_graph = build_agent_graph()

