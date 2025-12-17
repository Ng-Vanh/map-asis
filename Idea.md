# HỆ THỐNG RECOMMENDATION ĐỊA ĐIỂM - SYSTEM DESIGN

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục tiêu
- Xây dựng hệ thống gợi ý địa điểm thông minh cho Hà Nội, mở rộng ra toàn Việt Nam
- Kết hợp Knowledge Graph, Vector DB, Cache, và SQL để tối ưu tốc độ và độ chính xác
- Hỗ trợ các usecase: tìm kiếm, itinerary planning, recommendation cá nhân hóa

### 1.2 Usecase chính
1. **Tìm kiếm địa điểm** - "Tìm quán cafe gần đây"
2. **Itinerary planning** - "Lập lịch trình 1 ngày Old Quarter"
3. **Thông tin chi tiết** - "Cho tôi biết về Văn Miếu"
4. **Thông tin dynamic** - "Review gần đây về địa điểm này?"
5. **Gợi ý cá nhân hóa** - "Địa điểm phù hợp với gia đình có trẻ nhỏ"
6. **So sánh & ranking** - "So sánh 3 nhà hàng này"

---

## 2. KIẾN TRÚC HỆ THỐNG (PIPELINE)

```
User Query (Natural Language)
        ↓
┌─────────────────────────────┐
│ Intent & Entity Recognition │ ← LLM/NLP
│ - Extract: location, category, preferences │
│ - Classify: search/plan/compare/info │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│   Knowledge Graph Filter    │ ← Neo4j
│ - Filter theo category, location radius │
│ - Filter theo rating, price, open hours │
│ - Trả về: subset 20-50 địa điểm phù hợp │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  Vector DB Semantic Search  │ ← Pinecone/Qdrant
│ - Search trong description, tips, reviews │
│ - Semantic similarity với user query │
│ - Trả về: top 5-10 địa điểm relevant nhất │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│ Dynamic Data Fetch / Cache  │ ← Redis
│ - Recent reviews, events, weather │
│ - Trending social media, pricing │
│ - Cache TTL: 30min - 6 hours │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│   User Context & History    │ ← PostgreSQL
│ - User preferences, past visits │
│ - Session context, favorites │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  Agent / Reasoning Module   │ ← LangChain/Custom
│ - Multi-step reasoning │
│ - Ranking theo preferences │
│ - Multi-turn conversation │
└─────────────────────────────┘
        ↓
┌─────────────────────────────┐
│  LLM Response Generation    │ ← GPT/Claude
│ - Tổng hợp static + dynamic data │
│ - Generate natural language response │
│ - Format: text/list/itinerary/comparison │
└─────────────────────────────┘
        ↓
    Response to User
```

---

## 3. DATABASE STRATEGY CHI TIẾT

### 3.1 KNOWLEDGE GRAPH (Neo4j)
**Mục đích:** Lưu metadata có cấu trúc, hỗ trợ spatial & graph queries

#### Node Types:
```
Place, Province, District, Ward, Category, Tag
```

#### CSV Schema cho Import:
```csv
place_id          # Primary key (VD: HN-0001)
name              # Tên địa điểm
alt_names         # Tên khác (phân cách ;)
lat               # Vĩ độ (float)
lon               # Kinh độ (float)
address           # Địa chỉ đầy đủ
province_code     # Mã tỉnh (VD: HN)
district_code     # Mã quận (VD: HK, DD, BD)
ward_code         # Mã phường/xã
categories        # Loại hình chính (restaurant;cafe;temple)
subcategories     # Loại hình chi tiết (vietnamese_food;buddhist)
tags              # Tags mô tả (romantic;family-friendly;view)
rating            # Điểm trung bình (0-5)
review_count      # Số lượng reviews
popularityScore   # Điểm phổ biến (0-10)
priceLevel        # Mức giá (1-4: $ đến $$$$)
opening_hours     # Giờ mở cửa (08:00-22:00)
seasonality       # Mùa phù hợp (spring;summer;autumn;winter;all-year)
avg_visit_duration # Thời gian tham quan TB (phút)
suitable_for      # Phù hợp cho (family;couple;solo;group)
accessibility     # Khả năng tiếp cận (wheelchair;elderly;children)
crowd_level       # Mức độ đông (low;medium;high)
phone             # Số điện thoại
website           # Website chính thức
images            # URLs ảnh (phân cách ;)
verified          # Đã xác minh (true/false)
last_updated      # Timestamp cập nhật cuối
source            # Nguồn dữ liệu (google;manual;facebook)
```

