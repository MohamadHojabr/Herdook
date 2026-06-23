from core.type.base.base_request import BaseRequest


class SaveUserQuery(BaseRequest):
    query: str
    assistant_id: str
    chat_id: str
