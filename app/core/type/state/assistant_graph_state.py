import operator
from typing import Annotated, Optional, TypedDict, List, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from core.type.entity.assistant_entity import LLMOptions , AssistantEntity   


class AssistantGraphState(TypedDict):
    """State اصلی گراف که در تمام نودها منتقل می‌شود و شامل همه اطلاعات مورد نیاز است."""
    # ==================== اطلاعات اصلی دستیار ====================
    assistant: AssistantEntity  
    # ==================== اطلاعات اصلی گفتگو ====================
    question: str
    answer: str
    messages: Annotated[List[BaseMessage], add_messages]
    # ==================== اسناد بازیابی شده ====================
    retrieved_docs: List[str]
    # ==================== مدیریت خطا ====================
    error: Optional[str]
    failed_node: Optional[str]
    is_error: Annotated[bool, operator.add]           # ← خیلی مهم
    # ==================== مسیر Process ====================
    is_process_path: bool = False
    selected_process_id: Optional[str]