#### Relationships:
```cypher
(Place)-[:LOCATED_IN]->(District)-[:LOCATED_IN]->(Province)
(Place)-[:HAS_CATEGORY]->(Category)
(Place)-[:HAS_TAG]->(Tag)
(Place)-[:NEAR {distance: float}]->(Place)
```

#### Indexes:
```cypher
CREATE INDEX place_id FOR (p:Place) ON (p.place_id);
CREATE INDEX place_name FOR (p:Place) ON (p.name);
CREATE POINT INDEX place_location FOR (p:Place) ON (p.location);
CREATE INDEX category_name FOR (c:Category) ON (c.name);
CREATE INDEX place_rating FOR (p:Place) ON (p.rating);
CREATE INDEX place_price FOR (p:Place) ON (p.priceLevel);
```

#### Sample Cypher Import:
```cypher
LOAD CSV WITH HEADERS FROM 'file:///places_hanoi.csv' AS row
WITH row WHERE row.place_id IS NOT NULL

MERGE (place:Place {place_id: row.place_id})
ON CREATE SET
    place.name = row.name,
    place.alt_names = split(coalesce(row.alt_names,''), ';'),
    place.address = row.address,
    place.popularityScore = toFloat(coalesce(row.popularityScore, '0')),
    place.rating = toFloat(coalesce(row.rating, '0')),
    place.review_count = toInteger(coalesce(row.review_count, '0')),
    place.priceLevel = toInteger(coalesce(row.priceLevel, '0')),
    place.opening_hours = row.opening_hours,
    place.seasonality = split(coalesce(row.seasonality,''), ';'),
    place.avg_visit_duration = toInteger(coalesce(row.avg_visit_duration, '0')),
    place.suitable_for = split(coalesce(row.suitable_for,''), ';'),
    place.accessibility = split(coalesce(row.accessibility,''), ';'),
    place.crowd_level = row.crowd_level,
    place.phone = row.phone,
    place.website = row.website,
    place.images = split(coalesce(row.images,''), ';'),
    place.verified = toBoolean(coalesce(row.verified, 'false')),
    place.source = coalesce(row.source, 'import'),
    place.last_updated = datetime(),
    place.location = point({latitude: toFloat(row.lat), longitude: toFloat(row.lon)})

WITH place, row

MERGE (prov:Province {code: row.province_code})
ON CREATE SET prov.name = CASE row.province_code 
    WHEN 'HN' THEN 'Hà Nội'
    WHEN 'HCM' THEN 'Hồ Chí Minh'
    ELSE row.province_code
END
MERGE (place)-[:LOCATED_IN]->(prov)

WITH place, row
MERGE (dist:District {code: row.district_code})
MERGE (place)-[:IN_DISTRICT]->(dist)

WITH place, split(coalesce(row.categories,''), ';') AS categories
UNWIND categories AS cat
WITH place, trim(cat) AS category
WHERE category <> ''
MERGE (c:Category {name: category})
MERGE (place)-[:HAS_CATEGORY]->(c)

WITH place, split(coalesce(row.tags,''), ';') AS tags
UNWIND tags AS tag
WITH place, trim(tag) AS tagName
WHERE tagName <> ''
MERGE (t:Tag {name: tagName})
MERGE (place)-[:HAS_TAG]->(t);
```

#### Sample Queries:
```cypher
// Tìm cafe trong bán kính 2km, rating > 4.0, đang mở cửa
MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category {name: 'cafe'})
WHERE distance(p.location, point({latitude: 21.0285, longitude: 105.8542})) < 2000
AND p.rating >= 4.0
AND p.opening_hours CONTAINS '08:00'
RETURN p.place_id, p.name, p.rating, p.address
ORDER BY p.rating DESC
LIMIT 20;

// Tìm địa điểm gần nhất
MATCH (p1:Place {place_id: 'HN-0001'})
MATCH (p2:Place)
WHERE p1 <> p2
WITH p1, p2, distance(p1.location, p2.location) AS dist
WHERE dist < 1000
RETURN p2.place_id, p2.name, dist
ORDER BY dist
LIMIT 10;
```

---

### 3.2 VECTOR DATABASE (Pinecone/Qdrant/Weaviate)
**Mục đích:** Semantic search cho nội dung text dài (description, tips, reviews)

