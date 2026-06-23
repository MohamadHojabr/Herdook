from attrs import asdict
from chromadb.app import app
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.agents.agent_orchestrator import process_graph_stream
from endpoint.models.assistant_model import AssistantModel
router = APIRouter(prefix="/chat", tags=["Chat Endpoints"])
    
@router.post("/stream")
async def chat_stream(request: AssistantModel):
    entity = request.to_assistant_entity()

    async def event_generator():
        async for token in process_graph_stream(entity):
            if token:  
                yield token    
    return StreamingResponse(event_generator(), media_type="text/event-stream")