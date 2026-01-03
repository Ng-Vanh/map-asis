"""
Import Enhanced CSV Data to Neo4j
Supports Phase 1 features: opening_hours, price_range, contact info, multilingual
"""

from neo4j import GraphDatabase
import pandas as pd
import os
from typing import Dict, List
import json


class Neo4jImporter:
    """Import place data from CSV to Neo4j with Phase 1 enhancements"""
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all data (use with caution!)"""
        with self.driver.session() as session:
            print("⚠️  Clearing database...")
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")
    
    def create_constraints_and_indexes(self):
        """Create constraints and indexes for better performance"""
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT place_id IF NOT EXISTS FOR (p:Place) REQUIRE p.place_id IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE INDEX place_name IF NOT EXISTS FOR (p:Place) ON (p.name)",
                "CREATE INDEX place_location IF NOT EXISTS FOR (p:Place) ON (p.location)",
            ]
            
            print("Creating constraints and indexes...")
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✓ {constraint[:50]}...")
                except Exception as e:
                    print(f"⚠️  {constraint[:50]}... (may already exist)")
    
    def import_places_from_csv(self, csv_path: str, batch_size: int = 100):
        """
        Import places from CSV file with Phase 1 enhancements
        
        Args:
            csv_path: Path to CSV file
            batch_size: Number of records to process at once
        """
        print(f"\n📊 Loading CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        
        print(f"Found {len(df)} places")
        print(f"Columns: {list(df.columns)}")
        
        # Check for Phase 1 columns
        phase1_columns = ['opening_hours', 'phone', 'website', 'name_en', 
                         'price_range', 'min_price', 'max_price']
        has_phase1 = any(col in df.columns for col in phase1_columns)
        
        if has_phase1:
            print("✅ Phase 1 enhanced data detected!")
        else:
            print("⚠️  Basic data only (consider running enrich_data.py)")
        
        # Process in batches
        total = len(df)
        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            batch_df = df.iloc[start_idx:end_idx]
            
            self._import_batch(batch_df)
            
            print(f"✓ Imported {end_idx}/{total} places")
        
        print(f"\n✅ Import complete! Total: {total} places")
    
    def _import_batch(self, df: pd.DataFrame):
        """Import a batch of places"""
        with self.driver.session() as session:
            for _, row in df.iterrows():
                self._import_single_place(session, row)
    
    def _import_single_place(self, session, row):
        """Import a single place with all Phase 1 features"""
        
        # Prepare place properties
        place_props = {
            'place_id': str(row['place_id']),
            'osm_id': str(row.get('osm_id', '')),
            'name': str(row['name']),
            'lat': float(row['lat']),
            'lon': float(row['lon']),
        }
        
        # Optional basic fields
        if pd.notna(row.get('address')):
            place_props['address'] = str(row['address'])
        
        # Phase 1 fields
        if pd.notna(row.get('opening_hours')):
            place_props['opening_hours'] = str(row['opening_hours'])
        
        if pd.notna(row.get('phone')):
            place_props['phone'] = str(row['phone'])
        
        if pd.notna(row.get('website')):
            place_props['website'] = str(row['website'])
        
        if pd.notna(row.get('email')):
            place_props['email'] = str(row['email'])
        
        if pd.notna(row.get('facebook')):
            place_props['facebook'] = str(row['facebook'])
        
        # English fields
        if pd.notna(row.get('name_en')):
            place_props['name_en'] = str(row['name_en'])
        
        if pd.notna(row.get('description_en')):
            place_props['description_en'] = str(row['description_en'])
        
        # Price fields
        if pd.notna(row.get('price_range')):
            place_props['price_range'] = str(row['price_range'])
        
        if pd.notna(row.get('min_price')):
            place_props['min_price'] = int(row['min_price'])
        
        if pd.notna(row.get('max_price')):
            place_props['max_price'] = int(row['max_price'])
        
        # Additional fields
        if pd.notna(row.get('cuisine')):
            place_props['cuisine'] = str(row['cuisine'])
        
        if pd.notna(row.get('wifi')):
            place_props['wifi'] = str(row['wifi'])
        
        if pd.notna(row.get('wheelchair')):
            place_props['wheelchair'] = str(row['wheelchair'])
        
        # Create Place node with location point
        query = """
        MERGE (p:Place {place_id: $place_id})
        SET p += $props,
            p.location = point({latitude: $lat, longitude: $lon})
        """
        
        session.run(query, place_id=place_props['place_id'], 
                   props=place_props, 
                   lat=place_props['lat'], 
                   lon=place_props['lon'])
        
        # Import categories
        categories_str = row.get('categories', '')
        if pd.notna(categories_str) and categories_str:
            categories = [c.strip() for c in str(categories_str).split(',') if c.strip()]
            for category in categories:
                self._link_category(session, place_props['place_id'], category)
        
        # Import subcategories
        subcategories_str = row.get('subcategories', '')
        if pd.notna(subcategories_str) and subcategories_str:
            subcategories = [c.strip() for c in str(subcategories_str).split(',') if c.strip()]
            for subcategory in subcategories:
                self._link_category(session, place_props['place_id'], subcategory)
    
    def _link_category(self, session, place_id: str, category: str):
        """Link place to category"""
        query = """
        MATCH (p:Place {place_id: $place_id})
        MERGE (c:Category {name: $category})
        MERGE (p)-[:HAS_CATEGORY]->(c)
        """
        session.run(query, place_id=place_id, category=category)
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with self.driver.session() as session:
            stats = {}
            
            # Count places
            result = session.run("MATCH (p:Place) RETURN count(p) as count")
            stats['total_places'] = result.single()['count']
            
            # Count categories
            result = session.run("MATCH (c:Category) RETURN count(c) as count")
            stats['total_categories'] = result.single()['count']
            
            # Count places with opening hours
            result = session.run("MATCH (p:Place) WHERE p.opening_hours IS NOT NULL RETURN count(p) as count")
            stats['places_with_hours'] = result.single()['count']
            
            # Count places with prices
            result = session.run("MATCH (p:Place) WHERE p.price_range IS NOT NULL RETURN count(p) as count")
            stats['places_with_prices'] = result.single()['count']
            
            # Count places with English names
            result = session.run("MATCH (p:Place) WHERE p.name_en IS NOT NULL RETURN count(p) as count")
            stats['places_with_english'] = result.single()['count']
            
            # Count places with contact info
            result = session.run("MATCH (p:Place) WHERE p.phone IS NOT NULL OR p.website IS NOT NULL RETURN count(p) as count")
            stats['places_with_contact'] = result.single()['count']
            
            return stats


def main():
    """Main import workflow"""
    
    # Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")
    
    # CSV file path
    csv_path = "resource/data/hanoi_places_osm_filtered_full_row.csv"
    enriched_csv = "resource/data/hanoi_places_enriched.csv"
    
    print("="*80)
    print("  NEO4J IMPORTER - Phase 1 Enhanced")
    print("="*80)
    
    # Check which CSV to use
    if os.path.exists(enriched_csv):
        print(f"\n✅ Found enriched CSV: {enriched_csv}")
        csv_to_import = enriched_csv
    else:
        print(f"\n⚠️  Enriched CSV not found, using basic CSV: {csv_path}")
        print("   💡 Tip: Run 'python resource/test_db/enrich_data.py' to add Phase 1 features")
        csv_to_import = csv_path
    
    # Initialize importer
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Ask before clearing
        print("\n⚠️  WARNING: This will clear existing data in Neo4j!")
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("Import cancelled.")
            return
        
        # Clear and setup
        importer.clear_database()
        importer.create_constraints_and_indexes()
        
        # Import data
        print("\n" + "="*80)
        print("  IMPORTING DATA")
        print("="*80)
        importer.import_places_from_csv(csv_to_import, batch_size=100)
        
        # Show statistics
        print("\n" + "="*80)
        print("  DATABASE STATISTICS")
        print("="*80)
        stats = importer.get_statistics()
        
        print(f"\n📊 Total places: {stats['total_places']}")
        print(f"🏷️  Total categories: {stats['total_categories']}")
        print(f"\n✨ Phase 1 Features:")
        print(f"   ⏰ Places with opening hours: {stats['places_with_hours']} ({stats['places_with_hours']/stats['total_places']*100:.1f}%)")
        print(f"   💰 Places with prices: {stats['places_with_prices']} ({stats['places_with_prices']/stats['total_places']*100:.1f}%)")
        print(f"   🌐 Places with English names: {stats['places_with_english']} ({stats['places_with_english']/stats['total_places']*100:.1f}%)")
        print(f"   📞 Places with contact info: {stats['places_with_contact']} ({stats['places_with_contact']/stats['total_places']*100:.1f}%)")
        
        print("\n✅ Import successful!")
        
        # Recommendations
        if stats['places_with_hours'] < stats['total_places'] * 0.1:
            print("\n💡 Recommendation: Run data enrichment to add more Phase 1 features")
            print("   python resource/test_db/enrich_data.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        importer.close()


if __name__ == "__main__":
    main()