#### Document Structure:

**1. Place Description**
```json
{
  "id": "HN-0001-desc",
  "place_id": "HN-0001",
  "chunk_type": "description",
  "language": "vi",
  "content": "Hồ Hoàn Kiếm là trái tim văn hóa của Hà Nội. Hồ có diện tích 12 hecta, nằm ngay trung tâm thành phố. Theo truyền thuyết, vua Lê Lợi trả thanh gươm thần cho Rùa thần tại đây. Hồ có không khí yên bình, phù hợp cho việc dạo bộ sáng sớm hoặc tối muộn. Xung quanh hồ có nhiều quán cafe, nhà hàng với view đẹp.",
  "embedding": [0.123, 0.456, ...],
  "metadata": {
    "place_name": "Hoàn Kiếm Lake",
    "categories": ["scenic", "lake", "cultural"],
    "rating": 4.7,
    "price_level": 1,
    "language": "vi"
  }
}
```

**2. Expert Tips**
```json
{
  "id": "HN-0001-tip-001",
  "place_id": "HN-0001",
  "chunk_type": "tip",
  "language": "vi",
  "content": "Thời điểm đẹp nhất để tham quan là lúc bình minh (5:30-6:30) hoặc hoàng hôn (17:00-18:30). Buổi sáng có nhiều người tập thể dục, không khí trong lành. Tránh cuối tuần nếu muốn không gian yên tĩnh. Có thể thuê xe đạp xung quanh hồ với giá 30-50k/giờ.",
  "embedding": [0.789, 0.012, ...],
  "metadata": {
    "tip_category": "timing",
    "author_type": "local_expert",
    "place_name": "Hoàn Kiếm Lake"
  }
}
```

**3. Aggregated Review Summary**
```json
{
  "id": "HN-0001-review-summary",
  "place_id": "HN-0001",
  "chunk_type": "review_summary",
  "language": "vi",
  "content": "Điểm mạnh: Không khí lãng mạn, view đẹp chụp ảnh, vị trí trung tâm dễ tìm, miễn phí tham quan, an toàn cho trẻ em. Điểm yếu: Đông người vào cuối tuần và lễ tết, không có chỗ đỗ xe gần, thời tiết nóng mùa hè. Phù hợp: Cặp đôi hẹn hò, gia đình có con nhỏ, du khách lần đầu đến Hà Nội.",
  "embedding": [0.345, 0.678, ...],
  "metadata": {
    "sentiment": "positive",
    "review_period": "2023-2024",
    "review_count": 1250
  }
}
```

**4. Activity & Nearby Info**
```json
{
  "id": "HN-0001-activity",
  "place_id": "HN-0001",
  "chunk_type": "activity",
  "language": "vi",
  "content": "Hoạt động gần hồ: Dạo bộ quanh hồ (30-45 phút), chụp ảnh tại cầu Thê Húc, tham quan đền Ngọc Sơn (vé 30k), uống cafe tại các quán view hồ (50-150k), mua sắm tại chợ đêm cuối tuần, xem biểu diễn nghệ thuật đường phố. Địa điểm ăn uống gần: Phở Thìn Bờ Hồ, cafe Đinh, quán kem Tràng Tiền.",
  "embedding": [0.901, 0.234, ...],
  "metadata": {
    "activity_types": ["walking", "dining", "shopping", "photography"]
  }
}
```

**5. Historical & Cultural Context**
```json
{
  "id": "HN-0001-history",
  "place_id": "HN-0001",
  "chunk_type": "history",
  "language": "vi",
  "content": "Hồ Hoàn Kiếm có lịch sử hơn 1000 năm. Tên gọi xuất phát từ truyền thuyết vua Lê Lợi hoàn trả thanh gươm thần cho Rùa thần sau khi đánh thắng quân Minh. Trước đây hồ còn gọi là Lục Thủy (nước xanh) hoặc Hồ Thủy Quân. Đền Ngọc Sơn trên hồ được xây dựng từ thế kỷ 18, thờ Trần Hưng Đạo và Văn Xương.",
  "embedding": [0.567, 0.890, ...],
  "metadata": {
    "historical_period": "ancient",
    "cultural_significance": "high"
  }
}
```

