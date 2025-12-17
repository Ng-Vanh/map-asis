from neo4j import GraphDatabase
import os

# Cấu hình kết nối
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678") 

def find_nearby_places(lat, lon, radius_meters=1000, limit=20):
    # Sử dụng context manager để đảm bảo driver tự đóng kết nối khi xong
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        
        # Query Cypher với tham số (parameters)
        cypher_query = """
        WITH point({latitude: $lat, longitude: $lon}) AS myLocation
        MATCH (p:Place)
        WHERE p.location IS NOT NULL 
          AND point.distance(p.location, myLocation) <= $radius
        RETURN 
            p.name AS PlaceName, 
            p.address AS Address, 
            round(point.distance(p.location, myLocation)) AS DistanceInMeters
        ORDER BY DistanceInMeters ASC
        LIMIT toInteger($limit)
        """
        
        # Thực thi query
        # database_="neo4j" là database mặc định
        records, summary, keys = driver.execute_query(
            cypher_query,
            lat=lat,
            lon=lon,
            radius=radius_meters,
            limit=limit,
            database_="neo4j"
        )
        
        # Xử lý kết quả trả về
        print(f"Tìm thấy {len(records)} địa điểm trong bán kính {radius_meters}m:\n")
        print(f"{'KHOẢNG CÁCH':<15} | {'TÊN ĐỊA ĐIỂM':<30} | {'ĐỊA CHỈ'}")
        print("-" * 80)
        
        results = []
        for record in records:
            # Truy cập dữ liệu như dictionary
            place_name = record["PlaceName"]
            address = record["Address"] if record["Address"] else "N/A" # Xử lý nếu address null
            dist = record["DistanceInMeters"]
            
            print(f"{dist}m".ljust(15) + f" | {place_name[:28]:<30} | {address[:30]}...")
            
            # Lưu vào list nếu muốn trả về dữ liệu
            results.append({
                "name": place_name,
                "address": address,
                "distance": dist
            })
            
        return results

def find_places_by_category(lat, lon, radius=1000, keywords=['restaurant', 'food']):
    query = """
    WITH point({latitude: $lat, longitude: $lon}) AS myLocation,
         $keywords AS searchKeywords
    
    MATCH (p:Place)-[:HAS_CATEGORY]->(c:Category)
    WHERE p.location IS NOT NULL 
      AND point.distance(p.location, myLocation) <= $radius
      AND ANY(k IN searchKeywords WHERE toLower(c.name) CONTAINS toLower(k))
      
    RETURN DISTINCT 
        p.name AS name,
        p.address AS address,
        p.rating AS rating,
        p.priceLevel AS price,           // ← Thêm mức giá
        p.opening_hours AS hours,
        round(point.distance(p.location, myLocation)) AS distance
    ORDER BY distance ASC
    LIMIT 20
    """
    
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        records, _, _ = driver.execute_query(
            query,
            lat=lat, 
            lon=lon, 
            radius=radius, 
            keywords=keywords,
            database_="neo4j"
        )
        
        print(f"--- Tìm thấy {len(records)} địa điểm phù hợp ---")
        for r in records:
            rating_str = f"⭐ {r['rating']}" if r['rating'] else "Chưa đánh giá"
            price_str = f"| Giá: {'$' * r['price']}" if r['price'] else ""
            
            print(f"[{r['distance']}m] {r['name']} | {rating_str} {price_str}")
            print(f"   Đ/c: {r['address']}")
            if r['hours']:
                print(f"   Giờ mở cửa: {r['hours']}")
            print("-" * 30)
def inspect_database_schema():
    """
    Hàm tiện ích giúp in ra cấu trúc hiện tại của Database
    """
    print("\n=== KIỂM TRA SCHEMA NEO4J ===")
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # 1. Kiểm tra các Node Labels
        labels = driver.execute_query("CALL db.labels()", database_="neo4j")[0]
        print(f" Node Labels hiện có: {[r[0] for r in labels]}")

        # 2. Kiểm tra các Relationship Types
        rels = driver.execute_query("CALL db.relationshipTypes()", database_="neo4j")[0]
        print(f" Relationship Types (Mối quan hệ): {[r[0] for r in rels]}")

        # 3. Kiểm tra mẫu dữ liệu của Node 'Place'
        print("\n Mẫu dữ liệu của Node (Place):")
        sample_query = "MATCH (p:Place) RETURN p LIMIT 1"
        records, _, _ = driver.execute_query(sample_query, database_="neo4j")
        
        if records:
            node = records[0]['p']
            print(f"   - Các thuộc tính (Properties): {list(node.keys())}")
            
            # Check kỹ field tags
            if 'tags' in node:
                print(f"   - Kiểu dữ liệu 'tags': {type(node['tags'])} (Giá trị: {node['tags']})")
                if isinstance(node['tags'], list):
                    print("     -> Tags đang lưu dạng LIST (Dùng được hàm x IN p.tags)")
                elif isinstance(node['tags'], str):
                    print("     -> Tags đang lưu dạng STRING (Cần dùng split hoặc CONTAINS)")
            else:
                print("   - Cảnh báo: Không tìm thấy trường 'tags' trong node này.")
        else:
            print("   - Không tìm thấy node Place nào trong DB.")

        # 4. Đếm số lượng
        count = driver.execute_query("MATCH (n:Place) RETURN count(n) as c", database_="neo4j")[0][0]['c']
        print(f"\n Tổng số địa điểm (Place): {count}")


if __name__ == "__main__":
    # find_nearby_places(lat=21.0285, lon=105.8542, radius_meters=1000)
    find_places_by_category(lat=21.0285, lon=105.8542, radius=1000, keywords=['restaurant', 'food'])
    # inspect_database_schema()