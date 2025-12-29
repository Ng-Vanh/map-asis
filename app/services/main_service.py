from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from app.database.neo4j import Neo4jSpatialQuery
from app.database.qdrant import QdrantPlaceSearch
from app.models.model import AIService
from qdrant_client.models import Filter, FieldCondition, MatchValue

import os

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

def get_info_details(name):
    """
    Lấy thông tin chi tiết về một địa điểm
    """
    res_qdrant = qdrant_search.search_place_details(
        query=name,
        top_k=2
    )
    data = ""
    for item in res_qdrant:
        summary = item.get("payload", {}).get("summary", "")
        data += f"{summary}\n"

    ai_response = ai_service.generate_response(
        user_message=f"Can you provide detailed information about the place named '{name}'?",
        data_extend=data
    )
    return jsonify({"response": ai_response})


def search_places(lat, lon, categories, radius_meters=2000, limit=20):
    """
    Tìm kiếm địa điểm theo category xung quanh tọa độ
    
    Args:
        lat: Vĩ độ
        lon: Kinh độ
        categories: List các category (VD: ['restaurant', 'cafe'])
        radius_meters: Bán kính tìm kiếm (mét)
        limit: Số kết quả tối đa
    """
    places = neo4j_query.find_places_by_category(
        lat=lat,
        lon=lon,
        categories=categories,
        radius_meters=radius_meters,
        limit=limit
    )
    
    # Enrich places with images from Qdrant
    # NOTE: Only works for places that have Wikipedia pages
    # Many small cafes/restaurants may not have images
    for place in places:
        place['images'] = []  # Default empty
        # Images enrichment disabled for performance
        # Only semantic_search returns images (from Qdrant directly)
    
    # Enrich với thông tin từ AI nếu cần
    if places:
        places_summary = f"Tìm thấy {len(places)} địa điểm:\n"
        for place in places[:5]:  # Top 5
            places_summary += f"- {place['name']}: {place['address']}, cách {place['distance_meters']}m\n"
        
        ai_summary = ai_service.generate_response(
            user_message=f"Hãy tóm tắt ngắn gọn danh sách địa điểm này cho tôi",
            data_extend=places_summary
        )
        
        return jsonify({
            "total": len(places),
            "places": places,
            "summary": ai_summary
        })
    
    return jsonify({"total": 0, "places": [], "message": "Không tìm thấy địa điểm phù hợp"})


def nearby_landmark(landmark_name, categories, radius_meters=1000, limit=20):
    """
    Tìm địa điểm xung quanh một landmark nổi tiếng
    
    Args:
        landmark_name: Tên địa danh (VD: "Hồ Gươm", "Văn Miếu")
        categories: List category cần tìm
        radius_meters: Bán kính
        limit: Số kết quả
    """
    result = neo4j_query.find_places_nearby_landmark(
        landmark_name=landmark_name,
        categories=categories,
        radius_meters=radius_meters,
        limit=limit
    )
    
    if result.get('landmark') and result.get('nearby_places'):
        landmark_info = result['landmark']
        places = result['nearby_places']
        
        # Enrich places with images from Qdrant  
        # NOTE: Only works for places with Wikipedia pages
        for place in places:
            place['images'] = []  # Default empty - images enrichment disabled
        
        summary = f"Xung quanh {landmark_info['name']} ({landmark_info['address']}), có {len(places)} địa điểm:\n"
        for place in places[:5]:
            summary += f"- {place['name']}: {place['address']}, cách {place['distance_meters']}m\n"
        
        ai_response = ai_service.generate_response(
            user_message=f"Hãy mô tả ngắn gọn về các địa điểm xung quanh {landmark_name}",
            data_extend=summary
        )
        
        return jsonify({
            "landmark": landmark_info,
            "total": len(places),
            "nearby_places": places,
            "summary": ai_response
        })
    
    return jsonify({"error": f"Không tìm thấy landmark '{landmark_name}'"})


