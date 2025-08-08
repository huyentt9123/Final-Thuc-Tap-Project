from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

es = Elasticsearch("http://localhost:9200")
INDEX = "flight_offers"

def ensure_index():
    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX)
        print(f"Đã tạo index: {INDEX}")

# Gọi hàm này ở đầu chương trình hoặc trước khi truy vấn/ghi dữ liệu
ensure_index()
from models.flight import FlightOffer, FlightSegment

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
    return FlightOffer(
        id=offer["id"],
        price=float(offer["price"]["total"]),
        currency=offer["price"]["currency"],
        segments=segments,
        seats_left=offer.get("numberOfBookableSeats"),
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        adults=adults
    )

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

def save_flight_offer_to_es(flight_offer: dict):
    # Sử dụng id chuyến bay + ngày bay + origin + destination + adults làm _id để tránh trùng lặp theo tham số tìm kiếm
    doc_id = f"{flight_offer['id']}_{flight_offer['origin']}_{flight_offer['destination']}_{flight_offer['departure_date']}_{flight_offer.get('adults', 1)}"
    flight_offer["created_at"] = datetime.utcnow().isoformat()
    es.index(index=INDEX, id=doc_id, document=flight_offer)

def is_flight_data_fresh(doc, max_age_hours=12):
    created_at = datetime.fromisoformat(doc["created_at"]) if doc.get("created_at") else None
    if not created_at:
        return False
    return (datetime.utcnow() - created_at) < timedelta(hours=max_age_hours)