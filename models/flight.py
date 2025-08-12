from pydantic import BaseModel
from typing import List, Optional

class FlightSegment(BaseModel):
    departure_iata: str
    arrival_iata: str
    departure_time: str
    arrival_time: str
    carrier_code: str
    flight_number: str
    duration: str

class FlightOffer(BaseModel):
    id: str
    price: float
    currency: str
    segments: List[FlightSegment]
    seats_left: Optional[int]
    origin: str
    destination: str
    departure_date: str
    adults: int
    created_at: Optional[str] = None
    