# 🌍 PHASE 1 IMPLEMENTATION - MAP ASSISTANT

## 📋 Tổng quan

Đã triển khai thành công **Phase 1 Features** cho Map Assistant:

1. ✅ **Đa ngôn ngữ (Multilingual Support)** - Vietnamese & English
2. ✅ **Tích hợp Maps & Chỉ đường** - Google Maps integration
3. ✅ **Thời gian mở cửa Real-time** - Opening hours tracking
4. ✅ **Ước tính Chi phí** - Budget calculation & filtering

---

## 🎯 Features Chi tiết

### 1. Đa ngôn ngữ (Multilingual Support)

#### **Translation Service**
- File: [`app/services/translation_service.py`](app/services/translation_service.py)
- Auto-detect ngôn ngữ (Vietnamese/English)
- Dịch tự động tên địa điểm, mô tả, địa chỉ
- Cache dịch để tối ưu performance

**Sử dụng:**
```python
from app.services.translation_service import get_translation_service

translation = get_translation_service()

# Detect language
lang = translation.detect_language("Find cafes near me")  # Returns 'en'

# Translate
translated = translation.translate("Hồ Gươm", target_lang='en')
# Returns: "Sword Lake" or "Hoan Kiem Lake"

# Translate dictionary fields
data = {"name": "Hồ Gươm", "description": "Hồ nổi tiếng ở Hà Nội"}
translated_data = translation.translate_dict(data, target_lang='en')
# Returns: {..., "name_en": "Sword Lake", "description_en": "..."}
```

**API Support:**
Tất cả endpoints hiện hỗ trợ parameter `language`:
```json
POST /place_info
{
  "name": "Hồ Gươm",
  "language": "en"
}
```

---

### 2. Tích hợp Maps & Chỉ đường

#### **Maps Service**
- File: [`app/services/maps_service.py`](app/services/maps_service.py)
- Generate Google Maps URLs
- Tính khoảng cách (Haversine formula)
- Ước tính thời gian di chuyển
- Hỗ trợ multi-stop routing

**Features:**

**a) Google Maps URL cho địa điểm:**
```python
from app.services.maps_service import get_maps_service

maps = get_maps_service()

# Get place URL
url = maps.get_place_url(21.0285, 105.8542, "Hồ Gươm")
# Returns: https://www.google.com/maps/search/?api=1&query=Hồ+Gươm&query_place_id=21.0285,105.8542
```

**b) Chỉ đường:**
```python
# Get directions URL
directions_url = maps.get_directions_url(
    origin_lat=21.0285, origin_lon=105.8542,
    dest_lat=21.0277, dest_lon=105.8355,
    mode='driving'  # driving, walking, bicycling, transit
)
```

**c) Tính khoảng cách & thời gian:**
```python
# Calculate distance
distance = maps.calculate_distance(21.0285, 105.8542, 21.0277, 105.8355)
# Returns: {"meters": 850.5, "kilometers": 0.85}

# Estimate travel time
time = maps.estimate_travel_time(850, mode='walking')
# Returns: {"minutes": 10, "hours": 0.17}

# Get full travel info
travel_info = maps.get_travel_info(
    origin=(21.0285, 105.8542),
    destination=(21.0277, 105.8355),
    mode='walking'
)
# Returns: {distance, estimated_time, mode, directions_url}
```

**d) Multi-stop route:**
```python
stops = [
    (21.0285, 105.8542),  # Hồ Gươm
    (21.0277, 105.8355),  # Văn Miếu
    (21.0365, 105.8348)   # Lăng Bác
]

route = maps.get_multi_stop_route(stops, mode='driving')
# Returns: {total_distance, total_time, route_url, segments}
```

**e) Gợi ý phương tiện:**
```python
mode = maps.suggest_transport_mode(5000)  # 5km
# Returns: "bicycling" or "driving"
```

**API Integration:**
Tất cả response hiện bao gồm maps info:
```json
{
  "place_id": "HN-001",
  "name": "Hồ Gươm",
  "google_maps_url": "https://www.google.com/maps/...",
  "directions": {
    "distance": {"meters": 850, "kilometers": 0.85},
    "estimated_time": {"minutes": 10, "hours": 0.17},
    "mode": "walking",
    "directions_url": "https://www.google.com/maps/dir/..."
  },
  "suggested_transport": "walking"
}
```

