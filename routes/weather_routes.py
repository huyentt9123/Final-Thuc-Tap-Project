from fastapi import APIRouter, Query
from service.es_weather import get_latest_weather_by_city, get_forecast_by_city
from service.outfit import suggest_outfit_from_weather_doc
from datetime import datetime, timedelta
import re

router = APIRouter()

@router.get("/by-city")
def get_weather_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    """Lấy thời tiết hiện tại của thành phố"""
    data = get_latest_weather_by_city(city)
    return data or {"message": "Không có dữ liệu thời tiết"}

@router.get("/outfit-by-city")
def outfit_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    w = get_latest_weather_by_city(city)
    if not w:
        return {"message": "Không có dữ liệu thời tiết để gợi ý trang phục"}
    return suggest_outfit_from_weather_doc(w)

@router.get("/outfit-by-date")
def outfit_by_date(
    city: str = Query(..., description="Tên thành phố"),
    date: str = Query(..., description="Ngày YYYY-MM-DD")
):
    """Gợi ý outfit cho 1 ngày cụ thể"""
    forecast_data = get_forecast_by_city(city, 5)
    if not forecast_data.get("days"):
        return {"message": "Không có dữ liệu dự báo"}
    
    # Tìm ngày khớp
    target_day = None
    for day in forecast_data["days"]:
        if day["date"] == date:
            target_day = day
            break
    
    if not target_day or not target_day["items"]:
        available_dates = [day["date"] for day in forecast_data["days"]]
        return {"message": f"Không có dữ liệu thời tiết cho ngày {date}. Các ngày có sẵn: {', '.join(available_dates)}"}
    
    # Lấy mốc trưa (12:00) hoặc mốc gần nhất
    target_item = None
    for item in target_day["items"]:
        if item.get("hour") == "12:00":
            target_item = item
            break
    if not target_item:
        target_item = target_day["items"][len(target_day["items"])//2]
    
    outfit = suggest_outfit_from_weather_doc(target_item)
    return {
        "date": date,
        "city": city,
        "outfit": outfit,
        "sample_time": target_item.get("hour", ""),
        "weather_note": f"Trạng thái: {target_item.get('description', '')} - {target_item.get('temperature_c', 0)}°C"
    }
# lấy ra 5 khách sạn tốt nhất dựa vào điểm đánh giá và lượt đnánh giá nếu người dùng không nhập chi phí
@router.get("/rate-hotel")
def rate_hotel(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_latest_weather_by_city(city)
    return data or {"message": "Không có dữ liệu thời tiết"}

@router.get("/forecast-by-city")
def forecast_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_forecast_by_city(city)
    return data or {"message": "Không có dữ liệu dự báo"}
