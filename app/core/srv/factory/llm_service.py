import json
import re
from typing import Dict, List, Optional
from fastapi.responses import StreamingResponse
import httpx
from openai import OpenAI
from core.srv.vectorstore.chroma_db import Chroma_db
from core.type.dtos.rag_dto import RetrievalStatus, RetrivalResultDto
from endpoint.models.assistant_model import AssistantModel
from core.type.dtos.llm_dto import LLM_RawResponse, LLM_Response, LLMStatus, ProcessSuggestion, Response



class LLM_service:
    def __init__(self):
        self.llm = "deepseek"
    def ensure_json_format(self ,raw_response: str) -> LLM_RawResponse:
        """Ensure the string ends with a closing '}' character."""
        raw_response = raw_response.strip('```json').strip('```').strip()

        if not raw_response:
            return '{"t": "میزان توکن کافی نیست", "p": null}'
        raw_response = raw_response.strip()
        if not raw_response.endswith("}"):
            raw_response += '"}'

        return LLM_RawResponse(**json.loads(raw_response)) 
    
    def parse_response(self,raw_response)-> LLM_Response:
        try:
            llm_rawresponse = self.ensure_json_format(raw_response)
            result = LLM_Response(is_success=True , status=LLMStatus.SUCCESS )
            result.response.content = llm_rawresponse.t
            result.response.process_suggestion.id = llm_rawresponse.p
            result.response.process_suggestion.reason = "Process detected"
            return result
        except Exception as e:
           return LLM_Response(is_success=False , status=LLMStatus.FAILED , message=str(e))
    
    def normalize_text(text: str) -> str:
        """
        تمیز کردن متن فارسی برای استفاده در context مدل زبانی
        - نیم‌فاصله → فاصله معمولی
        - حذف فاصله‌ها و خطوط خالی اضافی
        - حذف کاراکترهای کنترلی ناخواسته
        """
        if not text or not text.strip():
            return ""

        # جایگزینی نیم‌فاصله و کاراکترهای مشابه
        text = text.replace('\u200c', ' ').replace('\u200d', ' ')

        # یکسان‌سازی فاصله‌ها
        text = re.sub(r'\s+', ' ', text)

        # تبدیل چند خط خالی به حداکثر یک خط خالی
        text = re.sub(r'\n\s*\n+', '\n\n', text.strip())

        return text.strip()
    def retrival_context(self , assistant_id:str , query:str , k:int , distance:float)-> RetrivalResultDto:
        try:
            chroma_db = Chroma_db()
            retrive_text = chroma_db.retrieve(assistant_id , query , k , distance)
            if not retrive_text:
                return RetrivalResultDto(context="", documents=[], metadata="", status=RetrievalStatus.NOTFOUND) 
            combined_string = ""
            doc_list:list[str] = []

            for item in retrive_text:
                # Check if metadata is a dictionary and has a key "type" with value "text"
                if isinstance(item.get("metadata"), dict):
                    head = item.get("metadata").get("head", "بدون عنوان")
                    text = item.get("document")
                    chunk = f"### {head}\n\n{text}\n"
                    combined_string += chunk + " "
                    doc_list.append(chunk)
            return RetrivalResultDto(context=combined_string, documents=doc_list, metadata="", status=RetrievalStatus.SUCCESS) 
        except:
            return RetrivalResultDto(context="", metadata="the retrive function has error", status=RetrievalStatus.FAILED) 
    # def get_system_prompt(self,
    #         model:AssistantModel  ,
    #         dynamic_processes: Optional[List[Dict]] = None,
    #         rag_context: Optional[List[str]] = None) -> str:
    #         processes_section = ""
    #         if dynamic_processes:
    #             try:
    #                 result_list = [{"process_id": item.id, "description": item.description} for item in dynamic_processes]
    #                 processes_section = json.dumps(result_list, indent=2, ensure_ascii=False)
    #             except Exception as e:
    #                 print(e)
    #         result_schema = {
    #                     "t": "your_text_response_here",
    #                     "p": "process_id_if_detected_otherwise_null"
    #                 }   
    #         system_prompt = f"""
    #                 You are an intelligent business assistant with these capabilities:
    #                 ### 1. Core Functions  
    #                 - **Business Understanding**:  
    #                 - You are an AI assistant specialized in {model.assistant_description}.  
    #                 - **Only respond to questions within this domain**. Politely decline unrelated requests.  
    #                 - If the user’s query is unclear, ask clarifying questions.  
    #                 - Business Description: {model.assistant_description}                     
    #                  ### 2. Knowledge Base Rules
    #                 - **RAG Context Handling**:
    #                 {f"Available Context Documents:{rag_context}" if rag_context else 
    #                 "IMPORTANT:when you have NO access to knowledge documents. If asked about domain-specific information, you MUST respond:"}
    #                 ### 3. Process Detection:
    #                 - **Process Detection**:
    #                 - When a user request matches a predefined process, respond this
    #                 - Then continue with a normal response
    #                 - **Dynamic Processes**
    #                 Available Processes:  
    #                 {processes_section}
    #                 ### Response Requirements:
    #                 You MUST always respond in VALID JSON format using this exact schema:
    #                 {result_schema}
    #                 ### 4. Response:
    #                 - **Token Management**:  
    #                 - Strictly adhere to token limits. Split/summarize if needed.
    #                   Token Limit: {model.llm_options.max_tokens}
    #                 """
    #         return   system_prompt.strip() 

    def get_system_prompt(self,
            model:AssistantModel  ,
            dynamic_processes: Optional[List[Dict]] = None,
            rag_context: Optional[List[str]] = None) -> str:
            processes_section = ""
            if dynamic_processes:
                try:
                    result_list = [{"process_id": item.id, "description": item.description} for item in dynamic_processes]
                    processes_section = json.dumps(result_list, indent=2, ensure_ascii=False)
                    
                except Exception as e:
                    print(e)
            system_prompt = f"""
                You are an intelligent business assistant with these capabilities:

                ### 1. Core Functions
                - You are an AI assistant specialized in {model.assistant_description}.
                - Only respond to questions within this domain.
                - Politely decline unrelated requests.
                - If the user’s query is unclear, ask clarifying questions.
                - Business Description: {model.assistant_description}

                ### 2. Knowledge Base Rules
                - RAG Context Handling:
                {f"Available Context Documents:{rag_context}" if rag_context else "You currently have NO access to external knowledge documents."}

                ### 3. Process Detection
                - When a user request matches a predefined process, detect it and include its **process_id**.
                - If no process matches, set process_id = null.
                - Available Processes:
                {processes_section}

                ### 4. Response Format (IMPORTANT)
                Always output your final response in this **exact format** — never add extra text, explanations, or markdown before or after it:

                [TEXT]
                <your human-friendly answer here>
                [/TEXT]

                [PROCESS_ID]
                <detected_process_id_or_null>
                [/PROCESS_ID]

                Example:
                [TEXT]
                برای شارژ حساب خود مراحل زیر را انجام دهید...
                [/TEXT]
                [PROCESS_ID]
                7a6b1e72-7fcc-440f-a544-0076bb6658c7
                [/PROCESS_ID]

                ### 5. Token Management
                - Respect token limits: {model.llm_options.max_tokens}
                """
            return   system_prompt.strip() 

    
    # def call_llm_with_system_prompt(self,model:AssistantModel) -> Dict:

    #         context = self.retrival_context(model.assistant_id , 
    #                                         model.query ,
    #                                         model.rag_options.countOfChunk , 
    #                                         model.rag_options.embeddingDistance)
            
    #         if context.status == RetrievalStatus.NOTFOUND: 
    #             return {'success': False,
    #                     'message': "NOTFOUND",
    #                     'response_text': ''
    #                     }
    #         system_prompt = self.get_system_prompt(model, model.process_list ,context.documents)
    #         # 2. فراخوانی مدل
    #         try:
    #             # client = OpenAI(api_key=model.llm_options.api_key, base_url=model.llm_options.base_url)
    #             # response = client.chat.completions.create(
    #             #     model=model.llm_options.model_name,
    #             #     messages=[
    #             #         {"role": "system", "content": system_prompt},
    #             #         {"role": "user", "content": model.query}
    #             #     ],
    #             #     stream=model.is_stream,
    #             #     temperature=model.llm_options.temperature,
    #             #     max_tokens=model.llm_options.max_tokens + 50,
    #             # )
    #             if model.is_stream:
    #                 return self.call_llm(model ,system_prompt)
    #             return self.parse_response(self.call_llm(model ,system_prompt))
    #         except Exception as e:
    #             return {'success': False,
    #                     'message': f"Error calling LLM: {str(e)}",
    #                     'response_text': ''
    #                     }

    def is_followup(self , model:AssistantModel) -> bool: 
        if len(model.recent_messages) < 2:
            return False
        model.is_stream = False
        try :
            prompt = f"Given this short recent conversation:\n{model.recent_messages}\nIs the user question a follow-up referring to prior context?\nQuestion: {model.query}\nAnswer with YES or NO."
        except Exception as e:
             print("Error:", e)
        resp = self.call_llm(model , prompt)  
        return resp.strip().upper().startswith("YES")
    
    # def rewrite_question_if_followup(self , model:AssistantModel) -> str:  
    #     model.is_stream = False
    #     prompt = f"""
    #     You are a helpful assistant that can handle follow-up questions.
    #     Here is the recent conversation history (most recent last):
    #     {model.recent_messages}

    #     The user has just asked this question:
    #     {model.query}

    #     If the user's question depends on the previous messages,
    #     rewrite it into a fully standalone question that keeps the same meaning.
    #     Otherwise, return the question unchanged.

    #     Return ONLY the rewritten or original question, nothing else.
    #     """
    #     rewritten_query = self.call_llm(model, prompt).strip()
    #     return rewritten_query

    def rewrite_question_if_followup(self, model: AssistantModel) -> Optional[str]:
        """
        Rewrites the user question into a standalone version only if it depends on prior context.
        If the question is already independent, returns None.
        """

        model.is_stream = False

        prompt = f"""
        You are a helpful assistant that can rewrite follow-up questions into standalone ones.

        ### Conversation History (most recent last)
        {model.recent_messages}

        ### Current User Question
        {model.query}

        ### Instructions
        - If the user's question clearly depends on previous messages (e.g., uses pronouns or context),
        rewrite it into a **complete standalone question** that preserves meaning.
        - If the user's question is already **independent**, respond exactly with:
        NO_CHANGE

        ### Output Format
        Return ONLY ONE of:
        - The rewritten standalone question (no quotes or markdown)
        - The text "NO_CHANGE"
        """

        rewritten_query = self.call_llm(model, prompt).strip()

        # ✅ Interpret model response
        if rewritten_query.upper().startswith("NO_CHANGE"):
            return None
        return rewritten_query

    
    def call_llm(self , model:AssistantModel , system_prompt):
        print("call_llm starting .........")
        client = OpenAI(api_key=model.llm_options.api_key, 
                        base_url=model.llm_options.base_url,
                        http_client=httpx.Client(verify=False))
        try:
            response = client.chat.completions.create(
                model=model.llm_options.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": model.query}
                ],
                stream=model.is_stream,
                temperature=model.llm_options.temperature,
                max_tokens=model.llm_options.max_tokens,
            )
        except Exception as e:
            print("in call_llm i have an error .........", e)
            return LLM_RawResponse(t=str(e))
        if model.is_stream:
            def generate():
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            return response.choices[0].message.content
     
    def call(self , model:AssistantModel):
        try:
            rewritten = self.rewrite_question_if_followup(model)
            if rewritten:
                    model.query = rewritten

            model.is_stream = True
            context = self.retrival_context(model.assistant_id , 
                                            model.query , 
                                            model.rag_options.countOfChunk , 
                                            model.rag_options.embeddingDistance)
            if context.status == RetrievalStatus.NOTFOUND:
                return LLM_Response(is_stream=model.is_stream , response="", status=LLMStatus.NOTFOUND , is_success= False)
            else:
                try:
                    system_prompt = self.get_system_prompt(model, model.process_list ,context.context)
                    if model.is_stream:
                        return self.call_llm(model ,system_prompt)
                    else:
                        llm_response = self.call_llm(model ,system_prompt)                    
                        res = self.parse_response(llm_response)
                        res.is_stream = model.is_stream
                        return res
                except Exception as e:
                    return LLM_Response(is_stream=model.is_stream , response=None , status=LLMStatus.FAILED , is_success=False)
            
        except Exception as e:
             print("Error:", e)
