from fastapi import APIRouter, Query
from typing import List, Optional
from models.hotel import Hotel
from service.es_hotel import get_average_rating, get_hotel_by_rating,calculate_weighted_rating

router = APIRouter()

# Lấy danh sách khách sạn hàng đầu theo rating và review count không chi phí 
@router.get("/top-hotel-rating", response_model=List[Hotel])
async def get_top_hotel_rating(
    city: Optional[str] = Query(None, description="Tên thành phố"),
    min_reviews: int = Query(3, description="Số lượt đánh giá tối thiểu (m)")
):
    target_city = city or "Hà Nội"

    # 1. Lấy điểm trung bình toàn bộ khách sạn (C)
    C = await get_average_rating(target_city)

    # 2. Lấy danh sách khách sạn của thành phố
    hotels = await get_hotel_by_rating(target_city)

    for hotel in hotels:
        hotel.weighted_rating = calculate_weighted_rating(hotel, min_reviews, C)

    hotels_sorted = sorted(hotels, key=lambda h: h.weighted_rating or 0, reverse=True)
    return hotels_sorted[:5]


# Lấy danh sách khách sạn hàng đầu theo số sao, rating và review count không chi phí 
@router.get("/top-hotel-star", response_model=List[Hotel])
async def get_top_hotel_start(
    city: Optional[str] = Query(None, description="Tên thành phố"),
    min_reviews: int = Query(3, description="Số lượt đánh giá tối thiểu (m)"),
    stars: Optional[List[int]] = Query(None, description="Danh sách số sao muốn lọc, ví dụ: ?stars=3&stars=4")
):
    target_city = city or "Hà Nội"

    # 1. Lấy điểm trung bình toàn bộ khách sạn (C)
    C = await get_average_rating(target_city)

    # 2. Lấy danh sách khách sạn của thành phố
    hotels = await get_hotel_by_rating(target_city)

    # 3. Nếu có lọc theo số sao
    if stars:
        hotels = [h for h in hotels if h.stars in stars]

    # 4. Tính weighted rating
    for hotel in hotels:
        hotel.weighted_rating =  calculate_weighted_rating(hotel, min_reviews, C)

    # 5. Sắp xếp theo weighted rating giảm dần
    hotels_sorted = sorted(hotels, key=lambda h: h.weighted_rating or 0, reverse=True)

    return hotels_sorted[:5]