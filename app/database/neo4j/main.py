from neo4j import GraphDatabase
from typing import List, Dict, Optional
import json
import os

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH_USER = os.getenv("NEO4J_USER", "neo4j")
AUTH_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")
AUTH = (AUTH_USER, AUTH_PASSWORD)


class Neo4jSpatialQuery:
    """Class quản lý các truy vấn spatial trên Neo4j"""
    
    def __init__(self, uri=URI, auth=AUTH):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        """Đóng kết nối"""
        self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def find_places_by_category(
        self, 
        lat: float, 
        lon: float, 
        categories: List[str],
        radius_meters: int = 1000,
        limit: int = 20
    ) -> List[Dict]:
        """
        Tìm địa điểm theo category xung quanh tọa độ
        
        Args:
            lat: Vĩ độ
            lon: Kinh độ
            categories: Danh sách category cần tìm (VD: ['restaurant', 'cafe'])
            radius_meters: Bán kính tìm kiếm (mét)
            limit: Số lượng kết quả tối đa
            
        Returns:
            List các địa điểm với thông tin: name, address, distance, categories
        """
        query = """
        WITH point({latitude: $lat, longitude: $lon}) AS myLocation
        
        MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category)
        WHERE p.location IS NOT NULL 
          AND point.distance(p.location, myLocation) <= $radius
          AND c.name IN $categories
        
        WITH DISTINCT p, myLocation,
             collect(DISTINCT c.name) AS matched_categories,
             round(point.distance(p.location, myLocation)) AS distance
        
        RETURN 
            p.place_id AS place_id,
            p.name AS name,
            p.address AS address,
            matched_categories AS categories,
            distance
        ORDER BY distance ASC
        LIMIT $limit
        """
        
        with self.driver.session(database="neo4j") as session:
            result = session.run(
                query,
                lat=lat,
                lon=lon,
                radius=radius_meters,
                categories=categories,
                limit=limit
            )
            
            places = []
            for record in result:
                places.append({
                    'place_id': record['place_id'],
                    'name': record['name'],
                    'address': record['address'],
                    'categories': record['categories'],
                    'distance_meters': record['distance']
                })
            
            return places


    def find_places_by_multiple_categories(
        self,
        lat: float,
        lon: float,
        category_groups: List[List[str]],
        radius_meters: int = 1000,
        limit: int = 20
    ) -> Dict[str, List[Dict]]:
        """
        Tìm địa điểm theo NHIỀU nhóm category cùng lúc
        
        Args:
            lat: Vĩ độ
            lon: Kinh độ
            category_groups: Danh sách các nhóm category
                VD: [['restaurant', 'cafe'], ['museum', 'gallery'], ['hotel']]
            radius_meters: Bán kính
            limit: Số kết quả mỗi nhóm
            
        Returns:
            Dictionary với key là tên nhóm, value là list địa điểm
        """
        results = {}
        
        for group in category_groups:
            group_name = '_'.join(group[:2])  # Tạo tên nhóm
            places = self.find_places_by_category(
                lat, lon, group, radius_meters, limit
            )
            results[group_name] = places
        
        return results


    def find_places_nearby_landmark(
        self,
        landmark_name: str,
        categories: List[str],
        radius_meters: int = 1000,
        limit: int = 20
    ) -> List[Dict]:
        """
        Tìm địa điểm xung quanh 1 landmark có sẵn
        VD: Tìm nhà hàng gần "Hồ Gươm"
        
        Args:
            landmark_name: Tên địa danh
            categories: Danh sách category
            radius_meters: Bán kính
            limit: Số kết quả
            
        Returns:
            Dict với landmark info và list địa điểm
        """
        query = """
        // Tìm landmark
        MATCH (landmark:Place)
        WHERE toLower(landmark.name) CONTAINS toLower($landmark_name)
          AND landmark.location IS NOT NULL
        
        WITH landmark
        LIMIT 1
        
        // Tìm địa điểm xung quanh landmark
        MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category)
        WHERE p.location IS NOT NULL
          AND point.distance(p.location, landmark.location) <= $radius
          AND c.name IN $categories
          AND p.place_id <> landmark.place_id
        
        WITH DISTINCT p, landmark,
             collect(DISTINCT c.name) AS matched_categories,
             round(point.distance(p.location, landmark.location)) AS distance
        
        RETURN 
            landmark.name AS landmark_name,
            landmark.address AS landmark_address,
            p.place_id AS place_id,
            p.name AS name,
            p.address AS address,
            matched_categories AS categories,
            distance
        ORDER BY distance ASC
        LIMIT $limit
        """
        
        with self.driver.session(database="neo4j") as session:
            result = session.run(
                query,
                landmark_name=landmark_name,
                categories=categories,
                radius=radius_meters,
                limit=limit
            )
            
            places = []
            landmark_info = None
            
            for record in result:
                if landmark_info is None:
                    landmark_info = {
                        'name': record['landmark_name'],
                        'address': record['landmark_address']
                    }
                
                places.append({
                    'place_id': record['place_id'],
                    'name': record['name'],
                    'address': record['address'],
                    'categories': record['categories'],
                    'distance_meters': record['distance']
                })
            
            return {
                'landmark': landmark_info,
                'nearby_places': places
            }


    def find_places_in_district(
        self,
        district_code: str,
        categories: List[str],
        limit: int = 20
    ) -> List[Dict]:
        """
        Tìm địa điểm theo category trong 1 quận/huyện
        
        Args:
            district_code: Mã quận/huyện
            categories: Danh sách category
            limit: Số kết quả
            
        Returns:
            List địa điểm
        """
        query = """
        MATCH (p:Place)-[:IN_DISTRICT]->(d:District {code: $district_code})
        MATCH (p)-[:HAS_CATEGORY]->(c:Category)
        WHERE c.name IN $categories
        
        WITH DISTINCT p,
             collect(DISTINCT c.name) AS matched_categories
        
        RETURN 
            p.place_id AS place_id,
            p.name AS name,
            p.address AS address,
            matched_categories AS categories
        ORDER BY p.name ASC
        LIMIT $limit
        """
        
        with self.driver.session(database="neo4j") as session:
            result = session.run(
                query,
                district_code=district_code,
                categories=categories,
                limit=limit
            )
            
            places = []
            for record in result:
                places.append({
                    'place_id': record['place_id'],
                    'name': record['name'],
                    'address': record['address'],
                    'categories': record['categories']
                })
            
            return places


    def get_available_categories(self, limit: int = 50) -> List[Dict]:
        """
        Lấy danh sách tất cả categories có trong database
        
        Returns:
            List categories với số lượng địa điểm
        """
        query = """
        MATCH (c:Category)<-[:HAS_CATEGORY]-(p:Place)
        RETURN 
            c.name AS category,
            count(p) AS place_count
        ORDER BY place_count DESC
        LIMIT $limit
        """
        
        with self.driver.session(database="neo4j") as session:
            result = session.run(query, limit=limit)
            
            categories = []
            for record in result:
                categories.append({
                    'category': record['category'],
                    'place_count': record['place_count']
                })
            
            return categories


    def print_places(self, places: List[Dict], title: str = "KẾT QUẢ TÌM KIẾM"):
        """Hiển thị kết quả đẹp mắt"""
        print(f"\n{'='*80}")
        print(f" {title}")
        print(f"{'='*80}")
        
        if not places:
            print(" Không tìm thấy địa điểm nào.")
            return
        
        print(f"Tìm thấy {len(places)} địa điểm:\n")
        
        for i, place in enumerate(places, 1):
            # Distance (if available)
            dist_str = f" {place.get('distance_meters', 0)}m" if 'distance_meters' in place else ""
            
            # Categories
            cats = ', '.join(place.get('categories', []))
            
            print(f"{i}. {place['name']}")
            print(f"   {dist_str}")
            print(f"    {cats}")
            print(f"    {place.get('address', 'N/A')}")
            print(f"    {place.get('place_id', 'N/A')}")
            print("-" * 80)


