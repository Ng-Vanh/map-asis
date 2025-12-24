# 📚 API DOCUMENTATION - Map Assistant

## Base URL
```
http://localhost:8864/api/v1
```

## Tổng quan
Hệ thống Map Assistant cung cấp 8 API endpoints chính để hỗ trợ tìm kiếm, gợi ý và lập kế hoạch tham quan địa điểm tại Hà Nội.

**Lưu ý:** Tất cả endpoints đều có prefix `/api/v1`

---

## 🔍 API Endpoints

### 🤖 0. Agent Chat (NEW - RECOMMENDED!)
**Chat tự nhiên - Agent tự động routing**

Đây là cách **dễ nhất** để sử dụng Map Assistant! User chỉ cần gửi message tự nhiên, agent tự động hiểu ý định và gọi đúng service.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "message": "Tìm quán cafe gần Hồ Gươm",
  "session_id": "optional-session-id",
  "chat_history": []
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tìm quán cafe gần Hồ Gươm",
  "intent": "search_places",
  "confidence": 0.95,
  "result": {
    "total": 15,
    "places": [...],
    "summary": "AI summary..."
  }
}
```

**Examples Messages:**
- "Tìm quán cafe gần đây"
- "So sánh Hồ Gươm và Hồ Tây"
- "Lập lịch trình 8 giờ cho gia đình"
- "Gợi ý địa điểm lãng mạn"
- "Cho tôi biết về Lăng Bác"

**📖 [Xem chi tiết AGENT_CHAT.md](AGENT_CHAT.md)**

---

### 1. Health Check
Kiểm tra trạng thái server

**Endpoint:** `GET /health`

**Response:**
```
OK
```

---

### 2. Lấy thông tin địa điểm
Lấy thông tin chi tiết về một địa điểm cụ thể

**Endpoint:** `POST /place_info`

**Request Body:**
```json
{
  "name": "Lăng Bác"
}
```

**Response:**
```json
{
  "response": "Lăng Chủ tịch Hồ Chí Minh là một trong những công trình kiến trúc quan trọng nhất của Việt Nam..."
}
```

---

### 3. Tìm kiếm địa điểm theo category
Tìm địa điểm theo loại hình (restaurant, cafe, hotel...) xung quanh tọa độ

**Endpoint:** `POST /search_places`

**Request Body:**
```json
{
  "lat": 21.0285,
  "lon": 105.8542,
  "categories": ["restaurant", "cafe"],
  "radius_meters": 2000,
  "limit": 20
}
```

**Parameters:**
- `lat` (float, required): Vĩ độ
- `lon` (float, required): Kinh độ
- `categories` (array, required): Danh sách category cần tìm
- `radius_meters` (int, optional): Bán kính tìm kiếm (mặc định: 2000m)
- `limit` (int, optional): Số kết quả tối đa (mặc định: 20)

**Response:**
```json
{
  "total": 15,
  "places": [
    {
      "place_id": "HN-0001",
      "name": "Phở Thìn Bờ Hồ",
      "address": "13 Lò Đúc, Hoàn Kiếm",
      "categories": ["restaurant"],
      "distance_meters": 450
    }
  ],
  "summary": "Tóm tắt AI về các địa điểm tìm thấy..."
}
```

---

### 4. Tìm địa điểm gần landmark
Tìm các địa điểm xung quanh một địa danh nổi tiếng

**Endpoint:** `POST /nearby_landmark`

**Request Body:**
```json
{
  "landmark_name": "Hồ Gươm",
  "categories": ["restaurant", "cafe"],
  "radius_meters": 1000,
  "limit": 20
}
```

**Parameters:**
- `landmark_name` (string, required): Tên địa danh
- `categories` (array, required): Danh sách category
- `radius_meters` (int, optional): Bán kính (mặc định: 1000m)
- `limit` (int, optional): Số kết quả (mặc định: 20)

**Response:**
```json
{
  "landmark": {
    "name": "Hồ Hoàn Kiếm",
    "address": "Hoàn Kiếm, Hà Nội"
  },
  "total": 12,
  "nearby_places": [...],
  "summary": "Mô tả AI về các địa điểm xung quanh..."
}
```

---

### 5. Tìm kiếm ngữ nghĩa (Semantic Search)
Tìm địa điểm bằng câu mô tả tự nhiên, kết hợp Neo4j + Qdrant

**Endpoint:** `POST /semantic_search`

**Request Body:**
```json
{
  "query": "quán cafe lãng mạn view đẹp phù hợp hẹn hò",
  "lat": 21.0285,
  "lon": 105.8542,
  "radius_meters": 5000,
  "top_k": 10
}
```

**Parameters:**
- `query` (string, required): Câu truy vấn tự nhiên
- `lat` (float, optional): Vĩ độ để filter theo vị trí
- `lon` (float, optional): Kinh độ
- `radius_meters` (int, optional): Bán kính filter (mặc định: 5000m)
- `top_k` (int, optional): Số kết quả (mặc định: 10)

**Response:**
```json
{
  "total": 8,
  "query": "quán cafe lãng mạn view đẹp",
  "places": [
    {
      "place_id": "HN-0025",
      "name": "The Hanoi Social Club",
      "score": 0.89,
      "summary": "Quán cafe có không gian xanh mát..."
    }
  ],
  "recommendation": "Giới thiệu AI về các địa điểm phù hợp nhất..."
}
```

---

### 6. So sánh địa điểm
So sánh chi tiết giữa 2-3 địa điểm về đặc điểm, ưu/nhược điểm

**Endpoint:** `POST /compare_places`

**Request Body:**
```json
{
  "place_names": ["Hồ Gươm", "Hồ Tây", "Văn Miếu"]
}
```

**Parameters:**
- `place_names` (array, required): Danh sách tên địa điểm (2-5 địa điểm)

**Response:**
```json
{
  "places": ["Hồ Gươm", "Hồ Tây", "Văn Miếu"],
  "comparison": "So sánh chi tiết từ AI về điểm mạnh/yếu, phù hợp cho đối tượng nào...",
  "details": [...]
}
```

---

### 7. Lập lịch trình tham quan (Itinerary Planning)
Tạo lịch trình tham quan thông minh dựa trên thời gian và sở thích

**Endpoint:** `POST /plan_itinerary`

**Request Body:**
```json
{
  "location": "Old Quarter Hanoi",
  "duration_hours": 8,
  "preferences": {
    "lat": 21.0285,
    "lon": 105.8542,
    "companions": "family",
    "interests": ["culture", "food", "shopping"]
  },
  "start_time": "09:00"
}
```

**Parameters:**
- `location` (string, required): Khu vực tham quan
- `duration_hours` (int, required): Số giờ tham quan
- `preferences` (object, optional): Sở thích và yêu cầu
  - `lat`, `lon`: Tọa độ xuất phát
  - `companions`: Đối tượng (solo/couple/family/group)
  - `interests`: Sở thích (array)
- `start_time` (string, optional): Giờ bắt đầu (mặc định: "09:00")

**Response:**
```json
{
  "location": "Old Quarter Hanoi",
  "duration_hours": 8,
  "start_time": "09:00",
  "preferences": {...},
  "available_places": {...},
  "itinerary": "📅 LỊCH TRÌNH CHI TIẾT:\n09:00 - Điểm A\n10:30 - Điểm B..."
}
```

---

### 8. Gợi ý địa điểm cá nhân hóa
Gợi ý địa điểm phù hợp dựa trên preferences của user

**Endpoint:** `POST /recommend_places`

**Request Body:**
```json
{
  "user_preferences": {
    "budget": 2,
    "interests": ["food", "culture"],
    "companions": "family",
    "avoid": ["nightlife"]
  },
  "current_location": {
    "lat": 21.0285,
    "lon": 105.8542
  },
  "limit": 10
}
```

**Parameters:**
- `user_preferences` (object, required): Sở thích người dùng
  - `budget` (int): Mức giá 1-4 ($ đến $$$$)
  - `interests` (array): Danh sách sở thích
  - `companions` (string): Đối tượng đi cùng
  - `avoid` (array): Loại địa điểm muốn tránh
- `current_location` (object, optional): Vị trí hiện tại
- `limit` (int, optional): Số gợi ý (mặc định: 10)

**Response:**
```json
{
  "user_preferences": {...},
  "total_recommendations": 8,
  "places": [...],
  "recommendation": "Dựa trên sở thích của bạn, đây là các địa điểm phù hợp nhất..."
}
```

---

## 📝 Ví dụ sử dụng với cURL

### Test search_places:
```bash
curl -X POST http://localhost:8864/api/v1/search_places \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 21.0285,
    "lon": 105.8542,
    "categories": ["restaurant", "cafe"],
    "radius_meters": 2000,
    "limit": 10
  }'
