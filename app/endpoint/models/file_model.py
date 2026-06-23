from typing import Optional

from pydantic import Field, ValidationInfo, field_validator
from core.type.base.base_request import BaseRequest

class FileProcessingResult(BaseRequest):
    assistant_id: str
    doc_id: str
    is_processed: bool = False
    message: Optional[str] = None

class FileProcessingRequest(BaseRequest):
    assistant_id: str = Field(..., min_length=1, description="Unique identifier for the assistant")
    doc_id: str = Field(..., min_length=1, description="File id must have value")
    file_base64: str
    file_name: str = Field(..., min_length=1, description="Field file_name must have value")
    file_size: int
    file_type: str = Field(..., min_length=1, description="Field file_type must have value")

    @field_validator('assistant_id', 'doc_id' , 'file_base64' , 'file_name' ,'file_type')
    @classmethod
    def check_empty_strings(cls, v: str, info: ValidationInfo) -> str:
        """Validate that string fields are not empty or just whitespace"""
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()
    @field_validator('file_size')
    @classmethod
    def validate_k(cls, v: int) -> int:
        """Additional validation for k if needed"""
        if v < 0:  # Example of additional validation
            raise ValueError("file is empty")
        return v


class DeleteFileModel(BaseRequest):
    assistant_id: str = Field(..., min_length=1, description="Unique identifier for the assistant id")
    doc_id: str = Field(..., min_length=1, description="File id must have value")
