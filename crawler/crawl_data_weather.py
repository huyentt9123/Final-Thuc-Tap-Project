import requests
import json
from datetime import datetime
from elasticsearch import Elasticsearch

# Kết nối Elasticsearch
es = Elasticsearch("http://localhost:9200")

# API key của bạn
API_KEY = "d8d6bdab1952598b62551beae207c7fe"
BASE_URL = "https://api.openweathermap.org/data/2.5"

def crawl_weather_by_coordinates(lat=21.0278, lon=105.8342, city_name="Hanoi"):
    """Crawl thời tiết theo tọa độ (Hà Nội)"""
    print("=== CRAWL THỜI TIẾT THEO TỌA ĐỘ ===")
    
    try:
        url = f"{BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',  # Celsius
            'lang': 'vi'  # Tiếng Việt
        }
        
        print(f"🌍 Crawl thời tiết tại tọa độ: {lat}, {lon}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_info = {
                "city": city_name,
                "country": data['sys']['country'],
                "coordinates": {"lat": lat, "lon": lon},
                "temperature_c": data['main']['temp'],
                "feels_like_c": data['main']['feels_like'],
                "temperature_min": data['main']['temp_min'],
                "temperature_max": data['main']['temp_max'],
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "description": data['weather'][0]['description'],
                "main_weather": data['weather'][0]['main'],
                "wind_speed": data['wind']['speed'],
                "wind_direction": data['wind'].get('deg', 0),
                "cloudiness": data['clouds']['all'],
                "visibility": data.get('visibility', 0) / 1000,  # km
                "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
                "sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'),
                "timestamp": datetime.now().isoformat(),
                "source": "openweathermap_coordinates",
                "type": "current"
            }
            
            print(f"📍 Thành phố: {data['name']}, {data['sys']['country']}")
            print(f"🌡️  Nhiệt độ: {data['main']['temp']}°C (cảm giác như {data['main']['feels_like']}°C)")
            print(f"🌤️  Thời tiết: {data['weather'][0]['description']}")
            print(f"💧 Độ ẩm: {data['main']['humidity']}%")
            print(f"💨 Gió: {data['wind']['speed']} m/s")
            print(f"🌅 Bình minh: {weather_info['sunrise']}")
            print(f"🌇 Hoàng hôn: {weather_info['sunset']}")
            
            return weather_info
        else:
            print(f"❌ Lỗi API: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi crawl thời tiết: {e}")
        return None



def crawl_forecast_5days(lat=21.0278, lon=105.8342, city_name="Hanoi"):
    """Crawl dự báo thời tiết 5 ngày"""
    print("=== DỰ BÁO THỜI TIẾT 5 NGÀY ===")
    
    try:
        url = f"{BASE_URL}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'vi'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            forecasts = []
            
            print(f"📅 Dự báo 5 ngày cho {city_name}:")
            
            for i, forecast in enumerate(data['list']):  # Lấy hết 40 bản ghi
                forecast_time = datetime.fromtimestamp(forecast['dt'])
                
                forecast_info = {
                    "city": city_name,
                    "forecast_time": forecast_time.isoformat(),
                    "forecast_date": forecast_time.strftime('%Y-%m-%d'),
                    "forecast_hour": forecast_time.strftime('%H:%M'),
                    "temperature_c": forecast['main']['temp'],
                    "feels_like_c": forecast['main']['feels_like'],
                    "humidity": forecast['main']['humidity'],
                    "pressure": forecast['main']['pressure'],
                    "description": forecast['weather'][0]['description'],
                    "wind_speed": forecast['wind']['speed'],
                    "cloudiness": forecast['clouds']['all'],
                    "rain_3h": forecast.get('rain', {}).get('3h', 0),
                    "timestamp": datetime.now().isoformat(),
                    "source": "openweathermap_forecast",
                    "type": "forecast"
                }
                
                forecasts.append(forecast_info)
                
                if i < 8:  # Hiển thị 8 dự báo đầu tiên
                    print(f"  📅 {forecast_time.strftime('%d/%m %H:%M')}: {forecast['main']['temp']}°C - {forecast['weather'][0]['description']}")
            
            print(f"✅ Lấy được {len(forecasts)} dự báo")
            return forecasts
        else:
            print(f"❌ Lỗi forecast API: {response.status_code}")
            return []
        
    except Exception as e:
        print(f"❌ Lỗi crawl forecast: {e}")
        return []

