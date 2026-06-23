from dataclasses import dataclass, field
from typing import Optional
from core.type.base.base_dto import BaseDTO


@dataclass(slots=True, kw_only=True)
class ConversationProcessResponse(BaseDTO):
    """DTO پاسخ پردازش مکالمه و Response Pool"""
    
    success: bool = False
    from_response_pool: bool = False
    message: Optional[str] = None
    process_id: Optional[str] = None
    response_text: Optional[str] = None
    chat_id: Optional[str] = None