def semantic_search(query, lat=None, lon=None, radius_meters=5000, top_k=10):
    """
    Tìm kiếm địa điểm bằng ngữ nghĩa kết hợp Neo4j + Qdrant
    
    Args:
        query: Câu truy vấn tự nhiên (VD: "quán cafe lãng mạn view đẹp")
        lat, lon: Tọa độ (optional)
        radius_meters: Bán kính filter
        top_k: Số kết quả
    """
    # Step 1: Semantic search với Qdrant
    vector_results = qdrant_search.search_place_details(
        query=query,
        top_k=top_k * 2,  # Lấy nhiều hơn để filter
        score_threshold=0.3
    )
    
    if not vector_results:
        return jsonify({"total": 0, "places": [], "message": "Không tìm thấy kết quả phù hợp"})
    
    # Step 2: Filter bằng Neo4j nếu có location
    place_ids = [item['place_id'] for item in vector_results]
    
    # Kết hợp thông tin
    results = []
    for item in vector_results[:top_k]:
        payload = item.get('payload', {})
        # Use 'title' from Wikipedia data, fallback to 'name'
        place_name = payload.get('title', payload.get('name', 'N/A'))
        results.append({
            'place_id': item['place_id'],
            'name': place_name,
            'score': item['score'],
            'summary': payload.get('summary', ''),
            'text': payload.get('text', ''),
            'images': payload.get('images', []),
            'url': payload.get('url', '')
        })
    
    # Generate AI response
    data_summary = "\n".join([f"{r['name']}: {r['summary'][:200]}..." for r in results[:5]])
    ai_response = ai_service.generate_response(
        user_message=f"Dựa trên yêu cầu '{query}', hãy giới thiệu các địa điểm phù hợp nhất",
        data_extend=data_summary
    )
    
    return jsonify({
        "total": len(results),
        "query": query,
        "places": results,
        "recommendation": ai_response
    })


def compare_places(place_names):
    """
    So sánh chi tiết giữa nhiều địa điểm
    
    Args:
        place_names: List tên địa điểm (VD: ["Hồ Gươm", "Hồ Tây"])
    """
    if not place_names or len(place_names) < 2:
        return jsonify({"error": "Cần ít nhất 2 địa điểm để so sánh"})
    
    # Tìm thông tin mỗi địa điểm từ Qdrant
    all_places_data = []
    for name in place_names:
        results = qdrant_search.search_place_details(
            query=name,
            top_k=1,
            score_threshold=0.0
        )
        if results:
            all_places_data.append({
                'name': name,
                'data': results[0]
            })
    
    if len(all_places_data) < 2:
        return jsonify({"error": "Không tìm thấy đủ thông tin để so sánh"})
    
    # Tạo prompt so sánh
    comparison_data = ""
    for place_info in all_places_data:
        payload = place_info['data'].get('payload', {})
        comparison_data += f"\n=== {place_info['name']} ===\n"
        comparison_data += f"{payload.get('summary', '')}\n"
        comparison_data += f"{payload.get('text', '')}\n"
    
    ai_response = ai_service.generate_response(
        user_message=f"Hãy so sánh chi tiết các địa điểm: {', '.join(place_names)}. Phân tích điểm mạnh, điểm yếu, phù hợp cho ai, và đưa ra lời khuyên nên chọn địa điểm nào.",
        data_extend=comparison_data
    )
    
    return jsonify({
        "places": place_names,
        "comparison": ai_response,
        "details": all_places_data
    })


