from core.type.base.base_request import BaseRequest
from pydantic import Field
from typing import List, Optional, Annotated
from annotated_types import MinLen, MaxLen, Ge, Le, Gt

from core.type.entity.assistant_entity import AssistantEntity

# ====================== Schemaهای Nested ======================
class LLMOptionsSchema(BaseRequest):
    provider: Optional[str] = Field(None, description="LLM provider")
    base_url: Optional[str] = Field(None, description="Base URL for LLM")
    api_key: Optional[str] = Field(None, min_length=8, max_length=256)
    model_name: Annotated[str, MinLen(2), MaxLen(50)] = ""
    temperature: Annotated[float, Ge(0.0), Le(2.0)] = 0.7
    max_tokens: Annotated[int, Gt(0), Le(10000)] = 100


class AssistantProcessSchema(BaseRequest):
    id: str
    description: str


class RAGOptionsSchema(BaseRequest):
    use_response_pool: bool = False
    semantic_similarity: Annotated[float, Ge(0.0), Le(2.0)] = 0.2
    embedding_distance: Annotated[float, Ge(0.0), Le(1.0)] = 0.1
    count_of_chunk: Annotated[int, Gt(0), Le(100)] = 5


# ====================== AssistantEntity اصلی ======================
class AssistantModel(BaseRequest):
    """مدل درخواست ورودی برای FastAPI"""
    assistant_id: Optional[str] = Field(None, description="ID of the assistant")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")
    assistant_description: Optional[str] = Field(None, description="توضیحات دستیار")
    query: Optional[Annotated[str, MinLen(1), MaxLen(10000)]] = Field(None)
    is_stream: bool = True

    llm_options: LLMOptionsSchema = Field(default_factory=LLMOptionsSchema)
    rag_options: RAGOptionsSchema = Field(default_factory=RAGOptionsSchema)
    process_list: List[AssistantProcessSchema] = Field(default_factory=list)
    recent_messages: List[str] = Field(default_factory=list)

    def to_assistant_entity(self) -> "AssistantEntity":
        """
        متد اختصاصی برای تبدیل به AssistantModel (dataclass)
        این متد خواناتر از to_entity عمومی است
        """
        from core.type.entity.assistant_entity import AssistantEntity 

        return self.to_entity(AssistantEntity)