---

### 3. Thời gian Mở cửa Real-time

#### **Opening Hours Model**
- File: [`app/models/enhanced_model.py`](app/models/enhanced_model.py)
- Parse opening hours từ nhiều format
- Check xem địa điểm có đang mở cửa không
- Hiển thị giờ mở/đóng theo ngày

**Sử dụng:**
```python
from app.models.enhanced_model import OpeningHours

# Create from string
hours = OpeningHours.from_string("09:00-22:00")

# Check if open now
is_open = hours.is_open_now()  # Returns True/False

# Get hours for specific day
monday_hours = hours.monday  # "09:00-22:00"

# Convert to dict
hours_dict = hours.to_dict()
```

**Data Format:**
```csv
opening_hours,phone,website
"Mo-Fr 09:00-22:00; Sa-Su 10:00-23:00",+84 24 3828 8093,https://example.com
```

**API Response:**
```json
{
  "place_id": "HN-001",
  "opening_hours": {
    "monday": "09:00-22:00",
    "tuesday": "09:00-22:00",
    ...
  },
  "is_open_now": true,
  "contact_info": {
    "phone": "+84 24 3828 8093",
    "website": "https://example.com"
  }
}
```

---

### 4. Ước tính Chi phí

#### **Budget Service**
- File: [`app/services/budget_service.py`](app/services/budget_service.py)
- Ước tính chi phí theo category
- Filter địa điểm theo ngân sách
- Tính tổng chi phí lịch trình
- So sánh giá giữa các địa điểm

**Features:**

**a) Ước tính chi phí địa điểm:**
```python
from app.services.budget_service import get_budget_service

budget = get_budget_service()

# Estimate place cost
cost = budget.estimate_place_cost(
    category='restaurant',
    num_people=2
)
# Returns:
# {
#   "per_person": {"min": 80000, "max": 300000, "avg": 190000},
#   "total": {"min": 160000, "max": 600000, "avg": 380000},
#   "price_range": "$$",
#   "currency": "VND"
# }
```

**b) Ước tính chi phí lịch trình:**
```python
places = [
    {"name": "Restaurant A", "categories": ["restaurant"]},
    {"name": "Cafe B", "categories": ["cafe"]},
    {"name": "Museum C", "categories": ["museum"]}
]

itinerary_cost = budget.estimate_itinerary_cost(
    places=places,
    num_people=2,
    include_transport=True,
    transport_budget=200000  # per person
)
# Returns:
# {
#   "total_cost": {"min": 800000, "max": 2000000, "avg": 1400000},
#   "per_person": {"min": 400000, "max": 1000000, "avg": 700000},
#   "breakdown": [...]
# }
```

**c) Filter theo ngân sách:**
```python
places = [...]  # List of places

affordable_places = budget.filter_by_budget(
    places=places,
    max_budget_per_person=150000,
    num_people=2
)
```

**d) So sánh giá:**
```python
places = [
    {"name": "Restaurant A", "categories": ["restaurant"]},
    {"name": "Restaurant B", "categories": ["restaurant"]}
]

comparison = budget.compare_prices(places)
# Returns:
# {
#   "comparisons": [
#     {"place": "Restaurant A", "price_range": "$$", "avg_cost": 150000, "rank": 1},
#     {"place": "Restaurant B", "price_range": "$$$", "avg_cost": 250000, "rank": 2}
#   ]
# }
```

**Default Price Ranges:**
```python
{
  "restaurant": {"min": 80000, "max": 300000},
  "cafe": {"min": 30000, "max": 100000},
  "fast_food": {"min": 50000, "max": 150000},
  "hotel": {"min": 300000, "max": 2000000},
  "museum": {"min": 0, "max": 40000},
  "temple": {"min": 0, "max": 30000},
  ...
}
```

**API Integration:**
```json
POST /plan_itinerary
{
  "location": "Old Quarter",
  "duration_hours": 8,
  "num_people": 2,
  "preferences": {
    "budget": 500000  // VND per person
  }
}

Response:
{
  "itinerary": "...",
  "cost_estimate": {
    "total_cost": {"min": 800000, "max": 2000000, "avg": 1400000},
    "per_person": {"avg": 700000},
    "breakdown": [...]
  }
}
```

