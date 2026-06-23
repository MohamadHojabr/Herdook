from typing import Any
from fastapi import APIRouter, HTTPException
from core.srv.vectorstore.chroma_db import Chroma_db
from endpoint.models.rag_model import RetrivalInputModel
from core.type.base.base_result import BaseResult

router = APIRouter(prefix="/chromadb", tags=["Chroma DB Endpoints"])

@router.post("/get-collections" , response_model= BaseResult[list[str]])
async def get_collections():
        try:
            chroma_client = Chroma_db() 
            collection_list = chroma_client.get_collections()
            collection_names = [col.name for col in collection_list]  # Extract just the names
            return BaseResult.success_response(data=collection_names)
        except Exception  as e:
            return BaseResult.error_response(message= str(e), error_code=500)
        except HTTPException  as e:
            return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))

@router.post("/delete-collection", response_model= BaseResult[str])
async def delete_collection(assistant_id:str):
        try:
            chroma_client = Chroma_db() 
            chroma_client.delete_collection(assistant_id)
            return BaseResult.success_response(data=f"collection {assistant_id} successfully deleted")
        except Exception  as e:
            return BaseResult.error_response(message= str(e), error_code=500)
        except HTTPException  as e:
            return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
@router.post("/get-records" , response_model= BaseResult[Any])
async def get_records(assistant_id:str):
        try:
            chroma_client = Chroma_db() 
            data  = chroma_client.get_collection_data(assistant_id)
            return BaseResult.success_response(data=data)
        except Exception  as e:
            return BaseResult.error_response(message= str(e), error_code=500)
        except HTTPException  as e:
            return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
@router.post("/retrival" , response_model= BaseResult[list[dict]])
async def retrival(model:RetrivalInputModel):
        try:
            chroma_client = Chroma_db() 
            result = chroma_client.retrieve(model.assistant_id,model.query,model.k, model.distance_threshold)
            print(f"retrival result : {result[0]['id'][:50]}")
            return BaseResult.success_response(data=result) 
        except Exception  as e:
            return BaseResult.error_response(message= str(e), error_code=500)
        except HTTPException  as e:
            return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
@router.post("/delete_all_collections/", response_model= BaseResult[Any] )
def delete_all_collections():
    try:
        chroma_client = Chroma_db() 
        chroma_client.delete_all_collections()
        return BaseResult.success_response(data="all collections deleted successfully")
    except Exception  as e:
        return BaseResult.error_response(message= str(e), error_code=500)
    except HTTPException  as e:
        return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
