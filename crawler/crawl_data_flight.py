# import requests
# import json
# import datetime
# from typing import List, Dict, Optional
# import time
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk

# class FlightCrawler:
#     """Crawl dữ liệu chuyến bay tới các thành phố du lịch Việt Nam"""
    
#     def __init__(self, api_key: str, elasticsearch_host: str = "http://localhost:9200"):
#         self.api_key = api_key
#         self.base_url = "https://api.aviationstack.com/v1/flights"
        
#         # Kết nối Elasticsearch
#         try:
#             self.es = Elasticsearch(elasticsearch_host)
#             # Test kết nối
#             if self.es.ping():
#                 print(f"✅ Kết nối Elasticsearch thành công: {elasticsearch_host}")
#             else:
#                 print(f"❌ Không thể kết nối Elasticsearch: {elasticsearch_host}")
#                 self.es = None
#         except Exception as e:
#             print(f"❌ Lỗi kết nối Elasticsearch: {e}")
#             self.es = None
        
#         # Danh sách các sân bay du lịch chính tại Việt Nam
#         self.vietnam_airports = {
#             "SGN": {
#                 "name": "Tân Sơn Nhất", 
#                 "city": "Hồ Chí Minh (Sài Gòn)",
#                 "region": "Miền Nam"
#             },
#             "HAN": {
#                 "name": "Nội Bài", 
#                 "city": "Hà Nội",
#                 "region": "Miền Bắc"
#             },
#             "DAD": {
#                 "name": "Đà Nẵng", 
#                 "city": "Đà Nẵng", 
#                 "region": "Miền Trung"
#             },
#             "PQC": {
#                 "name": "Phú Quốc", 
#                 "city": "Phú Quốc",
#                 "region": "Miền Nam"
#             },
#             "CXR": {
#                 "name": "Cam Ranh", 
#                 "city": "Nha Trang",
#                 "region": "Miền Trung"
#             },
#             "HPH": {
#                 "name": "Cát Bi", 
#                 "city": "Hải Phòng",
#                 "region": "Miền Bắc"
#             },
#             "HUI": {
#                 "name": "Phú Bài", 
#                 "city": "Huế",
#                 "region": "Miền Trung"
#             },
#             "VCA": {
#                 "name": "Cần Thơ", 
#                 "city": "Cần Thơ",
#                 "region": "Miền Nam"
#             }
#         }
        
#         # Các hãng hàng không Việt Nam
#         self.vietnam_airlines = [
#             "VN",  # Vietnam Airlines
#             "VJ",  # VietJet Air
#             "QH",  # Bamboo Airways
#             "BL"   # Jetstar Pacific
#         ]

#     def test_api_connection(self) -> bool:
#         """Test kết nối API với một request đơn giản"""
#         print("🔍 Đang test kết nối API aviationstack...")
        
#         params = {
#             'access_key': self.api_key,
#             'limit': 1
#         }
        
#         try:
#             response = requests.get(self.base_url, params=params)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 print(f"✅ API hoạt động tốt. Tìm thấy {data.get('pagination', {}).get('total', 0)} chuyến bay")
#                 return True
#             elif response.status_code == 401:
#                 print("❌ API Key không hợp lệ hoặc đã hết hạn")
#                 return False
#             elif response.status_code == 429:
#                 print("❌ Đã vượt quota API (100 requests/tháng)")
#                 return False
#             else:
#                 print(f"❌ Lỗi API: {response.status_code}")
#                 print(f"Response: {response.text}")
#                 return False
                
#         except Exception as e:
#             print(f"❌ Lỗi kết nối API: {e}")
#             return False

#     def get_flights_to_airport(self, airport_iata: str, limit: int = 50) -> Dict:
#         """Lấy dữ liệu chuyến bay đến một sân bay cụ thể"""
#         print(f"Đang lấy dữ liệu chuyến bay tới {airport_iata} - {self.vietnam_airports[airport_iata]['city']}")
        
#         params = {
#             'access_key': self.api_key,
#             'arr_iata': airport_iata,
#             'limit': limit
#         }
        
#         try:
#             response = requests.get(self.base_url, params=params)
#             print(f"API Response Status: {response.status_code}")
            
#             if response.status_code == 200:
#                 data = response.json()
#                 print(f"Tìm thấy {len(data.get('data', []))} chuyến bay tới {airport_iata}")
#                 return data
#             else:
#                 print(f"Lỗi API: {response.status_code}")
#                 print(f"Response: {response.text}")
#                 return {"error": response.text, "data": []}
                
