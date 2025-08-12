from fastapi import APIRouter, Query
from service.es_weather import get_latest_weather_by_city, get_forecast_by_city
from service.outfit import suggest_outfit_from_weather_doc
from datetime import datetime, timedelta
import re

router = APIRouter()

# lấy ra 5 khách sạn tốt nhất dựa vào điểm đánh giá và lượt đnánh giá nếu người dùng không nhập chi phí
@router.get("/rate-hotel")
def rate_hotel(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_latest_weather_by_city(city)
    return data or {"message": "Không có dữ liệu thời tiết"}

@router.get("/forecast-by-city")
def forecast_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_forecast_by_city(city)
    return data or {"message": "Không có dữ liệu dự báo"}
