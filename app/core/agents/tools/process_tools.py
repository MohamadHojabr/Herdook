from langchain_core.tools import tool
from typing import List
from core.type.entity.assistant_entity import AssistantEntity

def create_process_tools(assistant: AssistantEntity):
    """تبدیل process_list به LangChain Tools"""
    tools = []

    for process in assistant.process_list:
        process_id = process.id
        description = process.description or ""

        @tool
        def execute_process(user_query: str) -> dict:
            """اجرای یک فرآیند خاص"""
            result = {
                "process_id": process_id,
                "status": "selected",
                "message": f"فرآیند با آیدی {process_id} انتخاب شد."
            }
            return result

        # تنظیمات مهم ابزار برای اینکه مدل بهتر تصمیم بگیرد
        execute_process.name = process_id
        execute_process.description = description
        tools.append(execute_process)

    return tools