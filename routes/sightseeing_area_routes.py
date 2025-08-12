
from fastapi import APIRouter, Query
from typing import Optional
from service.es_sightseeing import get_hotel_by_rating
router = APIRouter()

# Lấy danh sách khu tham quan theo thành phố và thời tiết (không có chi phí)

@router.get("/no-cost-sightseeing")
async def get_no_cost_sightseeing(city: Optional[str] = Query(None, description="Tên thành phố")):
    return await get_hotel_by_rating(city)