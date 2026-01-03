"""
Interactive Demo for Phase 1 Features
Run: source ~/miniconda3/bin/activate && python demo_phase1.py
"""

import sys


def print_banner(text):
    """Print formatted banner"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def demo_translation():
    """Demo translation service"""
    print_banner("🌐 DEMO 1: MULTILINGUAL SUPPORT")
    
    from app.services.translation_service import get_translation_service
    
    translator = get_translation_service()
    
    print("1️⃣  Auto-detect language:")
    test_cases = [
        "Tìm quán cafe gần Hồ Gươm",
        "Find restaurants near Hoan Kiem Lake",
        "Cho tôi biết về Văn Miếu"
    ]
    
    for text in test_cases:
        lang = translator.detect_language(text)
        print(f"   '{text}' → Language: {lang.upper()}")
    
    print("\n2️⃣  Vietnamese → English translation:")
    vn_texts = [
        "Hồ Gươm là địa điểm nổi tiếng ở Hà Nội",
        "Quán cafe này có view đẹp",
        "Lịch trình 1 ngày tham quan phố cổ"
    ]
    
    for vn in vn_texts:
        en = translator.translate(vn, 'en')
        print(f"   VN: {vn}")
        print(f"   EN: {en}\n")
    
    input("Press Enter to continue...")


def demo_maps():
    """Demo maps service"""
    print_banner("🗺️  DEMO 2: MAPS & NAVIGATION")
    
    from app.services.maps_service import get_maps_service
    
    maps = get_maps_service()
    
    print("1️⃣  Generate Google Maps URL:")
    url = maps.get_place_url(21.0285, 105.8542, "Hồ Gươm")
    print(f"   Place: Hồ Gươm (Hoan Kiem Lake)")
    print(f"   URL: {url}\n")
    
    print("2️⃣  Calculate distance:")
    distance = maps.calculate_distance(
        21.0285, 105.8542,  # Hồ Gươm
        21.0277, 105.8355   # Văn Miếu
    )
    print(f"   From: Hồ Gươm")
    print(f"   To: Văn Miếu")
    print(f"   Distance: {distance['meters']:.0f}m ({distance['kilometers']:.2f}km)\n")
    
    print("3️⃣  Get travel information:")
    travel = maps.get_travel_info(
        (21.0285, 105.8542),
        (21.0277, 105.8355),
        mode='walking'
    )
    print(f"   Mode: {travel['mode']}")
    print(f"   Distance: {travel['distance']['kilometers']} km")
    print(f"   Estimated time: {travel['estimated_time']['minutes']} minutes")
    print(f"   Directions: {travel['directions_url'][:60]}...\n")
    
    print("4️⃣  Multi-stop route:")
    stops = [
        (21.0285, 105.8542),  # Hồ Gươm
        (21.0277, 105.8355),  # Văn Miếu  
        (21.0336, 105.8506)   # Old Quarter
    ]
    route = maps.get_multi_stop_route(stops, 'driving')
    print(f"   Stops: {route['total_stops']}")
    print(f"   Total distance: {route['total_distance']['kilometers']} km")
    print(f"   Total time: {route['total_time']['minutes']} minutes\n")
    
    print("5️⃣  Transport suggestions:")
    distances = [500, 2000, 5000, 20000]
    for dist in distances:
        mode = maps.suggest_transport_mode(dist)
        print(f"   {dist}m → {mode}")
    
    input("\nPress Enter to continue...")


def demo_budget():
    """Demo budget service"""
    print_banner("💰 DEMO 3: BUDGET ESTIMATION")
    
    from app.services.budget_service import get_budget_service
    
    budget = get_budget_service()
    
    print("1️⃣  Estimate cost by category:")
    categories = [
        ('cafe', 2),
        ('restaurant', 2),
        ('museum', 4),
        ('hotel', 2)
    ]
    
    for category, people in categories:
        cost = budget.estimate_place_cost(category, people)
        print(f"   {category.capitalize()} ({people} people):")
        print(f"     Per person: {cost['per_person']['min']:,} - {cost['per_person']['max']:,} VND")
        print(f"     Total: {cost['total']['avg']:,} VND ({cost['price_range']})\n")
    
    print("2️⃣  Itinerary cost estimation:")
    places = [
        {'name': 'Breakfast Cafe', 'categories': ['cafe']},
        {'name': 'Temple of Literature', 'categories': ['museum']},
        {'name': 'Lunch Restaurant', 'categories': ['restaurant']},
        {'name': 'Shopping', 'categories': ['shopping_mall']},
        {'name': 'Dinner Restaurant', 'categories': ['restaurant']}
    ]
    
    itinerary_cost = budget.estimate_itinerary_cost(
        places,
        num_people=2,
        include_transport=True
    )
    
    print(f"   Places: {itinerary_cost['total_places']}")
    print(f"   People: {itinerary_cost['num_people']}")
    print(f"   Total cost: {itinerary_cost['total_cost']['min']:,} - {itinerary_cost['total_cost']['max']:,} VND")
    print(f"   Per person: {itinerary_cost['per_person']['avg']:,} VND\n")
    
    print("   Breakdown:")
    for item in itinerary_cost['breakdown']:
        place_name = item['place']
        total = item['cost'].get('total', {}).get('avg', 0)
        print(f"     - {place_name}: {total:,} VND")
    
    print("\n3️⃣  Filter by budget:")
    all_places = [
        {'name': 'Budget Cafe', 'categories': ['cafe']},
        {'name': 'Luxury Restaurant', 'categories': ['restaurant']},
        {'name': 'Free Museum', 'categories': ['museum']},
        {'name': 'Expensive Spa', 'categories': ['spa']}
    ]
    
    budget_limit = 150000  # 150k VND per person
    filtered = budget.filter_by_budget(all_places, budget_limit, 1)
    
    print(f"   Budget limit: {budget_limit:,} VND/person")
    print(f"   Places within budget: {len(filtered)}/{len(all_places)}")
    for place in filtered:
        avg_cost = place['estimated_cost']['per_person']['avg']
        print(f"     ✓ {place['name']}: {avg_cost:,} VND")
    
    input("\nPress Enter to continue...")


def demo_opening_hours():
    """Demo opening hours"""
    print_banner("⏰ DEMO 4: OPENING HOURS")
    
    from app.models.enhanced_model import OpeningHours
    from datetime import datetime
    
    print("1️⃣  Create opening hours:")
    hours = OpeningHours(
        monday="09:00-22:00",
        tuesday="09:00-22:00",
        wednesday="09:00-22:00",
        thursday="09:00-22:00",
        friday="09:00-23:00",
        saturday="10:00-23:00",
        sunday="10:00-22:00"
    )
    
    print("   Monday-Thursday: 09:00-22:00")
    print("   Friday: 09:00-23:00")
    print("   Saturday: 10:00-23:00")
    print("   Sunday: 10:00-22:00\n")
    
    print("2️⃣  Check if open now:")
    now = datetime.now()
    is_open = hours.is_open_now()
    
    print(f"   Current time: {now.strftime('%A, %H:%M')}")
    print(f"   Status: {'🟢 OPEN' if is_open else '🔴 CLOSED'}\n")
    
    print("3️⃣  Parse from string:")
    simple_hours = OpeningHours.from_string("09:00-22:00")
    print(f"   Input: '09:00-22:00'")
    print(f"   Parsed: Open daily 09:00-22:00")
    
    input("\nPress Enter to continue...")


def demo_enhanced_place():
    """Demo enhanced place model"""
    print_banner("📍 DEMO 5: ENHANCED PLACE MODEL")
    
    from app.models.enhanced_model import (
        EnhancedPlace, MultilingualInfo, OpeningHours,
        PriceInfo, ContactInfo
    )
    
    print("Creating enhanced place with all Phase 1 features...\n")
    
    place = EnhancedPlace(
        place_id="DEMO-001",
        name="Cà Phê Giảng",
        lat=21.0336,
        lon=105.8506,
        address="39 Nguyen Huu Huan, Hoan Kiem",
        categories=["cafe"],
        multilingual=MultilingualInfo(
            vietnamese={
                "name": "Cà Phê Giảng",
                "description": "Nổi tiếng với cà phê trứng, một đặc sản của Hà Nội"
            },
            english={
                "name": "Giang Cafe",
                "description": "Famous for egg coffee, a Hanoi specialty"
            }
        ),
        opening_hours=OpeningHours(
            monday="07:00-22:00",
            tuesday="07:00-22:00",
            wednesday="07:00-22:00",
            thursday="07:00-22:00",
            friday="07:00-22:00",
            saturday="07:00-22:00",
            sunday="07:00-22:00"
        ),
        price_info=PriceInfo(
            range="$",
            min_price=25000,
            max_price=60000,
            currency="VND"
        ),
        contact_info=ContactInfo(
            phone="+84 24 3828 8093"
        )
    )
    
    print("📱 Vietnamese version:")
    vn_dict = place.to_dict('vi')
    print(f"   Name: {vn_dict['name']}")
    print(f"   Description: {vn_dict['description']}")
    print(f"   Status: {'🟢 Open' if vn_dict['is_open_now'] else '🔴 Closed'}")
    print(f"   Price: {vn_dict['price_info']['range']} ({vn_dict['price_info']['min_price']:,} - {vn_dict['price_info']['max_price']:,} VND)")
    print(f"   Contact: {vn_dict['contact_info']['phone']}")
    print(f"   Maps: {vn_dict['google_maps_url'][:60]}...\n")
    
    print("🌐 English version:")
    en_dict = place.to_dict('en')
    print(f"   Name: {en_dict['name']}")
    print(f"   Description: {en_dict['description']}")
    print(f"   Status: {'🟢 Open' if en_dict['is_open_now'] else '🔴 Closed'}")
    print(f"   Price: {en_dict['price_info']['range']} ({en_dict['price_info']['min_price']:,} - {en_dict['price_info']['max_price']:,} VND)")
    
    input("\nPress Enter to continue...")


def main():
    """Run interactive demo"""
    print("\n" + "="*80)
    print("  🚀 MAP ASSISTANT - PHASE 1 INTERACTIVE DEMO")
    print("="*80)
    print("\n  This demo showcases all Phase 1 features:")
    print("  1. 🌐 Multilingual Support (Vietnamese ↔ English)")
    print("  2. 🗺️  Maps Integration (URLs, Directions, Routes)")
    print("  3. 💰 Budget Estimation (Cost calculation, Filtering)")
    print("  4. ⏰ Opening Hours (Real-time status)")
    print("  5. 📍 Enhanced Place Model (Complete place information)")
    print("\n" + "="*80)
    
    input("\nPress Enter to start demo...")
    
    try:
        demo_translation()
        demo_maps()
        demo_budget()
        demo_opening_hours()
        demo_enhanced_place()
        
        print_banner("🎉 DEMO COMPLETE!")
        print("✅ All Phase 1 features demonstrated successfully!\n")
        print("Next steps:")
        print("  1. Run full test suite: python test_phase1.py")
        print("  2. Start Flask API: python main.py")
        print("  3. Read docs: PHASE1_FEATURES.md")
        print("  4. Try API calls: Check PHASE1_FEATURES.md for examples\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
