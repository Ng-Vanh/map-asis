import requests
import json
import time
from typing import List, Dict, Optional
import csv

class OSMDataScraper:
    def __init__(self):
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        
    def search_places_by_bbox(self, 
                              bbox: tuple,  # (min_lat, min_lon, max_lat, max_lon)
                              categories: List[str]) -> List[Dict]:
        """
        Tìm địa điểm trong bounding box theo categories
        
        bbox: (20.95, 105.75, 21.15, 105.90) # Hanoi
        categories: ['tourism', 'amenity', 'historic', 'leisure']
        """
        
        # Xây dựng Overpass query
        category_filters = []
        for cat in categories:
            category_filters.append(f'node["{cat}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});')
            category_filters.append(f'way["{cat}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});')
        
        query = f"""
        [out:json][timeout:60];
        (
          {' '.join(category_filters)}
        );
        out body;
        >;
        out skel qt;
        """
        
        print(f"Querying OSM for {len(categories)} categories...")
        response = requests.post(self.overpass_url, data={'data': query})
        
        if response.status_code == 200:
            data = response.json()
            return self.parse_osm_elements(data.get('elements', []))
        else:
            print(f"Error: {response.status_code}")
            return []
    
    def search_specific_place(self, place_name: str, city: str = "Hanoi") -> Optional[Dict]:
        """
        Tìm địa điểm cụ thể theo tên
        """
        params = {
            'q': f"{place_name}, {city}, Vietnam",
            'format': 'json',
            'addressdetails': 1,
            'extratags': 1,
            'namedetails': 1,
            'limit': 1
        }
        
        headers = {'User-Agent': 'HanoiPlacesKG/1.0'}
        response = requests.get(f"{self.nominatim_url}/search", 
                               params=params, 
                               headers=headers)
        
        time.sleep(1)  # Respect rate limit
        
        if response.status_code == 200:
            results = response.json()
            if results:
                return self.parse_nominatim_result(results[0])
        return None
    
    def get_place_details(self, osm_type: str, osm_id: str) -> Optional[Dict]:
        """
        Lấy chi tiết địa điểm từ OSM ID
        osm_type: 'node', 'way', 'relation'
        """
        params = {
            'osm_type': osm_type[0].upper(),  # N, W, R
            'osm_id': osm_id,
            'format': 'json',
            'addressdetails': 1,
            'extratags': 1,
            'namedetails': 1
        }
        
        headers = {'User-Agent': 'HanoiPlacesKG/1.0'}
        response = requests.get(f"{self.nominatim_url}/lookup", 
                               params=params,
                               headers=headers)
        
        time.sleep(1)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                return self.parse_nominatim_result(results[0])
        return None
    
    def parse_osm_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Parse OSM elements thành format chuẩn
        """
        places = []
        
        for elem in elements:
            if elem.get('type') not in ['node', 'way']:
                continue
                
            tags = elem.get('tags', {})
            if not tags.get('name'):
                continue
            
            place = {
                'osm_id': f"{elem['type'][0].upper()}{elem['id']}",
                'osm_type': elem['type'],
                'name': tags.get('name'),
                'name_en': tags.get('name:en'),
                'name_vi': tags.get('name:vi'),
                'lat': elem.get('lat') or elem.get('center', {}).get('lat'),
                'lon': elem.get('lon') or elem.get('center', {}).get('lon'),
                
                # Categories
                'tourism': tags.get('tourism'),
                'amenity': tags.get('amenity'),
                'historic': tags.get('historic'),
                'leisure': tags.get('leisure'),
                'natural': tags.get('natural'),
                'building': tags.get('building'),
                
                # Details
                'description': tags.get('description'),
                'website': tags.get('website') or tags.get('url'),
                'phone': tags.get('phone') or tags.get('contact:phone'),
                'email': tags.get('email') or tags.get('contact:email'),
                'opening_hours': tags.get('opening_hours'),
                
                # Address
                'addr_street': tags.get('addr:street'),
                'addr_housenumber': tags.get('addr:housenumber'),
                'addr_district': tags.get('addr:district'),
                'addr_city': tags.get('addr:city'),
                'addr_postcode': tags.get('addr:postcode'),
                
                # Attributes
                'wheelchair': tags.get('wheelchair'),
                'internet_access': tags.get('internet_access'),
                'cuisine': tags.get('cuisine'),
                'religion': tags.get('religion'),
                'denomination': tags.get('denomination'),
                
                # Wikidata & Wikipedia
                'wikidata': tags.get('wikidata'),
                'wikipedia': tags.get('wikipedia'),
                
                # Images
                'image': tags.get('image'),
                'wikimedia_commons': tags.get('wikimedia_commons'),
                
                # All tags for reference
                'all_tags': tags
            }
            
            places.append(place)
        
        return places
    
    def parse_nominatim_result(self, result: Dict) -> Dict:
        """
        Parse Nominatim result
        """
        return {
            'osm_id': result.get('osm_id'),
            'osm_type': result.get('osm_type'),
            'name': result.get('name'),
            'display_name': result.get('display_name'),
            'lat': float(result.get('lat', 0)),
            'lon': float(result.get('lon', 0)),
            
            'category': result.get('category'),
            'type': result.get('type'),
            'importance': result.get('importance'),
            
            # Address details
            'address': result.get('address', {}),
            
            # Extra tags
            'extratags': result.get('extratags', {}),
            
            # Name variants
            'namedetails': result.get('namedetails', {}),
            
            # Bounding box
            'boundingbox': result.get('boundingbox'),
        }
    
    def export_to_csv(self, places: List[Dict], filename: str):
        """
        Export dữ liệu ra CSV format cho Neo4j import
        """
        if not places:
            print("No places to export")
            return
        
        fieldnames = [
            'place_id', 'osm_id', 'name', 'alt_names', 'description',
            'lat', 'lon', 'address',
            'province_code', 'district_code', 'ward_code',
            'categories', 'subcategories', 'tags',
            'rating', 'review_count', 'popularityScore', 'priceLevel',
            'opening_hours', 'avg_visit_duration', 'seasonality',
            'suitable_for', 'accessibility', 'crowd_level',
            'phone', 'website', 'images',
            'wikidata', 'wikipedia',
            'verified', 'last_updated', 'source'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, place in enumerate(places, 1):
                # Build categories
                categories = []
                if place.get('tourism'):
                    categories.append(place['tourism'])
                if place.get('amenity'):
                    categories.append(place['amenity'])
                if place.get('historic'):
                    categories.append(place['historic'])
                if place.get('leisure'):
                    categories.append(place['leisure'])
                
                # Build alt names
                alt_names = []
                if place.get('name_en'):
                    alt_names.append(place['name_en'])
                if place.get('name_vi') and place['name_vi'] != place.get('name'):
                    alt_names.append(place['name_vi'])
                
                # Build address
                addr_parts = []
                if place.get('addr_housenumber'):
                    addr_parts.append(place['addr_housenumber'])
                if place.get('addr_street'):
                    addr_parts.append(place['addr_street'])
                if place.get('addr_district'):
                    addr_parts.append(place['addr_district'])
                
                row = {
                    'place_id': f"HN-OSM-{idx:04d}",
                    'osm_id': place.get('osm_id', ''),
                    'name': place.get('name', ''),
                    'alt_names': ';'.join(alt_names),
                    'description': place.get('description', ''),
                    'lat': place.get('lat', ''),
                    'lon': place.get('lon', ''),
                    'address': ', '.join(addr_parts) if addr_parts else '',
                    'province_code': 'HN',
                    'district_code': self.extract_district_code(place),
                    'ward_code': '',
                    'categories': ';'.join(categories),
                    'subcategories': place.get('cuisine', ''),
                    'tags': '',
                    'rating': '',
                    'review_count': '',
                    'popularityScore': '',
                    'priceLevel': '',
                    'opening_hours': place.get('opening_hours', ''),
                    'avg_visit_duration': '',
                    'seasonality': 'all-year',
                    'suitable_for': '',
                    'accessibility': place.get('wheelchair', ''),
                    'crowd_level': '',
                    'phone': place.get('phone', ''),
                    'website': place.get('website', ''),
                    'images': place.get('image', ''),
                    'wikidata': place.get('wikidata', ''),
                    'wikipedia': place.get('wikipedia', ''),
                    'verified': 'false',
                    'last_updated': '2025-11-25',
                    'source': 'osm'
                }
                
                writer.writerow(row)
        
        print(f"Exported {len(places)} places to {filename}")
    
    def extract_district_code(self, place: Dict) -> str:
        """
        Extract district code from address
        """
        district = place.get('addr_district') or ''
        district = str(district).lower()
        
        district_map = {
            'hoàn kiếm': 'HK',
            'ba đình': 'BD',
            'đống đa': 'DD',
            'hai bà trưng': 'HBT',
            'tây hồ': 'TH',
            'cầu giấy': 'CG',
            'long biên': 'LB',
            'thanh xuân': 'TX',
            'hoàng mai': 'HM',
            'hà đông': 'HD',
            'nam từ liêm': 'NTL',
            'bắc từ liêm': 'BTL',
        }
        
        for key, code in district_map.items():
            if key in district:
                return code
        
        return ''


# ===== USAGE EXAMPLES =====

def example_1_search_hanoi_tourism():
    """
    Ví dụ 1: Tìm tất cả địa điểm du lịch ở Hà Nội
    """
    scraper = OSMDataScraper()
    
    # Bounding box của Hà Nội
    hanoi_bbox = (20.95, 105.75, 21.15, 105.90)
    
    # Categories quan tâm
    categories = [
        'tourism',   # attractions, hotels, museums
        'amenity',   # restaurants, cafes, bars
        'historic',  # monuments, memorials
        'leisure',   # parks, gardens
    ]
    
    places = scraper.search_places_by_bbox(hanoi_bbox, categories)
    print(f"Found {len(places)} places")
    
    # Export to CSV
    # scraper.export_to_csv(places, 'hanoi_places_osm.csv')
    
    return places


def example_2_search_specific_places():
    """
    Ví dụ 2: Tìm các địa điểm cụ thể
    """
    scraper = OSMDataScraper()
    
    famous_places = [
        "Hoan Kiem Lake",
        "Temple of Literature",
        "Ho Chi Minh Mausoleum",
        "One Pillar Pagoda",
        "Old Quarter",
        "West Lake",
        "Tran Quoc Pagoda",
        "Vietnam Museum of Ethnology",
        "Hanoi Opera House",
        "Long Bien Bridge"
    ]
    
    results = []
    for place_name in famous_places:
        print(f"Searching: {place_name}")
        result = scraper.search_specific_place(place_name)
        if result:
            results.append(result)
            print(f"  Found: {result.get('display_name')}")
        time.sleep(1)
    
    return results


def example_3_targeted_queries():
    """
    Ví dụ 3: Query theo loại địa điểm cụ thể
    """
    scraper = OSMDataScraper()
    hanoi_bbox = (20.95, 105.75, 21.15, 105.90)
    
    # Query cafes
    query_cafes = f"""
    [out:json][timeout:30];
    (
      node["amenity"="cafe"]({hanoi_bbox[0]},{hanoi_bbox[1]},{hanoi_bbox[2]},{hanoi_bbox[3]});
      way["amenity"="cafe"]({hanoi_bbox[0]},{hanoi_bbox[1]},{hanoi_bbox[2]},{hanoi_bbox[3]});
    );
    out body;
    """
    
    response = requests.post(scraper.overpass_url, data={'data': query_cafes})
    cafes = scraper.parse_osm_elements(response.json().get('elements', []))
    
    print(f"Found {len(cafes)} cafes in Hanoi")
    scraper.export_to_csv(cafes, 'hanoi_cafes_osm.csv')
    
    return cafes


if __name__ == "__main__":
    # Chạy example 1: Lấy tất cả địa điểm du lịch
    print("=== Example 1: Search all tourism places ===")
    places = example_1_search_hanoi_tourism()
    
    # Hiển thị 5 địa điểm đầu
    print("\nFirst 5 places:")
    for place in places[:13]:
        print(f"- {place['name']} ({place.get('tourism') or place.get('amenity')})")
        print(f"  Location: {place['lat']}, {place['lon']}")
        print(f"  Wikidata: {place.get('wikidata')}")
        print()