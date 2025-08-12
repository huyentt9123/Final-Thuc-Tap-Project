from typing import List
from elasticsearch import AsyncElasticsearch
from models.sightseeing import SightseeingArea

es = AsyncElasticsearch("http://localhost:9200")
INDEX = "sightseeing"  # hoặc tên index bạn dùng


# Lấy khu vui chơi theo thành phố
async def get_hotel_by_rating(city: str) -> List[SightseeingArea]:
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

    sightseeings = []
    for hit in hits:
        source = hit["_source"]
        source['open_close'] = source.get('open,close', None)
        source.pop('open,close', None)  # xóa trường cũ tránh lỗi Pydantic
        sightseeing = SightseeingArea(**source)  # trực tiếp tạo model từ dict
        sightseeings.append(sightseeing)
    return sightseeings