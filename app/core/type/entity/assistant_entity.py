from dataclasses import dataclass, field
from typing import List, Optional, Annotated
from annotated_types import Ge, Le, Gt, MinLen, MaxLen
from core.type.base.base_entity import BaseEntity

# ====================== نوع‌های مشترک (Reusable) ======================
Temperature = Annotated[float, Ge(0.0), Le(2.0)]
MaxTokens = Annotated[int, Gt(0), Le(10000)]
Similarity = Annotated[float, Ge(0.0), Le(2.0)]
Distance = Annotated[float, Ge(0.0), Le(1.0)]
ChunkCount = Annotated[int, Gt(0), Le(100)]

# ====================== LLMOptions ======================
@dataclass(slots=True, kw_only=True)
class LLMOptions(BaseEntity):
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Annotated[str, MinLen(2), MaxLen(50)] = ""
    temperature: Temperature = 0.7
    max_tokens: MaxTokens = 100

    def __post_init__(self):
        """اعتبارسنجی و نرمال‌سازی بعد از ساخت"""
        if self.api_key is not None:
            if any(char.isspace() for char in self.api_key):
                raise ValueError("API key cannot contain spaces")
            if len(self.api_key) < 8 or len(self.api_key) > 256:
                raise ValueError("API key length must be between 8 and 256 characters")

        if self.model_name and (len(self.model_name) < 2 or len(self.model_name) > 50):
            raise ValueError("model_name length must be between 2 and 50 characters")


# ====================== AssistantProccess ======================
@dataclass(slots=True, kw_only=True)
class AssistantProcess(BaseEntity):          # نام را به صورت صحیح انگلیسی تغییر دادم (Process نه Proccess)
    id: str
    description: str


# ====================== RAGOptions ======================
@dataclass(slots=True, kw_only=True)
class RAGOptions(BaseEntity):
    use_response_pool: bool = False
    semantic_similarity: Similarity = 0.2
    embedding_distance: Distance = 0.1
    count_of_chunk: ChunkCount = 5


# ====================== AssistantEntity ======================
@dataclass(slots=True, kw_only=True)
class AssistantEntity(BaseEntity):
    assistant_id: Optional[str] = None
    conversation_id: Optional[str] = None
    assistant_description: Optional[str] = None
    query: Optional[Annotated[str, MinLen(1), MaxLen(10000)]] = None
    is_stream: bool = True
    llm_options: LLMOptions = field(default_factory=LLMOptions)
    rag_options: RAGOptions = field(default_factory=RAGOptions)
    process_list: List[AssistantProcess] = field(default_factory=list)
    recent_messages: List[str] = field(default_factory=list)

    def __post_init__(self):
        """اعتبارسنجی سطح مدل (مشابه field_validator قبلی)"""

        if self.query is None and self.assistant_id is None:
            raise ValueError("Either query or assistant_id must be provided")
        
        if isinstance(self.llm_options, dict):
            self.llm_options = LLMOptions(**self.llm_options)   # یا LLMOptions.from_dict اگر داشته باشی

        if isinstance(self.rag_options, dict):
            self.rag_options = RAGOptions(**self.rag_options)

        if isinstance(self.process_list, list):
            self.process_list = [
                AssistantProcess(**item) if isinstance(item, dict) else item
                for item in self.process_list
            ]

        if self.assistant_description:
            self.assistant_description = self.assistant_description.strip()

        if self.query:
            self.query = self.query.strip()
