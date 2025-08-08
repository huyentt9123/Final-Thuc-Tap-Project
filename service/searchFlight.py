from service.flightAPI import search_flights_amadeus

from service.es_flight import (
    save_flight_offer_to_es,
    map_amadeus_to_model,
    get_flights_from_es,
    is_flight_data_fresh,
)

def search_flight_with_cache(origin, destination, departure_date, adults=1):
    # 1) Thử lấy từ Elasticsearch
    cached_offers = get_flights_from_es(origin, destination, departure_date, adults)
    if cached_offers:
        # Kiểm tra độ mới của một bản ghi
        if is_flight_data_fresh(cached_offers[0]):
            print("[Flights] Source: elasticsearch (cache hit)")
            return cached_offers

    # 2) Không có hoặc đã cũ -> Gọi Amadeus
    offers = search_flights_amadeus(origin, destination, departure_date, adults)
    saved_offers = []
    for offer in offers:
        mapped = map_amadeus_to_model(offer, origin, destination, departure_date, adults)
        doc = mapped.model_dump()
        save_flight_offer_to_es(doc)
        saved_offers.append(doc)
    print("[Flights] Source: amadeus (cache miss -> fetched & saved)")
    return saved_offers