#### Metadata cho Filtering:
```python
{
  "place_id": "HN-0001",
  "place_name": "Hoàn Kiếm Lake",
  "categories": ["scenic", "lake", "cultural"],
  "rating": 4.7,
  "price_level": 1,
  "chunk_type": "description|tip|review|activity|history",
  "language": "vi|en",
  "author_type": "expert|user|system",
  "sentiment": "positive|neutral|negative",
  "created_at": "2024-01-15"
}
```

#### Index Configuration (Pinecone example):
```python
index = pinecone.Index(
    name="hanoi-places",
    dimension=1536,  # OpenAI ada-002
    metric="cosine",
    metadata_config={
        "indexed": [
            "place_id",
            "categories",
            "rating",
            "price_level",
            "chunk_type",
            "language"
        ]
    }
)
```

#### Sample Search Query:
```python
# Query: "Tìm địa điểm lãng mạn, view đẹp, phù hợp hẹn hò"
query_embedding = embed("lãng mạn view đẹp hẹn hò yên tĩnh")

results = index.query(
    vector=query_embedding,
    filter={
        "place_id": {"$in": kg_filtered_ids},  # From KG step
        "chunk_type": {"$in": ["description", "tip", "review"]},
        "language": "vi"
    },
    top_k=10,
    include_metadata=True
)
```

---

### 3.3 CACHE / REDIS
**Mục đích:** Lưu dữ liệu động, thay đổi thường xuyên

#### Key Structure & TTL:
```
place:{place_id}:reviews:latest        TTL: 1 hour
place:{place_id}:events:active         TTL: 6 hours
place:{place_id}:weather:current       TTL: 30 minutes
place:{place_id}:social:trending       TTL: 2 hours
place:{place_id}:pricing:current       TTL: 1 day
place:{place_id}:crowd:realtime        TTL: 15 minutes
district:{district_code}:trending      TTL: 4 hours
category:{category}:hot:daily          TTL: 12 hours
```

#### Data Structures:

**1. Recent Reviews**
```json
// Key: place:HN-0001:reviews:latest
{
  "place_id": "HN-0001",
  "reviews": [
    {
      "id": "rev-001",
      "user": "nguyen_van_a",
      "rating": 5,
      "text": "View đẹp quá, đi lúc hoàng hôn rất lãng mạn!",
      "date": "2025-11-24",
      "source": "google",
      "helpful_count": 12
    },
    {
      "id": "rev-002",
      "user": "tran_thi_b",
      "rating": 4,
      "text": "Đẹp nhưng hơi đông người vào cuối tuần",
      "date": "2025-11-23",
      "source": "facebook",
      "helpful_count": 8
    }
  ],
  "last_updated": "2025-11-25T10:30:00Z"
}
```

**2. Active Events**
```json
// Key: place:HN-0001:events:active
{
  "place_id": "HN-0001",
  "events": [
    {
      "id": "evt-001",
      "name": "Hội hoa xuân Hồ Gươm",
      "type": "festival",
      "start_date": "2025-01-25",
      "end_date": "2025-02-10",
      "description": "Triển lãm hoa xuân và đèn lồng",
      "hours": "08:00-22:00",
      "price": "free"
    }
  ]
}
```

**3. Weather Data**
```json
// Key: place:HN-0001:weather:current
{
  "place_id": "HN-0001",
  "location": "Hoàn Kiếm, Hà Nội",
  "temperature": 22,
  "condition": "sunny",
  "humidity": 65,
  "wind_speed": 10,
  "good_for_visit": true,
  "recommendation": "Thời tiết đẹp, phù hợp dạo bộ",
  "timestamp": "2025-11-25T11:00:00Z"
}
```

**4. Social Media Trending**
```json
// Key: place:HN-0001:social:trending
{
  "place_id": "HN-0001",
  "instagram_mentions": 1250,
  "facebook_checkins": 890,
  "tiktok_views": 45000,
  "trending_score": 8.5,
  "trending_hashtags": ["#hoankiem", "#hanoi", "#vietnam"],
  "last_updated": "2025-11-25T10:00:00Z"
}
```

**5. Real-time Pricing**
```json
// Key: place:HN-0003:pricing:current
{
  "place_id": "HN-0003",
  "place_name": "Temple of Literature",
  "pricing": {
    "adult": 30000,
    "student": 15000,
    "child": 0,
    "currency": "VND"
  },
  "promotions": [
    {
      "description": "Miễn phí cho người trên 60 tuổi",
      "valid_until": "2025-12-31"
    }
  ]
}
```

