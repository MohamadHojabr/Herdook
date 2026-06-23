import httpx
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek
from core.type.entity.assistant_entity import LLMOptions   

def get_llm(llm_model: LLMOptions, streaming: bool = False):
    """سوئیچ بین مدل‌ها با پشتیبانی صحیح از streaming"""
    provider = llm_model.provider.lower().strip()
    
    # ایجاد دو کلاینت جدا (sync + async) — این مهم‌ترین قسمت است
    http_client = httpx.Client(verify=False, timeout=60.0)
    http_async_client = httpx.AsyncClient(verify=False, timeout=60.0)

    common_params = {
        "temperature": llm_model.temperature,
        "max_tokens": llm_model.max_tokens,
        "streaming": streaming,
    }

    if provider == "openai":
        return ChatOpenAI(
            model=llm_model.model_name,
            api_key=llm_model.api_key,
            http_client=http_client,
            http_async_client=http_async_client,   # ← خیلی مهم برای streaming + astream
            **common_params
        )

    elif provider == "deepseek":
        # اگر از langchain_deepseek استفاده می‌کنی:
        return ChatDeepSeek(
            model=llm_model.model_name,
            api_key=llm_model.api_key,
            http_client=http_client,
            http_async_client=http_async_client,
            **common_params
        )

    elif provider == "groq":
        return ChatGroq(
            model=llm_model.model_name,
            api_key=llm_model.api_key,
            http_client=http_client,
            http_async_client=http_async_client,
            **common_params
        )

    elif provider == "anthropic":
        return ChatAnthropic(
            model=llm_model.model_name,
            api_key=llm_model.api_key,
            http_client=http_client,
            http_async_client=http_async_client,
            **common_params
        )

    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=llm_model.model_name,
            api_key=llm_model.api_key,
            http_client=http_client,           # بعضی مدل‌ها فقط sync قبول می‌کنن
            http_async_client=http_async_client,
            **common_params
        )

    elif provider.startswith("ollama"):
        # Ollama معمولاً نیازی به http_client خاص نداره
        return ChatOllama(
            model=llm_model.model_name,
            temperature=llm_model.temperature,
            # streaming رو LangChain خودش مدیریت می‌کنه
        )

    # fallback
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=llm_model.api_key,
        http_client=http_client,
        http_async_client=http_async_client,
        streaming=streaming,
        temperature=llm_model.temperature
    )