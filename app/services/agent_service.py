"""
Agent Service - Intent Classification & Routing
Xử lý message tự nhiên từ user và route đến service phù hợp
"""

from flask import jsonify
from app.models.model import AIService
from app.database.neo4j.main import Neo4jSpatialQuery
from app.database.qdrant.main import QdrantPlaceSearch
import json
import re
import os

# Initialize services
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_AUTH = (
    os.getenv("NEO4J_USER", "neo4j"),
    os.getenv("NEO4J_PASSWORD", "12345678")
)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)

neo4j_query = Neo4jSpatialQuery(uri=NEO4J_URI, auth=NEO4J_AUTH)
qdrant_search = QdrantPlaceSearch(
    qdrant_url=QDRANT_HOST,
    qdrant_port=QDRANT_PORT,
    collection_name="map_assistant_v2"
)
ai_service = AIService()


class AgentRouter:
    """
    Agent Router - Phân tích intent và route đến service phù hợp
    """
    
    def __init__(self):
        self.intent_examples = {
            "search_places": [
                "tìm quán cafe gần đây",
                "tìm nhà hàng trong bán kính 2km",
                "có quán ăn nào gần không"
            ],
            "nearby_landmark": [
                "tìm khách sạn gần Hồ Gươm",
                "có gì xung quanh Văn Miếu",
                "địa điểm ăn uống gần Lăng Bác"
            ],
            "semantic_search": [
                "quán cafe lãng mạn view đẹp",
                "nhà hàng phù hợp hẹn hò",
                "địa điểm chụp ảnh đẹp"
            ],
            "place_info": [
                "cho tôi biết về Hồ Gươm",
                "thông tin Văn Miếu",
                "Lăng Bác có gì đặc biệt"
            ],
            "compare_places": [
                "so sánh Hồ Gươm và Hồ Tây",
                "nên đi Văn Miếu hay Hoàng Thành",
                "khác nhau giữa 3 museum này"
            ],
            "plan_itinerary": [
                "lập lịch trình 1 ngày Old Quarter",
                "tạo kế hoạch tham quan 8 giờ",
                "gợi ý lịch đi chơi cho gia đình"
            ],
            "recommend_places": [
                "gợi ý địa điểm cho gia đình",
                "địa điểm phù hợp ngân sách sinh viên",
                "nơi nào tốt cho người cao tuổi"
            ]
        }
    
    def classify_intent(self, message: str) -> dict:
        """
        Phân loại intent của user message
        Returns: {
            "intent": "search_places",
            "confidence": 0.95,
            "entities": {...}
        }
        """
        # Tạo prompt cho LLM để classify intent
        intent_prompt = f"""
Bạn là một AI agent phân tích ý định người dùng cho hệ thống Map Assistant.

Các intent có thể:
1. search_places - Tìm địa điểm theo category (cafe, restaurant, hotel...)
2. nearby_landmark - Tìm địa điểm gần một landmark nổi tiếng
3. semantic_search - Tìm kiếm bằng mô tả (lãng mạn, view đẹp...)
4. place_info - Hỏi thông tin chi tiết về một địa điểm cụ thể
5. compare_places - So sánh nhiều địa điểm
6. plan_itinerary - Lập lịch trình tham quan
7. recommend_places - Gợi ý địa điểm theo preferences

Message từ user: "{message}"

Hãy phân tích và trả về JSON format SAU ĐÂY (KHÔNG THÊM GÌ KHÁC):
{{
    "intent": "tên_intent",
    "confidence": 0.0-1.0,
    "entities": {{
        "categories": ["cafe", "restaurant"],
        "landmark_name": "Hồ Gươm",
        "place_names": ["Hồ Gươm", "Hồ Tây"],
        "location": "Old Quarter",
        "preferences": {{
            "companions": "family",
            "interests": ["food", "culture"]
        }},
        "duration_hours": 8,
        "query_description": "lãng mạn view đẹp"
    }}
}}

Chỉ điền các entities có trong message. Entities không có thì bỏ qua.
"""
        
        try:
            # Gọi LLM để classify
            response = ai_service.client.chat.completions.create(
                model=ai_service.model,
                messages=[
                    {"role": "system", "content": "You are an intent classification assistant. Return ONLY valid JSON."},
                    {"role": "user", "content": intent_prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON từ response
            # Remove markdown code blocks nếu có
            result_text = re.sub(r'```json\s*', '', result_text)
            result_text = re.sub(r'```\s*', '', result_text)
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"Error in classify_intent: {e}")
            # Fallback: semantic search cho mọi query
            return {
                "intent": "semantic_search",
                "confidence": 0.5,
                "entities": {
                    "query_description": message
                }
            }
    
    def route_to_service(self, intent_result: dict, original_message: str) -> dict:
        """
        Route đến service phù hợp dựa trên intent
        """
        intent = intent_result.get("intent")
        entities = intent_result.get("entities", {})
        
        try:
            if intent == "search_places":
                return self._handle_search_places(entities, original_message)
            
            elif intent == "nearby_landmark":
                return self._handle_nearby_landmark(entities, original_message)
            
            elif intent == "semantic_search":
                return self._handle_semantic_search(entities, original_message)
            
            elif intent == "place_info":
                return self._handle_place_info(entities, original_message)
            
            elif intent == "compare_places":
                return self._handle_compare_places(entities, original_message)
            
            elif intent == "plan_itinerary":
                return self._handle_plan_itinerary(entities, original_message)
            
            elif intent == "recommend_places":
                return self._handle_recommend_places(entities, original_message)
            
            else:
                # Default: semantic search
                return self._handle_semantic_search(entities, original_message)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn."
            }
    
    def _handle_search_places(self, entities: dict, original_message: str) -> dict:
        """Xử lý search_places intent"""
        from app.services.main_service import search_places
        
        # Extract parameters
        categories = entities.get("categories", ["restaurant", "cafe"])
        lat = entities.get("lat", 21.0285)  # Default: Hà Nội center
        lon = entities.get("lon", 105.8542)
        radius = entities.get("radius_meters", 2000)
        
        return search_places(lat, lon, categories, radius, 20)
    
    def _handle_nearby_landmark(self, entities: dict, original_message: str) -> dict:
        """Xử lý nearby_landmark intent"""
        from app.services.main_service import nearby_landmark
        
        landmark_name = entities.get("landmark_name", "")
        categories = entities.get("categories", ["restaurant", "cafe"])
        radius = entities.get("radius_meters", 1000)
        
        if not landmark_name:
            # Thử extract từ message
            landmark_name = self._extract_landmark_from_message(original_message)
        
        return nearby_landmark(landmark_name, categories, radius, 20)
    
    def _handle_semantic_search(self, entities: dict, original_message: str) -> dict:
        """Xử lý semantic_search intent"""
        from app.services.main_service import semantic_search
        
        query = entities.get("query_description", original_message)
        return semantic_search(query, top_k=10)
    
    def _handle_place_info(self, entities: dict, original_message: str) -> dict:
        """Xử lý place_info intent"""
        from app.services.main_service import get_info_details
        
        # Extract place name từ entities hoặc message
        place_name = entities.get("place_name", "")
        if not place_name and entities.get("landmark_name"):
            place_name = entities.get("landmark_name")
        
        if not place_name:
            place_name = self._extract_place_name_from_message(original_message)
        
        return get_info_details(place_name)
    
    def _handle_compare_places(self, entities: dict, original_message: str) -> dict:
        """Xử lý compare_places intent"""
        from app.services.main_service import compare_places
        
        place_names = entities.get("place_names", [])
        
        if not place_names or len(place_names) < 2:
            # Thử extract từ message
            place_names = self._extract_multiple_places_from_message(original_message)
        
        return compare_places(place_names)
    
    def _handle_plan_itinerary(self, entities: dict, original_message: str) -> dict:
        """Xử lý plan_itinerary intent"""
        from app.services.main_service import plan_itinerary
        
        location = entities.get("location", "Hà Nội")
        duration = entities.get("duration_hours", 8)
        preferences = entities.get("preferences", {})
        
        return plan_itinerary(location, duration, preferences)
    
    def _handle_recommend_places(self, entities: dict, original_message: str) -> dict:
        """Xử lý recommend_places intent"""
        from app.services.main_service import recommend_places
        
        preferences = entities.get("preferences", {})
        current_location = entities.get("current_location")
        
        return recommend_places(preferences, current_location, 10)
    
    def _extract_landmark_from_message(self, message: str) -> str:
        """Extract landmark name từ message"""
        # Simple extraction - có thể cải thiện
        landmarks = ["Hồ Gươm", "Hồ Tây", "Văn Miếu", "Lăng Bác", 
                     "Hoàng Thành", "Chùa Một Cột", "Đền Ngọc Sơn"]
        
        for landmark in landmarks:
            if landmark.lower() in message.lower():
                return landmark
        return ""
    
    def _extract_place_name_from_message(self, message: str) -> str:
        """Extract place name từ message"""
        # Có thể dùng NER hoặc pattern matching
        return message  # Tạm thời return full message
    
    def _extract_multiple_places_from_message(self, message: str) -> list:
        """Extract multiple place names từ message"""
        # Simple extraction
        places = []
        common_places = ["Hồ Gươm", "Hồ Tây", "Văn Miếu", "Lăng Bác", "Hoàng Thành"]
        
        for place in common_places:
            if place.lower() in message.lower():
                places.append(place)
        
        return places


# Global agent router instance
agent_router = AgentRouter()


def chat_handler(message: str, context: dict = None) -> dict:
    """
    Main chat handler - Xử lý message tự nhiên từ user
    
    Args:
        message: Message từ user
        context: Context của conversation (optional)
    
    Returns:
        Response với kết quả và metadata
    """
    if not message or not message.strip():
        return jsonify({
            "success": False,
            "message": "Xin lỗi, tôi không nhận được câu hỏi của bạn."
        })
    
    try:
        # Step 1: Classify intent
        intent_result = agent_router.classify_intent(message)
        
        # Step 2: Route to appropriate service
        service_result = agent_router.route_to_service(intent_result, message)
        
        # Step 3: Combine với metadata
        response = {
            "success": True,
            "message": message,
            "intent": intent_result.get("intent"),
            "confidence": intent_result.get("confidence"),
            "result": service_result.json if hasattr(service_result, 'json') else service_result
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Bạn có thể diễn đạt lại được không?"
        })


def chat_with_context(message: str, session_id: str = None, chat_history: list = None) -> dict:
    """
    Chat với context và history
    
    Args:
        message: Message hiện tại
        session_id: ID của session (để lưu context)
        chat_history: Lịch sử chat trước đó
    
    Returns:
        Response với context
    """
    # Có thể extend để lưu context vào Redis/PostgreSQL
    # Giờ chỉ process message đơn giản
    return chat_handler(message)