#         except Exception as e:
#             print(f"Lỗi khi gọi API: {e}")
#             return {"error": str(e), "data": []}

#     def get_flights_from_airport(self, airport_iata: str, limit: int = 50) -> Dict:
#         """Lấy dữ liệu chuyến bay từ một sân bay cụ thể"""
#         print(f"Đang lấy dữ liệu chuyến bay từ {airport_iata} - {self.vietnam_airports[airport_iata]['city']}")
        
#         params = {
#             'access_key': self.api_key,
#             'dep_iata': airport_iata,
#             'limit': limit
#         }
        
#         try:
#             response = requests.get(self.base_url, params=params)
#             print(f"API Response Status: {response.status_code}")
            
#             if response.status_code == 200:
#                 data = response.json()
#                 print(f"Tìm thấy {len(data.get('data', []))} chuyến bay từ {airport_iata}")
#                 return data
#             else:
#                 print(f"Lỗi API: {response.status_code}")
#                 print(f"Response: {response.text}")
#                 return {"error": response.text, "data": []}
                
#         except Exception as e:
#             print(f"Lỗi khi gọi API: {e}")
#             return {"error": str(e), "data": []}

#     def get_domestic_flights(self, limit: int = 100) -> Dict:
#         """Lấy dữ liệu chuyến bay nội địa tới các thành phố du lịch"""
#         print("=== CRAWL CHUYẾN BAY NỘI ĐỊA ===")
        
#         all_flights = []
        
#         # Lấy chuyến bay tới mỗi sân bay du lịch
#         for airport_code in self.vietnam_airports.keys():
#             flights_data = self.get_flights_to_airport(airport_code, limit // len(self.vietnam_airports))
            
#             if 'data' in flights_data:
#                 # Lọc chuyến bay nội địa (từ và tới đều ở Việt Nam)
#                 domestic_flights = []
#                 for flight in flights_data['data']:
#                     dep_airport = flight.get('departure', {}).get('iata', '')
#                     arr_airport = flight.get('arrival', {}).get('iata', '')
                    
#                     # Kiểm tra cả hai sân bay đều ở Việt Nam
#                     if (dep_airport in self.vietnam_airports.keys() and 
#                         arr_airport in self.vietnam_airports.keys()):
                        
#                         # Thêm thông tin thành phố du lịch
#                         flight['destination_info'] = self.vietnam_airports[arr_airport]
#                         flight['origin_info'] = self.vietnam_airports[dep_airport]
#                         domestic_flights.append(flight)
                
#                 all_flights.extend(domestic_flights)
            
#             # Tạm dừng để tránh vượt rate limit
#             time.sleep(1)
        
#         return {
#             "total_flights": len(all_flights),
#             "data": all_flights,
#             "crawl_time": datetime.datetime.now().isoformat(),
#             "airports_covered": list(self.vietnam_airports.keys())
#         }

#     def get_international_flights_to_vietnam(self, limit: int = 100) -> Dict:
#         """Lấy dữ liệu chuyến bay quốc tế tới Việt Nam"""
#         print("=== CRAWL CHUYẾN BAY QUỐC TẾ TỚI VIỆT NAM ===")
        
#         all_flights = []
        
#         # Tập trung vào 3 sân bay quốc tế chính
#         main_airports = ["SGN", "HAN", "DAD"]
        
#         for airport_code in main_airports:
#             flights_data = self.get_flights_to_airport(airport_code, limit // len(main_airports))
            
#             if 'data' in flights_data:
#                 # Lọc chuyến bay quốc tế (từ nước ngoài tới Việt Nam)
#                 international_flights = []
#                 for flight in flights_data['data']:
#                     dep_airport = flight.get('departure', {}).get('iata', '')
#                     arr_airport = flight.get('arrival', {}).get('iata', '')
                    
#                     # Kiểm tra chuyến bay từ nước ngoài tới Việt Nam
#                     if (dep_airport not in self.vietnam_airports.keys() and 
#                         arr_airport in self.vietnam_airports.keys()):
                        
#                         # Thêm thông tin thành phố du lịch
#                         flight['destination_info'] = self.vietnam_airports[arr_airport]
#                         international_flights.append(flight)
                
#                 all_flights.extend(international_flights)
            
#             # Tạm dừng để tránh vượt rate limit
#             time.sleep(1)
        
#         return {
#             "total_flights": len(all_flights),
#             "data": all_flights,
#             "crawl_time": datetime.datetime.now().isoformat(),
#             "airports_covered": main_airports
#         }

