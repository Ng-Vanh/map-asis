import requests
import time
import json

OTM_API_KEY = "5ae2e3f221c38a28845f05b6ebdfdf5e3c00c7b57dae9438a4a18665"

# Tọa độ khung bao quanh (Bounding Box) khu vực nội thành Hà Nội
# Bạn có thể lấy tọa độ này từ http://bboxfinder.com/
MIN_LON, MIN_LAT = 105.7900, 20.9900 # Góc trái dưới
MAX_LON, MAX_LAT = 105.8600, 21.0500 # Góc phải trên

def get_places_in_bbox(min_lon, min_lat, max_lon, max_lat):
    """Lấy danh sách địa điểm trong một hình chữ nhật nhỏ"""
    url = "https://api.opentripmap.com/0.1/en/places/bbox"
    params = {
        "apikey": OTM_API_KEY,
        "lon_min": min_lon,
        "lat_min": min_lat,
        "lon_max": max_lon,
        "lat_max": max_lat,
        "kinds": "interesting_places",
        "format": "json", # Bắt buộc format json để trả về List
        "limit": 500
    }
    try:
        res = requests.get(url, params=params)
        
        # In ra URL để debug nếu cần
        # print(res.url) 

        if res.status_code == 200:
            data = res.json()
            
            # --- SỬA LỖI TẠI ĐÂY ---
            # Kiểm tra xem dữ liệu trả về có phải là List không
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Nếu trả về Dict, có thể là lỗi hoặc GeoJSON
                if "error" in data:
                    print(f"\n⚠️ Lỗi từ API: {data['error']}")
                elif "features" in data:
                    # Trường hợp trả về GeoJSON
                    print("\n⚠️ API trả về GeoJSON thay vì JSON list.")
                    return [] # Hoặc xử lý GeoJSON nếu bạn muốn
                else:
                    print(f"\n⚠️ Dữ liệu lạ: {data}")
                return []
        else:
            print(f"\n❌ Lỗi HTTP {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"\n❌ Lỗi kết nối: {e}")
        
    return []
def get_place_details(xid):
    """Lấy chi tiết (mô tả, ảnh) của 1 địa điểm"""
    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
    params = {"apikey": OTM_API_KEY}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def scan_hanoi_grid(steps=5):
    """
    Chia Hà Nội thành lưới (steps x steps) ô nhỏ để quét
    steps=5 nghĩa là chia thành 25 ô nhỏ.
    """
    lat_step = (MAX_LAT - MIN_LAT) / steps
    lon_step = (MAX_LON - MIN_LON) / steps
    
    all_places = {} # Dùng dict để tự loại bỏ trùng lặp theo xid

    print(f"🚀 Bắt đầu quét Hà Nội với lưới {steps}x{steps}...")

    for i in range(steps):
        for j in range(steps):
            # Tính tọa độ ô nhỏ hiện tại
            current_min_lat = MIN_LAT + (i * lat_step)
            current_max_lat = MIN_LAT + ((i + 1) * lat_step)
            current_min_lon = MIN_LON + (j * lon_step)
            current_max_lon = MIN_LON + ((j + 1) * lon_step)
            
            print(f"scanning grid [{i},{j}]...", end="\r")
            
            # 1. Lấy danh sách địa điểm trong ô này
            places = get_places_in_bbox(current_min_lon, current_min_lat, current_max_lon, current_max_lat)
            
            for p in places:
                all_places[p['xid']] = p # Lưu vào dict
            
            # Ngủ 0.5s để không bị khóa API
            time.sleep(0.5)

    print(f"\n✅ Đã tìm thấy tổng cộng {len(all_places)} địa điểm duy nhất!")
    return list(all_places.values())

# --- CHẠY CHƯƠNG TRÌNH ---
# 1. Quét lấy danh sách
list_places = scan_hanoi_grid(steps=4) 

# 2. Lấy chi tiết từng cái (Demo lấy 5 cái đầu tiên thôi nhé kẻo lâu)
print("\n--- Lấy thông tin chi tiết ---")
for place in list_places[:5]: 
    xid = place['xid']
    name = place['name']
    
    details = get_place_details(xid)
    
    if details:
        # Trích xuất mô tả (nếu có)
        desc = details.get('wikipedia_extracts', {}).get('text', 'Không có mô tả')
        print(f"📍 {name}")
        print(f"   Mô tả: {desc[:100]}...") # In 100 ký tự đầu
        print("-" * 30)
        
        # Ở bước này, bạn sẽ gọi lệnh UPDATE vào Neo4j
        time.sleep(0.5)