**6. Real-time Crowd Level**
```json
// Key: place:HN-0001:crowd:realtime
{
  "place_id": "HN-0001",
  "crowd_level": "medium",
  "crowd_percentage": 60,
  "wait_time_minutes": 0,
  "best_time_to_visit": "06:00-08:00 or 18:00-20:00",
  "timestamp": "2025-11-25T11:15:00Z"
}
```

#### Redis Commands Example:
```redis
# Set with TTL
SETEX place:HN-0001:reviews:latest 3600 '{"reviews": [...]}'

# Get data
GET place:HN-0001:weather:current

# Check if exists
EXISTS place:HN-0001:events:active

# Get multiple keys
MGET place:HN-0001:reviews:latest place:HN-0001:weather:current

# Delete cache
DEL place:HN-0001:*
```

---

### 3.4 SQL DATABASE (PostgreSQL)
**Mục đích:** User data, session, preferences, history

#### Schema:

**1. Users Table**
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    preferences JSONB,  -- {travel_style, interests, budget}
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Sample preferences:
{
  "travel_style": "leisure",
  "interests": ["food", "culture", "photography"],
  "budget_level": 2,
  "accessibility_needs": ["wheelchair"],
  "language": "vi",
  "avoid_categories": ["nightlife"]
}
```

**2. Sessions Table**
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    context JSONB,  -- Current conversation context
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_created (created_at)
);

-- Sample context:
{
  "current_query": "Tìm quán cafe lãng mạn",
  "current_location": {"lat": 21.0285, "lon": 105.8542},
  "conversation_history": [...],
  "selected_places": ["HN-0001", "HN-0007"],
  "itinerary_draft": {...}
}
```

**3. User History Table**
```sql
CREATE TABLE user_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    place_id VARCHAR(50),
    action_type VARCHAR(20),  -- viewed, visited, favorited, rated
    rating DECIMAL(2,1),
    notes TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_place (user_id, place_id),
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_action_type (action_type)
);
```

**4. User Preferences (Detailed)**
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    preference_key VARCHAR(100),
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, preference_key),
    INDEX idx_user_pref (user_id, preference_key)
);

-- Examples:
-- (user_123, 'favorite_cuisine', 'vietnamese')
-- (user_123, 'avoid_spicy', 'true')
-- (user_123, 'preferred_price_range', '1-2')
```

**5. Favorites/Bookmarks Table**
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    place_id VARCHAR(50),
    list_name VARCHAR(100),  -- 'want_to_go', 'favorites', 'visited'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, place_id, list_name),
    INDEX idx_user_list (user_id, list_name)
);
```

**6. Itineraries Table**
```sql
CREATE TABLE itineraries (
    itinerary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    title VARCHAR(255),
    description TEXT,
    date DATE,
    places JSONB,  -- [{place_id, order, time_slot, notes}, ...]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_itinerary (user_id, date)
);
```

#### Sample Queries:
```sql
-- Get user preferences
SELECT preferences FROM users WHERE user_id = 'user-123';

-- Get user visit history
SELECT place_id, action_type, timestamp 
FROM user_history 
WHERE user_id = 'user-123' 
ORDER BY timestamp DESC 
LIMIT 20;

-- Get favorite places
SELECT place_id, notes 
FROM favorites 
WHERE user_id = 'user-123' AND list_name = 'favorites';

-- User similarity (for collaborative filtering)
SELECT u2.user_id, COUNT(*) as common_places
FROM user_history u1
JOIN user_history u2 ON u1.place_id = u2.place_id
WHERE u1.user_id = 'user-123' 
  AND u2.user_id != 'user-123'
  AND u1.action_type IN ('visited', 'favorited')
GROUP BY u2.user_id
ORDER BY common_places DESC
LIMIT 10;
```

---

## 4. QUERY FLOW EXAMPLES

### Example 1: Simple Search
**Query:** "Tìm quán cafe gần Hồ Tây, view đẹp"

**Step 1 - Intent Recognition:**
```
Intent: search_place
Entities: 
  - location: "Hồ Tây" (lat: 21.0586, lon: 105.821)
  - category: "cafe"
  - preferences: "view đẹp"
```

**Step 2 - Knowledge Graph Filter:**
```cypher
MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category {name: 'cafe'})
WHERE distance(p.location, point({latitude: 21.0586, longitude: 105.821})) < 2000
AND p.rating >= 4.0
RETURN p.place_id, p.name, p.rating
LIMIT 30
```
→ Result: 30 cafes

