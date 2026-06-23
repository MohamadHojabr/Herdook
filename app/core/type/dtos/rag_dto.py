from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from core.type.base.base_dto import BaseDTO   # مسیر را درست کن


class RetrievalStatus(str, Enum):
    SUCCESS = "success"
    NOTFOUND = "notfound"
    FAILED = "failed"


@dataclass(slots=True, kw_only=True)
class RetrivalResultDto(BaseDTO):
    """نتیجه بازیابی اسناد (DTO)"""
    
    documents: List[str] = field(default_factory=list)
    context: str = ""
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    status: RetrievalStatus = RetrievalStatus.NOTFOUND

    def __post_init__(self):
        # پاک‌سازی و نرمال‌سازی خاص این DTO
        self.documents = [doc.strip() for doc in self.documents if doc and str(doc).strip()]
        
        if not self.context:
            self.context = "No relevant context found."
        
        if self.metadata is None:
            self.metadata = {}