#     def process_flight_data(self, flight: Dict) -> Dict:
#         """Xử lý và chuẩn hóa dữ liệu chuyến bay"""
#         processed = {
#             "flight_info": {
#                 "number": flight.get('flight', {}).get('number', ''),
#                 "iata": flight.get('flight', {}).get('iata', ''),
#                 "date": flight.get('flight_date', ''),
#                 "status": flight.get('flight_status', '')
#             },
#             "airline": {
#                 "name": flight.get('airline', {}).get('name', ''),
#                 "iata": flight.get('airline', {}).get('iata', ''),
#                 "icao": flight.get('airline', {}).get('icao', '')
#             },
#             "departure": {
#                 "airport": flight.get('departure', {}).get('airport', ''),
#                 "iata": flight.get('departure', {}).get('iata', ''),
#                 "city": flight.get('origin_info', {}).get('city', ''),
#                 "terminal": flight.get('departure', {}).get('terminal', ''),
#                 "gate": flight.get('departure', {}).get('gate', ''),
#                 "scheduled": flight.get('departure', {}).get('scheduled', ''),
#                 "estimated": flight.get('departure', {}).get('estimated', ''),
#                 "actual": flight.get('departure', {}).get('actual', ''),
#                 "delay": flight.get('departure', {}).get('delay', 0)
#             },
#             "arrival": {
#                 "airport": flight.get('arrival', {}).get('airport', ''),
#                 "iata": flight.get('arrival', {}).get('iata', ''),
#                 "city": flight.get('destination_info', {}).get('city', ''),
#                 "region": flight.get('destination_info', {}).get('region', ''),
#                 "terminal": flight.get('arrival', {}).get('terminal', ''),
#                 "gate": flight.get('arrival', {}).get('gate', ''),
#                 "scheduled": flight.get('arrival', {}).get('scheduled', ''),
#                 "estimated": flight.get('arrival', {}).get('estimated', ''),
#                 "actual": flight.get('arrival', {}).get('actual', ''),
#                 "delay": flight.get('arrival', {}).get('delay', 0)
#             },
#             "aircraft": flight.get('aircraft', {}),
#             "live": flight.get('live', {})
#         }
        
#         return processed

    

#     def crawl_all_vietnam_flights(self):
#         """Crawl tất cả dữ liệu chuyến bay liên quan đến du lịch Việt Nam"""
#         print("="*60)
#         print("BẮT ĐẦU CRAWL DỮ LIỆU CHUYẾN BAY DU LỊCH VIỆT NAM")
#         print("="*60)
        
#         # Test API trước khi crawl
#         if not self.test_api_connection():
#             print("⚠️ API không khả dụng. Sử dụng dữ liệu mẫu để demo...")
#             sample_data = self.get_sample_flight_data()
            
#             # Xử lý dữ liệu mẫu
#             processed_domestic = []
#             for flight in sample_data['domestic_flights']['data']:
#                 processed_domestic.append(self.process_flight_data(flight))
            
#             processed_international = []
#             for flight in sample_data['international_flights']['data']:
#                 processed_international.append(self.process_flight_data(flight))
            
#             summary = {
#                 "crawl_summary": {
#                     "crawl_time": datetime.datetime.now().isoformat(),
#                     "total_domestic_flights": len(processed_domestic),
#                     "total_international_flights": len(processed_international),
#                     "total_flights": len(processed_domestic) + len(processed_international),
#                     "airports_info": self.vietnam_airports,
#                     "data_source": "sample_data",
#                     "note": "Dữ liệu mẫu - API không khả dụng"
#                 },
#                 "domestic_flights": {
#                     "count": len(processed_domestic),
#                     "data": processed_domestic
#                 },
#                 "international_flights": {
#                     "count": len(processed_international),
#                     "data": processed_international
#                 }
#             }
            
#             # Lưu kết quả
#             self.save_to_json(summary, f'vietnam_flights_sample_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
#             # Lưu vào Elasticsearch
#             if self.es:
#                 print("\n📊 ĐANG LƯU DỮ LIỆU MẪU VÀO ELASTICSEARCH...")
#                 self.create_elasticsearch_index()
#                 self.save_flights_to_elasticsearch(summary)
            
#             # In báo cáo
#             self.print_summary(summary)
            
#             return summary
        
#         # 1. Crawl chuyến bay nội địa
#         domestic_flights = self.get_domestic_flights(limit=50)
        
#         # 2. Crawl chuyến bay quốc tế tới Việt Nam
#         international_flights = self.get_international_flights_to_vietnam(limit=50)
        
