"""
Test script cho các services mới của Map Assistant
Chạy file này để test các API endpoints
"""

import requests # type: ignore
import json

BASE_URL = "http://localhost:8864/api/v1"

def print_response(title, response):
    """In response đẹp mắt"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print(f"{'='*80}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
    print(f"{'='*80}\n")


def test_health():
    """Test health check"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code} - {response.text}")


def test_agent_chat():
    """Test Agent Chat - Natural Language"""
    test_messages = [
        "Lên kế hoạch tham quan ở Cầu Giấy ?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        payload = {"message": message}
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print_response(f"AGENT CHAT {i}: {message}", response)


def test_place_info():
    """Test lấy thông tin địa điểm"""
    payload = {
        "name": "Lăng Bác"
    }
    response = requests.post(f"{BASE_URL}/place_info", json=payload)
    print_response("THÔNG TIN ĐỊA ĐIỂM - Lăng Bác", response)


def test_search_places():
    """Test tìm kiếm địa điểm theo category"""
    payload = {
        "lat": 21.0285,
        "lon": 105.8542,
        "categories": ["restaurant", "cafe"],
        "radius_meters": 2000,
        "limit": 10
    }
    response = requests.post(f"{BASE_URL}/search_places", json=payload)
    print_response("TÌM KIẾM ĐỊA ĐIỂM - Nhà hàng & Cafe gần Hồ Gươm", response)


def test_nearby_landmark():
    """Test tìm địa điểm gần landmark"""
    payload = {
        "landmark_name": "Yu Tan",
        "categories": ["hotel", "accommodation"],
        "radius_meters": 2000,
        "limit": 10
    }
    response = requests.post(f"{BASE_URL}/nearby_landmark", json=payload)
    print_response("TÌM KHÁCH SẠN GẦN Yu Tan", response)


def test_semantic_search():
    """Test semantic search"""
    payload = {
        "query": "quán cafe yên tĩnh view đẹp phù hợp làm việc",
        "top_k": 5
    }
    response = requests.post(f"{BASE_URL}/semantic_search", json=payload)
    print_response("SEMANTIC SEARCH - Cafe yên tĩnh view đẹp", response)


def test_compare_places():
    """Test so sánh địa điểm"""
    payload = {
        "place_names": ["Lăng Bác", "Văn Miếu", "Hoàng Thành Thăng Long"]
    }
    response = requests.post(f"{BASE_URL}/compare_places", json=payload)
    print_response("SO SÁNH ĐỊA ĐIỂM - 3 Di tích lịch sử", response)


def test_plan_itinerary():
    """Test lập lịch trình"""
    payload = {
        "location": "Old Quarter Hanoi",
        "duration_hours": 8,
        "preferences": {
            "lat": 21.0285,
            "lon": 105.8542,
            "companions": "family",
            "interests": ["culture", "food", "shopping"]
        },
        "start_time": "09:00"
    }
    response = requests.post(f"{BASE_URL}/plan_itinerary", json=payload)
    print_response("LẬP LỊCH TRÌNH - 8 giờ tham quan Old Quarter", response)


def test_recommend_places():
    """Test gợi ý địa điểm cá nhân hóa"""
    payload = {
        "user_preferences": {
            "budget": 2,
            "interests": ["food", "culture", "shopping"],
            "companions": "family",
            "avoid": ["nightlife"]
        },
        "current_location": {
            "lat": 21.0285,
            "lon": 105.8542
        },
        "limit": 5
    }
    response = requests.post(f"{BASE_URL}/recommend_places", json=payload)
    print_response("GỢI Ý CÁ NHÂN HÓA - Cho gia đình", response)


def run_all_tests():
    """Chạy tất cả tests"""
    print("\n" + "="*80)
    print("🚀 BẮT ĐẦU TEST TẤT CẢ SERVICES")
    print("="*80)
    
    try:
        test_health()
        
        print("\n🤖 0. TEST AGENT CHAT (NATURAL LANGUAGE)")
        test_agent_chat()
        
        print("\n📍 1. TEST THÔNG TIN ĐỊA ĐIỂM")
        test_place_info()
        
        print("\n📍 2. TEST TÌM KIẾM ĐỊA ĐIỂM")
        test_search_places()
        
        print("\n📍 3. TEST TÌM KIẾM GẦN LANDMARK")
        test_nearby_landmark()
        
        print("\n📍 4. TEST SEMANTIC SEARCH")
        test_semantic_search()
        
        print("\n📍 5. TEST SO SÁNH ĐỊA ĐIỂM")
        test_compare_places()
        
        print("\n📍 6. TEST LẬP LỊCH TRÌNH")
        test_plan_itinerary()
        
        print("\n📍 7. TEST GỢI Ý CÁ NHÂN HÓA")
        test_recommend_places()
        
        print("\n" + "="*80)
        print("✅ HOÀN THÀNH TẤT CẢ TESTS")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        print("Đảm bảo server đang chạy tại http://localhost:8864")


if __name__ == "__main__":
    # Chạy tất cả tests
    # run_all_tests()
    
    # Hoặc chạy từng test riêng lẻ:
    # test_health()
    test_agent_chat()  # NEW: Test Agent Chat
    # test_place_info()
    # test_search_places()
    # test_nearby_landmark()
    # test_semantic_search()
    # test_compare_places()
    # test_plan_itinerary()
    # test_recommend_places()
