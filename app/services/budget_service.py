"""
Price and Budget Service (Phase 1)
- Estimate costs for places and itineraries
- Filter by budget
- Compare prices
"""

from typing import Dict, List, Optional
from enum import Enum


class PriceRange(Enum):
    """Standard price range categories"""
    BUDGET = "$"        # < 100k VND
    MODERATE = "$$"     # 100k - 300k VND
    EXPENSIVE = "$$$"   # 300k - 500k VND
    LUXURY = "$$$$"     # > 500k VND


class BudgetService:
    """Service for price estimation and budget management"""
    
    def __init__(self):
        # Default price estimates by category (VND per person)
        self.default_prices = {
            # Food & Drink
            "restaurant": {"min": 80000, "max": 300000},
            "cafe": {"min": 30000, "max": 100000},
            "fast_food": {"min": 50000, "max": 150000},
            "street_food": {"min": 20000, "max": 50000},
            "bar": {"min": 50000, "max": 200000},
            "pub": {"min": 100000, "max": 300000},
            
            # Attractions
            "museum": {"min": 0, "max": 40000},  # Many free
            "temple": {"min": 0, "max": 30000},
            "park": {"min": 0, "max": 20000},
            "zoo": {"min": 50000, "max": 100000},
            "theatre": {"min": 100000, "max": 500000},
            "cinema": {"min": 80000, "max": 150000},
            
            # Accommodation
            "hotel": {"min": 300000, "max": 2000000},
            "hostel": {"min": 100000, "max": 400000},
            "guesthouse": {"min": 200000, "max": 800000},
            
            # Shopping
            "shopping_mall": {"min": 100000, "max": 1000000},
            "market": {"min": 50000, "max": 300000},
            
            # Services
            "spa": {"min": 200000, "max": 1000000},
            "massage": {"min": 150000, "max": 500000},
            
            # Transportation (per trip)
            "taxi": {"min": 30000, "max": 200000},
            "bus": {"min": 7000, "max": 15000},
            "motorbike_rental": {"min": 100000, "max": 150000},  # per day
        }
    
    def get_price_range_symbol(self, avg_price: int) -> str:
        """
        Convert average price to symbol
        
        Args:
            avg_price: Average price in VND
        
        Returns:
            Price range symbol ($, $$, $$$, $$$$)
        """
        if avg_price < 100000:
            return PriceRange.BUDGET.value
        elif avg_price < 300000:
            return PriceRange.MODERATE.value
        elif avg_price < 500000:
            return PriceRange.EXPENSIVE.value
        else:
            return PriceRange.LUXURY.value
    
    def estimate_place_cost(self, 
                           category: str,
                           num_people: int = 1,
                           custom_price: Optional[Dict] = None) -> Dict:
        """
        Estimate cost for visiting a place
        
        Args:
            category: Place category (restaurant, cafe, etc.)
            num_people: Number of people
            custom_price: Custom price dict with 'min' and 'max' (optional)
        
        Returns:
            Dictionary with price estimation
        """
        # Use custom price if provided, otherwise use default
        if custom_price and 'min' in custom_price and 'max' in custom_price:
            price_info = custom_price
        else:
            # Get default price for category
            price_info = self.default_prices.get(category.lower(), 
                                                {"min": 50000, "max": 200000})
        
        min_total = price_info['min'] * num_people
        max_total = price_info['max'] * num_people
        avg_total = (min_total + max_total) / 2
        
        return {
            "category": category,
            "num_people": num_people,
            "per_person": {
                "min": price_info['min'],
                "max": price_info['max'],
                "avg": int((price_info['min'] + price_info['max']) / 2)
            },
            "total": {
                "min": int(min_total),
                "max": int(max_total),
                "avg": int(avg_total)
            },
            "price_range": self.get_price_range_symbol(int(avg_total / num_people)),
            "currency": "VND"
        }
    
    def estimate_itinerary_cost(self,
                               places: List[Dict],
                               num_people: int = 1,
                               include_transport: bool = True,
                               transport_budget: int = 200000) -> Dict:
        """
        Estimate total cost for an itinerary
        
        Args:
            places: List of places with category info
            num_people: Number of people
            include_transport: Whether to include transport costs
            transport_budget: Estimated transport budget per person
        
        Returns:
            Dictionary with cost breakdown
        """
        total_min = 0
        total_max = 0
        breakdown = []
        
        for place in places:
            category = place.get('categories', ['attraction'])[0] if place.get('categories') else 'attraction'
            
            # Check if place has custom price info
            custom_price = None
            if 'price_info' in place:
                price_info = place['price_info']
                if price_info and 'min_price' in price_info and 'max_price' in price_info:
                    custom_price = {
                        'min': price_info['min_price'],
                        'max': price_info['max_price']
                    }
            
            cost = self.estimate_place_cost(category, num_people, custom_price)
            
            total_min += cost['total']['min']
            total_max += cost['total']['max']
            
            breakdown.append({
                "place": place.get('name', 'Unknown'),
                "category": category,
                "cost": cost
            })
        
        # Add transport if requested
        if include_transport:
            transport_total = transport_budget * num_people
            total_min += transport_total
            total_max += transport_total
            
            breakdown.append({
                "place": "Transportation",
                "category": "transport",
                "cost": {
                    "total": {
                        "min": transport_total,
                        "max": transport_total,
                        "avg": transport_total
                    }
                }
            })
        
        avg_total = (total_min + total_max) / 2
        
        return {
            "num_people": num_people,
            "total_places": len(places),
            "total_cost": {
                "min": int(total_min),
                "max": int(total_max),
                "avg": int(avg_total)
            },
            "per_person": {
                "min": int(total_min / num_people),
                "max": int(total_max / num_people),
                "avg": int(avg_total / num_people)
            },
            "breakdown": breakdown,
            "currency": "VND"
        }
    
    def filter_by_budget(self,
                        places: List[Dict],
                        max_budget_per_person: int,
                        num_people: int = 1) -> List[Dict]:
        """
        Filter places that fit within budget
        
        Args:
            places: List of places
            max_budget_per_person: Maximum budget per person (VND)
            num_people: Number of people
        
        Returns:
            Filtered list of places within budget
        """
        filtered = []
        
        for place in places:
            category = place.get('categories', ['attraction'])[0] if place.get('categories') else 'attraction'
            
            # Check custom price or use default
            custom_price = None
            if 'price_info' in place:
                price_info = place['price_info']
                if price_info and 'min_price' in price_info:
                    custom_price = {
                        'min': price_info['min_price'],
                        'max': price_info.get('max_price', price_info['min_price'] * 2)
                    }
            
            cost = self.estimate_place_cost(category, num_people, custom_price)
            
            # Check if average cost per person fits budget
            if cost['per_person']['avg'] <= max_budget_per_person:
                place['estimated_cost'] = cost
                filtered.append(place)
        
        return filtered
    
    def compare_prices(self, places: List[Dict]) -> Dict:
        """
        Compare prices of multiple places
        
        Args:
            places: List of places to compare
        
        Returns:
            Comparison with rankings
        """
        comparisons = []
        
        for place in places:
            category = place.get('categories', ['attraction'])[0] if place.get('categories') else 'attraction'
            cost = self.estimate_place_cost(category, 1)
            
            comparisons.append({
                "place": place.get('name', 'Unknown'),
                "category": category,
                "price_range": cost['price_range'],
                "avg_cost": cost['per_person']['avg']
            })
        
        # Sort by average cost
        comparisons.sort(key=lambda x: x['avg_cost'])
        
        # Add rankings
        for i, comp in enumerate(comparisons, 1):
            comp['rank'] = i
            if i == 1:
                comp['note'] = "Most affordable"
            elif i == len(comparisons):
                comp['note'] = "Most expensive"
        
        return {
            "total_compared": len(comparisons),
            "comparisons": comparisons,
            "price_range": {
                "lowest": comparisons[0]['avg_cost'] if comparisons else 0,
                "highest": comparisons[-1]['avg_cost'] if comparisons else 0
            }
        }


# Singleton instance
_budget_service = None

def get_budget_service() -> BudgetService:
    """Get singleton budget service instance"""
    global _budget_service
    if _budget_service is None:
        _budget_service = BudgetService()
    return _budget_service
