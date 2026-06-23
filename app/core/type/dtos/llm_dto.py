
from enum import Enum
from pydantic import BaseModel, Field, field_validator, HttpUrl, model_validator
from typing import List, Optional
class LLMStatus(str, Enum):
    SUCCESS = "success"
    NOTFOUND = "notfound"
    FAILED = "failed"

class ProcessSuggestion(BaseModel):
    id: str = ""
    reason: str = ""


class Response(BaseModel):
    error_message: str = ""
    content: str = ""
    process_suggestion: ProcessSuggestion = Field(default_factory=ProcessSuggestion)


class LLM_Response(BaseModel):
    message: str = ""
    is_success: bool = False
    is_stream: bool = False
    response: Response = Field(default_factory=Response)
    status: LLMStatus = LLMStatus.NOTFOUND

    @model_validator(mode="after")
    def sync_message_with_response(self) -> "LLM_Response":
        if not self.response.content:
            self.response.content = self.message
        return self    
class LLM_RawResponse(BaseModel):
    t:str
    p: Optional[str] = None