#         # 3. Xử lý dữ liệu
#         processed_domestic = []
#         for flight in domestic_flights['data']:
#             processed_domestic.append(self.process_flight_data(flight))
        
#         processed_international = []
#         for flight in international_flights['data']:
#             processed_international.append(self.process_flight_data(flight))
        
#         # 4. Tạo báo cáo tổng hợp
#         summary = {
#             "crawl_summary": {
#                 "crawl_time": datetime.datetime.now().isoformat(),
#                 "total_domestic_flights": len(processed_domestic),
#                 "total_international_flights": len(processed_international),
#                 "total_flights": len(processed_domestic) + len(processed_international),
#                 "airports_info": self.vietnam_airports
#             },
#             "domestic_flights": {
#                 "count": len(processed_domestic),
#                 "data": processed_domestic
#             },
#             "international_flights": {
#                 "count": len(processed_international),
#                 "data": processed_international
#             }
#         }
        
#         # 5. Lưu kết quả
#         self.save_to_json(summary, f'vietnam_flights_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
#         # 6. Lưu vào Elasticsearch
#         if self.es:
#             print("\n📊 ĐANG LƯU DỮ LIỆU VÀO ELASTICSEARCH...")
#             self.create_elasticsearch_index()
#             self.save_flights_to_elasticsearch(summary)
        
#         # 7. In báo cáo
#         self.print_summary(summary)
        
#         return summary

#     # def print_summary(self, data: Dict):
#     #     """In báo cáo tóm tắt"""
#     #     print("\n" + "="*60)
#     #     print("BÁO CÁO TÓM TẮT")
#     #     print("="*60)
        
#     #     summary = data['crawl_summary']
#     #     print(f"Thời gian crawl: {summary['crawl_time']}")
#     #     print(f"Tổng số chuyến bay: {summary['total_flights']}")
#     #     print(f"- Chuyến bay nội địa: {summary['total_domestic_flights']}")
#     #     print(f"- Chuyến bay quốc tế: {summary['total_international_flights']}")
        
#     #     print(f"\nCác sân bay du lịch được theo dõi:")
#     #     for code, info in summary['airports_info'].items():
#     #         print(f"- {code}: {info['name']} ({info['city']}) - {info['region']}")
        
#     #     # Thống kê chuyến bay nội địa theo thành phố
#     #     print(f"\nChuyến bay nội địa theo thành phố đến:")
#     #     city_stats = {}
#     #     for flight in data['domestic_flights']['data']:
#     #         city = flight['arrival']['city']
#     #         city_stats[city] = city_stats.get(city, 0) + 1
        
#     #     for city, count in sorted(city_stats.items(), key=lambda x: x[1], reverse=True):
#     #         print(f"- {city}: {count} chuyến bay")
        
#     #     print("\n" + "="*60)

#     def create_elasticsearch_index(self, index_name: str = "vietnam_flights"):
#         """Tạo index trong Elasticsearch với mapping phù hợp"""
#         if not self.es:
#             print("❌ Elasticsearch không khả dụng")
#             return False
        
#         # Mapping cho dữ liệu chuyến bay
#         mapping = {
#             "mappings": {
#                 "properties": {
#                     "flight_info": {
#                         "properties": {
#                             "number": {"type": "keyword"},
#                             "iata": {"type": "keyword"},
#                             "date": {"type": "date"},
#                             "status": {"type": "keyword"}
#                         }
#                     },
#                     "airline": {
#                         "properties": {
#                             "name": {"type": "text", "analyzer": "standard"},
#                             "iata": {"type": "keyword"},
#                             "icao": {"type": "keyword"}
#                         }
#                     },
#                     "departure": {
#                         "properties": {
#                             "airport": {"type": "text", "analyzer": "standard"},
#                             "iata": {"type": "keyword"},
#                             "city": {"type": "text", "analyzer": "standard"},
#                             "terminal": {"type": "keyword"},
#                             "gate": {"type": "keyword"},
#                             "scheduled": {"type": "date"},
#                             "estimated": {"type": "date"},
#                             "actual": {"type": "date"},
#                             "delay": {"type": "integer"}
#                         }
#                     },
#                     "arrival": {
#                         "properties": {
#                             "airport": {"type": "text", "analyzer": "standard"},
#                             "iata": {"type": "keyword"},
#                             "city": {"type": "text", "analyzer": "standard"},
#                             "region": {"type": "keyword"},
#                             "terminal": {"type": "keyword"},
#                             "gate": {"type": "keyword"},
#                             "scheduled": {"type": "date"},
#                             "estimated": {"type": "date"},
#                             "actual": {"type": "date"},
#                             "delay": {"type": "integer"}
#                         }
#                     },
#                     "aircraft": {
#                         "properties": {
#                             "registration": {"type": "keyword"},
#                             "iata": {"type": "keyword"},
#                             "icao": {"type": "keyword"}
#                         }
#                     },
#                     "search_text": {
#                         "type": "text", 
#                         "analyzer": "standard"
#                     },
#                     "flight_type": {"type": "keyword"},
#                     "created_at": {"type": "date"}
#                 }
#             }
#         }
        
