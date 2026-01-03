from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from app.database.neo4j import Neo4jSpatialQuery
from app.database.qdrant import QdrantPlaceSearch
from app.models.model import AIService
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Phase 1 Services
from app.services.translation_service import get_translation_service
from app.services.maps_service import get_maps_service
from app.services.budget_service import get_budget_service
from app.models.enhanced_model import OpeningHours

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

# Phase 1 Services
translation_service = get_translation_service()
maps_service = get_maps_service()
budget_service = get_budget_service()

def get_info_details(name, language='vi'):
    """
    Lấy thông tin chi tiết về một địa điểm
    
    Args:
        name: Tên địa điểm
        language: Ngôn ngữ trả về ('vi' hoặc 'en')
    """
    res_qdrant = qdrant_search.search_place_details(
        query=name,
        top_k=2
    )
    data = ""
    place_info = {}
    
    for item in res_qdrant:
        summary = item.get("payload", {}).get("summary", "")
        data += f"{summary}\n"
        
        # Get place details for Phase 1 features
        if not place_info:
            payload = item.get("payload", {})
            place_info = {
                'name': payload.get('title', name),
                'summary': payload.get('summary', ''),
                'images': payload.get('images', []),
                'url': payload.get('url', '')
            }
            
            # Add coordinates if available
            # Note: Need to get from Neo4j or OSM data
            place_info['lat'] = payload.get('lat', 21.0285)
            place_info['lon'] = payload.get('lon', 105.8542)

    # Generate maps URL and add Phase 1 features
    if place_info:
        place_info['google_maps_url'] = maps_service.get_place_url(
            place_info['lat'], 
            place_info['lon'], 
            place_info['name']
        )
        
        # Check opening hours if available
        if place_info.get('opening_hours'):
            try:
                opening_hours = OpeningHours(place_info['opening_hours'])
                place_info['is_open_now'] = opening_hours.is_open_now()
            except:
                place_info['is_open_now'] = None
    
    # Generate AI response
    prompt = f"Can you provide detailed information about the place named '{name}'?"
    if language == 'en':
        prompt = f"Provide detailed information about '{name}' in English."
    
    ai_response = ai_service.generate_response(
        user_message=prompt,
        data_extend=data
    )
    
    # Translate if needed
    if language == 'en' and translation_service.detect_language(ai_response) == 'vi':
        ai_response = translation_service.translate(ai_response, 'en')
    
    return jsonify({
        "response": ai_response,
        "place_info": place_info,
        "language": language
    })


