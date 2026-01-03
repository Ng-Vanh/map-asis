"""
Test Phase 1 Features
- Multilingual support
- Maps integration
- Opening hours
- Budget estimation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_translation_service():
    """Test translation service"""
    from app.services.translation_service import get_translation_service
    
    print("\n" + "="*80)
    print("TEST 1: Translation Service")
    print("="*80)
    
    translation = get_translation_service()
    
    # Test 1: Detect language
    print("\n1. Language Detection:")
    vi_text = "Tìm quán cafe gần đây"
    en_text = "Find cafes nearby"
    
    print(f"   '{vi_text}' -> {translation.detect_language(vi_text)}")
    print(f"   '{en_text}' -> {translation.detect_language(en_text)}")
    
    # Test 2: Translation
    print("\n2. Translation:")
    translated = translation.translate("Hồ Gươm", target_lang='en')
    print(f"   'Hồ Gươm' (vi -> en) -> '{translated}'")
    
    translated = translation.translate("Sword Lake", target_lang='vi')
    print(f"   'Sword Lake' (en -> vi) -> '{translated}'")
    
    # Test 3: Dictionary translation
    print("\n3. Dictionary Translation:")
    data = {
        "name": "Văn Miếu",
        "description": "Trường đại học đầu tiên của Việt Nam"
    }
    
    translated_data = translation.translate_dict(data, target_lang='en')
    print(f"   Original: {data}")
    print(f"   Translated: {translated_data}")
    
    print("\n✅ Translation Service Test Complete!")


def test_maps_service():
    """Test maps service"""
    from app.services.maps_service import get_maps_service
    
    print("\n" + "="*80)
    print("TEST 2: Maps Service")
    print("="*80)
    
    maps = get_maps_service()
    
    # Test 1: Generate place URL
    print("\n1. Place URL:")
    url = maps.get_place_url(21.0285, 105.8542, "Hồ Gươm")
    print(f"   Hồ Gươm: {url}")
    
    # Test 2: Calculate distance
    print("\n2. Distance Calculation:")
    # Hồ Gươm -> Văn Miếu
    distance = maps.calculate_distance(21.0285, 105.8542, 21.0277, 105.8355)
    print(f"   Hồ Gươm -> Văn Miếu:")
    print(f"     Distance: {distance['meters']:.2f}m ({distance['kilometers']:.2f}km)")
    
    # Test 3: Travel info
    print("\n3. Travel Information:")
    travel_info = maps.get_travel_info(
        origin=(21.0285, 105.8542),
        destination=(21.0277, 105.8355),
        mode='walking'
    )
    print(f"   Mode: {travel_info['mode']}")
    print(f"   Distance: {travel_info['distance']['kilometers']}km")
    print(f"   Time: {travel_info['estimated_time']['minutes']} minutes")
    print(f"   Directions: {travel_info['directions_url'][:80]}...")
    
    # Test 4: Multi-stop route
    print("\n4. Multi-stop Route:")
    stops = [
        (21.0285, 105.8542),  # Hồ Gươm
        (21.0277, 105.8355),  # Văn Miếu
        (21.0365, 105.8348)   # Lăng Bác
    ]
    
    route = maps.get_multi_stop_route(stops, mode='driving')
    print(f"   Stops: {route['total_stops']}")
    print(f"   Total Distance: {route['total_distance']['kilometers']}km")
    print(f"   Total Time: {route['total_time']['minutes']} minutes")
    print(f"   Route URL: {route['route_url'][:80]}...")
    
    # Test 5: Transport mode suggestion
    print("\n5. Transport Mode Suggestion:")
    distances = [500, 2000, 5000, 20000]
    for dist in distances:
        mode = maps.suggest_transport_mode(dist)
        print(f"   {dist}m -> {mode}")
    
    print("\n✅ Maps Service Test Complete!")


def test_budget_service():
    """Test budget service"""
    from app.services.budget_service import get_budget_service
    
    print("\n" + "="*80)
    print("TEST 3: Budget Service")
    print("="*80)
    
    budget = get_budget_service()
    
    # Test 1: Estimate place cost
    print("\n1. Place Cost Estimation:")
    categories = ['restaurant', 'cafe', 'hotel', 'museum']
    
    for category in categories:
        cost = budget.estimate_place_cost(category, num_people=2)
        print(f"   {category.title()} (2 people):")
        print(f"     Per person: {cost['per_person']['min']:,} - {cost['per_person']['max']:,} VND")
        print(f"     Total: {cost['total']['avg']:,} VND ({cost['price_range']})")
    
    # Test 2: Itinerary cost
    print("\n2. Itinerary Cost Estimation:")
    places = [
        {"name": "Restaurant A", "categories": ["restaurant"]},
        {"name": "Cafe B", "categories": ["cafe"]},
        {"name": "Museum C", "categories": ["museum"]}
    ]
    
    itinerary_cost = budget.estimate_itinerary_cost(
        places=places,
        num_people=2,
        include_transport=True
    )
    
    print(f"   Places: {itinerary_cost['total_places']}")
    print(f"   People: {itinerary_cost['num_people']}")
    print(f"   Total Cost: {itinerary_cost['total_cost']['min']:,} - {itinerary_cost['total_cost']['max']:,} VND")
    print(f"   Per Person: {itinerary_cost['per_person']['avg']:,} VND")
    print(f"\n   Breakdown:")
    for item in itinerary_cost['breakdown']:
        avg_cost = item['cost'].get('total', {}).get('avg', 0)
        print(f"     - {item['place']}: {avg_cost:,} VND")
    
    # Test 3: Budget filtering
    print("\n3. Budget Filtering:")
    places = [
        {"name": "Expensive Restaurant", "categories": ["restaurant"], "price_info": {"min_price": 300000, "max_price": 500000}},
        {"name": "Cheap Cafe", "categories": ["cafe"], "price_info": {"min_price": 20000, "max_price": 50000}},
        {"name": "Mid Restaurant", "categories": ["restaurant"], "price_info": {"min_price": 100000, "max_price": 200000}}
    ]
    
    max_budget = 150000
    affordable = budget.filter_by_budget(places, max_budget_per_person=max_budget, num_people=1)
    
    print(f"   Budget limit: {max_budget:,} VND/person")
    print(f"   Found {len(affordable)} affordable places:")
    for place in affordable:
        avg_cost = place['estimated_cost']['per_person']['avg']
        print(f"     - {place['name']}: {avg_cost:,} VND")
    
    # Test 4: Price comparison
    print("\n4. Price Comparison:")
    comparison = budget.compare_prices(places)
    
    print(f"   Comparing {comparison['total_compared']} places:")
    for comp in comparison['comparisons']:
        print(f"     #{comp['rank']} {comp['place']}: {comp['avg_cost']:,} VND ({comp['price_range']}) - {comp.get('note', '')}")
    
    print("\n✅ Budget Service Test Complete!")


def test_opening_hours():
    """Test opening hours model"""
    from app.models.enhanced_model import OpeningHours
    from datetime import datetime
    
    print("\n" + "="*80)
    print("TEST 4: Opening Hours")
    print("="*80)
    
    # Test 1: Create from string
    print("\n1. Create from String:")
    hours = OpeningHours.from_string("09:00-22:00")
    print(f"   Input: '09:00-22:00'")
    print(f"   Monday: {hours.monday}")
    print(f"   Is open now: {hours.is_open_now()}")
    print(f"   Current time: {datetime.now().strftime('%H:%M')}")
    
    # Test 2: Different hours per day
    print("\n2. Different Hours per Day:")
    hours2 = OpeningHours(
        monday="09:00-21:00",
        tuesday="09:00-21:00",
        wednesday="09:00-21:00",
        thursday="09:00-21:00",
        friday="09:00-22:00",
        saturday="10:00-23:00",
        sunday="10:00-20:00"
    )
    
    today = datetime.now().strftime('%A').lower()
    today_hours = getattr(hours2, today)
    print(f"   Today ({today}): {today_hours}")
    print(f"   Is open: {hours2.is_open_now()}")
    
    # Test 3: Convert to dict
    print("\n3. Convert to Dictionary:")
    hours_dict = hours2.to_dict()
    print(f"   Dict keys: {list(hours_dict.keys())}")
    
    print("\n✅ Opening Hours Test Complete!")


def test_enhanced_place():
    """Test enhanced place model"""
    from app.models.enhanced_model import EnhancedPlace, MultilingualInfo, OpeningHours, PriceInfo, ContactInfo
    
    print("\n" + "="*80)
    print("TEST 5: Enhanced Place Model")
    print("="*80)
    
    # Create enhanced place
    place = EnhancedPlace(
        place_id="HN-TEST-001",
        name="Cà Phê Giảng",
        lat=21.0336,
        lon=105.8506,
        address="39 Nguyen Huu Huan, Hoan Kiem",
        categories=["cafe"],
        multilingual=MultilingualInfo(
            vietnamese={"name": "Cà Phê Giảng", "description": "Nổi tiếng với cà phê trứng"},
            english={"name": "Giang Cafe", "description": "Famous for egg coffee"}
        ),
        opening_hours=OpeningHours.from_string("07:00-22:00"),
        price_info=PriceInfo(
            range="$",
            min_price=25000,
            max_price=60000,
            currency="VND"
        ),
        contact_info=ContactInfo(
            phone="+84 24 3828 8093",
            website="",
            facebook="giangcafe.hanoi"
        )
    )
    
    # Test Vietnamese output
    print("\n1. Vietnamese Output:")
    place_dict_vi = place.to_dict(language='vi')
    print(f"   Name: {place_dict_vi['name']}")
    print(f"   Description: {place_dict_vi['description']}")
    print(f"   Google Maps: {place_dict_vi['google_maps_url'][:60]}...")
    print(f"   Price Range: {place_dict_vi['price_info']['range']}")
    print(f"   Is Open Now: {place_dict_vi['is_open_now']}")
    
    # Test English output
    print("\n2. English Output:")
    place_dict_en = place.to_dict(language='en')
    print(f"   Name: {place_dict_en['name']}")
    print(f"   Description: {place_dict_en['description']}")
    
    print("\n✅ Enhanced Place Model Test Complete!")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "PHASE 1 FEATURE TESTS" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        test_translation_service()
        test_maps_service()
        test_budget_service()
        test_opening_hours()
        test_enhanced_place()
        
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*20 + "✅ ALL TESTS PASSED SUCCESSFULLY! ✅" + " "*22 + "║")
        print("╚" + "="*78 + "╝")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
