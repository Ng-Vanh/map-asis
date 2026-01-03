# Phase 1 Deployment Guide

## 📊 Current Status

### ✅ Completed
1. **Services**: translation_service, maps_service, budget_service
2. **Models**: Enhanced data models with Phase 1 fields
3. **Integration**: main_service và agent_service đã được cập nhật
4. **Testing**: 21 tests passed
5. **Scripts**: 
   - `resource/test_db/enrich_data.py` - Enrich CSV từ OpenStreetMap
   - `resource/test_db/import_to_neo4j.py` - Import vào Neo4j
6. **UI**: ChatInterface.jsx đã cập nhật hiển thị Phase 1 features

### 🎯 Deployment Steps

## Step 1: Import Data vào Neo4j

### Option A: Import Basic Data (Nhanh - Dùng CSV hiện tại)

```bash
# Activate environment
source ~/miniconda3/bin/activate

# Import basic data
cd /media/sda3/Workspace/map-assis
python resource/test_db/import_to_neo4j.py
```

**Kết quả:**
- Import được tất cả places từ CSV
- Chỉ có basic fields: name, address, categories, coordinates
- **Không có** Phase 1 fields: opening_hours, prices, contact_info
- API vẫn hoạt động nhưng Phase 1 features sẽ ước tính/mặc định

### Option B: Enrich Data trước khi Import (Khuyến nghị - Có đầy đủ Phase 1 data)

```bash
# Activate environment
source ~/miniconda3/bin/activate
cd /media/sda3/Workspace/map-assis

# Step 1: Enrich data từ OpenStreetMap
python resource/test_db/enrich_data.py

# Tham số tùy chọn:
# --input: CSV file đầu vào (mặc định: hanoi_places_osm_filtered.csv)
# --output: CSV file đầu ra (mặc định: hanoi_places_enriched.csv)
# --limit: Giới hạn số records (test với 50-100 trước)
# --delay: Delay giữa API calls (mặc định: 1.5s, tối thiểu 1.5s)

# Test với 50 records đầu tiên
python resource/test_db/enrich_data.py --limit 50 --delay 1.5

# Hoặc enrich toàn bộ (mất ~1-2 giờ cho 2000+ records)
python resource/test_db/enrich_data.py --delay 1.5
```

**⚠️ Lưu ý về Data Enrichment:**
- OpenStreetMap Overpass API có rate limit nghiêm ngặt
- Delay tối thiểu: 1.5 giây giữa mỗi request
- Toàn bộ dataset (~2000 places) mất 50-60 phút
- Script có resume capability (lưu progress, có thể tiếp tục nếu bị gián đoạn)
- Chạy trong screen/tmux để tránh bị ngắt kết nối

**Script sẽ enrich:**
- ⏰ Opening hours (Mo-Su 08:00-17:00)
- 📞 Phone numbers
- 🌐 Website URLs
- 📧 Email addresses
- 📱 Social media (Facebook)
- 🌍 English translations (name, description)
- 🍽️ Cuisine types
- 💰 Price ranges (estimate từ category nếu không có)
- ♿ Accessibility info

```bash
# Step 2: Import enriched data vào Neo4j
python resource/test_db/import_to_neo4j.py

# Script sẽ tự động detect enriched CSV
```

**Kết quả:**
- ✅ Đầy đủ Phase 1 fields
- ✅ Opening hours real-time check hoạt động
- ✅ Price filtering chính xác
- ✅ Contact info đầy đủ
- ✅ Multilingual data (Vietnamese + English)

## Step 2: Verify Import

```bash
# Check statistics
python -c "
from resource.test_db.import_to_neo4j import Neo4jImporter
importer = Neo4jImporter()
stats = importer.get_statistics()
for key, value in stats.items():
    print(f'{key}: {value}')
"
```

**Expected Output:**
```
total_places: 2000+
places_with_hours: 1500+ (75%+)
places_with_prices: 1800+ (90%+)
places_with_english: 1600+ (80%+)
places_with_contact: 1200+ (60%+)
```

## Step 3: Start Services

### Backend

```bash
# Terminal 1: Start embedding service (nếu cần)
cd /media/sda3/Workspace/map-assis
source ~/miniconda3/bin/activate
cd serve
bash serve.sh
```

```bash
# Terminal 2: Start Flask API
cd /media/sda3/Workspace/map-assis
source ~/miniconda3/bin/activate
python main.py
# API running on http://localhost:8864
```

### Frontend

```bash
# Terminal 3: Start React UI
cd /media/sda3/Workspace/map-assis/ui
npm install  # nếu chưa install
npm run dev
# UI running on http://localhost:5173
```

## Step 4: Test Phase 1 Features

### Test trong UI (http://localhost:5173)

**1. Test Multilingual (Vietnamese ↔ English):**
```
Vietnamese: "Tìm quán cafe gần Hồ Gươm"
English: "Find coffee shops near Hoan Kiem Lake"
```

**2. Test Opening Hours:**
```
"Quán nào đang mở cửa gần tôi?"
"Find restaurants open now near Old Quarter"
```

**3. Test Price/Budget:**
```
"Tìm nhà hàng giá rẻ trong bán kính 2km"
"Lập lịch trình 1 ngày với ngân sách 500,000 VND"
```

**4. Test Maps & Directions:**
```
"Chỉ đường đến Văn Miếu từ Hồ Gươm"
"Find route from my location to Temple of Literature"
```

**5. Test Itinerary with Budget:**
```
"Lập lịch trình 2 ngày Old Quarter cho 2 người, ngân sách 2 triệu"
```

### Test qua API (http://localhost:8864)

