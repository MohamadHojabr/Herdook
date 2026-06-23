from langgraph.graph import StateGraph, START, END
from core.type.state.assistant_graph_state import AssistantGraphState


from ..nodes.nodes import (
    rewrite_query_node,
    router_node,
    retrieve_node,
    generate_node,
    process_agent_node,
    error_handler_node
)


def build_rag_graph():
    workflow = StateGraph(state_schema=AssistantGraphState)

    workflow.add_node("rewrite", rewrite_query_node)
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("process_agent", process_agent_node)
    workflow.add_node("error_handler", error_handler_node)

    # جریان ثابت
    workflow.add_edge(START, "rewrite")
    workflow.add_edge("rewrite", "router")

    # ==================== CONDITIONAL ROUTING ====================
    def route_after_router(state: AssistantGraphState) -> str:
        print(f"📊 [Router] Routing to Process Agent with selected_process_id: {state.get('is_process_path')}")  # لاگ برای دیباگ

        if state.get("is_process_path") is True:
            return "process_agent"
        else:
            return "retrieve"

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "process_agent": "process_agent",
            "retrieve": "retrieve"
        }
    )

    # ادامه مسیر RAG
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    workflow.add_edge("process_agent", END)

    # ==================== Error Handling ====================
    # def route_on_error(state: AssistantGraphState) -> str:
    #     if state.get("is_error", False):
    #         return "error_handler"
    #     return "continue"

    # nodes_map = {
    #     "rewrite": "router",
    #     "router": "retrieve",      # این مقدار پیش‌فرض است، conditional آن را override می‌کند
    #     "retrieve": "generate",
    #     "generate": END,
    #     "process_agent": END,
    # }

    # for node, default_next in nodes_map.items():
    #     workflow.add_conditional_edges(
    #         node,
    #         route_on_error,
    #         {
    #             "error_handler": "error_handler",
    #             "continue": default_next
    #         }
    #     )

    # workflow.add_edge("error_handler", END)

    return workflow