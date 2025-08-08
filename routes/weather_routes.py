from fastapi import APIRouter, Query
from service.es_weather import get_latest_weather_by_city, get_forecast_by_city

router = APIRouter()

@router.get("/by-city")
def weather_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_latest_weather_by_city(city)
    return data or {"message": "Không có dữ liệu thời tiết"}

@router.get("/forecast-by-city")
def forecast_by_city(city: str = Query(..., description="Tên thành phố, ví dụ: Hanoi")):
    data = get_forecast_by_city(city)
    return data or {"message": "Không có dữ liệu dự báo"}
