from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.srv.embedding.embbeding_service import EmbeddingService
from core.srv.factory.llm_service import LLM_service
from core.srv.vectorstore.chroma_db import Chroma_db
from core.type.dtos.llm_dto import LLM_Response
from endpoint.models.response_pool_model import SaveUserQuery
from endpoint.models.assistant_model import AssistantModel
from core.type.base.base_result import BaseResult

router = APIRouter(prefix="/assistant", tags=["Assistant Endpoints"])


@router.post("/request/stream")
async def assistant_request_stream(model: AssistantModel):
    try:
        model.is_stream = True
        lls_service = LLM_service()
        result = lls_service.call(model)

        # ✅ در حالت stream خروجی باید فقط StreamingResponse باشد
        if isinstance(result, StreamingResponse):
            return result

        # اگر به هر دلیل خروجی stream نبود، برگردان خطا
        return StreamingResponse(
            iter(["[ERROR] Stream not available\n"]),
            media_type="text/event-stream"
        )

    except Exception as e:
        # در حالت stream، حتی خطاها باید stream شوند
        def error_gen():
            yield f"[ERROR] {str(e)}\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")
@router.post("/request/", response_model=BaseResult[Any])
async def assistant_request(model: AssistantModel):
    try:
        model.is_stream = False
        lls_service = LLM_service()
        result = lls_service.call(model)

        if isinstance(result, LLM_Response):
            return BaseResult.success_response(data=result)

        return BaseResult.error_response(
            message="Unexpected response type",
            error_code=500
        )

    except Exception as e:
        return BaseResult.error_response(message=str(e), error_code=500)
    
@router.post("/sentence_distance/", response_model= BaseResult[Any] )
def sentence_distance(sentence1, sentence2):
    distance = EmbeddingService().sentence_distance(sentence1, sentence2)   
    return BaseResult.success_response(data="ok")

@router.post("/save_user_chat/", response_model= BaseResult[Any] )
def save_user_chat(model: SaveUserQuery):
    try:
        chroma_client = Chroma_db() 
        chat_collection_name = chroma_client.get_chat_collection_name(model.assistant_id)
        chroma_client.add_documents(
            collection_name=chat_collection_name, 
            documents=[model.query], 
            metadatas=[{"type": "user_request" , "chat_id":model.chat_id}], 
            ids=[model.chat_id])
        return BaseResult.success_response(data="ok")    
    except Exception  as e:
        return BaseResult.error_response(message= str(e), error_code=500)
    except HTTPException  as e:
        return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
