# 🏗️ KIẾN TRÚC HỆ THỐNG MAP ASSISTANT

## Tổng quan Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / CLIENT                            │
│                    (Web App / Mobile App)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK API SERVER                            │
│                     (Port 8864)                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              ROUTES LAYER                                 │   │
│  │  /health  /place_info  /search_places  /nearby_landmark  │   │
│  │  /semantic_search  /compare_places  /plan_itinerary      │   │
│  │  /recommend_places                                        │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │              SERVICES LAYER                               │   │
│  │  (main_service.py)                                        │   │
│  │                                                            │   │
│  │  - get_info_details()       - compare_places()           │   │
│  │  - search_places()          - plan_itinerary()           │   │
│  │  - nearby_landmark()        - recommend_places()         │   │
│  │  - semantic_search()                                      │   │
│  └────────┬──────────────┬──────────────┬────────────────────┘   │
└───────────┼──────────────┼──────────────┼─────────────────────────┘
            │              │              │
            │              │              │
    ┌───────▼────┐  ┌──────▼──────┐  ┌───▼────────┐
    │            │  │             │  │            │
    │   NEO4J    │  │   QDRANT    │  │ AI SERVICE │
    │   Graph    │  │   Vector    │  │ GPT/Claude │
    │     DB     │  │     DB      │  │            │
    │            │  │             │  │            │
    └────────────┘  └─────────────┘  └────────────┘
         │                 │               │
         │                 │               │
    Port 7687         Port 6333      OpenAI API
```

---

## Chi tiết từng Layer

### 1️⃣ **CLIENT LAYER**
```
┌──────────────────────────────┐
│     Web Browser / Mobile     │
│   - React / Next.js          │
│   - Flutter / React Native   │
│   - Simple HTML/JS           │
└──────────────────────────────┘
```

**Responsibilities:**
- Send HTTP requests
- Display results
- Handle user interactions

---

### 2️⃣ **API ROUTES LAYER**

```python
app/routes/main_routes.py

┌─────────────────────────────────────┐
│  API Endpoints                      │
├─────────────────────────────────────┤
│  GET  /health                       │
│  POST /place_info                   │
│  POST /search_places                │
│  POST /nearby_landmark              │
│  POST /semantic_search              │
│  POST /compare_places               │
│  POST /plan_itinerary               │
│  POST /recommend_places             │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Route requests to services
- Validate input data
- Format responses
- Error handling

---

### 3️⃣ **SERVICES LAYER**

```python
app/services/main_service.py

┌──────────────────────────────────────────────┐
│  Business Logic Services                     │
├──────────────────────────────────────────────┤
│                                              │
│  📍 search_places()                          │
│     ├─► Neo4j spatial query                 │
│     ├─► Filter by category                  │
│     └─► AI summary                          │
│                                              │
│  🏛️ nearby_landmark()                        │
│     ├─► Find landmark in Neo4j              │
│     ├─► Spatial search around it            │
│     └─► AI description                      │
│                                              │
│  🧠 semantic_search()                        │
│     ├─► Qdrant vector search                │
│     ├─► Neo4j filtering (optional)          │
│     └─► AI recommendation                   │
│                                              │
│  ⚖️ compare_places()                         │
│     ├─► Fetch from Qdrant                   │
│     └─► AI comparison analysis              │
│                                              │
│  📅 plan_itinerary()                         │
│     ├─► Neo4j multi-category search         │
│     └─► AI agent reasoning + planning       │
│                                              │
│  💡 recommend_places()                       │
│     ├─► Spatial + Semantic search           │
│     └─► AI personalized suggestions         │
│                                              │
└──────────────────────────────────────────────┘
```

**Responsibilities:**
- Implement business logic
- Orchestrate database calls
- Call AI services
- Data transformation

---

### 4️⃣ **DATABASE LAYER**

#### A. NEO4J (Graph Database)

```
app/database/neo4j/main.py

┌─────────────────────────────────────┐
│      Neo4j Spatial Queries          │
├─────────────────────────────────────┤
│                                     │
│  Nodes:                             │
│  - Place (with location point)      │
│  - Category                         │
│  - District, Province               │
│  - Tag                              │
│                                     │
│  Relationships:                     │
│  - (Place)-[:HAS_CATEGORY]->()      │
│  - (Place)-[:LOCATED_IN]->()        │
│  - (Place)-[:HAS_TAG]->()           │
│                                     │
│  Key Functions:                     │
│  - find_places_by_category()        │
│  - find_places_nearby_landmark()    │
│  - find_places_in_district()        │
│  - find_places_by_multiple_categories() │
│                                     │
└─────────────────────────────────────┘

Data Model:
(Place {
  place_id, name, address,
  location: point{lat, lon},
  rating, price_level
}) -[:HAS_CATEGORY]-> (Category {name})
```

**Strengths:**
- Fast spatial queries (point.distance)
- Graph relationships
- Complex filtering
- Metadata storage

---

#### B. QDRANT (Vector Database)

```
app/database/qdrant/main.py

┌─────────────────────────────────────┐
│    Qdrant Semantic Search           │
├─────────────────────────────────────┤
│                                     │
│  Collection: map_assistant_v2       │
│                                     │
│  Vector: 768-dim embeddings         │
│  (from PhoBERT / Sentence-BERT)     │
│                                     │
│  Payload:                           │
│  - place_id                         │
│  - name                             │
│  - summary (text)                   │
│  - text (full description)          │
│                                     │
│  Key Functions:                     │
│  - search_place_details()           │
│  - _get_embedding()                 │
│                                     │
└─────────────────────────────────────┘

Query Flow:
Text → Embedding Service → Vector
     → Qdrant.search() → Top-K results
```

