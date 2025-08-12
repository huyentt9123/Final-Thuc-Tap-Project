from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from typing import Dict

from pymongo import MongoClient
from utils.config import settings

es = Elasticsearch("http://localhost:9200")
INDEX = "flight_offers"

# MongoDB setup (chỉ để lưu, không dùng tìm kiếm)
try:
    _mongo_client = MongoClient(settings.MONGODB_URL)
    _mongo_db = _mongo_client[settings.DATABASE_NAME]
    _mongo_col = _mongo_db["flight_offers"]
except Exception as _e:
    _mongo_client = None
    _mongo_col = None
    print(f"[Mongo] init error: {_e}")


def ensure_index():
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX)
        print(f"Đã tạo index: {INDEX}")

# Gọi hàm này ở đầu chương trình hoặc trước khi truy vấn/ghi dữ liệu
ensure_index()
from models.flight import FlightOffer, FlightSegment

# Tỷ giá USD sang VND (có thể cập nhật từ API tỷ giá thực tế)
USD_TO_VND_RATE = 24000

def convert_price_to_vnd(price: float, currency: str) -> int:
    """Chuyển đổi giá từ tiền tệ gốc sang VND (số nguyên)"""
    if currency == "VND":
        return int(price)
    elif currency == "USD":
        return int(price * USD_TO_VND_RATE)
    else:
        # Mặc định coi như USD nếu không biết loại tiền tệ
        return int(price * USD_TO_VND_RATE)

def map_amadeus_to_model(offer: dict, origin: str, destination: str, departure_date: str, adults: int) -> FlightOffer:
    segments = []
    for itinerary in offer.get("itineraries", []):
        for seg in itinerary.get("segments", []):
            segments.append(FlightSegment(
                departure_iata=seg["departure"]["iataCode"],
                arrival_iata=seg["arrival"]["iataCode"],
                departure_time=seg["departure"]["at"],
                arrival_time=seg["arrival"]["at"],
                carrier_code=seg["carrierCode"],
                flight_number=seg["number"],
                duration=seg["duration"]
            ))
    # Chuyển đổi giá sang VND
    original_price = float(offer["price"]["total"])
    original_currency = offer["price"]["currency"]
    price_vnd = convert_price_to_vnd(original_price, original_currency)
    
    return FlightOffer(
        id=offer["id"],
        price=price_vnd,  # Giá đã chuyển sang VND
        currency="VND",   # Luôn lưu bằng VND
        segments=segments,
        seats_left=offer.get("numberOfBookableSeats"),
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        adults=adults
    )

def _build_doc_id(doc: Dict) -> str:
    return f"{doc['id']}_{doc['origin']}_{doc['destination']}_{doc['departure_date']}_{doc.get('adults', 1)}"


def get_flight_from_es(origin, destination, departure_date, adults=1):
    query = {
        "bool": {
            "must": [
                {"match": {"origin": origin}},
                {"match": {"destination": destination}},
                {"match": {"departure_date": departure_date}},
                {"term": {"adults": adults}},
            ]
        }
    }
    res = es.search(index=INDEX, query=query, size=1)
    hits = res["hits"]["hits"]
    print(f"[ES] get_flight_from_es hits: {len(hits)}")
    if hits:
        return hits[0]["_source"]
    return None

# Hàm mới: lấy tất cả chuyến bay theo bộ tham số (cache list)
def get_flights_from_es(origin, destination, departure_date, adults=1):
    query = {
        "bool": {
            "must": [
                {"match": {"origin": origin}},
                {"match": {"destination": destination}},
                {"match": {"departure_date": departure_date}},
                {"term": {"adults": adults}},
            ]
        }
    }
    res = es.search(index=INDEX, query=query, size=200)
    hits = res["hits"]["hits"]
    print(f"[ES] get_flights_from_es hits: {len(hits)}")
    return [h["_source"] for h in hits]


def _save_to_mongo(doc: Dict) -> None:
    if _mongo_col is None:
        return
    try:
        doc_id = _build_doc_id(doc)
        body = dict(doc)
        body["_id"] = doc_id
        _mongo_col.update_one({"_id": doc_id}, {"$set": body}, upsert=True)
    except Exception as e:
        print(f"[Mongo] save error: {e}")


def save_flight_offer_to_es(flight_offer: dict):
    # Sử dụng id chuyến bay + ngày bay + origin + destination + adults làm _id để tránh trùng lặp theo tham số tìm kiếm
    doc_id = _build_doc_id(flight_offer)
    flight_offer["created_at"] = datetime.utcnow().isoformat()
    es.index(index=INDEX, id=doc_id, document=flight_offer)
    # Ghi song song vào Mongo để người khác có thể xem
    _save_to_mongo(flight_offer)


def is_flight_data_fresh(doc, max_age_hours=12):
    created_at = datetime.fromisoformat(doc["created_at"]) if doc.get("created_at") else None
    if not created_at:
        return False
    return (datetime.utcnow() - created_at) < timedelta(hours=max_age_hours)