```

### Test semantic_search:
```bash
curl -X POST http://localhost:8864/api/v1/semantic_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quán cafe yên tĩnh view đẹp",
    "top_k": 5
  }'
```

### Test plan_itinerary:
```bash
curl -X POST http://localhost:8864/api/v1/plan_itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Old Quarter",
    "duration_hours": 8,
    "preferences": {
      "lat": 21.0285,
      "lon": 105.8542,
      "companions": "family",
      "interests": ["culture", "food"]
    },
    "start_time": "09:00"
  }'
```

---

## 🚀 Test với Python

Sử dụng file `test_services.py`:

```bash
python test_services.py
```

Hoặc test từng endpoint riêng lẻ:

```python
import requests

# Test search places
response = requests.post(
    "http://localhost:8864/api/v1/search_places",
    json={
        "lat": 21.0285,
        "lon": 105.8542,
        "categories": ["restaurant"],
        "radius_meters": 2000,
        "limit": 10
    }
)
print(response.json())
```

---

## 💡 Ghi chú

1. **Neo4j** cung cấp spatial queries và graph relationships
2. **Qdrant** cung cấp semantic search với vector embeddings
3. **AI Service** (GPT/Claude) tổng hợp và generate response tự nhiên

Tất cả services đều kết hợp 3 layers này để mang lại kết quả tối ưu!

---

## 🔧 Cấu trúc dữ liệu Categories

Các category phổ biến:
- **Ăn uống:** restaurant, cafe, bar, street_food
- **Tham quan:** museum, gallery, historical, temple, pagoda, scenic
- **Mua sắm:** shopping, market, mall
- **Lưu trú:** hotel, accommodation, hostel
- **Giải trí:** entertainment, nightlife, park

---

## ⚠️ Error Handling

Tất cả APIs trả về HTTP status codes:
- `200`: Success
- `400`: Bad Request (thiếu parameters)
- `404`: Not Found (không tìm thấy dữ liệu)
- `500`: Internal Server Error

Error response format:
```json
{
  "error": "Mô tả lỗi chi tiết"
}
```
