from fastapi import APIRouter, Query
from typing import List, Optional, Union
from models.hotel import Hotel
from service.es_hotel import get_average_rating, get_hotel_by_rating,calculate_weighted_rating
import re

router = APIRouter()


def _parse_price_to_int(price_point: Optional[Union[str, int]]) -> Optional[int]:
    if price_point is None:
        return None
    if isinstance(price_point, int):
        return price_point
    s = str(price_point).strip().lower()
    s = s.replace('vnđ', '').replace('vnd', '').replace('₫', '').strip()

    # Pattern: 2tr5 -> 2.5 triệu
    m = re.match(r"^\s*(\d+)\s*tr\s*(\d+)\s*$", s)
    if m:
        try:
            return int(m.group(1)) * 1_000_000 + int(m.group(2)) * 100_000
        except Exception:
            pass

    # Pattern: number with unit 'triệu'/'tr'/'m'
    m = re.search(r"([0-9]+(?:[\.,][0-9]+)?)\s*(triệu|tr|m)\b", s)
    if m:
        try:
            amount = m.group(1).replace(',', '.')
            return int(float(amount) * 1_000_000)
        except Exception:
            pass

    # Pattern: number with unit 'nghìn'/'ngàn'/'ngan'/'k'
    m = re.search(r"([0-9]+(?:[\.,][0-9]+)?)\s*(nghìn|ngàn|ngan|k)\b", s)
    if m:
        try:
            amount = m.group(1).replace(',', '.')
            return int(float(amount) * 1_000)
        except Exception:
            pass

    # Fallback: remove all non-digits (handles formats like 1.500.000 or 1,500,000)
    digits = re.sub(r"[^0-9]", "", s)
    if digits:
        try:
            return int(digits)
        except Exception:
            return None
    return None


def _filter_by_price_range(hotels: List[Hotel], min_price: Optional[int], max_price: Optional[int]) -> List[Hotel]:
    if min_price is None and max_price is None:
        return hotels
    filtered: List[Hotel] = []
    for h in hotels:
        p = _parse_price_to_int(h.price_point)
        if p is None:
            continue
        if min_price is not None and p < min_price:
            continue
        if max_price is not None and p > max_price:
            continue
        filtered.append(h)
    return filtered


# Lấy danh sách khách sạn hàng đầu theo rating và review count không chi phí 
@router.get("/top-hotel-rating", response_model=List[Hotel])
async def get_top_hotel_rating(
    city: Optional[str] = Query(None, description="Tên thành phố"),
    min_reviews: int = Query(3, description="Số lượt đánh giá tối thiểu (m)"),
    min_price: Optional[int] = Query(None, description="Giá tối thiểu"),
    max_price: Optional[int] = Query(None, description="Giá tối đa")
):
    target_city = city or "Hà Nội"

    # 1. Lấy điểm trung bình toàn bộ khách sạn (C)
    C = await get_average_rating(target_city)

    # 2. Lấy danh sách khách sạn của thành phố
    hotels = await get_hotel_by_rating(target_city)

    # 3. Tính weighted rating
    for hotel in hotels:
        hotel.weighted_rating = calculate_weighted_rating(hotel, min_reviews, C)

    # 4. Lọc theo khoảng giá nếu có
    hotels = _filter_by_price_range(hotels, min_price, max_price)

    # 5. Sắp xếp theo weighted rating giảm dần
    hotels_sorted = sorted(hotels, key=lambda h: h.weighted_rating or 0, reverse=True)
    return hotels_sorted[:5]


# Lấy danh sách khách sạn hàng đầu theo số sao, rating và review count không chi phí 
@router.get("/top-hotel-star", response_model=List[Hotel])
async def get_top_hotel_start(
    city: Optional[str] = Query(None, description="Tên thành phố"),
    min_reviews: int = Query(3, description="Số lượt đánh giá tối thiểu (m)"),
    stars: Optional[List[int]] = Query(None, description="Danh sách số sao muốn lọc, ví dụ: ?stars=3&stars=4"),
    min_price: Optional[int] = Query(None, description="Giá tối thiểu"),
    max_price: Optional[int] = Query(None, description="Giá tối đa")
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

    # 5. Lọc theo khoảng giá nếu có
    hotels = _filter_by_price_range(hotels, min_price, max_price)

    # 6. Sắp xếp theo weighted rating giảm dần
    hotels_sorted = sorted(hotels, key=lambda h: h.weighted_rating or 0, reverse=True)

    return hotels_sorted[:5]