# ==================== DEMO USAGE ====================

def demo_basic_search(lat=21.0285, lon=105.8542,categories=['restaurant', 'cafe'],radius_meters=1000,limit=10):
    """Demo 1: Tìm nhà hàng/cafe xung quanh tọa độ"""
    print("\n DEMO 1: Tìm nhà hàng và cafe gần Hồ Gươm")
    
    with Neo4jSpatialQuery() as query:
        places = query.find_places_by_category(
            lat=lat,
            lon=lon,
            categories=categories,
            radius_meters=1000,
            limit=10
        )
        
        query.print_places(places, "Nhà hàng & Cafe gần Hồ Gươm")


def demo_landmark_search(place = "Yu Tan",categories=['hotel'],radius_meters=2000,limit=10):
    """Demo 2: Tìm địa điểm xung quanh landmark"""
    print(f"\n DEMO 2: Tìm khách sạn gần {place}")
    
    with Neo4jSpatialQuery() as query:
        result = query.find_places_nearby_landmark(
            landmark_name=place,
            categories=categories,
            radius_meters=radius_meters,
            limit=limit
        )
        
        if result['landmark']:
            print(f"\n Landmark: {result['landmark']['name']}")
            print(f"   {result['landmark']['address']}")
        
        query.print_places(result['nearby_places'], "Khách sạn gần {place}")


def demo_district_search():
    """Demo 3: Tìm địa điểm trong quận"""
    print("\n DEMO 3: Tìm museum trong quận Hoàn Kiếm")

    with Neo4jSpatialQuery() as query:
        places = query.find_places_in_district(
            district_code="HK",  # Hoàn Kiếm
            categories=['museum', 'gallery', 'historical'],
            limit=10
        )
        
        query.print_places(places, "Museum & Gallery ở Quận Hoàn Kiếm")


def demo_multiple_categories():
    """Demo 4: Tìm nhiều loại địa điểm cùng lúc"""
    print("\n DEMO 4: Tìm nhiều loại địa điểm xung quanh")
    
    with Neo4jSpatialQuery() as query:
        results = query.find_places_by_multiple_categories(
            lat=21.0285,
            lon=105.8542,
            category_groups=[
                ['restaurant', 'cafe'],
                ['museum', 'gallery'],
                ['hotel', 'accommodation']
            ],
            radius_meters=1500,
            limit=5
        )
        
        for group_name, places in results.items():
            query.print_places(places, f"Nhóm: {group_name.replace('_', ' & ').title()}")


def show_available_categories():
    """Demo 5: Xem các category có sẵn"""
    print("\nDanh sách Categories có trong Database:")
    print("="*80)
    
    with Neo4jSpatialQuery() as query:
        categories = query.get_available_categories(limit=30)
        
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat['category']} ({cat['place_count']} địa điểm)")


if __name__ == "__main__":

    # Chạy các demo
    # show_available_categories()
    # demo_basic_search()
    demo_landmark_search()
    # demo_district_search()
    # demo_multiple_categories()

