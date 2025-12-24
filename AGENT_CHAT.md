# 🤖 AGENT CHAT - Natural Language Interface

## Tổng quan

Agent Chat là tính năng **thông minh nhất** của Map Assistant - cho phép user chat tự nhiên mà **không cần biết API nào**.

### 🎯 Vấn đề
Trước đây user phải:
- Biết có endpoint nào
- Gọi đúng API
- Format đúng parameters

### ✨ Giải pháp
Bây giờ user chỉ cần:
- Gửi message tự nhiên
- Agent tự động hiểu ý định
- Gọi đúng service và trả về kết quả

---

## 🏗️ Kiến trúc Agent

```
User Message
    ↓
┌──────────────────────────┐
│   Agent Router           │
│                          │
│  1. Intent Classifier    │ ← LLM phân tích ý định
│     ↓                    │
│  2. Entity Extractor     │ ← Extract thông tin
│     ↓                    │
│  3. Service Router       │ ← Gọi service phù hợp
│     ↓                    │
│  4. Response Generator   │ ← Format response
└──────────────────────────┘
    ↓
Natural Response
```

---

## 🎯 Các Intent được hỗ trợ

### 1. **search_places** - Tìm địa điểm theo category
**Examples:**
- "Tìm quán cafe gần đây"
- "Có nhà hàng nào trong bán kính 2km không?"
- "Tìm khách sạn gần Hà Nội"

**Entities extracted:**
- categories: ["cafe", "restaurant", "hotel"]
- lat, lon: location
- radius_meters: bán kính

---

### 2. **nearby_landmark** - Tìm địa điểm gần landmark
**Examples:**
- "Tìm quán ăn gần Hồ Gươm"
- "Có gì xung quanh Văn Miếu?"
- "Khách sạn gần Lăng Bác"

**Entities extracted:**
- landmark_name: "Hồ Gươm"
- categories: ["restaurant"]
- radius_meters: bán kính

---

### 3. **semantic_search** - Tìm kiếm bằng mô tả
**Examples:**
- "Quán cafe lãng mạn view đẹp"
- "Nhà hàng phù hợp hẹn hò"
- "Địa điểm chụp ảnh đẹp cho couple"

**Entities extracted:**
- query_description: full description

---

### 4. **place_info** - Thông tin địa điểm cụ thể
**Examples:**
- "Cho tôi biết về Hồ Gươm"
- "Lăng Bác có gì đặc biệt?"
- "Thông tin Văn Miếu"

**Entities extracted:**
- place_name: "Hồ Gươm"

---

### 5. **compare_places** - So sánh địa điểm
**Examples:**
- "So sánh Hồ Gươm và Hồ Tây"
- "Nên đi Văn Miếu hay Hoàng Thành?"
- "Khác biệt giữa 3 museum này"

**Entities extracted:**
- place_names: ["Hồ Gươm", "Hồ Tây"]

---

### 6. **plan_itinerary** - Lập lịch trình
**Examples:**
- "Lập lịch trình 1 ngày Old Quarter"
- "Tạo kế hoạch 8 giờ cho gia đình"
- "Gợi ý lịch đi chơi"

**Entities extracted:**
- location: "Old Quarter"
- duration_hours: 8
- preferences: {"companions": "family"}

---

### 7. **recommend_places** - Gợi ý cá nhân hóa
**Examples:**
- "Gợi ý địa điểm cho gia đình có con nhỏ"
- "Địa điểm phù hợp ngân sách sinh viên"
- "Nơi nào tốt cho người cao tuổi?"

**Entities extracted:**
- preferences: {"companions": "family", "budget": 2}

---

## 🚀 API Endpoint

### POST /api/v1/chat

