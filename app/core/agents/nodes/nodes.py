import json
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from core.agents.tools.process_tools import create_process_tools
from core.srv.factory.llm_factory import get_llm
from core.srv.vectorstore.chroma_db import Chroma_db
from core.type.state.assistant_graph_state import AssistantGraphState
from core.agents.graph.prompt_builder import PromptBuilder as prompts

# ==================== GENERATE NODE ====================
async def generate_node(state: AssistantGraphState) -> AssistantGraphState:
    try:
        print(f"📊 [Generate Node] Starting generation with question.....")  # لاگ برای دیباگ
        llm = get_llm(state["assistant"].llm_options, streaming=True)
        assistant = state["assistant"]

        context = "\n\n".join(state.get("retrieved_docs", []))
        
        prompt = prompts.get_assistant_response_prompt()

        chain_input = {
            "context": context,
            "question": state["question"],
            "assistant_description": assistant.assistant_description,
            "max_tokens": assistant.llm_options.max_tokens
        }
        chain = prompt | llm

        answer_chunks = []
        async for chunk in chain.astream(chain_input):
            if chunk.content:
                answer_chunks.append(chunk.content)

        full_answer = "".join(answer_chunks)
        state["messages"].append(AIMessage(content=full_answer))
        state["answer"] = full_answer  
        return state

    except Exception as ex:
        error_str = f"Generate Answer Error: {str(ex)}"
        fallback_msg = "متأسفانه در حال حاضر امکان تولید پاسخ وجود ندارد. لطفاً کمی بعد دوباره تلاش کنید."
        state["messages"].append(AIMessage(content=fallback_msg))
        state["answer"] = fallback_msg
        state["error"] = error_str
        state["failed_node"] = "generate"
        state["is_error"] = True
        return state
# ==================== RETRIEVE NODE ====================
async def retrieve_node(state: AssistantGraphState) -> AssistantGraphState:
    try:
        print(f"📊 [Retrieve Node] Starting retrieval with question.....")  # لاگ برای دیباگ
        assistant = state["assistant"]
        query = state["question"]

        chroma_client = Chroma_db()
        retriever = chroma_client.retrieve(
            collection_name=assistant.assistant_id,
            query=query,
            top_k=assistant.rag_options.count_of_chunk
        )
        
        doc_contents = [doc['document'] for doc in retriever]
        state["retrieved_docs"] = doc_contents
        return state
    
    except Exception as ex:
        error_str = f"Retrieve Documents Error: {str(ex)}"
        print(error_str)
        state["retrieved_docs"] = []
        state["error"] = error_str
        state["failed_node"] = "retrieve"
        state["is_error"] = True
        state["messages"] = []
        return state
# ==================== REWRITE NODE ====================
async def rewrite_query_node(state: AssistantGraphState) -> AssistantGraphState:
    try:
        print(f"📊 [Rewrite Node] Starting query rewrite with question.....")  # لاگ برای دیباگ
        llm = get_llm(state["assistant"].llm_options)
        
        # all_messages = state.get("messages", [])
        # recent_messages = all_messages[-10:] if all_messages else []
        #print(f"📊 [Rewrite] Recent messages for context: {all_messages}")  # لاگ برای دیباگ
        recent_messages = state["assistant"].recent_messages[:-1] 
        prompt = prompts.get_rewrite_query_prompt()
        chain = prompt | llm | StrOutputParser()
        
        rewritten = chain.invoke({
            "question": state["question"],
            "recent_messages": recent_messages
        }).strip()
        state["question"] = rewritten
        state["messages"].append(HumanMessage(content=rewritten))
        return state

    except Exception as ex:
        print(f"Rewrite Error: {ex}")
        state["is_error"] = True
        state["error"] = str(ex)
        state["failed_node"] = "rewrite"
        return state
