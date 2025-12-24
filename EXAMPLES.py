"""
📚 HƯỚNG DẪN SỬ DỤNG MAP ASSISTANT
Examples & Use Cases cho các tính năng mới
"""

# =============================================================================
# 1. TÌM KIẾM ĐỊA ĐIỂM THEO CATEGORY & LOCATION
# =============================================================================

# Use Case: "Tìm nhà hàng và cafe trong bán kính 2km quanh Hồ Gươm"
search_places_example = {
    "endpoint": "POST /api/v1/search_places",
    "body": {
        "lat": 21.0285,
        "lon": 105.8542,
        "categories": ["restaurant", "cafe"],
        "radius_meters": 2000,
        "limit": 20
    },
    "description": "Tìm địa điểm theo loại hình xung quanh tọa độ",
    "response": {
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
        "summary": "AI summary về các địa điểm..."
    }
}


# =============================================================================
# 2. TÌM ĐỊA ĐIỂM GẦN LANDMARK
# =============================================================================

# Use Case: "Tìm khách sạn gần Văn Miếu"
nearby_landmark_example = {
    "endpoint": "POST /api/v1/nearby_landmark",
    "body": {
        "landmark_name": "Văn Miếu",
        "categories": ["hotel", "accommodation"],
        "radius_meters": 1500,
        "limit": 10
    },
    "description": "Tìm địa điểm xung quanh một landmark nổi tiếng",
    "response": {
        "landmark": {
            "name": "Văn Miếu - Quốc Tử Giám",
            "address": "58 Quốc Tử Giám, Đống Đa"
        },
        "total": 8,
        "nearby_places": [...],
        "summary": "AI summary..."
    }
}


# =============================================================================
# 3. SEMANTIC SEARCH - TÌM KIẾM NGỮ NGHĨA
# =============================================================================

# Use Case: "Tìm quán cafe yên tĩnh, view đẹp, phù hợp làm việc"
semantic_search_example = {
    "endpoint": "POST /api/v1/semantic_search",
    "body": {
        "query": "quán cafe yên tĩnh view đẹp phù hợp làm việc có wifi tốt",
        "top_k": 10
    },
    "description": "Tìm kiếm bằng ngôn ngữ tự nhiên, AI hiểu ngữ nghĩa",
    "response": {
        "total": 8,
        "query": "quán cafe yên tĩnh view đẹp...",
        "places": [
            {
                "place_id": "HN-0025",
                "name": "The Hanoi Social Club",
                "score": 0.89,
                "summary": "..."
            }
        ],
        "recommendation": "AI recommendation..."
    }
}

# Các query tự nhiên khác:
semantic_queries = [
    "nhà hàng lãng mạn cho buổi hẹn hò đầu tiên",
    "địa điểm chụp ảnh đẹp cho couple",
    "quán ăn bình dân giá rẻ cho sinh viên",
    "chùa thanh tịnh phù hợp cầu an",
    "quán bar sôi động cuối tuần",
    "museum phù hợp cho trẻ em học lịch sử",
    "công viên yên tĩnh cho người cao tuổi tập thể dục"
]


# =============================================================================
# 4. SO SÁNH NHIỀU ĐỊA ĐIỂM
# =============================================================================

# Use Case: "So sánh 3 di tích lịch sử: Lăng Bác, Văn Miếu, Hoàng Thành"
compare_places_example = {
    "endpoint": "POST /api/v1/compare_places",
    "body": {
        "place_names": [
            "Lăng Bác",
            "Văn Miếu",
            "Hoàng Thành Thăng Long"
        ]
    },
    "description": "So sánh chi tiết ưu/nhược điểm của nhiều địa điểm",
    "response": {
        "places": ["Lăng Bác", "Văn Miếu", "Hoàng Thành Thăng Long"],
        "comparison": """
        AI phân tích chi tiết:
        - Điểm mạnh/yếu của từng địa điểm
        - Phù hợp cho đối tượng nào
        - Thời gian tham quan
        - Giá vé
        - Khuyến nghị nên chọn địa điểm nào
        """,
        "details": [...]
    }
}

# Use cases khác:
compare_use_cases = [
    ["Hồ Gươm", "Hồ Tây"],  # So sánh 2 hồ
    ["Phở Gia Truyền", "Phở Thìn", "Phở Bát Đàn"],  # So sánh 3 quán phở
    ["Night Market", "Dong Xuan Market"],  # So sánh chợ
]


