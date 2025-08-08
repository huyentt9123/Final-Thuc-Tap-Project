from fastapi import APIRouter, Query
from typing import List
from service.searchFlight import search_flight_with_cache
from models.flight import FlightOffer

router = APIRouter()

@router.get("/search-flights", response_model=List[FlightOffer])
def search_flights(
    origin: str = Query(...),
    destination: str = Query(...),
    departure_date: str = Query(...),
    adults: int = Query(1)
):
    return search_flight_with_cache(origin, destination, departure_date, adults)