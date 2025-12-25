# 🗺️ Map Assistant - Hệ thống Gợi ý Địa điểm Thông minh

## 📋 Tổng quan

Map Assistant là hệ thống recommendation địa điểm thông minh cho Hà Nội, kết hợp:
- **Knowledge Graph (Neo4j)** - Spatial queries & relationships
- **Vector Database (Qdrant)** - Semantic search  
- **AI Service (GPT/Claude)** - Natural language generation
- **Embedding Service** - Text embeddings

## ✨ Tính năng chính

### 🎯 9 Services đã triển khai:

0. **🤖 Agent Chat** - Chat tự nhiên, tự động routing (NEW!)
1. **📍 Thông tin địa điểm** - Lấy chi tiết về địa điểm
2. **🔍 Tìm kiếm theo category** - Tìm restaurant/cafe/hotel theo vị trí
3. **🏛️ Tìm kiếm gần landmark** - Tìm địa điểm xung quanh điểm nổi tiếng
4. **🧠 Semantic search** - Tìm kiếm bằng ngôn ngữ tự nhiên
5. **⚖️ So sánh địa điểm** - So sánh chi tiết nhiều địa điểm
6. **📅 Lập lịch trình** - Planning itinerary thông minh
7. **💡 Gợi ý cá nhân hóa** - Recommendation dựa trên preferences
8. **❤️ Health check** - Kiểm tra trạng thái server

## 🏗️ Kiến trúc hệ thống

```
User Query
    ↓
┌─────────────────────┐
│   Flask API Server   │
│   (main_routes.py)   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Services Layer      │
│  (main_service.py)   │
└─────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Neo4j    │  Qdrant   │   AI Service    │
│  Spatial  │  Vector   │   GPT/Claude    │
│  Queries  │  Search   │   Generation    │
└─────────────────────────────────────────┘
```

## 🚀 Cài đặt & Chạy

### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
Tạo file `.env`:
```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345678

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=map_assistant_v2

# Embedding Service
EMBEDDING_SERVICE_URL=http://localhost:8080/embed

# AI Service
API_KEY=your-api-key
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4
```

### 3. Khởi động services

#### Neo4j:
```bash
# Chạy Neo4j database
neo4j start
```

#### Qdrant:
```bash
# Chạy Qdrant vector database
docker run -p 6333:6333 qdrant/qdrant
```

#### Embedding Service:
```bash
cd serve/
bash serve.sh
```

#### Flask API:
```bash
python main.py
```

Server sẽ chạy tại: `http://localhost:8864`

## 📚 Documentation

### API Documentation
Xem chi tiết tại: [API_DOCS.md](API_DOCS.md)

### Idea & System Design
Xem chi tiết tại: [Idea.md](Idea.md)

## 🧪 Testing

### Chạy tất cả tests:
```bash
python test_services.py
```

### Test từng API riêng lẻ:
```python
# Trong test_services.py
test_search_places()      # Test tìm kiếm địa điểm
test_semantic_search()    # Test semantic search
test_plan_itinerary()     # Test lập lịch trình
test_recommend_places()   # Test gợi ý cá nhân hóa
```

### Test với cURL:
```bash
# Health check
curl http://localhost:8864/api/v1/health

# Search places
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

## 📊 Cấu trúc thư mục

```
map-assis/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── neo4j/          # Neo4j spatial queries
│   │   └── qdrant/         # Qdrant vector search
│   ├── models/
│   │   └── model.py        # AI service
│   ├── routes/
│   │   └── main_routes.py  # API endpoints
│   └── services/
│       └── main_service.py # Business logic (8 services)
├── resource/
│   ├── data/               # CSV data files
│   ├── test_API/           # API tests
│   └── test_db/            # Database tests
├── serve/
│   ├── embed_service.py    # Embedding service
│   └── serve.sh            # Start script
├── main.py                 # Flask app entry
├── test_services.py        # Service tests
├── API_DOCS.md            # API documentation
├── Idea.md                # System design
└── requirements.txt       # Dependencies
```

## 🎯 Use Cases

### 🤖 NEW: Natural Language Chat (RECOMMENDED!)
```python
# User chỉ cần chat tự nhiên!
POST /api/v1/chat
{
  "message": "Tìm quán cafe gần Hồ Gươm"
}

# Hoặc:
{
  "message": "Lập lịch trình 8 giờ Old Quarter cho gia đình"
}

# Agent tự động hiểu và gọi đúng service!
```

### 1. Tìm kiếm đơn giản
```python
# "Tìm quán cafe gần đây"
POST /search_places
{
  "lat": 21.0285,
  "lon": 105.8542,
  "categories": ["cafe"],
  "radius_meters": 1000
}
```

### 2. Tìm kiếm ngữ nghĩa
```python
# "Quán cafe lãng mạn view đẹp phù hợp hẹn hò"
POST /semantic_search
{
  "query": "cafe lãng mạn view đẹp hẹn hò"
}
```

### 3. Lập lịch trình
```python
# "Lập lịch 1 ngày Old Quarter cho gia đình"
POST /plan_itinerary
{
  "location": "Old Quarter",
  "duration_hours": 8,
  "preferences": {
    "companions": "family",
    "interests": ["culture", "food"]
  }
}
```

### 4. Gợi ý cá nhân hóa
```python
# "Gợi ý địa điểm phù hợp gia đình, ngân sách vừa phải"
POST /recommend_places
{
  "user_preferences": {
    "budget": 2,
    "companions": "family",
    "interests": ["food", "culture"]
  }
}
```

## 🔧 Tech Stack

- **Backend:** Flask (Python)
- **Knowledge Graph:** Neo4j 5.x
- **Vector DB:** Qdrant
- **AI:** OpenAI GPT / Anthropic Claude
- **Embeddings:** Custom embedding service
- **Data:** OpenStreetMap + Wikipedia + Manual curation

## 📈 Roadmap tiếp theo

### Phase 2: Real-time Data
- [ ] Tích hợp Redis cache cho dynamic data
- [ ] Weather API integration
- [ ] Real-time crowd level
- [ ] Recent reviews từ social media

### Phase 3: Advanced Features
- [ ] Multi-language support (EN, KR, CN, JP)
- [ ] User authentication & history
- [ ] PostgreSQL cho user preferences
- [ ] Collaborative filtering recommendations
- [ ] Mobile app integration

### Phase 4: Scale to Vietnam
- [ ] Mở rộng từ Hà Nội ra toàn Việt Nam
- [ ] Thêm data cho TP.HCM, Đà Nẵng, Huế...
- [ ] Multi-region support
- [ ] Performance optimization

## 🤝 Contributing

Contributions are welcome! Các tính năng có thể phát triển thêm:

1. **Advanced Filtering:**
   - Filter theo giá, rating, review count
   - Filter theo accessibility (wheelchair, elderly)
   - Filter theo seasonality

2. **Multi-modal Search:**
   - Image search (tìm địa điểm bằng ảnh)
   - Voice search integration
   - Map-based visual search

3. **Social Features:**
   - User reviews & ratings
   - Share itineraries
   - Follow other users
   - Community recommendations

4. **Business Integration:**
   - Booking integration
   - Price comparison
   - Promotion & deals
   - Restaurant reservation


**⭐ Nếu project hữu ích, đừng quên star repo!**