# =============================================================================
# 5. LẬP LỊCH TRÌNH THAM QUAN
# =============================================================================

# Use Case: "Lập lịch 1 ngày tham quan Old Quarter cho gia đình"
plan_itinerary_example = {
    "endpoint": "POST /api/v1/plan_itinerary",
    "body": {
        "location": "Old Quarter Hanoi",
        "duration_hours": 8,
        "preferences": {
            "lat": 21.0285,
            "lon": 105.8542,
            "companions": "family",
            "interests": ["culture", "food", "shopping"]
        },
        "start_time": "09:00"
    },
    "description": "AI tự động lập lịch trình tối ưu",
    "response": {
        "location": "Old Quarter Hanoi",
        "duration_hours": 8,
        "itinerary": """
        📅 LỊCH TRÌNH CHI TIẾT 8 GIỜ OLD QUARTER
        
        🌅 SÁNG (09:00 - 12:00)
        ├─ 09:00: Phở sáng tại Phở Gia Truyền
        ├─ 10:00: Dạo Hồ Hoàn Kiếm
        └─ 11:00: Tham quan Đền Ngọc Sơn (vé 30k)
        
        🌞 TRƯA (12:00 - 14:00)
        ├─ 12:00: Bún chả Hàng Quạt
        └─ 13:30: Nghỉ tại cafe view hồ
        
        🌆 CHIỀU (14:00 - 17:00)
        ├─ 14:00: Nhà hát múa rối nước
        ├─ 15:30: Chợ Đồng Xuân
        └─ 16:30: Kem Tràng Tiền
        
        💡 Lưu ý: Tránh giờ cao điểm, mang nước...
        """
    }
}

# Các scenarios khác:
itinerary_scenarios = [
    {
        "name": "Romantic Date",
        "companions": "couple",
        "duration": 6,
        "interests": ["romantic", "food", "view"]
    },
    {
        "name": "Solo Backpacker",
        "companions": "solo",
        "duration": 10,
        "interests": ["culture", "street_food", "photography"]
    },
    {
        "name": "Business Trip",
        "companions": "business",
        "duration": 4,
        "interests": ["cafe", "coworking", "restaurant"]
    }
]


# =============================================================================
# 6. GỢI Ý CÁ NHÂN HÓA
# =============================================================================

# Use Case: "Gợi ý địa điểm cho gia đình có con nhỏ, ngân sách vừa"
recommend_places_example = {
    "endpoint": "POST /api/v1/recommend_places",
    "body": {
        "user_preferences": {
            "budget": 2,  # 1-4: $ đến $$$$
            "interests": ["food", "culture", "park"],
            "companions": "family",
            "avoid": ["nightlife", "bar"]
        },
        "current_location": {
            "lat": 21.0285,
            "lon": 105.8542
        },
        "limit": 10
    },
    "description": "AI gợi ý địa điểm phù hợp với sở thích",
    "response": {
        "user_preferences": {...},
        "total_recommendations": 8,
        "places": [...],
        "recommendation": """
        Dựa trên sở thích của bạn:
        1. Vườn Bách Thảo - Yên tĩnh, rộng rãi, an toàn cho trẻ
        2. Bảo tàng Dân tộc học - Học hỏi, giá vừa phải
        3. Nhà hàng Koto - Thân thiện với trẻ em
        ...
        """
    }
}

# Các personas khác:
user_personas = [
    {
        "name": "Budget Traveler",
        "preferences": {
            "budget": 1,
            "interests": ["street_food", "free_attractions"],
            "companions": "solo"
        }
    },
    {
        "name": "Luxury Tourist",
        "preferences": {
            "budget": 4,
            "interests": ["fine_dining", "spa", "luxury_hotel"],
            "companions": "couple"
        }
    },
    {
        "name": "Culture Enthusiast",
        "preferences": {
            "budget": 2,
            "interests": ["museum", "temple", "historical"],
            "companions": "group"
        }
    },
    {
        "name": "Food Lover",
        "preferences": {
            "budget": 3,
            "interests": ["restaurant", "street_food", "market"],
            "companions": "friends"
        }
    }
]


# =============================================================================
# 7. WORKFLOW THỰC TẾ - COMBINED USE CASES
# =============================================================================