def crawl_multiple_cities_vietnam():
    """Crawl thời tiết hiện tại và dự báo 5 ngày cho nhiều thành phố Việt Nam"""
    print("=== CRAWL NHIỀU THÀNH PHỐ VIỆT NAM (HIỆN TẠI & DỰ BÁO) ===")
    
    vietnam_cities = [
        {"name": "Hanoi", "lat": 21.0278, "lon": 105.8342},
        {"name": "Ho Chi Minh City", "lat": 10.8231, "lon": 106.6297},
        {"name": "Da Nang", "lat": 16.0471, "lon": 108.2068},
        {"name": "Nha Trang", "lat": 12.2821, "lon": 109.1814},
        {"name": "Ha Long", "lat": 20.9334, "lon": 107.2750}
    ]
    
    all_weather = []
    
    for city in vietnam_cities:
        print(f"\n🏙️  Đang crawl {city['name']}...")
        try:
            # Crawl thời tiết hiện tại
            weather = crawl_weather_by_coordinates(
                lat=city['lat'], 
                lon=city['lon'], 
                city_name=city['name']
            )
            if weather:
                weather["type"] = "current"
                all_weather.append(weather)
            # Crawl dự báo 5 ngày
            forecasts = crawl_forecast_5days(
                lat=city['lat'],
                lon=city['lon'],
                city_name=city['name']
            )
            all_weather.extend(forecasts)
            # Tránh spam API
            import time
            time.sleep(1)
        except Exception as e:
            print(f"❌ Lỗi crawl {city['name']}: {e}")
    return all_weather

def save_to_elasticsearch(weather_data):
    """Lưu vào Elasticsearch"""
    try:
        if isinstance(weather_data, list):
            for data in weather_data:
                es.index(index="weather", document=data)
            print(f"💾 Đã lưu {len(weather_data)} bản ghi vào Elasticsearch")
        else:
            es.index(index="weather", document=weather_data)
            print("💾 Đã lưu 1 bản ghi vào Elasticsearch")
    except Exception as e:
        print(f"❌ Lỗi Elasticsearch: {e}")

def delete_all_weather_data():
    try:
        es.indices.delete(index="weather", ignore=[400, 404])
        print("🗑️ Đã xóa toàn bộ dữ liệu cũ trong index 'weather'")
    except Exception as e:
        print(f"❌ Lỗi khi xóa index: {e}")


if __name__ == "__main__":
    print("🌤️  CRAWL THỜI TIẾT OPENWEATHERMAP")
    print("="*60)
    
    # Xóa dữ liệu cũ trước khi crawl mới
    delete_all_weather_data()
    
    all_data = []
    
    # Crawl nhiều thành phố (hiện tại & dự báo)
    cities_weather = crawl_multiple_cities_vietnam()
    all_data.extend(cities_weather)
    
    # Lưu dữ liệu
    if all_data:
        save_to_elasticsearch(all_data)
        print(f"\n🎯 HOÀN THÀNH! Crawl được {len(all_data)} bản ghi thời tiết")
        # Thống kê
        current_count = sum(1 for item in all_data if item.get('type') == 'current')
        forecast_count = sum(1 for item in all_data if item.get('type') == 'forecast')
        print(f"   📊 Thời tiết hiện tại: {current_count} bản ghi")
        print(f"   📅 Dự báo: {forecast_count} bản ghi")
    
