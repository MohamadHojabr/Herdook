import json
from core.type.entity.assistant_entity import AssistantEntity
from core.type.state.assistant_graph_state import AssistantGraphState
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.checkpoint.memory import MemorySaver
from core.agents.graph.builder import build_rag_graph

memory_checkpointer = MemorySaver()
workflow = build_rag_graph()
graph = workflow.compile(
    checkpointer=memory_checkpointer)

async def process_graph_stream(assistant: AssistantEntity):
    print("Starting RAG chat stream...")
    
    initial_state: AssistantGraphState = {
        "messages": [HumanMessage(content=assistant.query)],
        "question": assistant.query,
        "assistant": assistant,
        "retrieved_docs": [],
        "is_error": False,
        "error": None,
        "failed_node": None,
    }

    config = {"configurable": {"thread_id": assistant.conversation_id}}
    print(f"Received chat stream request : {assistant.conversation_id}")

    try:
        async for event in graph.astream_events(initial_state, config, version="v2"):
            node_name = event.get("metadata", {}).get("langgraph_node")
            # === Streaming توکن‌های LLM ===
            if node_name == "process_agent":
                data = event.get("data", {})
                answer = data.get("output", {}).get("selected_process_id")
                if answer:
                    process_response= json.dumps({"type": "process_id", "data": answer})  + "\n"
                    yield process_response
            if (
                event["event"] == "on_chat_model_stream"
                and node_name == "generate"
                
            ):
                chunk = event["data"]["chunk"]
                if chunk.content:
                    text_response= json.dumps({"type": "text", "data": chunk.content})  + "\n"
                    yield text_response

            elif event["event"] == "on_chain_start":
                node_name = event.get("name")
                if node_name == "rewrite":
                    yield json.dumps({"type": "status", "data": "در حال فکر ..."})  + "\n"
                elif node_name == "retrieve":
                    yield json.dumps({"type": "status", "data": "در حال بازیابی اسناد"}) + "\n"
                elif node_name == "generate":
                    yield json.dumps({"type": "status", "data": "در حال تولید پاسخ..."}) + "\n"
                
            # === تشخیص خطا از state ===
            elif event["event"] == "on_chain_end":
                node_name = event.get("name")
                output = event["data"].get("output", {})

                if isinstance(output, dict) and output.get("is_error"):
                    error_message = output.get("answer", "خطایی رخ داد")
                    yield json.dumps({"type": "error", "data": error_message})          # پیام خطا را هم stream کن
                    return                                 # پایان streaming

    except Exception as ex:
        error_msg = f"خطای سیستمی: {str(ex)}"
        print(f"Streaming pipeline error: {error_msg}")
        yield json.dumps({"type": "error", "data": error_msg})


