from pydantic import BaseModel
from typing import TypeVar, Type

T = TypeVar("T")   # برای dataclass هدف

class BaseRequest(BaseModel):
    """کلاس پایه برای تمام Schemaهای Pydantic در پروژه"""

    model_config = {
        #"extra": "forbid",           # امنیت بالا - فیلد اضافی قبول نکند
        "from_attributes": True,     # برای تبدیل از ORM یا dataclass اگر لازم شد
    }

    def to_entity(self, entity_class: Type[T]) -> T:
        """
        تبدیل Pydantic Schema به dataclass مربوطه
        
        مثال استفاده:
            assistant_entity.to_entity(AssistantModel)
        """
        # تبدیل به دیکشنری ساده
        data = self.model_dump()

        # اگر entity_class متد from_dict داشته باشد (که قبلاً نوشتیم)، از آن استفاده کن
        if hasattr(entity_class, "from_dict") and callable(entity_class.from_dict):
            return entity_class.from_dict(data)
        
        # در غیر این صورت مستقیماً با **data بساز (برای موارد ساده)
        return entity_class(**data)