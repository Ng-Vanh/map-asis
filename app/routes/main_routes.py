from flask import request
def init_routes(app):
    @app.api_route("/health", methods=["GET"])
    def health_check():
        return "OK", 200

    @app.api_route("/chat", methods=["POST"])
    def chat_route():
        """
        🤖 Agent Chat - Xử lý message tự nhiên
        Body: {
            "message": "Tìm quán cafe gần Hồ Gươm",
            "session_id": "optional-session-id",
            "chat_history": []  # optional
        }
        """
        data = request.get_json()
        from app.services.agent_service import chat_handler
        
        message = data.get("message")
        return chat_handler(message)

    @app.api_route("/place_info", methods=["POST"])
    def place_info_route():
        """Lấy thông tin chi tiết về địa điểm"""
        data = request.get_json()
        from app.services.main_service import get_info_details
        return get_info_details(data.get("name"))
    
    @app.api_route("/search_places", methods=["POST"])
    def search_places_route():
        """
        Tìm kiếm địa điểm theo category và vị trí
        Body: {
            "lat": 21.0285, 
            "lon": 105.8542, 
            "categories": ["restaurant", "cafe"],
            "radius_meters": 2000,
            "limit": 20
        }
        """
        data = request.get_json()
        from app.services.main_service import search_places
        return search_places(
            lat=data.get("lat"),
            lon=data.get("lon"),
            categories=data.get("categories", []),
            radius_meters=data.get("radius_meters", 2000),
            limit=data.get("limit", 20)
        )
    
    @app.api_route("/nearby_landmark", methods=["POST"])
    def nearby_landmark_route():
        """
        Tìm địa điểm xung quanh landmark
        Body: {
            "landmark_name": "Hồ Gươm",
            "categories": ["restaurant", "cafe"],
            "radius_meters": 1000,
            "limit": 20
        }
        """
        data = request.get_json()
        from app.services.main_service import nearby_landmark
        return nearby_landmark(
            landmark_name=data.get("landmark_name"),
            categories=data.get("categories", []),
            radius_meters=data.get("radius_meters", 1000),
            limit=data.get("limit", 20)
        )
    
    @app.api_route("/semantic_search", methods=["POST"])
    def semantic_search_route():
        """
        Tìm kiếm địa điểm bằng ngữ nghĩa
        Body: {
            "query": "quán cafe lãng mạn view đẹp",
            "lat": 21.0285,  # optional
            "lon": 105.8542,  # optional
            "radius_meters": 5000,
            "top_k": 10
        }
        """
        data = request.get_json()
        from app.services.main_service import semantic_search
        return semantic_search(
            query=data.get("query"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            radius_meters=data.get("radius_meters", 5000),
            top_k=data.get("top_k", 10)
        )
    
    @app.api_route("/compare_places", methods=["POST"])
    def compare_places_route():
        """
        So sánh nhiều địa điểm
        Body: {
            "place_names": ["Hồ Gươm", "Hồ Tây", "Văn Miếu"]
        }
        """
        data = request.get_json()
        from app.services.main_service import compare_places
        return compare_places(data.get("place_names", []))
    
    @app.api_route("/plan_itinerary", methods=["POST"])
    def plan_itinerary_route():
        """
        Lập lịch trình tham quan
        Body: {
            "location": "Old Quarter",
            "duration_hours": 8,
            "preferences": {
                "lat": 21.0285,
                "lon": 105.8542,
                "companions": "family",
                "interests": ["culture", "food", "shopping"]
            },
            "start_time": "09:00"
        }
        """
        data = request.get_json()
        from app.services.main_service import plan_itinerary
        return plan_itinerary(
            location=data.get("location"),
            duration_hours=data.get("duration_hours", 8),
            preferences=data.get("preferences", {}),
            start_time=data.get("start_time", "09:00")
        )
    
    @app.api_route("/recommend_places", methods=["POST"])
    def recommend_places_route():
        """
        Gợi ý địa điểm cá nhân hóa
        Body: {
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
        """
        data = request.get_json()
        from app.services.main_service import recommend_places
        return recommend_places(
            user_preferences=data.get("user_preferences", {}),
            current_location=data.get("current_location"),
            limit=data.get("limit", 10)
        )
