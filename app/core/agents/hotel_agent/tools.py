from langchain_core.tools import tool
from typing import Optional

@tool
def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    min_stars: Optional[int] = None
) -> str:
    """جستجوی هتل در شهر مورد نظر"""
    # در واقعیت به API هتل متصل می‌شود
    return f"""
    در {city} برای تاریخ {check_in} تا {check_out}، {guests} نفر:
    - هتل اسپادانا (۴ ستاره) - قیمت: ۲,۸۰۰,۰۰۰ تومان
    - هتل عباسی (۵ ستاره) - قیمت: ۴,۲۰۰,۰۰۰ تومان
    - هتل کوثر (۴ ستاره) - قیمت: ۲,۴۰۰,۰۰۰ تومان
    """

@tool
def get_hotel_details(hotel_id: str) -> str:
    """دریافت جزئیات کامل یک هتل"""
    if hotel_id == "spadana":
        return "هتل اسپادانا: ۴ ستاره، نزدیک میدان امام، صبحانه رایگان، استخر، پارکینگ"
    return "اطلاعات هتل یافت نشد."

@tool
def check_availability(
    hotel_id: str,
    check_in: str,
    check_out: str,
    guests: int
) -> str:
    """چک کردن موجودی و قیمت دقیق"""
    return f"اتاق برای هتل {hotel_id} در تاریخ‌های مورد نظر موجود است. قیمت کل: ۸,۴۰۰,۰۰۰ تومان"

@tool
def book_hotel(
    hotel_id: str,
    check_in: str,
    check_out: str,
    guests: int,
    guest_name: str
) -> str:
    """رزرو نهایی هتل"""
    return f"""
    رزرو با موفقیت انجام شد!
    کد رزرو: RZ-{guest_name[:3].upper()}-7842
    هتل: {hotel_id}
    تاریخ: {check_in} تا {check_out}
    تعداد نفر: {guests}
    """