---

## 🗂️ Enhanced Data Model

### New Schema Fields

Đã mở rộng data model với các fields mới:

#### **CSV Schema (Enhanced):**
```csv
place_id,name,lat,lon,address,categories,
opening_hours,phone,website,email,facebook,
name_en,description_en,
price_range,min_price,max_price,currency,
cuisine,wifi,wheelchair,outdoor_seating
```

#### **Models Created:**
- [`EnhancedPlace`](app/models/enhanced_model.py#L128) - Place model với Phase 1 features
- [`OpeningHours`](app/models/enhanced_model.py#L15) - Opening hours management
- [`PriceInfo`](app/models/enhanced_model.py#L58) - Price information
- [`ContactInfo`](app/models/enhanced_model.py#L81) - Contact details
- [`MultilingualInfo`](app/models/enhanced_model.py#L95) - Bilingual support

---

## 🔧 Data Enrichment

### Enrichment Script

File: [`resource/test_db/enrich_data.py`](resource/test_db/enrich_data.py)

**Chức năng:**
1. ✅ Fetch thông tin từ OpenStreetMap Overpass API
2. ✅ Extract opening hours, contact info
3. ✅ Add price estimates
4. ✅ Generate sample enriched data

**Sử dụng:**
```bash
cd resource/test_db
python enrich_data.py

# Options:
# 1. Enrich CSV with OSM data (slow, rate-limited)
# 2. Add price estimates to CSV
# 3. Generate sample enriched data
```

**⚠️ Lưu ý về Data:**
- OSM Overpass API có rate limit nghiêm ngặt (1-2 seconds/request)
- Nhiều địa điểm nhỏ không có thông tin đầy đủ trên OSM
- Recommended: Enrich từng phần nhỏ (100 rows/lần)
- Nên chạy vào off-peak hours

**Sample Output:**
```json
{
  "place_id": "HN-SAMPLE-001",
  "name": "Cà Phê Giảng",
  "name_en": "Giang Cafe",
  "opening_hours": "Mo-Su 07:00-22:00",
  "phone": "+84 24 3828 8093",
  "price_range": "$",
  "min_price": 25000,
  "max_price": 60000
}
```

---

## 🔄 Service Updates

### main_service.py - Enhanced

Đã cập nhật tất cả services để hỗ trợ Phase 1:

#### **1. get_info_details()**
```python
# New signature
get_info_details(name, language='vi')

# Returns:
{
  "response": "...",  # AI response in specified language
  "place_info": {
    "name": "...",
    "google_maps_url": "...",
    "lat": 21.0285,
    "lon": 105.8542
  },
  "language": "en"
}
```

#### **2. search_places()**
```python
# New signature
search_places(lat, lon, categories, radius_meters=2000, limit=20, 
              language='vi', user_location=None)

# Returns places with:
{
  "places": [
    {
      "name": "...",
      "name_en": "...",  // if language='en'
      "google_maps_url": "...",
      "directions": {...},  // if user_location provided
      "suggested_transport": "walking",
      "estimated_cost": {...}
    }
  ],
  "language": "en"
}
```

#### **3. plan_itinerary()**
```python
# New signature
plan_itinerary(location, duration_hours, preferences=None, 
               start_time="09:00", language='vi', num_people=1)

# Returns:
{
  "itinerary": "...",  # AI response in specified language
  "cost_estimate": {...},  # Total budget breakdown
  "route_info": {...},  # Multi-stop routing
  "language": "en"
}
```

### agent_service.py - Enhanced

Agent chat hiện hỗ trợ multilingual:

```python
# New signature
chat_handler(message, context=None, language=None)

# Auto-detect language if not specified
# Translate message if needed for intent classification
# Return response in user's language

# Example:
chat_handler("Find cafes near Hoan Kiem Lake", language='en')
# Auto-translates to Vietnamese for processing
# Returns English response
```

---

## 📊 Example Usage

### Example 1: Multilingual Search

**Request (English):**
```bash
curl -X POST http://localhost:8864/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find romantic cafes with nice views",
    "language": "en"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Find romantic cafes with nice views",
  "detected_language": "en",
  "intent": "semantic_search",
  "result": {
    "places": [
      {
        "name": "Cà Phê Giảng",
        "name_en": "Giang Cafe",
        "google_maps_url": "...",
        "estimated_cost": {"per_person": {"avg": 45000}}
      }
    ],
    "summary": "Here are some romantic cafes with beautiful views..."
  }
}
```

### Example 2: Budget-based Itinerary

**Request:**
```bash
curl -X POST http://localhost:8864/plan_itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Old Quarter",
    "duration_hours": 8,
    "num_people": 2,
    "preferences": {
      "budget": 500000,
      "companions": "couple",
      "interests": ["food", "culture"]
    },
    "language": "vi"
  }'
```

**Response:**
```json
{
  "itinerary": "**Lịch trình 8 giờ Old Quarter**\n\n09:00 - ...",
  "cost_estimate": {
    "total_cost": {"avg": 1400000},
    "per_person": {"avg": 700000},
    "breakdown": [...]
  },
  "route_info": {
    "total_distance": {"kilometers": 5.2},
    "total_time": {"hours": 1.5},
    "route_url": "https://www.google.com/maps/dir/..."
  }
}
```

### Example 3: Search with Directions

**Request:**
```bash
curl -X POST http://localhost:8864/search_places \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 21.0285,
    "lon": 105.8542,
    "categories": ["restaurant"],
    "radius_meters": 1000,
    "language": "en",
    "user_location": {"lat": 21.0300, "lon": 105.8550}
  }'
```

**Response:**
```json
{
  "places": [
    {
      "name": "Nhà Hàng Chả Cá",
      "name_en": "Cha Ca Restaurant",
      "distance_meters": 350,
      "directions": {
        "distance": {"meters": 350, "kilometers": 0.35},
        "estimated_time": {"minutes": 4, "hours": 0.07},
        "mode": "walking",
        "directions_url": "https://www.google.com/maps/dir/..."
      },
      "suggested_transport": "walking",
      "estimated_cost": {
        "per_person": {"avg": 200000},
        "price_range": "$$"
      }
    }
  ]
}
```

---

## 🚀 Next Steps

### Recommended Improvements:

**1. Data Enrichment Priority:**
- ✅ Run enrichment script cho top 1000 places
- ✅ Focus on tourist hotspots first
- ✅ Manually verify và correct thông tin quan trọng

**2. API Enhancements:**
- ⏳ Add caching cho translations (Redis)
- ⏳ Implement rate limiting cho external APIs
- ⏳ Add error handling cho missing data

**3. UI Updates:**
- ⏳ Display Google Maps links as buttons
- ⏳ Show cost estimates prominently
- ⏳ Add language toggle (VI/EN)
- ⏳ Display opening hours với visual indicators

**4. External API Integration:**
- ⏳ Google Places API cho real-time data
- ⏳ Weather API integration
- ⏳ Real-time traffic/transport info

---

## 📝 Testing

### Test Script

```bash
# Test translation
curl -X POST http://localhost:8864/place_info \
  -d '{"name": "Hồ Gươm", "language": "en"}'

# Test budget filtering
curl -X POST http://localhost:8864/plan_itinerary \
  -d '{"location": "Old Quarter", "duration_hours": 4, "preferences": {"budget": 300000}}'

# Test multilingual chat
curl -X POST http://localhost:8864/chat \
  -d '{"message": "Where can I find cheap street food?", "language": "en"}'
```

---

## 🎉 Summary

Phase 1 đã hoàn thành với **4 major features**:
- ✅ Multilingual support (VI/EN)
- ✅ Maps & directions integration
- ✅ Opening hours tracking
- ✅ Budget calculation & filtering

**Files Created/Modified:**
- ✅ `app/models/enhanced_model.py` (NEW)
- ✅ `app/services/translation_service.py` (NEW)
- ✅ `app/services/maps_service.py` (NEW)
- ✅ `app/services/budget_service.py` (NEW)
- ✅ `resource/test_db/enrich_data.py` (NEW)
- ✅ `app/services/main_service.py` (ENHANCED)
- ✅ `app/services/agent_service.py` (ENHANCED)

**Ready for Phase 2!** 🚀