**Strengths:**
- Semantic understanding
- Natural language queries
- Similar places discovery
- Content-based search

---

#### C. AI SERVICE (LLM)

```
app/models/model.py

┌─────────────────────────────────────┐
│      AI Service Integration         │
├─────────────────────────────────────┤
│                                     │
│  Provider: OpenAI / Anthropic       │
│  Model: GPT-4 / Claude-3.5          │
│                                     │
│  Function:                          │
│  - generate_response()              │
│    ├─► Takes user query             │
│    ├─► Takes data context           │
│    └─► Returns natural language     │
│                                     │
│  Use Cases:                         │
│  - Summarize search results         │
│  - Generate comparisons             │
│  - Plan itineraries                 │
│  - Explain recommendations          │
│  - Answer questions                 │
│                                     │
└─────────────────────────────────────┘

Prompt Template:
System: "You are a helpful Travel assistant"
User: "{user_message}"
Data: "{data_extend}"
Output: Natural Vietnamese text
```

**Strengths:**
- Natural language generation
- Context understanding
- Reasoning & planning
- Personalization

---

### 5️⃣ **EMBEDDING SERVICE**

```
serve/embed_service.py

┌─────────────────────────────────────┐
│    Text Embedding Service           │
├─────────────────────────────────────┤
│                                     │
│  Model: PhoBERT / Sentence-BERT     │
│  Dimension: 768                     │
│                                     │
│  Endpoint:                          │
│  POST /embed                        │
│  Body: {"texts": ["..."]}           │
│  Returns: {"embeddings": [...]}     │
│                                     │
│  Port: 8080                         │
│                                     │
└─────────────────────────────────────┘
```

---

## Data Flow Examples

### Example 1: Simple Search

```
1. User: "Tìm quán cafe gần Hồ Gươm"
        ↓
2. API: POST /search_places
   {lat: 21.0285, lon: 105.8542, categories: ["cafe"]}
        ↓
3. Service: search_places()
        ↓
4. Neo4j: Spatial query
   MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category {name: 'cafe'})
   WHERE distance(p.location, point(...)) < 2000
        ↓
5. Results: 15 cafes found
        ↓
6. AI Service: Generate summary
   "Tìm thấy 15 quán cafe trong bán kính 2km..."
        ↓
7. Response to user
```

---

### Example 2: Semantic Search

```
1. User: "Quán cafe lãng mạn view đẹp"
        ↓
2. API: POST /semantic_search
   {query: "quán cafe lãng mạn view đẹp"}
        ↓
3. Service: semantic_search()
        ↓
4. Embedding Service: 
   Text → 768-dim vector
        ↓
5. Qdrant: Vector similarity search
   Find top 10 most similar places
        ↓
6. Results: Scored by similarity (0.85, 0.82, ...)
        ↓
7. AI Service: Generate recommendation
   "Dựa trên yêu cầu của bạn, đây là các địa điểm phù hợp..."
        ↓
8. Response to user
```

---

### Example 3: Itinerary Planning

```
1. User: "Lập lịch 8 giờ Old Quarter"
        ↓
2. API: POST /plan_itinerary
   {location: "Old Quarter", duration_hours: 8}
        ↓
3. Service: plan_itinerary()
        ↓
4. Neo4j: Find multiple categories
   - Restaurants: 5 places
   - Museums: 3 places
   - Shopping: 4 places
        ↓
5. AI Service: Agent reasoning
   - Consider time slots (morning, lunch, afternoon)
   - Optimize travel distance
   - Balance activity types
        ↓
6. AI generates detailed itinerary:
   09:00 - Breakfast at X
   10:00 - Visit Museum Y
   12:00 - Lunch at Z
   ...
        ↓
7. Response to user
```

---

## Technology Stack Summary

| Layer | Technology | Port | Purpose |
|-------|-----------|------|---------|
| API | Flask | 8864 | REST API Server |
| Graph DB | Neo4j | 7687 | Spatial queries, relationships |
| Vector DB | Qdrant | 6333 | Semantic search |
| AI | OpenAI/Claude | - | Natural language generation |
| Embedding | Custom Service | 8080 | Text → Vector |
| Language | Python 3.x | - | Backend |

---

## Scaling Considerations

```
Current (Single Server):
┌────────────────────┐
│   All-in-one       │
│   Flask + DBs      │
└────────────────────┘

Future (Microservices):
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ API    │  │ Neo4j  │  │ Qdrant │  │   AI   │
│ Gateway│  │Service │  │Service │  │Service │
└────────┘  └────────┘  └────────┘  └────────┘
    │            │            │            │
    └────────────┴────────────┴────────────┘
              Load Balancer
```

---

## Security & Best Practices

✅ **Implemented:**
- Environment variables for credentials
- Input validation
- Error handling
- Modular architecture

🔜 **To Implement:**
- Rate limiting
- Authentication (JWT)
- API keys
- Request logging
- HTTPS/SSL

---

**Xem thêm:**
- [README.md](README.md) - Overview
- [API_DOCS.md](API_DOCS.md) - API Documentation
- [Idea.md](Idea.md) - System Design Details