def plan_itinerary(location, duration_hours, preferences=None, start_time="09:00"):
    """
    Lập lịch trình tham quan thông minh
    
    Args:
        location: Khu vực (VD: "Old Quarter", hoặc lat/lon)
        duration_hours: Số giờ tham quan
        preferences: Dict preferences (VD: {"companions": "family", "interests": ["culture", "food"]})
        start_time: Giờ bắt đầu
    """
    if preferences is None:
        preferences = {}
    
    # Extract categories từ interests
    interests = preferences.get('interests', ['restaurant', 'cafe', 'museum'])
    companions = preferences.get('companions', 'solo')
    
    # Tìm địa điểm phù hợp (giả sử có tọa độ)
    # Trong thực tế cần convert location name -> coordinates
    lat = preferences.get('lat', 21.0285)  # Default: Hồ Gươm
    lon = preferences.get('lon', 105.8542)
    
    # Tìm nhiều loại địa điểm
    category_groups = [
        ['restaurant', 'cafe'],
        ['museum', 'gallery', 'historical'],
        ['shopping', 'market']
    ]
    
    results = neo4j_query.find_places_by_multiple_categories(
        lat=lat,
        lon=lon,
        category_groups=category_groups,
        radius_meters=3000,
        limit=5
    )
    
    # Tổng hợp dữ liệu
    itinerary_data = f"Khu vực: {location}\n"
    itinerary_data += f"Thời gian: {duration_hours} giờ, bắt đầu {start_time}\n"
    itinerary_data += f"Đối tượng: {companions}\n\n"
    
    for group_name, places in results.items():
        itinerary_data += f"\n{group_name.replace('_', ' ').title()}:\n"
        for place in places:
            itinerary_data += f"  - {place['name']}: {place['address']}\n"
    
    # Dùng AI để lập lịch trình thông minh
    ai_response = ai_service.generate_response(
        user_message=f"""Hãy lập lịch trình chi tiết {duration_hours} giờ tham quan {location} 
        bắt đầu từ {start_time} cho {companions}. 
        Bao gồm: thời gian cụ thể, địa điểm, hoạt động, ăn uống, nghỉ ngơi.
        Tối ưu để không phải di chuyển xa, hợp lý về thời gian.
        Sử dụng các địa điểm trong dữ liệu bên dưới.""",
        data_extend=itinerary_data
    )
    
    return jsonify({
        "location": location,
        "duration_hours": duration_hours,
        "start_time": start_time,
        "preferences": preferences,
        "available_places": results,
        "itinerary": ai_response
    })


def recommend_places(user_preferences, current_location=None, limit=10):
    """
    Gợi ý địa điểm cá nhân hóa dựa trên preferences
    
    Args:
        user_preferences: Dict preferences
            VD: {"budget": 2, "interests": ["food", "culture"], 
                 "companions": "family", "avoid": ["nightlife"]}
        current_location: Dict với lat, lon (optional)
        limit: Số gợi ý
    """
    interests = user_preferences.get('interests', ['restaurant', 'cafe'])
    companions = user_preferences.get('companions', 'solo')
    budget = user_preferences.get('budget', 2)  # 1-4
    
    # Nếu có location, tìm nearby
    if current_location and 'lat' in current_location and 'lon' in current_location:
        places = neo4j_query.find_places_by_category(
            lat=current_location['lat'],
            lon=current_location['lon'],
            categories=interests,
            radius_meters=5000,
            limit=limit * 2
        )
    else:
        # Tìm theo semantic
        query_text = f"{' '.join(interests)} phù hợp cho {companions}"
        vector_results = qdrant_search.search_place_details(
            query=query_text,
            top_k=limit,
            score_threshold=0.3
        )
        places = [{
            'place_id': item['place_id'],
            'name': item.get('payload', {}).get('name', 'N/A'),
            'score': item['score']
        } for item in vector_results]
    
    # Generate recommendation với AI
    places_summary = "\n".join([f"{p['name']}" for p in places[:limit]])
    
    ai_response = ai_service.generate_response(
        user_message=f"""Dựa trên sở thích: {user_preferences}, 
        hãy gợi ý và giải thích tại sao các địa điểm sau phù hợp:
        {places_summary}
        Sắp xếp theo độ phù hợp và giải thích chi tiết.""",
        data_extend=places_summary
    )
    
    return jsonify({
        "user_preferences": user_preferences,
        "total_recommendations": len(places[:limit]),
        "places": places[:limit],
        "recommendation": ai_response
    })