**Step 3 - Vector Search:**
```python
query_embedding = embed("cafe view đẹp không gian thoáng mát")
vector_results = vector_db.search(
    vector=query_embedding,
    filter={"place_id": {"$in": kg_results}},
    top_k=5
)
```
→ Result: Top 5 cafes with best semantic match

**Step 4 - Fetch Dynamic Data:**
```python
for place_id in top_5:
    reviews = redis.get(f"place:{place_id}:reviews:latest")
    weather = redis.get(f"place:{place_id}:weather:current")
```

**Step 5 - Generate Response:**
```
Dựa trên tìm kiếm của bạn, đây là 5 quán cafe có view đẹp gần Hồ Tây:

1. **The Hanoi Social Club** ⭐4.8
   - View: Vườn xanh mát, không gian yên tĩnh
   - Giá: $$
   - Review gần đây: "View đẹp, thức ăn ngon, phù hợp làm việc"
   
2. **Cong Caphe** ⭐4.6
   ...
```

### Example 2: Itinerary Planning
**Query:** "Lập lịch trình 1 ngày Old Quarter cho gia đình có trẻ em"

**Step 1 - Intent Recognition:**
```
Intent: plan_itinerary
Entities:
  - location: "Old Quarter"
  - duration: "1 day"
  - companions: "family with children"
```

**Step 2 - KG Multi-step Query:**
```cypher
// Find family-friendly places in Old Quarter
MATCH (p:Place)-[:IN_DISTRICT]->(d:District {code: 'HK'})
WHERE 'family' IN p.suitable_for
AND 'children' IN p.accessibility
AND p.rating >= 4.0
RETURN p
ORDER BY p.popularityScore DESC
```

**Step 3 - Vector Search for Context:**
```python
# Search for activity descriptions suitable for families
query = "hoạt động vui chơi cho gia đình có trẻ em an toàn thú vị"
semantic_results = vector_db.search(query, filters)
```

**Step 4 - Agent Reasoning:**
```
1. Filter places by opening hours
2. Calculate travel time between locations
3. Consider meal times (breakfast, lunch, dinner)
4. Add rest periods for children
5. Optimize route to minimize walking
```

**Step 5 - Generate Itinerary:**
```
📅 Lịch trình 1 ngày Old Quarter cho gia đình:

🌅 Sáng (8:00 - 12:00)
├─ 8:00: Phở sáng tại Phố Cổ
├─ 9:00: Dạo phố cổ 36 phố phường
└─ 10:30: Hồ Hoàn Kiếm + đền Ngọc Sơn (vé 30k)

🌞 Trưa (12:00 - 14:00)
├─ 12:00: Bún chả Hàng Quạt
└─ 13:30: Nghỉ ngơi tại cafe view hồ

🌆 Chiều (14:00 - 18:00)
├─ 14:00: Nhà hát múa rối nước Thăng Long
├─ 16:00: Chợ Đồng Xuân (mua quà)
└─ 17:30: Kem Tràng Tiền

💡 Lưu ý: Thời tiết hôm nay nắng đẹp (22°C), phù hợp dạo phố
```

---

## 5. DATA COLLECTION PIPELINE

### 5.1 Static Data Sources
```
1. Google Maps API
   - Basic info, coordinates, reviews
   - Rating, price level, opening hours
   
2. Manual curation
   - Expert descriptions
   - Cultural/historical context
   - Local tips
   
3. Official tourism sites
   - Vietnam Tourism
   - Hanoi Tourism
   
4. Social media scraping (với permission)
   - Instagram hashtags
   - Facebook check-ins
   - TikTok trends
```

### 5.2 Dynamic Data Sources
```
1. Weather API (OpenWeatherMap)
   - Real-time weather
   - Forecast

2. Google Places API
   - Recent reviews
   - Popular times
   - Current crowd level

3. Social media APIs
   - Instagram Graph API
   - Facebook Graph API
   - Twitter API

4. Event platforms
   - Facebook Events
   - Local event websites
```

### 5.3 Update Frequency
```
Static data (KG + Vector):  Monthly or on-demand
Reviews cache:              1 hour
Weather:                    30 minutes
Events:                     6 hours
Social trending:            2 hours
Crowd level:                15 minutes
```

---

## 6. TECH STACK RECOMMENDATION