# ==================== ERROR HANDLER NODE ====================
async def error_handler_node(state: AssistantGraphState) -> AssistantGraphState:
    """نود اختصاصی مدیریت خطاها - پیام مناسب به کاربر می‌دهد"""
    print(f"📊 [Error Handler] Handling error for failed node .....")  # لاگ برای دیباگ
    failed_node = state.get("failed_node", "unknown")
    error_detail = state.get("error", "خطای ناشناخته")

    # می‌توانی بر اساس نود خطا داده، پیام متفاوت بدهی
    if failed_node == "retrieve":
        user_message = "در حال حاضر امکان جستجو در دانش پایه وجود ندارد. لطفاً کمی بعد دوباره امتحان کنید."
    elif failed_node == "rewrite":
        user_message = "متأسفانه در پردازش سؤال شما مشکلی پیش آمد. لطفاً سؤال خود را دوباره مطرح کنید."
    elif failed_node == "generate":
        user_message = "متأسفانه در تولید پاسخ مشکلی رخ داد. لطفاً کمی بعد دوباره تلاش کنید."
    else:
        user_message = "متأسفانه در پردازش درخواست شما خطایی رخ داد. لطفاً دوباره امتحان کنید."
    state["answer"] = user_message
    state["messages"].append(AIMessage(content=user_message))
    state["is_error"] = True
    #state["error"] = error_detail
    state["failed_node"] = failed_node
    return state
# ==================== ROUTER NODE ====================
async def router_node(state: AssistantGraphState) -> AssistantGraphState:
    """تصمیم‌گیری بین Process Agent و RAG"""
    try:
        print(f"📊 [Router Node] Starting routing decision with question.....")  # لاگ برای دیباگ
        llm = get_llm(state["assistant"].llm_options)
        
        processes_info = "\n".join([
            f"• {p.id}: {p.description}" 
            for p in getattr(state["assistant"], 'process_list', [])
        ]) if state.get("assistant") else "هیچ فرآیندی وجود ندارد."
        prompt = prompts.get_router_prompt()
        chain = prompt | llm | StrOutputParser()
        decision = chain.invoke({
            "question": state["question"],
            "processes_info": processes_info
        }).strip().upper()
        res = json.loads(decision.lower())
        print(f"📊 [Router] LLM decision: {res}")  # لاگ تصمیم LLM برای دیباگ
        if res['process_id']:
            state["is_process_path"] = True
            state["selected_process_id"] = res['process_id']
        else:            
            state["is_process_path"] = False
            state["selected_process_id"] = None
        return state

    except Exception as ex:
        print(f"Router node error: {ex}")
        state["is_process_path"] = False
        state["is_error"] = True
        #state["error"] = str(ex)
        state["failed_node"] = "router"
        return state
#==================== PROCESS AGENT NODE ====================
async def process_agent_node(state: AssistantGraphState) -> AssistantGraphState:
    """نود Agent برای اجرای Processها"""
    print(f"📊 [Process Agent Node] Starting process agent with question.....")  # لاگ برای دیباگ
    try:
        # print(f"📊 [Process Agent] State before agent .....")  # لاگ برای دیباگ
        # tools = create_process_tools(state["assistant"])
        
        # if not tools:
        #     state["answer"] = "در حال حاضر هیچ فرآیندی تعریف نشده است."
        #     return state

        # llm = get_llm(state["assistant"].llm_options, streaming=True)

        # system_prompt = f"""تو یک دستیار هوشمند کسب‌وکار هستی.
        # درخواست کاربر مربوط به اجرای یک فرآیند است.
        # ابزار مناسب را انتخاب کن و بعد فقط process_id رو برگردون بدونه هیچ چیز دیگری."""

        # agent = create_react_agent(model=llm, tools=tools, prompt=system_prompt)

        # result = await agent.ainvoke({"messages": state["messages"]})

        # for msg in result["messages"]:
        #     if isinstance(msg, ToolMessage):
        #         tool_object = json.loads(msg.content)
        #         state["selected_process_id"] = tool_object['process_id']
        #         state["is_process_path"] = True
        #         print(f"Selected process ID: {state['selected_process_id']}")  # لاگ برای دیباگ
        #         break
        print(f"📊 [Process Agent] Currently, {state['selected_process_id']}")  # لاگ برای دیباگ
        return state

    except Exception as ex:
        print(f"[Process Agent] Error: {ex}")
        state["answer"] = "متأسفانه در اجرای فرآیند مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
        state["is_error"] = True
        state["error"] = str(ex)
        state["failed_node"] = "process_agent"
        return state


