from service.searchFlight import search_flight_with_cache

# Danh sách các tuyến phổ biến
popular_routes = [
    ("HAN", "SGN"),
    ("SGN", "HAN"),
    ("HAN", "DAD"),
    ("SGN", "DAD"),
    # ... thêm tuyến khác nếu muốn
]

from datetime import datetime, timedelta

def crawl_next_5_days():
    for origin, destination in popular_routes:
        for i in range(1, 6):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            print(f"Crawling {origin} -> {destination} on {date}")
            search_flight_with_cache(origin, destination, date, adults=1)

if __name__ == "__main__":
    crawl_next_5_days()