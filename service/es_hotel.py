from typing import List
from elasticsearch import AsyncElasticsearch
from models.hotel import Hotel  # giả sử bạn đã định nghĩa model Hotel

es = AsyncElasticsearch("http://localhost:9200")
INDEX = "hotels"  # hoặc tên index bạn dùng

# Lấy điểm trung bình rating của khách sạn trong city
async def get_average_rating(city: str) -> float:
    agg_query = {
        "size": 0,
        "query": {
            "match_phrase": {
                "address": city
            }
        },
        "aggs": {
            "avg_rating": {"avg": {"field": "rating"}}
        }
    }
    resp = await es.search(index=INDEX, body=agg_query)
    return resp["aggregations"]["avg_rating"]["value"] or 0

# Lấy khách sạn theo thành phố
async def get_hotel_by_rating(city: str) -> List[Hotel]:
    query = {
        "size": 240,
        "query": {
            "match_phrase": {
                "address": city
            }
        }
    }
    resp = await es.search(index=INDEX, body=query)
    hits = resp["hits"]["hits"]

    hotels = []
    for hit in hits:
        source = hit["_source"]
        hotel = Hotel(**source)  # trực tiếp tạo model từ dict
        hotels.append(hotel)
    return hotels

# Tính weighted rating theo công thức IMDB
def calculate_weighted_rating(hotel: Hotel, min_reviews: int, C: float) -> float:
    v = hotel.review_count
    R = hotel.rating
    m = min_reviews
    if v == 0:
        return 0
    return (v / (v + m)) * R + (m / (v + m)) * C
