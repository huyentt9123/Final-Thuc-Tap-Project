from pydantic import BaseModel, HttpUrl
from typing import Optional, Union

class Hotel(BaseModel):
    name: str
    link: Optional[HttpUrl]
    image: Optional[HttpUrl]
    address: Optional[str]
    stars: Optional[int]
    rating: float
    review_count: int
    price_point: Optional[Union[str, int]]  # Chấp nhận chuỗi hoặc số nguyên
    weighted_rating: Optional[float] = None

    class Config:
        orm_mode = True
        allow_mutation = True   # Cho phép chỉnh sửa thuộc tính sau khi tạo object
