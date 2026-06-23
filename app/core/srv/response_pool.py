from core.srv.factory.llm_service import LLM_service
from core.srv.vectorstore.chroma_db import Chroma_db
from endpoint.models.assistant_model import AssistantModel
from core.type.dtos.respoonse_pool_dto import ConversationProcessResponse
from core.type.dtos.llm_dto import LLMStatus


class ResponsePool:
    """A class to manage and aggregate responses."""

    def __init__(self):
        self.responses = []
    def process_response(self, model: AssistantModel)-> ConversationProcessResponse:
        """Process a response and return a score."""
        if(model.rag_options.useResponsePool):
            rp = self.from_response_pool(model)
            if(rp.success): 
                return rp
            else:
                return self.from_llm(model)
        else: 
            return self.from_llm(model)


    def from_response_pool(self, model: AssistantModel):
        similar_question = self.search_question(model.assistant_id , model.query ,model.rag_options.semanticSimilarity)
        if  similar_question:
            return ConversationProcessResponse(
                success=True,
                from_response_pool=True,
                message="Response already in pool",
                chat_id=similar_question[0]['metadata']['chat_id'],
            )
        else:
            return ConversationProcessResponse(
                success=False,
                from_response_pool=False,
                message="Response is not found in pool",
                chat_id="",
            )

    def from_llm(self, model: AssistantModel):
            lls_service = LLM_service()
            result = lls_service.call(model)

            if result.is_success and result.status == LLMStatus.NOTFOUND:
                return ConversationProcessResponse(
                    success=False,
                    from_response_pool=False,
                    message='NOTFOUND',
                    process_id=None,
                    response_text=None
                )
            return ConversationProcessResponse(
                success=result.is_success,
                from_response_pool=False,
                message=result.message,
                process_id=result.response.process_suggestion.id,
                response_text=result.response.content,
            )   

    def search_question(self, assistant_id,query, search_range):
        """Search for a similar question in the pool."""
        chroma_db = Chroma_db()
        collection_name = chroma_db.get_chat_collection_name(assistant_id)
        result = chroma_db.retrieve(collection_name , query , 1 , search_range)
        return result

