from typing import Dict, Any


def suggest_outfit(temp_c: float,
                   feels_like_c: float | None = None,
                   humidity: float = 60,
                   wind_speed: float = 3,
                   rain_3h: float = 0,
                   description: str = "",
                   uv_index: float = 0,
                   time_of_day: str = "day") -> Dict[str, Any]:
    """
    Gợi ý trang phục dựa trên điều kiện thời tiết
    
    Args:
        temp_c: Nhiệt độ thực (°C)
        feels_like_c: Nhiệt độ cảm giác (°C)
        humidity: Độ ẩm (%)
        wind_speed: Tốc độ gió (m/s)
        rain_3h: Lượng mưa 3h (mm)
        description: Mô tả thời tiết
        uv_index: Chỉ số UV
        time_of_day: Thời điểm trong ngày ("morning", "day", "evening", "night")
    """
    t = feels_like_c if feels_like_c is not None else temp_c
    desc = (description or "").lower()
    
    # Phân tích điều kiện thời tiết
    rainy = (rain_3h or 0) > 0 or any(w in desc for w in ["mưa", "rain", "drizzle", "shower"])
    sunny = any(w in desc for w in ["nắng", "clear", "sunny"])
    cloudy = any(w in desc for w in ["mây", "cloud", "overcast"])
    windy = (wind_speed or 0) >= 8
    very_humid = (humidity or 0) > 80
    high_uv = (uv_index or 0) > 6

    items: list[str] = []
    outer: str | None = None
    shoes: str = "sneaker"
    accessories: list[str] = []
    notes: list[str] = []
    colors: list[str] = []

    # Xử lý điều kiện đặc biệt trước
    if rainy:
        outer = "áo mưa/áo khoác chống nước"
        shoes = "giày chống trượt/boots"
        accessories += ["ô", "túi chống nước"]
        notes += ["mang theo đồ thay"]
        colors += ["tối màu (ít bẩn)"]
    
    if windy:
        outer = outer or "áo khoác chắn gió"
        notes += ["tránh váy/áo rộng"]
        accessories += ["dây buộc tóc"]

    # Gợi ý theo nhiệt độ
    if t is None:
        items = ["áo phông", "quần thoải mái"]
    elif t <= 10:  # Rất lạnh
        items = ["áo giữ nhiệt", "len dày/hoodie", "quần dài dày"]
        outer = outer or "áo khoác/áo phao dày"
        accessories += ["mũ len", "khăn", "găng tay"]
        shoes = "boots/giày kín"
        notes += ["mặc nhiều lớp"]
    elif t <= 15:  # Lạnh
        items = ["áo dài tay", "len nhẹ", "quần dài"]
        outer = outer or "áo khoác mỏng"
        accessories += ["khăn nhẹ"]
    elif t <= 20:  # Mát
        items = ["áo dài tay/len nhẹ", "quần dài"]
        outer = outer or "khoác nhẹ (có thể cởi)"
        if time_of_day in ["evening", "night"]:
            accessories += ["áo khoác nhẹ"]
    elif t <= 27:  # Ấm
        items = ["áo phông/sơ mi mỏng", "quần nhẹ/short"]
        if time_of_day in ["morning", "evening"]:
            outer = "khoác nhẹ (tùy chọn)"
    elif t <= 32:  # Nóng
        items = ["áo cotton/linen thoáng", "quần short/váy"]
        shoes = "sandal/giày thoáng"
        colors += ["sáng màu", "trắng/pastel"]
    else:  # Rất nóng (> 32°C)
        items = ["áo siêu thoáng", "quần short/váy ngắn"]
        shoes = "sandal/dép"
        notes += ["uống nước thường xuyên", "tránh ra ngoài 10h-15h"]
        colors += ["trắng/sáng màu"]

    # Xử lý độ ẩm cao
    if very_humid:
        notes += ["chọn vải cotton/linen", "tránh polyester/jean dày"]
        if t > 25:
            notes += ["mang theo khăn lau mồ hôi"]

    # Xử lý UV và ánh nắng
    if (sunny and t >= 24) or high_uv:
        accessories += ["mũ rộng vành", "kính râm", "kem chống nắng"]
        colors += ["sáng màu (phản xạ)"]
        if high_uv:
            notes += ["tránh áo tank top", "che chắn da"]

    # Gợi ý theo thời điểm trong ngày
    if time_of_day == "morning" and t < 25:
        notes += ["mang khoác nhẹ (có thể cởi sau)"]
    elif time_of_day == "evening" and t < 20:
        outer = outer or "áo khoác nhẹ"
    elif time_of_day == "night":
        if t < 18:
            outer = outer or "áo khoác"
        colors += ["tối màu (an toàn)"]

    # Loại bỏ trùng lặp
    accessories = list(dict.fromkeys(accessories))
    notes = list(dict.fromkeys(notes))
    colors = list(dict.fromkeys(colors))

    return {
        "outfit": items,
        "outerwear": outer,
        "footwear": shoes,
        "accessories": accessories,
        "colors": colors,
        "notes": ", ".join(notes) if notes else "",
        "weather_summary": f"{t:.1f}°C, độ ẩm {humidity}%, gió {wind_speed}m/s",
        "comfort_level": _get_comfort_level(t, humidity, wind_speed, rainy)
    }


def _get_comfort_level(temp: float, humidity: float, wind_speed: float, rainy: bool) -> str:
    """Đánh giá mức độ thoải mái của thời tiết"""
    if rainy:
        return "Không thoải mái (mưa)"
    
    # Heat index approximation
    if temp > 30 and humidity > 70:
        return "Rất khó chịu (nóng ẩm)"
    elif temp > 32:
        return "Khó chịu (quá nóng)"
    elif temp < 10:
        return "Khó chịu (quá lạnh)"
    elif wind_speed > 10:
        return "Hơi khó chịu (gió mạnh)"
    elif 18 <= temp <= 26 and humidity < 70:
        return "Rất thoải mái"
    elif 15 <= temp <= 30:
        return "Thoải mái"
    else:
        return "Bình thường"


def _get_time_of_day_from_hour(hour_str: str) -> str:
    """Xác định thời điểm trong ngày từ giờ"""
    try:
        hour = int(hour_str.split(':')[0])
        if 5 <= hour < 11:
            return "morning"
        elif 11 <= hour < 17:
            return "day"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    except:
        return "day"


def suggest_outfit_from_weather_doc(w: Dict[str, Any]) -> Dict[str, Any]:
    time_of_day = _get_time_of_day_from_hour(w.get("hour", "12:00"))
    
    return suggest_outfit(
        temp_c=w.get("temperature_c"),
        feels_like_c=w.get("feels_like_c"),
        humidity=w.get("humidity", 60),
        wind_speed=w.get("wind_speed", 3),
        rain_3h=w.get("rain_3h", 0),
        description=w.get("description", ""),
        uv_index=w.get("uv_index", 0),
        time_of_day=time_of_day
    )
