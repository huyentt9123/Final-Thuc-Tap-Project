from pydantic import BaseModel
from typing import List, Optional

# 1 chặng
class FlightSegment(BaseModel):
    departure_iata: str
    arrival_iata: str
    departure_time: str
    arrival_time: str
    carrier_code: str
    flight_number: str
    duration: str

# 1 chuyến bay nhưng có nhiêu chặng
class FlightOffer(BaseModel):
    id: str
    price: int  # Giá vé bằng VND (số nguyên)
    currency: str
    segments: List[FlightSegment]
    seats_left: Optional[int]
    origin: str
    destination: str
    departure_date: str
    adults: int
    created_at: Optional[str] = None
    