#         try:
#             # Xóa index cũ nếu tồn tại
#             if self.es.indices.exists(index=index_name):
#                 self.es.indices.delete(index=index_name)
#                 print(f"🗑️ Đã xóa index cũ: {index_name}")
            
#             # Tạo index mới
#             self.es.indices.create(index=index_name, body=mapping)
#             print(f"✅ Đã tạo index Elasticsearch: {index_name}")
#             return True
            
#         except Exception as e:
#             print(f"❌ Lỗi tạo index Elasticsearch: {e}")
#             return False

#     def prepare_flight_for_elasticsearch(self, flight: Dict, flight_type: str = "domestic") -> Dict:
#         """Chuẩn bị dữ liệu chuyến bay để lưu vào Elasticsearch"""
#         # Tạo text tìm kiếm tổng hợp
#         search_components = [
#             flight.get('flight_info', {}).get('number', ''),
#             flight.get('flight_info', {}).get('iata', ''),
#             flight.get('airline', {}).get('name', ''),
#             flight.get('departure', {}).get('airport', ''),
#             flight.get('departure', {}).get('city', ''),
#             flight.get('arrival', {}).get('airport', ''),
#             flight.get('arrival', {}).get('city', ''),
#             flight.get('arrival', {}).get('region', ''),
#         ]
        
#         search_text = ' '.join(filter(None, search_components))
        
#         # Thêm các trường bổ sung
#         flight['search_text'] = search_text
#         flight['flight_type'] = flight_type
#         flight['created_at'] = datetime.datetime.now().isoformat()
        
#         return flight

#     def save_flights_to_elasticsearch(self, flights_data: Dict, index_name: str = "vietnam_flights") -> bool:
#         """Lưu danh sách chuyến bay vào Elasticsearch"""
#         if not self.es:
#             print("❌ Elasticsearch không khả dụng")
#             return False
        
#         try:
#             # Chuẩn bị dữ liệu để bulk insert
#             actions = []
            
#             # Chuyến bay nội địa
#             for flight in flights_data['domestic_flights']['data']:
#                 prepared_flight = self.prepare_flight_for_elasticsearch(flight, "domestic")
#                 action = {
#                     "_index": index_name,
#                     "_source": prepared_flight
#                 }
#                 actions.append(action)
            
#             # Chuyến bay quốc tế
#             for flight in flights_data['international_flights']['data']:
#                 prepared_flight = self.prepare_flight_for_elasticsearch(flight, "international")
#                 action = {
#                     "_index": index_name,
#                     "_source": prepared_flight
#                 }
#                 actions.append(action)
            
#             # Bulk insert
#             if actions:
#                 success, failed = bulk(self.es, actions)
#                 print(f"✅ Đã lưu {success} chuyến bay vào Elasticsearch")
#                 if failed:
#                     print(f"❌ {len(failed)} chuyến bay lưu thất bại")
#                 return True
#             else:
#                 print("⚠️ Không có dữ liệu để lưu vào Elasticsearch")
#                 return False
                
#         except Exception as e:
#             print(f"❌ Lỗi lưu dữ liệu vào Elasticsearch: {e}")
#             return False

    
# def main():
#     """Hàm chính để chạy crawler"""
#     # API key của bạn
#     API_KEY = "9df4acf29081bd44b7fcca42f2c77821"
    
#     print("🛫 VIETNAM FLIGHT CRAWLER 🛬")
#     print("="*60)
#     print("Crawl dữ liệu chuyến bay và lưu vào Elasticsearch...")
#     print("="*60)
    
#     # Tạo crawler instance
#     crawler = FlightCrawler(API_KEY)
    
#     # Chạy crawl
#     results = crawler.crawl_all_vietnam_flights()
    
#     print("\n✅ Crawl hoàn thành!")
#     if crawler.es:
#         print("📊 Dữ liệu đã được lưu vào Elasticsearch")
#     else:
#         print("⚠️ Elasticsearch không khả dụng - chỉ lưu file JSON")

# if __name__ == "__main__":
#     main()