**Request:**
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
    "summary": "Tìm thấy 15 quán cafe..."
  }
}
```

---

## 💡 Examples

### Example 1: Simple Search
```bash
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tìm quán cafe gần đây"}'
```

**Response:**
```json
{
  "success": true,
  "intent": "search_places",
  "confidence": 0.92,
  "result": {
    "total": 20,
    "places": [
      {"name": "Cafe A", "distance_meters": 450},
      {"name": "Cafe B", "distance_meters": 680}
    ]
  }
}
```

---

### Example 2: Semantic Search
```bash
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quán cafe lãng mạn view đẹp phù hợp hẹn hò"}'
```

**Response:**
```json
{
  "success": true,
  "intent": "semantic_search",
  "confidence": 0.88,
  "result": {
    "places": [...],
    "recommendation": "Dựa trên yêu cầu của bạn..."
  }
}
```

---

### Example 3: Compare Places
```bash
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "So sánh Hồ Gươm và Hồ Tây"}'
```

---

### Example 4: Plan Itinerary
```bash
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Lập lịch trình 8 giờ Old Quarter cho gia đình"}'
```

---

## 🧪 Testing

### Test với script:
```bash
python test_services.py
```

### Test riêng Agent Chat:
```python
import requests

def test_agent_chat(message):
    response = requests.post(
        "http://localhost:8864/api/v1/chat",
        json={"message": message}
    )
    print(response.json())

# Test
test_agent_chat("Tìm quán cafe gần Hồ Gươm")
test_agent_chat("So sánh Văn Miếu và Hoàng Thành")
test_agent_chat("Gợi ý lịch trình 1 ngày")
```

---

## 🔍 Cách hoạt động

### Step 1: Intent Classification
LLM phân tích message và xác định intent:
```python
intent_result = agent_router.classify_intent(message)
# {
#   "intent": "search_places",
#   "confidence": 0.95,
#   "entities": {...}
# }
```

### Step 2: Entity Extraction
Extract thông tin cần thiết từ message:
- Categories (cafe, restaurant...)
- Location (Hồ Gươm, Old Quarter...)
- Preferences (family, budget...)
- Duration (8 giờ...)

### Step 3: Service Routing
Gọi service phù hợp:
```python
if intent == "search_places":
    return search_places(lat, lon, categories, radius)
elif intent == "semantic_search":
    return semantic_search(query)
...
```

### Step 4: Response Generation
Trả về kết quả tự nhiên kèm metadata

---

## ✨ Ưu điểm

### 1. **Natural UX**
- User chat như với người thật
- Không cần biết API
- Không cần format JSON

### 2. **Intelligent Routing**
- Tự động phân loại intent
- Extract entities chính xác
- Fallback to semantic search

### 3. **Context-Aware**
- Có thể maintain conversation
- Remember user preferences
- Multi-turn dialogue

### 4. **Flexible**
- Hiểu nhiều cách diễn đạt
- Xử lý typos
- Robust với edge cases

---

## 🔮 Future Enhancements

### Phase 2: Context Management
```python
{
  "message": "Còn gì gần đó không?",
  "session_id": "abc123",
  "chat_history": [
    {"user": "Tìm cafe gần Hồ Gươm", "bot": "..."}
  ]
}
```

### Phase 3: Multi-turn Conversation
```
User: "Tìm quán cafe"
Bot: "Bạn muốn tìm ở khu vực nào?"
User: "Gần Hồ Gươm"
Bot: "Tìm thấy 15 quán cafe..."
```

### Phase 4: Voice Interface
- Speech-to-text
- Text-to-speech
- Voice commands

### Phase 5: Proactive Suggestions
```
Bot: "Bạn đang ở gần Hồ Gươm, có muốn xem các quán cafe gần đây không?"
```

---

## 📊 Intent Classification Accuracy

Target metrics:
- Intent accuracy: >90%
- Entity extraction: >85%
- Response time: <2s
- User satisfaction: >4.5/5

---

## 🎯 Best Practices

### For Users:
1. ✅ Diễn đạt rõ ràng
2. ✅ Cung cấp context đầy đủ
3. ✅ Một câu hỏi mỗi lần
4. ❌ Tránh câu hỏi quá phức tạp

### For Developers:
1. Monitor intent classification accuracy
2. Collect feedback để improve
3. Update intent examples regularly
4. Handle edge cases gracefully

---

## 🚀 Kết luận

**Agent Chat** là tính năng **game-changer** cho Map Assistant:

✅ User experience tự nhiên
✅ Không cần học API
✅ Intelligent routing
✅ Scalable architecture

**Bây giờ user chỉ cần chat, hệ thống lo phần còn lại!** 🎉

---

## 📖 Xem thêm

- [API_DOCS.md](API_DOCS.md) - Chi tiết tất cả APIs
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [README.md](README.md) - Getting started
