from apps.agent_runtime.graphs.nodes import analyze_node, format_node, llm_node, tool_node
from apps.agent_runtime.graphs.router import should_continue
from apps.agent_runtime.graphs.state import AgentState
from langgraph.graph import StateGraph, START, END

def build_base_agent_graph(checkpointer = None):
    builder = StateGraph(AgentState)

    builder.add_node("analyze", analyze_node)
    builder.add_node("llm", llm_node)
    builder.add_node("tools", tool_node)
    builder.add_node("format", format_node)

    builder.add_edge(START,"analyze")
    builder.add_edge("analyze", "llm")
    builder.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            "format": "format",
        },
    )
    builder.add_edge("tools", "llm")
    builder.add_edge("format", END)

    return builder.compile(checkpointer = checkpointer)

base_graph = build_base_agent_graph()