def search_places(lat, lon, categories, radius_meters=2000, limit=20, language='vi', user_location=None):
    """
    Tìm kiếm địa điểm theo category xung quanh tọa độ (Enhanced with Phase 1 features)
    
    Args:
        lat: Vĩ độ
        lon: Kinh độ
        categories: List các category (VD: ['restaurant', 'cafe'])
        radius_meters: Bán kính tìm kiếm (mét)
        limit: Số kết quả tối đa
        language: Ngôn ngữ ('vi' hoặc 'en')
        user_location: Current user location (lat, lon) for directions
    """
    places = neo4j_query.find_places_by_category(
        lat=lat,
        lon=lon,
        categories=categories,
        radius_meters=radius_meters,
        limit=limit
    )
    
    # Enrich places with Phase 1 features
    for place in places:
        place['images'] = []  # Default empty
        
        # Add Google Maps URL
        place['google_maps_url'] = maps_service.get_place_url(
            place.get('lat', lat),
            place.get('lon', lon),
            place.get('name', '')
        )
        
        # Check opening hours (Phase 1)
        if place.get('opening_hours'):
            try:
                opening_hours = OpeningHours(place['opening_hours'])
                place['is_open_now'] = opening_hours.is_open_now()
                place['opening_hours_display'] = place['opening_hours']
            except:
                place['is_open_now'] = None
                place['opening_hours_display'] = place['opening_hours']
        else:
            place['is_open_now'] = None
        
        # Add contact info if available
        if place.get('phone') or place.get('website') or place.get('email'):
            place['contact_info'] = {
                'phone': place.get('phone'),
                'website': place.get('website'),
                'email': place.get('email')
            }
        
        # Add directions if user location provided
        if user_location and 'lat' in user_location and 'lon' in user_location:
            travel_info = maps_service.get_travel_info(
                origin=(user_location['lat'], user_location['lon']),
                destination=(place.get('lat', lat), place.get('lon', lon)),
                mode='driving'
            )
            place['directions'] = travel_info
            
            # Suggest transport mode based on distance
            place['suggested_transport'] = maps_service.suggest_transport_mode(
                travel_info['distance']['meters']
            )
        
        # Add price info from database or estimate
        if place.get('min_price') or place.get('max_price') or place.get('price_range'):
            place['price_info'] = {
                'price_range': place.get('price_range', '$$'),
                'min_price': place.get('min_price'),
                'max_price': place.get('max_price')
            }
        else:
            # Estimate cost if no price data
            category = place.get('categories', ['attraction'])[0] if place.get('categories') else 'attraction'
            place['estimated_cost'] = budget_service.estimate_place_cost(category, 1)
        
        # Translate name if English requested
        if language == 'en':
            place['name_en'] = translation_service.translate(place['name'], 'en')
            if place.get('address'):
                place['address_en'] = translation_service.translate(place['address'], 'en')
    
    # Enrich với thông tin từ AI nếu cần
    if places:
        places_summary = f"Tìm thấy {len(places)} địa điểm:\n"
        for place in places[:5]:  # Top 5
            places_summary += f"- {place['name']}: {place['address']}, cách {place['distance_meters']}m\n"
        
        prompt = "Hãy tóm tắt ngắn gọn danh sách địa điểm này cho tôi"
        if language == 'en':
            prompt = "Please provide a brief summary of these places in English"
        
        ai_summary = ai_service.generate_response(
            user_message=prompt,
            data_extend=places_summary
        )
        
        # Translate if needed
        if language == 'en' and translation_service.detect_language(ai_summary) == 'vi':
            ai_summary = translation_service.translate(ai_summary, 'en')
        
        return jsonify({
            "total": len(places),
            "places": places,
            "summary": ai_summary,
            "language": language
        })
    
    message = "Không tìm thấy địa điểm phù hợp"
    if language == 'en':
        message = "No suitable places found"
    
    return jsonify({"total": 0, "places": [], "message": message, "language": language})


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
        
        # Enrich places with Phase 1 features
        for place in places:
            place['images'] = []  # Default empty
            
            # Add Google Maps URL
            place['google_maps_url'] = maps_service.get_place_url(
                place.get('lat'),
                place.get('lon'),
                place.get('name', '')
            )
            
            # Check opening hours
            if place.get('opening_hours'):
                try:
                    opening_hours = OpeningHours(place['opening_hours'])
                    place['is_open_now'] = opening_hours.is_open_now()
                except:
                    place['is_open_now'] = None
            
            # Add price info
            if place.get('min_price') or place.get('max_price'):
                place['price_info'] = {
                    'price_range': place.get('price_range', '$$'),
                    'min_price': place.get('min_price'),
                    'max_price': place.get('max_price')
                }
            else:
                category = place.get('categories', ['attraction'])[0] if place.get('categories') else 'attraction'
                place['estimated_cost'] = budget_service.estimate_place_cost(category, 1)
            
            # Add contact info
            if place.get('phone') or place.get('website'):
                place['contact_info'] = {
                    'phone': place.get('phone'),
                    'website': place.get('website')
                }
        
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
    
    # Kết hợp thông tin và enrich với Phase 1
    results = []
    for item in vector_results[:top_k]:
        payload = item.get('payload', {})
        # Use 'title' from Wikipedia data, fallback to 'name'
        place_name = payload.get('title', payload.get('name', 'N/A'))
        
        place = {
            'place_id': item['place_id'],
            'name': place_name,
            'summary': payload.get('summary', ''),
            'images': payload.get('images', []),
            'url': payload.get('url', ''),
            'score': item.get('score', 0),
            'lat': payload.get('lat', 21.0285),
            'lon': payload.get('lon', 105.8542)
        }
        
        # Add Phase 1 features
        place['google_maps_url'] = maps_service.get_place_url(
            place['lat'], place['lon'], place_name
        )
        
        # Opening hours check
        if payload.get('opening_hours'):
            try:
                opening_hours = OpeningHours(payload['opening_hours'])
                place['is_open_now'] = opening_hours.is_open_now()
                place['opening_hours'] = payload['opening_hours']
            except:
                place['is_open_now'] = None
        
        # Price info
        if payload.get('min_price') or payload.get('max_price'):
            place['price_info'] = {
                'price_range': payload.get('price_range', '$$'),
                'min_price': payload.get('min_price'),
                'max_price': payload.get('max_price')
            }
        
        results.append(place)
    
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


