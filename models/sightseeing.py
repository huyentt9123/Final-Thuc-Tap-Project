
from pydantic import BaseModel
from typing import Optional

class SightseeingArea(BaseModel):
    name: str
    address: str
    price: Optional[str]                 # Giá dạng text (vd: "188.000vnd")
    approximate_price: Optional[int]     # Giá ước lượng dạng số
    open_close: Optional[str]         # Ví dụ: "07h00 - 20h30 hàng ngày"
    type: Optional[str]                   # indoor / outdoor
    describe: Optional[str]               # Mô tả địa điểm
