from langgraph.prebuilt import create_react_agent
from core.type.entity.assistant_entity import LLMOptions
from core.srv.factory.llm_factory import get_llm
from core.agents.hotel_agent.tools import book_hotel, check_availability, get_hotel_details, search_hotels
llm_options = LLMOptions(provider="deepseek", 
                         temperature=0.7, 
                         max_tokens=1500 , 
                         api_key="sk-1878eecec3c54d30823cdd3b6365e988", 
                         model_name="deepseek-v4-flash")

tools = [search_hotels, get_hotel_details, check_availability, book_hotel]
llm = get_llm(llm_options)
system_prompt = """تو یک دستیار حرفه‌ای رزرو هتل هستی.
مراحل کار را به ترتیب منطقی انجام بده:
1. ابتدا هتل‌ها را جستجو کن.
2. جزئیات هتل مناسب را بگیر.
3. موجودی را چک کن.
4. در نهایت رزرو را انجام بده.

همیشه با کاربر تعامل کن و اگر نیاز به اطلاعات بیشتری بود، از او بپرس.
پاسخ نهایی را واضح و مرتب بده."""

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt
)