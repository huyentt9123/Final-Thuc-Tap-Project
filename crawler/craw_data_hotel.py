from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re
import random

CHROMEDRIVER_PATH = r"E:\chromedriver-win64\chromedriver-win64\chromedriver.exe"

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

url = "https://khachsan.chudu24.com/t.halong.html"
driver.get(url)

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article.post-hotel-list-item.hotel-item"))
    )
except:
    print("Không tìm thấy phần tử khách sạn trong 20 giây")

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("Bản đồ", "").strip()
    return text

def estimate_price(stars, rating, utilities):
    star_num = 0
    if isinstance(stars, str):
        match = re.search(r"(\d)", stars)
        if match:
            star_num = int(match.group(1))

    try:
        rating_num = float(rating)
    except:
        rating_num = 0.0

    base_price = 1000000

    if star_num == 5:
        if rating_num >= 8.5:
            base_price = 3000000
        else:
            base_price = 2500000
    elif star_num == 4:
        if rating_num >= 8.0:
            base_price = 1800000
        else:
            base_price = 1500000
    elif star_num == 3:
        base_price = 1200000
    else:
        base_price = 1000000

    if any("Thương hiệu quốc tế" in u for u in utilities):
        base_price += 300000
    elif any("Hồ bơi" in u for u in utilities):
        base_price += 200000
    elif any("Ưu đãi giá tốt" in u for u in utilities):
        base_price += 100000

    fluctuation = base_price * 0.05
    price_final = base_price + random.uniform(-fluctuation, fluctuation)

    return int(price_final)

hotels = []

for article in soup.select("article.post-hotel-list-item.hotel-item"):
    name_tag = article.select_one("h2 a")
    name = name_tag.text.strip() if name_tag else "Không có tên"

    link = "https:" + name_tag.get("href") if name_tag and name_tag.get("href") else "Không có link"

    img_tag = article.select_one("div.post-thumbnail img")
    image_url = img_tag['src'] if img_tag and img_tag.get('src') else "Không có ảnh"

    location_tag = article.select_one(".post-location span")
    address_raw = location_tag.text if location_tag else "Không có địa chỉ"
    address = clean_text(address_raw)

    # Chuyển stars về int
    star_img_tag = article.select_one(".post-rating img")
    stars_int = 0
    if star_img_tag:
        src = star_img_tag.get("src", "")
        match_star = re.search(r"star-yellow-(\d)\.png", src)
        if match_star:
            stars_int = int(match_star.group(1))

    # Chuyển rating về float
    rating_tag = article.select_one(".snippetReviewRatingClass")
    try:
        rating_float = float(rating_tag.text.strip()) if rating_tag else 0.0
    except:
        rating_float = 0.0

    # Chuyển review_count về int
    review_count_tag = article.select_one(".post-rating-reviews .generateWrapLink")
    review_count_int = 0
    if review_count_tag:
        review_text = clean_text(review_count_tag.text)
        # Lấy số nguyên từ chuỗi, ví dụ: "123 đánh giá" -> 123
        match_review = re.search(r'(\d+)', review_text.replace('.', '').replace(',', ''))
        if match_review:
            review_count_int = int(match_review.group(1))

    # Lấy giá và chuyển về int
    price_point_tag = article.select_one(".hotel-price")
    if not price_point_tag:
        price_point_tag = article.select_one(".price-point")

    price_point_raw = price_point_tag.text if price_point_tag else ""
    price_point_clean = clean_text(price_point_raw)
    price_point_int = 0
    if price_point_clean:
        # Loại bỏ ký tự không phải số
        number_str = re.sub(r'[^\d]', '', price_point_clean)
        if number_str.isdigit():
            price_point_int = int(number_str)

    # Tiện ích
    raw_utilities = [label.text.strip() for label in article.select(".post-features-list .label")]

    utilities = []
    for u in raw_utilities:
        if not re.search(r'giá từ|từ', u, flags=re.IGNORECASE):
            utilities.append(u)

    # Nếu không có giá thì ước lượng giá
    if price_point_int == 0:
        price_point_int = estimate_price(f"{stars_int} sao", rating_float, utilities)

    hotels.append({
        "name": name,
        "link": link,
        "image": image_url,
        "address": address,
        "stars": stars_int,
        "rating": rating_float,
        "review_count": review_count_int,
        "price_point": price_point_int,
        "utilities": utilities
    })

for hotel in hotels:
    print(json.dumps(hotel, ensure_ascii=False, indent=2))

with open("hotel_HL5.json", "w", encoding="utf-8") as f:
    json.dump(hotels, f, ensure_ascii=False, indent=2)

driver.quit()
