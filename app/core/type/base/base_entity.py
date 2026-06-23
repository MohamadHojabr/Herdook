# ====================== کلاس پایه ======================
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Type, TypeVar
import uuid

from pydantic import json

T = TypeVar("T", bound="BaseEntity")  # برای type hinting

@dataclass(slots=True, kw_only=True)
class BaseEntity:
    """کلاس پایه برای همه موجودیت‌ها"""
    id: str = field(
        default_factory=lambda: str(uuid.uuid4()),
        init=False,         
        repr=False          
    )
    created_at: datetime = field(
        default_factory=datetime.now,
        init=False,
        repr=False
    )
    updated_at: datetime = field(
        default_factory=datetime.now,
        init=False,
        repr=False
    )

    def __post_init__(self):
        """اعتبارسنجی و به‌روزرسانی پایه"""
        self.updated_at = datetime.now()
        """کلاس پایه برای همه dataclasses (اختیاری اما مفید)"""


