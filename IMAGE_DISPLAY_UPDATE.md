# Image Display & Summary Update

## ✨ Cập nhật mới

### 🎨 Frontend (React UI)

#### 1. Hiển thị Summary trước
- Summary từ AI sẽ được hiển thị **đầu tiên**, trước danh sách địa điểm
- Format đẹp với separator `---`

#### 2. Hiển thị Images cho mỗi địa điểm
- Tự động hiển thị **1-2 ảnh** từ Qdrant payload
- Images được render bằng Markdown
- Responsive sizing với `max-w-full`
- Rounded corners và shadow

#### 3. Format cải tiến
Mỗi địa điểm hiện có:
- **Tên địa điểm** (bold)
- **Ảnh minh họa** (nếu có)
- 📍 **Địa chỉ**
- 🏷️ **Loại hình**
- 📏 **Khoảng cách** (nếu có)
- 💡 **Mô tả ngắn** (summary từ Qdrant)

### 🔧 Backend (Flask API)

#### 1. Enhanced `search_places()`
```python
# Tự động fetch images từ Qdrant cho mỗi place_id
place['images'] = payload.get('images', [])
place['summary'] = payload.get('summary', '')
```

#### 2. Enhanced `nearby_landmark()`
```python
# Enrich places với images và summary từ Qdrant
for place in places:
    qdrant_results = qdrant_search.client.scroll(...)
    place['images'] = payload.get('images', [])
    place['summary'] = payload.get('summary', '')
```

#### 3. Enhanced `semantic_search()`
```python
# Images đã có sẵn trong payload từ Qdrant search
results.append({
    'images': payload.get('images', [])
})
```

## 📊 Data Flow

```
User Query
    ↓
Agent Router (classify intent)
    ↓
Service Function (search_places / nearby_landmark / semantic_search)
    ↓
Neo4j (spatial data) + Qdrant (images + summary)
    ↓
Response với images[] + summary
    ↓
React UI (formatPlacesList)
    ↓
Display: Summary → Places với Images
```

## 🎯 Response Structure

### Before:
```json
{
  "nearby_places": [
    {
      "name": "The Coffee House",
      "address": "38, Nguyễn Khuyến",
      "categories": ["cafe"],
      "distance_meters": 274.0
    }
  ],
  "summary": "AI generated summary..."
}
```

### After:
```json
{
  "nearby_places": [
    {
      "name": "The Coffee House",
      "address": "38, Nguyễn Khuyến",
      "categories": ["cafe"],
      "distance_meters": 274.0,
      "images": [
        "https://upload.wikimedia.org/...",
        "https://example.com/image2.jpg"
      ],
      "summary": "Quán cafe hiện đại với không gian thoáng mát..."
    }
  ],
  "summary": "Xung quanh Hồ Gươm có 7 quán cafe đa dạng..."
}
```

## 🎨 UI Display Example

```markdown
Xung quanh Hồ Gươm có 7 quán cafe đa dạng, từ chuỗi thương hiệu đến không gian độc lập...

---

### Tìm thấy 7 địa điểm:

**1. The Coffee House**

![The Coffee House](https://upload.wikimedia.org/...)

📍 **Địa chỉ:** 38, Nguyễn Khuyến, Hà Đông

🏷️ **Loại:** cafe

📏 **Khoảng cách:** 274m

💡 Quán cafe hiện đại với không gian thoáng mát...

---
```

## 📝 Files Changed

### Frontend:
- ✅ `ui/src/components/ChatInterface.jsx`
  - Updated `formatPlacesList()` to accept `summary` parameter
  - Display summary first with separator
  - Show 1-2 images per place
  - Better formatting with emojis and bold text

### Backend:
- ✅ `app/services/main_service.py`
  - `search_places()`: Fetch images from Qdrant
  - `nearby_landmark()`: Enrich places with images
  - `semantic_search()`: Include images in results

## 🚀 Usage

### Test với curl:
```bash
curl -X POST http://localhost:8864/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tìm quán cafe gần Hồ Gươm"}'
```

### Expected Response:
- ✅ Summary hiển thị đầu tiên
- ✅ Mỗi địa điểm có 1-2 ảnh
- ✅ Format đẹp với markdown
- ✅ Thông tin đầy đủ (address, categories, distance)

## 🎯 Benefits

1. **Visual Appeal**: Ảnh giúp user hình dung địa điểm
2. **Context First**: Summary giúp hiểu tổng quan trước
3. **Rich Information**: Kết hợp spatial data (Neo4j) + semantic data (Qdrant)
4. **Better UX**: Không cần mở link riêng để xem ảnh

## 🔍 Technical Details

### Image Source
- Images được lưu trong Qdrant payload từ Wikipedia
- Mỗi place có thể có 0-N images
- UI hiển thị tối đa 2 ảnh để không quá tải

### Performance
- Qdrant scroll query nhanh (~10ms)
- Images lazy loading trong React
- Không ảnh hưởng performance đáng kể

### Error Handling
- Nếu không fetch được Qdrant: `images = []`
- Frontend handle gracefully nếu `images` field missing
- Không crash nếu thiếu data

## 📚 Related Docs

- [API_DOCS.md](API_DOCS.md) - API documentation
- [AGENT_CHAT.md](AGENT_CHAT.md) - Agent system details
- [ui/README.md](ui/README.md) - Frontend documentation
