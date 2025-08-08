from elasticsearch import Elasticsearch
from typing import Optional, Dict, List
from datetime import datetime

es = Elasticsearch("http://localhost:9200")
INDEX = "weather"

# Map mã sân bay → tên city trong ES
AIRPORT_TO_CITY: Dict[str, str] = {
    "HAN": "Hanoi",
    "SGN": "Ho Chi Minh City",
    "DAD": "Da Nang",
    "CXR": "Nha Trang",
    "VDO": "Ha Long",
}

def get_latest_weather_by_city(city: str) -> Optional[dict]:
    # Ưu tiên type current; nếu không có thì lấy bất kỳ
    query_current = {
        "bool": {
            "must": [
                {"match": {"city": city}},
                {"term": {"type": "current"}},
            ]
        }
    }
    res = es.search(index=INDEX, query=query_current, size=1, sort=[{"timestamp": {"order": "desc"}}])
    hits = res.get("hits", {}).get("hits", [])
    if hits:
        return hits[0]["_source"]
    # fallback: không filter type
    query_any = {"match": {"city": city}}
    res = es.search(index=INDEX, query=query_any, size=1, sort=[{"timestamp": {"order": "desc"}}])
    hits = res.get("hits", {}).get("hits", [])
    if hits:
        return hits[0]["_source"]
    return None

# def get_latest_weather_by_airport(airport_code: str) -> Optional[dict]:
#     city = AIRPORT_TO_CITY.get(airport_code.upper())
#     if not city:
#         return None
#     return get_latest_weather_by_city(city)

def get_forecast_by_city(city: str, days: int = 6) -> dict:
    # Lấy dự báo từ bây giờ trở đi, type=forecast, sort theo thời gian
    now_iso = datetime.utcnow().isoformat()
    query = {
        "bool": {
            "must": [
                {"match": {"city": city}},
                {"term": {"type": "forecast"}},
                {"range": {"forecast_time": {"gte": now_iso}}}
            ]
        }
    }
    # tối đa 5 ngày * 8 mốc/ ngày (3h) ~ 40
    size = max(40, days * 8)
    res = es.search(index=INDEX, query=query, size=size, sort=[{"forecast_time": {"order": "asc"}}])
    hits = res.get("hits", {}).get("hits", [])
    grouped: Dict[str, List[dict]] = {}
    for h in hits:
        src = h.get("_source", {})
        date_key = src.get("forecast_date") or (src.get("forecast_time", "")[0:10])
        item = {
            "time": src.get("forecast_time"),
            "hour": src.get("forecast_hour"),
            "description": src.get("description"),
            "temperature_c": src.get("temperature_c"),
            "feels_like_c": src.get("feels_like_c"),
            "humidity": src.get("humidity"),
            "wind_speed": src.get("wind_speed"),
        }
        grouped.setdefault(date_key, []).append(item)
    days_list = []
    for date_key in sorted(grouped.keys())[:days]:
        days_list.append({"date": date_key, "items": grouped[date_key]})
    return {"city": city, "days": days_list}


