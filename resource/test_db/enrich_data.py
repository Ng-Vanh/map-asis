"""
Data Enrichment Script for Phase 1
Enriches place data with:
- Opening hours
- Contact information (phone, website)
- Price information
- English translations

Uses OpenStreetMap Overpass API and Google Places API (optional)
"""

import pandas as pd
import requests
import time
import json
from typing import Dict, List, Optional
import os
from pathlib import Path


class DataEnricher:
    """Enrich place data with additional information"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.osm_cache = {}
    
    def get_osm_details(self, osm_id: str, osm_type: str = "node") -> Optional[Dict]:
        """
        Get detailed information from OpenStreetMap
        
        Args:
            osm_id: OSM ID (e.g., "104770283")
            osm_type: OSM type (node, way, relation)
        
        Returns:
            Dictionary with OSM details
        """
        # Check cache
        cache_key = f"{osm_type}/{osm_id}"
        if cache_key in self.osm_cache:
            return self.osm_cache[cache_key]
        
        # Query Overpass API
        query = f"""
        [out:json];
        {osm_type}({osm_id});
        out body;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if 'elements' in data and len(data['elements']) > 0:
                element = data['elements'][0]
                tags = element.get('tags', {})
                
                # Extract relevant information
                details = {
                    'opening_hours': tags.get('opening_hours', ''),
                    'phone': tags.get('phone', tags.get('contact:phone', '')),
                    'website': tags.get('website', tags.get('contact:website', '')),
                    'email': tags.get('email', tags.get('contact:email', '')),
                    'facebook': tags.get('contact:facebook', ''),
                    'name_en': tags.get('name:en', ''),
                    'description_en': tags.get('description:en', ''),
                    'cuisine': tags.get('cuisine', ''),
                    'diet': tags.get('diet:vegetarian', ''),
                    'outdoor_seating': tags.get('outdoor_seating', ''),
                    'wifi': tags.get('internet_access', ''),
                    'wheelchair': tags.get('wheelchair', ''),
                    'payment_cards': tags.get('payment:cards', ''),
                }
                
                # Cache result
                self.osm_cache[cache_key] = details
                
                return details
            
        except Exception as e:
            print(f"Error fetching OSM details for {osm_id}: {e}")
        
        return None
    
    def enrich_csv_data(self, 
                       input_csv: str, 
                       output_csv: str,
                       start_row: int = 0,
                       max_rows: int = 100,
                       delay: float = 1.0):
        """
        Enrich CSV data with OSM details
        
        Args:
            input_csv: Input CSV file path
            output_csv: Output CSV file path
            start_row: Starting row (for resuming)
            max_rows: Maximum rows to process
            delay: Delay between API calls (seconds)
        """
        print(f"Loading CSV: {input_csv}")
        df = pd.read_csv(input_csv)
        
        # Add new columns if they don't exist
        new_columns = [
            'opening_hours', 'phone', 'website', 'email', 'facebook',
            'name_en', 'description_en', 'cuisine', 'diet',
            'outdoor_seating', 'wifi', 'wheelchair', 'payment_cards'
        ]
        
        for col in new_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Process rows
        end_row = min(start_row + max_rows, len(df))
        print(f"Processing rows {start_row} to {end_row} (total: {len(df)})")
        
        for idx in range(start_row, end_row):
            row = df.iloc[idx]
            osm_id = str(row['osm_id']).replace('N', '').replace('W', '').replace('R', '')
            
            # Determine OSM type
            osm_type = 'node'
            if str(row['osm_id']).startswith('W'):
                osm_type = 'way'
            elif str(row['osm_id']).startswith('R'):
                osm_type = 'relation'
            
            print(f"\n[{idx+1}/{end_row}] Processing: {row['name']} (OSM: {osm_type}/{osm_id})")
            
            # Get OSM details
            details = self.get_osm_details(osm_id, osm_type)
            
            if details:
                # Update dataframe
                for key, value in details.items():
                    if key in df.columns and value:
                        df.at[idx, key] = value
                        print(f"  ✓ {key}: {value[:50] if len(str(value)) > 50 else value}")
            else:
                print(f"  ✗ No details found")
            
            # Save progress periodically
            if (idx + 1) % 10 == 0:
                df.to_csv(output_csv, index=False)
                print(f"\n💾 Progress saved to {output_csv}")
            
            # Delay to respect API rate limits
            time.sleep(delay)
        
        # Final save
        df.to_csv(output_csv, index=False)
        print(f"\n✅ Enrichment complete! Saved to {output_csv}")
        print(f"Processed {end_row - start_row} rows")
    
    def estimate_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimate price ranges based on category
        
        Args:
            df: DataFrame with place data
        
        Returns:
            DataFrame with estimated prices
        """
        # Add price columns if they don't exist
        if 'price_range' not in df.columns:
            df['price_range'] = ''
        if 'min_price' not in df.columns:
            df['min_price'] = 0
        if 'max_price' not in df.columns:
            df['max_price'] = 0
        
        # Default prices by category (VND)
        price_estimates = {
            'restaurant': {'min': 80000, 'max': 300000, 'range': '$$'},
            'cafe': {'min': 30000, 'max': 100000, 'range': '$'},
            'fast_food': {'min': 50000, 'max': 150000, 'range': '$'},
            'hotel': {'min': 300000, 'max': 2000000, 'range': '$$$'},
            'bar': {'min': 50000, 'max': 200000, 'range': '$$'},
            'museum': {'min': 0, 'max': 40000, 'range': '$'},
            'temple': {'min': 0, 'max': 30000, 'range': '$'},
            'spa': {'min': 200000, 'max': 1000000, 'range': '$$$'},
        }
        
        for idx, row in df.iterrows():
            categories = str(row['categories']).lower() if pd.notna(row['categories']) else ''
            
            # Find matching category
            for category, prices in price_estimates.items():
                if category in categories:
                    df.at[idx, 'min_price'] = prices['min']
                    df.at[idx, 'max_price'] = prices['max']
                    df.at[idx, 'price_range'] = prices['range']
                    break
        
        return df
    
    def generate_sample_enriched_data(self, output_file: str, num_samples: int = 10):
        """
        Generate sample enriched data for testing
        
        Args:
            output_file: Output JSON file
            num_samples: Number of samples
        """
        samples = []
        
        sample_places = [
            {
                'place_id': 'HN-SAMPLE-001',
                'name': 'Cà Phê Giảng',
                'name_en': 'Giang Cafe',
                'lat': 21.0336,
                'lon': 105.8506,
                'address': '39 Nguyen Huu Huan, Hoan Kiem',
                'categories': ['cafe'],
                'opening_hours': 'Mo-Su 07:00-22:00',
                'phone': '+84 24 3828 8093',
                'website': '',
                'price_range': '$',
                'min_price': 25000,
                'max_price': 60000,
                'description_en': 'Famous for egg coffee, a Hanoi specialty',
            },
            {
                'place_id': 'HN-SAMPLE-002',
                'name': 'Nhà Hàng Chả Cá Lã Vọng',
                'name_en': 'Cha Ca La Vong Restaurant',
                'lat': 21.0314,
                'lon': 105.8519,
                'address': '14 Cha Ca, Hoan Kiem',
                'categories': ['restaurant'],
                'opening_hours': 'Mo-Su 11:00-21:00',
                'phone': '+84 24 3825 3929',
                'website': 'https://chacalavong.vn',
                'price_range': '$$',
                'min_price': 150000,
                'max_price': 300000,
                'description_en': 'Legendary restaurant serving traditional Hanoi fish dish since 1871',
            },
            {
                'place_id': 'HN-SAMPLE-003',
                'name': 'Văn Miếu - Quốc Tử Giám',
                'name_en': 'Temple of Literature',
                'lat': 21.0277,
                'lon': 105.8355,
                'address': '58 Quoc Tu Giam, Dong Da',
                'categories': ['temple', 'museum', 'historical'],
                'opening_hours': 'Tu-Su 08:00-17:00',
                'phone': '+84 24 3845 2917',
                'website': 'https://vanmieu.gov.vn',
                'price_range': '$',
                'min_price': 30000,
                'max_price': 30000,
                'description_en': "Vietnam's first national university, built in 1070",
            }
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_places, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Generated {len(sample_places)} sample enriched places: {output_file}")


def main():
    """Main enrichment workflow"""
    enricher = DataEnricher()
    
    # Paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'resource' / 'data'
    
    input_csv = data_dir / 'hanoi_places_osm_filtered_full_row.csv'
    output_csv = data_dir / 'hanoi_places_enriched.csv'
    sample_json = data_dir / 'sample_enriched_places.json'
    
    print("=== Data Enrichment Script ===\n")
    print("Options:")
    print("1. Enrich CSV with OSM data (WARNING: Slow, rate-limited)")
    print("2. Add price estimates to CSV")
    print("3. Generate sample enriched data")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        print("\n⚠️  WARNING: This will make many API calls and is rate-limited.")
        print("OSM Overpass API has strict rate limits. Recommended: 1-2 seconds delay between requests.")
        
        start_row = int(input("Start from row (0 for beginning): ").strip() or 0)
        max_rows = int(input("Max rows to process (100 recommended): ").strip() or 100)
        delay = float(input("Delay between requests in seconds (1.5 recommended): ").strip() or 1.5)
        
        confirm = input(f"\nWill process rows {start_row} to {start_row + max_rows}. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            enricher.enrich_csv_data(
                str(input_csv),
                str(output_csv),
                start_row=start_row,
                max_rows=max_rows,
                delay=delay
            )
    
    elif choice == '2':
        print("\n📊 Adding price estimates...")
        if output_csv.exists():
            df = pd.read_csv(output_csv)
        else:
            df = pd.read_csv(input_csv)
        
        df = enricher.estimate_prices(df)
        df.to_csv(output_csv, index=False)
        print(f"✅ Prices added to {output_csv}")
    
    elif choice == '3':
        print("\n📝 Generating sample enriched data...")
        enricher.generate_sample_enriched_data(str(sample_json))
    
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
