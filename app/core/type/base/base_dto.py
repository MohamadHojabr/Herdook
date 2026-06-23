from dataclasses import dataclass, asdict, fields
from typing import Any, Dict, ClassVar
import json


@dataclass(slots=True, kw_only=True)
class BaseDTO:
    """
    پایه همه DTOها در پروژه
    - سبک و سریع
    - متدهای مشترک تبدیل
    - پشتیبانی از slots برای عملکرد بهتر
    """

    # اگر بخواهی همه DTOها frozen (immutable) باشند، اینجا frozen=True بگذار
    # اما معمولاً برای DTOهای پاسخ، mutable بودن بهتر است.

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """تبدیل به دیکشنری ساده"""
        data = asdict(self)
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data

    def to_json(self, exclude_none: bool = False, indent: int | None = None) -> str:
        """تبدیل مستقیم به JSON"""
        return json.dumps(self.to_dict(exclude_none=exclude_none), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseDTO":
        """ساخت از دیکشنری (برای nestedها باید در کلاس فرزند override شود)"""
        # فیلتر کردن کلیدهای اضافی (امنیت)
        valid_fields = {f.name for f in fields(cls)}
        cleaned_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**cleaned_data)

    def __str__(self) -> str:
        """نمایش خوانا"""
        return f"{self.__class__.__name__}({self.to_dict(exclude_none=True)})"

    def __repr__(self) -> str:
        return self.__str__()