### 6.1 Core Components
```
Knowledge Graph:     Neo4j 5.x
Vector Database:     Pinecone / Qdrant / Weaviate
Cache:               Redis 7.x
SQL Database:        PostgreSQL 15+
Message Queue:       RabbitMQ / Kafka
```

### 6.2 Backend
```
API Server:          FastAPI / Node.js
Agent Framework:     LangChain / LlamaIndex
LLM:                 GPT-4 / Claude-3.5 / Gemini
Embeddings:          OpenAI ada-002 / Cohere
Task Queue:          Celery
```

### 6.3 Frontend
```
Web:                 React / Next.js
Mobile:              React Native / Flutter
Maps:                Mapbox / Google Maps
```

### 6.4 Infrastructure
```
Container:           Docker + Kubernetes
Cloud:               AWS / GCP
Monitoring:          Grafana + Prometheus
Logging:             ELK Stack
```

---

## 7. API ARCHITECTURE

### 7.1 Main Endpoints

```python
# Search
POST /api/v1/search
{
  "query": "tìm quán cafe lãng mạn gần hồ tây",
  "user_location": {"lat": 21.0586, "lon": 105.821},
  "filters": {
    "categories": ["cafe"],
    "price_level": [1, 2],
    "rating_min": 4.0
  }
}

# Place detail
GET /api/v1/places/{place_id}
GET /api/v1/places/{place_id}/dynamic  # Real-time data

# Itinerary planning
POST /api/v1/itinerary/generate
{
  "location": "Old Quarter",
  "duration_hours": 8,
  "companions": "family_with_children",
  "interests": ["culture", "food"]
}

# Recommendations
POST /api/v1/recommend
{
  "user_id": "user-123",
  "current_location": {"lat": 21.0285, "lon": 105.8542},
  "context": "đang ở hồ hoàn kiếm, muốn tìm nơi ăn trưa"
}

# Multi-turn conversation
POST /api/v1/chat
{
  "session_id": "session-456",
  "message": "còn địa điểm nào gần đó không?"
}
```

---

## 8. SCALING CONSIDERATIONS

### 8.1 Performance Targets
```
Search latency:          < 500ms (p95)
KG query:                < 100ms
Vector search:           < 200ms
Cache hit rate:          > 80%
API availability:        99.9%
```

### 8.2 Data Volume Estimates
```
Places (Hanoi):          ~50,000
Places (Vietnam):        ~500,000
Vector chunks:           ~2,000,000 (avg 4 chunks/place)
Daily API calls:         ~1,000,000
Daily cache updates:     ~100,000
```

### 8.3 Caching Strategy
```
L1: Application cache (in-memory)     - 1 min
L2: Redis cache                       - 1-6 hours
L3: CDN cache (static assets)         - 1 day
```

---

## 9. FUTURE ENHANCEMENTS

### 9.1 Phase 2 Features
- Multi-language support (EN, KR, CN, JP)
- Voice search & commands
- AR navigation
- Real-time collaborative planning
- Social features (share itineraries)

### 9.2 Phase 3 Features
- Predictive recommendations
- Dynamic pricing optimization
- Integration with booking platforms
- Gamification (badges, achievements)
- Community contributions

---

## 10. MONITORING & METRICS

### 10.1 Key Metrics
```
User metrics:
- Daily/Monthly Active Users
- Search success rate
- Average session duration
- Itinerary completion rate

System metrics:
- API latency (p50, p95, p99)
- Database query time
- Cache hit rate
- Error rate

Business metrics:
- Popular searches
- Top recommended places
- User satisfaction score
- Conversion rate (if booking integrated)
```

### 10.2 A/B Testing
```
- Recommendation algorithms
- UI/UX variations
- Prompt engineering for LLM
- Ranking weights (popularity vs rating vs distance)
```

---

## 11. CONCLUSION

Hệ thống này kết hợp sức mạnh của:
- **Knowledge Graph** cho structural filtering nhanh
- **Vector DB** cho semantic understanding
- **Redis Cache** cho real-time dynamic data
- **PostgreSQL** cho user personalization

Pipeline xử lý từ query → filter → search → enrich → reason → respond tạo ra trải nghiệm recommendation thông minh, chính xác và cá nhân hóa.

Kiến trúc modular cho phép scale từng component độc lập và dễ dàng mở rộng từ Hà Nội ra toàn Việt Nam.