# Workflow 1: Planning a Day Trip
workflow_day_trip = """
Bước 1: Semantic search để tìm khu vực phù hợp
POST /api/v1/semantic_search
Body: {"query": "khu vực phù hợp cho gia đình có trẻ em"}

Bước 2: Search các địa điểm cụ thể trong khu vực
POST /api/v1/search_places  
Body: {"lat": 21.0285, "lon": 105.8542, "categories": ["restaurant", "park", "museum"]}

Bước 3: So sánh một vài địa điểm
POST /api/v1/compare_places
Body: {"place_names": ["Bảo tàng A", "Bảo tàng B"]}

Bước 4: Lập lịch trình hoàn chỉnh
POST /api/v1/plan_itinerary
Body: {"location": "Selected Area", "duration_hours": 8, ...}
"""

# Workflow 2: Finding Perfect Restaurant
workflow_restaurant = """
Bước 1: Semantic search với mô tả chi tiết
POST /api/v1/semantic_search
Body: {"query": "nhà hàng lãng mạn view đẹp giá vừa phải"}

Bước 3: Lấy thông tin chi tiết
POST /api/v1/place_info
Body: {"name": "Selected Restaurant"}

Bước 3: Tìm địa điểm nearby để sau khi ăn
POST /api/v1/nearby_landmark
Body: {"landmark_name": "Restaurant Name", "categories": ["cafe", "bar"]}
"""

# Workflow 3: Multi-day Itinerary
workflow_multi_day = """
Day 1: Old Quarter
POST /api/v1/plan_itinerary
Body: {"location": "Old Quarter", "duration_hours": 8}

Day 2: Ba Đình District  
POST /api/v1/plan_itinerary
Body: {"location": "Ba Dinh", "duration_hours": 8}

Day 3: West Lake Area
POST /api/v1/plan_itinerary
Body: {"location": "West Lake", "duration_hours": 8}
"""


# =============================================================================
# 8. ADVANCED QUERIES
# =============================================================================

advanced_examples = {
    "filter_by_distance": {
        "query": "Tìm tất cả museum trong 3km",
        "endpoint": "/api/v1/search_places",
        "body": {
            "lat": 21.0285,
            "lon": 105.8542,
            "categories": ["museum"],
            "radius_meters": 3000
        }
    },
    
    "multi_category_search": {
        "query": "Tìm cả nhà hàng, cafe VÀ khách sạn",
        "endpoint": "/api/v1/search_places",
        "body": {
            "categories": ["restaurant", "cafe", "hotel"]
        }
    },
    
    "contextual_recommendation": {
        "query": "Gợi ý dựa trên vị trí hiện tại và sở thích",
        "endpoint": "/api/v1/recommend_places",
        "body": {
            "current_location": {"lat": 21.0285, "lon": 105.8542},
            "user_preferences": {"interests": ["food"]}
        }
    },
    
    "smart_itinerary": {
        "query": "Lịch trình tối ưu cho 6 giờ",
        "endpoint": "/api/v1/plan_itinerary",
        "body": {
            "duration_hours": 6,
            "start_time": "14:00",  # Bắt đầu chiều
            "preferences": {"interests": ["cafe", "shopping"]}
        }
    }
}


# =============================================================================
# 9. TIPS & BEST PRACTICES
# =============================================================================

best_practices = """
✅ DO'S:
1. Luôn cung cấp lat/lon chính xác cho spatial queries
2. Sử dụng semantic_search cho queries mơ hồ
3. Dùng compare_places khi phân vân giữa 2-3 options
4. Cung cấp đầy đủ preferences cho recommendation tốt hơn
5. Test với các categories khác nhau

❌ DON'TS:
1. Đừng dùng radius quá lớn (>10km) - sẽ chậm
2. Đừng compare quá nhiều địa điểm (>5) cùng lúc
3. Đừng lập itinerary quá dài (>12 giờ)
4. Đừng skip current_location khi dùng recommend_places

💡 PRO TIPS:
- Kết hợp nhiều API để có trải nghiệm tốt nhất
- Sử dụng semantic_search trước, rồi search_places để refine
- Lưu user_preferences để reuse cho recommendation
- Test với nhiều use cases khác nhau
"""


if __name__ == "__main__":
    print("📚 Xem các examples ở trên để sử dụng Map Assistant API")
    print("\n🚀 Chạy: python test_services.py để test thực tế")
    print("📖 Đọc: API_DOCS.md để xem chi tiết documentation")