```bash
# Test multilingual search
curl -X POST http://localhost:8864/api/v1/search-places \
  -H "Content-Type: application/json" \
  -d '{
    "query": "coffee shop",
    "language": "en",
    "user_location": {"lat": 21.0285, "lon": 105.8542}
  }'

# Test itinerary with budget
curl -X POST http://localhost:8864/api/v1/plan-itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "duration_days": 1,
    "num_people": 2,
    "budget_per_person": 250000,
    "language": "vi"
  }'

# Test chat with language detection
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find restaurants open now"
  }'
```

## 📋 Expected UI Display

Sau khi deploy, UI sẽ hiển thị:

### Place Card Format:
```
**1. Café Giảng** (Giang Cafe)

[Image 1] [Image 2]

📍 Địa chỉ: 39 Nguyễn Hữu Huân, Hoàn Kiếm
🏷️ Loại: Cafe, Vietnamese Coffee
📏 Khoảng cách: 850m

⏰ Trạng thái: 🟢 Đang mở cửa

💰 Giá: $$ (25,000 - 60,000 VND)

📞 Phone: +84 24 3828 6027
🌐 Website: cafegianghanoi.com

🗺️ [Xem trên Google Maps]

🚶 Chỉ đường: 850m (~12 phút)
🚶 Đề xuất: walking

📍 [Chỉ đường chi tiết]

💡 Quán cà phê trứng nổi tiếng với hơn 70 năm lịch sử...

---
```

## 🔍 Verification Checklist

### Data Layer:
- [ ] Neo4j running và có data (check statistics)
- [ ] CSV enriched (nếu chọn Option B)
- [ ] Phase 1 fields có trong database

### Backend:
- [ ] Flask API running (port 8864)
- [ ] Translation service working (test /api/v1/chat với English)
- [ ] Maps service returning URLs
- [ ] Budget service filtering correctly
- [ ] Opening hours check working

### Frontend:
- [ ] React UI running (port 5173)
- [ ] Welcome message hiển thị Phase 1 features
- [ ] Place cards hiển thị đầy đủ fields:
  - [ ] Name + English name
  - [ ] Opening status (🟢/🔴)
  - [ ] Price range
  - [ ] Google Maps link
  - [ ] Directions info
  - [ ] Contact info

### Integration:
- [ ] Search với language='en' trả về English results
- [ ] Budget filtering hoạt động
- [ ] Itinerary có estimated_cost
- [ ] Chat auto-detect language

## 🚀 Production Recommendations

### 1. Environment Variables
Tạo `.env` file:
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Qdrant
QDRANT_URL=http://localhost:6333

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...

# Rate Limits
OSM_API_DELAY=1.5
MAX_ENRICHMENT_CONCURRENT=1
```

### 2. Caching
- Translation cache (in-memory) - đã implement
- Consider Redis cho production
- Cache opening hours check (5-10 phút)
- Cache price estimates

### 3. Error Handling
- Fallback nếu OSM API timeout
- Default prices nếu không có data
- Graceful degradation Phase 1 features

### 4. Monitoring
- Log translation API calls
- Track OSM API rate limit
- Monitor Google Maps API usage
- Database query performance

## 📊 Performance Metrics

### Expected Response Times:
- Search places: 200-500ms
- Get place details: 100-300ms
- Plan itinerary: 500-1000ms
- Chat (với translation): 1-2s
- Directions: 300-600ms

### Resource Usage:
- Memory: ~500MB (Flask + services)
- CPU: Low (translation có cache)
- Network: OSM enrichment heavy, runtime minimal
- Database: Neo4j ~1GB for 2000 places

## 🆘 Troubleshooting

### Issue: Opening hours không hiển thị
**Cause**: CSV chưa enriched
**Fix**: Chạy `enrich_data.py` trước hoặc check `places_with_hours` statistic

### Issue: Prices đều là estimate
**Cause**: OSM không có price data
**Fix**: Normal behavior, budget_service dùng category defaults

### Issue: Translation slow
**Cause**: API calls cho mỗi request
**Fix**: Cache đã có, check cache hit rate

### Issue: Google Maps links không hoạt động
**Cause**: Coordinates không chính xác
**Fix**: Verify lat/lon trong Neo4j

### Issue: UI không hiển thị Phase 1 fields
**Cause**: API response không có data
**Fix**: Check API response structure, verify ChatInterface.jsx updated

## 📈 Next Steps (Future Phases)

### Phase 2 Ideas:
- 📸 User-generated content (photos, reviews)
- 👥 Social features (share itineraries)
- 🤖 Advanced AI recommendations
- 📱 Mobile app
- 🔔 Notifications (place opening soon, events)
- ⭐ Rating system
- 🎫 Booking integration

### Phase 3 Ideas:
- 🌐 More languages (Chinese, Korean, Japanese)
- 🗺️ Offline maps
- 🎯 Personalization (user preferences)
- 📊 Analytics dashboard
- 💳 Payment integration
- 🏨 Hotel/accommodation
- ✈️ Transportation booking

## 📝 Summary

**Ready to Deploy:**
✅ All services implemented and tested
✅ Import script ready
✅ UI updated for Phase 1 display
✅ Documentation complete

**Choose Path:**
- **Quick Start**: Import basic data → Test basic features → Enrich later
- **Full Phase 1**: Enrich data → Import → Full Phase 1 features

**Recommendation**: 
Start với Option A (basic import) để test integration, sau đó chạy enrichment trong background (50-100 records test trước) để có full Phase 1 experience.

**Time Estimate:**
- Option A: 5-10 phút (immediate testing)
- Option B: 1-2 giờ (complete Phase 1 data)