def plan_itinerary(location, duration_hours, preferences=None, start_time="09:00", language='vi', num_people=1):
    """
    Lập lịch trình tham quan thông minh (Enhanced with Phase 1 features)
    
    Args:
        location: Khu vực (VD: "Old Quarter", hoặc lat/lon)
        duration_hours: Số giờ tham quan
        preferences: Dict preferences (VD: {"companions": "family", "interests": ["culture", "food"]})
        start_time: Giờ bắt đầu
        language: Ngôn ngữ ('vi' hoặc 'en')
        num_people: Số người
    """
    if preferences is None:
        preferences = {}
    
    # Extract categories từ interests
    interests = preferences.get('interests', ['restaurant', 'cafe', 'museum'])
    companions = preferences.get('companions', 'solo')
    budget_limit = preferences.get('budget', None)  # VND per person
    
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
    
    # Flatten results for cost estimation
    all_places = []
    for group_name, places in results.items():
        all_places.extend(places)
    
    # Filter by budget if specified
    if budget_limit:
        all_places = budget_service.filter_by_budget(
            all_places, 
            max_budget_per_person=budget_limit,
            num_people=num_people
        )
        
        # Re-organize into groups
        results = {
            'restaurants_cafes': [p for p in all_places if any(c in p.get('categories', []) for c in ['restaurant', 'cafe'])],
            'attractions': [p for p in all_places if any(c in p.get('categories', []) for c in ['museum', 'gallery', 'historical'])],
            'shopping': [p for p in all_places if any(c in p.get('categories', []) for c in ['shopping', 'market'])]
        }
    
    # Estimate total cost
    cost_estimate = budget_service.estimate_itinerary_cost(
        all_places[:10],  # Limit to realistic itinerary size
        num_people=num_people,
        include_transport=True,
        transport_budget=200000  # 200k VND per person for transport
    )
    
    # Calculate multi-stop route
    stops = [(lat, lon)]  # Start point
    for place in all_places[:5]:  # Add up to 5 places
        if 'lat' in place and 'lon' in place:
            stops.append((place['lat'], place['lon']))
    
    route_info = None
    if len(stops) > 1:
        route_info = maps_service.get_multi_stop_route(
            stops,
            mode='driving'
        )
    
    # Tổng hợp dữ liệu
    itinerary_data = f"Khu vực: {location}\n"
    itinerary_data += f"Thời gian: {duration_hours} giờ, bắt đầu {start_time}\n"
    itinerary_data += f"Đối tượng: {companions}\n"
    itinerary_data += f"Số người: {num_people}\n"
    if budget_limit:
        itinerary_data += f"Ngân sách: {budget_limit:,} VND/người\n"
    itinerary_data += "\n"
    
    for group_name, places in results.items():
        itinerary_data += f"\n{group_name.replace('_', ' ').title()}:\n"
        for place in places:
            itinerary_data += f"  - {place['name']}: {place['address']}\n"
    
    # Dùng AI để lập lịch trình thông minh
    prompt = f"""Hãy lập lịch trình chi tiết {duration_hours} giờ tham quan {location} 
        bắt đầu từ {start_time} cho {companions} ({num_people} người). 
        Bao gồm: thời gian cụ thể, địa điểm, hoạt động, ăn uống, nghỉ ngơi.
        Tối ưu để không phải di chuyển xa, hợp lý về thời gian.
        Sử dụng các địa điểm trong dữ liệu bên dưới."""
    
    if budget_limit:
        prompt += f"\nLưu ý: Ngân sách {budget_limit:,} VND/người. Tổng chi phí ước tính: {cost_estimate['per_person']['avg']:,} VND/người"
    
    if language == 'en':
        prompt = f"""Create a detailed {duration_hours}-hour itinerary for {location}
        starting at {start_time} for {companions} ({num_people} people).
        Include: specific times, places, activities, meals, rest breaks.
        Optimize for minimal travel distance and realistic timing.
        Use the places from the data below."""
        
        if budget_limit:
            prompt += f"\nNote: Budget {budget_limit:,} VND/person. Estimated cost: {cost_estimate['per_person']['avg']:,} VND/person"
    
    ai_response = ai_service.generate_response(
        user_message=prompt,
        data_extend=itinerary_data
    )
    
    # Translate if needed
    if language == 'en' and translation_service.detect_language(ai_response) == 'vi':
        ai_response = translation_service.translate(ai_response, 'en')
    
    return jsonify({
        "location": location,
        "duration_hours": duration_hours,
        "start_time": start_time,
        "num_people": num_people,
        "preferences": preferences,
        "available_places": results,
        "itinerary": ai_response,
        "cost_estimate": cost_estimate,
        "route_info": route_info,
        "language": language
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

