import json
from typing import Dict, List, Optional
from click import prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.type.entity.assistant_entity import AssistantEntity

class PromptBuilder:   

    # @staticmethod
    # def get_rewrite_query_prompt() -> ChatPromptTemplate:
    #     return ChatPromptTemplate.from_messages([
    #             ("system", """You are an expert query rewriter specialized in conversational RAG systems.
    #     Your ONLY job is to turn the current user question into a clear, fully standalone query optimized for semantic search.

    #     Rules:
    #     - Keep the exact same language as the user.
    #     - Merge necessary context from history if needed.
    #     - Return ONLY the rewritten query. No explanation."""),
                
    #             MessagesPlaceholder(variable_name="recent_messages"),
    #             ("human", "Current question: {question}\n\nRewritten query:")
    #         ])   
    @staticmethod
    def get_rewrite_query_prompt() -> ChatPromptTemplate:
        prompt = ChatPromptTemplate.from_template(
            """You are an expert Query Rewriter for a conversational RAG system.

            ## Current Question:
            {question}

            ## Conversation History (excluding current question):
            {recent_messages}

            Your task:

            1. Carefully analyze whether the Current Question is a **follow-up** that depends on the conversation history or not.

            2. If it **IS a follow-up** (depends on context):
            - Resolve all pronouns (او، این، اون، من، اسم من， etc.), references, and omitted information.
            - Make the query completely standalone and self-contained.
            - Preserve the exact user intent.

            3. If it is **NOT a follow-up**:
            - Only improve clarity, grammar, and retrieval quality without adding any new information.

            ### Important Rules:
            - Always preserve the user's original language (Persian/Farsi).
            - Do NOT invent any information not explicitly mentioned in the history.
            - Pay special attention to short, vague, or repetitive questions — they are very likely follow-ups.
            - Common follow-up signals: "اسم من چی بود"، "چی شد"، "اون یکی"، "دوباره"، "قبلی"، pronouns, etc.
            - The rewritten query must be understandable by itself without any conversation history.
            - Return **ONLY** the rewritten query. No explanation, no prefix, no markdown.

            ### Examples of good rewriting:
            - User: "اسم من چی بود" → "نام من محمد رضا است، لطفاً آن را به خاطر بسپار."
            - User: "اون چطوره؟" (after talking about a building) → "وضعیت ساختمان شماره X در سامانه پادشارژ چگونه است؟"
            """)
        return prompt 
    # @staticmethod
    # def get_rewrite_query_prompt() -> ChatPromptTemplate:
    #     prompt = ChatPromptTemplate.from_template(
    #         """You are a Query Rewriter for a conversational RAG system.
    #             ##Current Question:
    #             {question}

    #             ##Conversation History (excluding current question):
    #             {recent_messages}

    #             Your task:

    #             1. Determine whether the current question depends on conversation context.
    #             2. If it does:
    #             - Resolve all pronouns, references, omitted subjects and follow-up context.
    #             - Rewrite the question as a fully standalone query.
    #             3. If it does not:
    #             - Rewrite only to improve clarity and retrieval quality.

    #             Requirements:
    #             - Preserve the user's original language.
    #             - Preserve intent exactly.
    #             - Do not invent information.
    #             - Use only information explicitly present in the conversation.
    #             - The output must be understandable without seeing the conversation.
    #             - Return only the rewritten query.
    #         """
    #     )
    #     return prompt 

    @staticmethod
    def get_router_prompt() -> ChatPromptTemplate:
        prompt = ChatPromptTemplate.from_template("""
            تو یک روتر هوشمند و بسیار دقیق هستی.

            سؤال کاربر: {question}

            فرآیندهای موجود:
            {processes_info}

            تسک تو:
            بررسی کن درخواست کاربر مربوط به اجرای یکی از فرآیندهای بالا هست یا نه.

            **فقط** JSON زیر را برگردان و هیچ متن دیگری ننویس (حتی یک کلمه قبل یا بعدش):

            {{
            "type": "PROCESS",
            "process_id": "آیدی_فرآیند_دقیق"
            }}

            یا

            {{
            "type": "RAG",
            "process_id": null
            }}

            قوانین سخت:
            - همیشه از "type" و "process_id" با حروف کوچک استفاده کن.
            - اگر RAG بود، حتماً `null` را با حروف **کوچک** بنویس.
            - process_id باید دقیقاً مطابق آیدی موجود در لیست Processes باشد.
            - هیچ توضیح، کامنت، یا متن اضافی ننویس.
            - JSON باید ۱۰۰٪ معتبر باشد.
            """)
        return prompt
    @staticmethod
    def get_grade_documents_prompt() -> ChatPromptTemplate:
        prompt = ChatPromptTemplate.from_template(
        """تو یک قاضی بسیار دقیق و سخت‌گیر در سیستم RAG هستی.

        سوال کاربر:
        {question}

        اسناد زیر را یکی‌یکی بررسی کن:

        {context}

        برای هر سند دقیقاً یک خط به این شکل بنویس (هیچ کلمه اضافی، هیچ توضیحی، هیچ فاصله اضافی):

        سند ۱: YES
        سند ۲: NO
        سند ۳: YES
        ...

        قوانین طلایی (حتما رعایت کن):
        - YES فقط وقتی که سند **مستقیماً** به سوال پاسخ می‌دهد یا اطلاعات کلیدی و مرتبط دارد.
        - NO در همه موارد دیگر (حتی اگر کمی مرتبط باشد).
        - دقیقاً به تعداد اسناد خط خروجی بده.
        - هیچ چیز دیگری ننویس (نه توضیح، نه "سند ۱:" اضافه، نه فاصله خالی).

        شروع کن:"""
            )

        return prompt

    # @staticmethod
    # def get_assistant_response_prompt() -> ChatPromptTemplate:
    #             prompt = ChatPromptTemplate.from_messages([
    #                 ("system","""
    #                 You are an intelligent business assistant with these capabilities:

    #                 ### 1. Core Functions
    #                 - You are an AI assistant specialized in {assistant_description}.
    #                 - Only respond to questions within this domain.
    #                 - Politely decline unrelated requests.
    #                 - If the user’s query is unclear, ask clarifying questions.
    #                 - Business Description: {assistant_description}

    #                 ### 2. Knowledge Base Rules
    #                 - RAG Context Handling:
    #                 "Available Context Documents:{context}"

    #                 ### 3. Process Detection
    #                 - When a user request matches a predefined process, detect it and include its **process_id**.
    #                 - If no process matches, set process_id = null.
    #                 - Available Processes:
    #                 {processes_section}

    #                 ### 4. Response Format (IMPORTANT)
    #                 Always output your final response in this **exact format** — never add extra text, explanations, or markdown before or after it:

    #                 [TEXT]
    #                 <your human-friendly answer here>
    #                 [/TEXT]

    #                 [PROCESS_ID]
    #                 <detected_process_id_or_null>
    #                 [/PROCESS_ID]

    #                 Example:
    #                 [TEXT]
    #                 برای شارژ حساب خود مراحل زیر را انجام دهید...
    #                 [/TEXT]
    #                 [PROCESS_ID]
    #                 7a6b1e72-7fcc-440f-a544-0076bb6658c7
    #                 [/PROCESS_ID]

    #                 ### 5. Token Management
    #                 - Respect token limits: {max_tokens}
    #                 """.strip()),
    #                 ("human", "{question}")
    #             ])
    #             return prompt
    @staticmethod
    def get_assistant_response_prompt() -> ChatPromptTemplate:
                prompt = ChatPromptTemplate.from_messages([
                    ("system","""
                    You are an intelligent business assistant with these capabilities:

                    ### 1. Core Functions
                    - You are an AI assistant specialized in {assistant_description}.
                    - Only respond to questions within this domain.
                    - Politely decline unrelated requests.
                    - If the user’s query is unclear, ask clarifying questions.
                    - Business Description: {assistant_description}

                    ### 2. Knowledge Base Rules
                    - RAG Context Handling:
                    "Available Context Documents:{context}"
                     
                    ### 3. Token Management
                    - Respect token limits: {max_tokens}
                    """.strip()),
                    ("human", "{question}")
                ])
                return prompt
