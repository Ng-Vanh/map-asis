"""
Maps Integration Service (Phase 1)
- Generate Google Maps URLs
- Calculate directions and distances
- Provide navigation information
"""

from typing import Dict, List, Optional, Tuple
import urllib.parse
import math


class MapsService:
    """Service for maps integration and navigation"""
    
    def __init__(self):
        self.google_maps_base = "https://www.google.com/maps"
    
    def get_place_url(self, lat: float, lon: float, place_name: str = "") -> str:
        """
        Generate Google Maps URL for a place
        
        Args:
            lat: Latitude
            lon: Longitude
            place_name: Optional place name for better search
        
        Returns:
            Google Maps URL
        """
        if place_name:
            # Search by name and coordinates
            query = f"{place_name}"
            encoded_query = urllib.parse.quote(query)
            return f"{self.google_maps_base}/search/?api=1&query={encoded_query}&query_place_id={lat},{lon}"
        else:
            # Direct coordinates
            return f"{self.google_maps_base}/search/?api=1&query={lat},{lon}"
    
    def get_directions_url(self, 
                          origin_lat: float, 
                          origin_lon: float,
                          dest_lat: float, 
                          dest_lon: float,
                          mode: str = "driving") -> str:
        """
        Generate Google Maps directions URL
        
        Args:
            origin_lat, origin_lon: Starting point
            dest_lat, dest_lon: Destination
            mode: Travel mode (driving, walking, bicycling, transit)
        
        Returns:
            Google Maps directions URL
        """
        origin = f"{origin_lat},{origin_lon}"
        destination = f"{dest_lat},{dest_lon}"
        
        # Valid modes: driving, walking, bicycling, transit
        valid_modes = ["driving", "walking", "bicycling", "transit"]
        if mode not in valid_modes:
            mode = "driving"
        
        return (f"{self.google_maps_base}/dir/?api=1"
                f"&origin={origin}"
                f"&destination={destination}"
                f"&travelmode={mode}")
    
    def calculate_distance(self, 
                          lat1: float, lon1: float,
                          lat2: float, lon2: float) -> Dict[str, float]:
        """
        Calculate distance between two points using Haversine formula
        
        Returns:
            Dictionary with distance in meters and kilometers
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_phi/2) ** 2 + 
             math.cos(phi1) * math.cos(phi2) * 
             math.sin(delta_lambda/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance_m = R * c
        distance_km = distance_m / 1000
        
        return {
            "meters": round(distance_m, 2),
            "kilometers": round(distance_km, 2)
        }
    
    def estimate_travel_time(self, distance_meters: float, 
                            mode: str = "driving") -> Dict[str, int]:
        """
        Estimate travel time based on distance and mode
        (Rough estimation - for better accuracy, use Google Maps API)
        
        Args:
            distance_meters: Distance in meters
            mode: Travel mode
        
        Returns:
            Dictionary with time in minutes and hours
        """
        # Average speeds (km/h)
        speeds = {
            "walking": 5,
            "bicycling": 15,
            "driving": 30,  # City driving
            "transit": 25   # Public transport
        }
        
        speed = speeds.get(mode, 30)
        distance_km = distance_meters / 1000
        
        # Time in hours
        time_hours = distance_km / speed
        time_minutes = int(time_hours * 60)
        
        return {
            "minutes": time_minutes,
            "hours": round(time_hours, 2)
        }
    
    def get_travel_info(self,
                       origin: Tuple[float, float],
                       destination: Tuple[float, float],
                       mode: str = "driving") -> Dict:
        """
        Get comprehensive travel information
        
        Args:
            origin: (lat, lon) tuple
            destination: (lat, lon) tuple
            mode: Travel mode
        
        Returns:
            Dictionary with distance, time, and directions URL
        """
        origin_lat, origin_lon = origin
        dest_lat, dest_lon = destination
        
        # Calculate distance
        distance = self.calculate_distance(origin_lat, origin_lon, 
                                           dest_lat, dest_lon)
        
        # Estimate time
        travel_time = self.estimate_travel_time(distance['meters'], mode)
        
        # Generate directions URL
        directions_url = self.get_directions_url(
            origin_lat, origin_lon,
            dest_lat, dest_lon,
            mode
        )
        
        return {
            "distance": distance,
            "estimated_time": travel_time,
            "mode": mode,
            "directions_url": directions_url
        }
    
    def get_multi_stop_route(self,
                            stops: List[Tuple[float, float]],
                            mode: str = "driving") -> Dict:
        """
        Calculate route information for multiple stops
        
        Args:
            stops: List of (lat, lon) tuples
            mode: Travel mode
        
        Returns:
            Dictionary with total distance, time, and waypoints
        """
        if len(stops) < 2:
            return {"error": "Need at least 2 stops"}
        
        total_distance_m = 0
        total_time_min = 0
        segments = []
        
        for i in range(len(stops) - 1):
            origin = stops[i]
            destination = stops[i + 1]
            
            travel_info = self.get_travel_info(origin, destination, mode)
            
            total_distance_m += travel_info['distance']['meters']
            total_time_min += travel_info['estimated_time']['minutes']
            
            segments.append({
                "from": i + 1,
                "to": i + 2,
                "distance": travel_info['distance'],
                "time": travel_info['estimated_time']
            })
        
        # Generate multi-stop directions URL
        waypoints = "|".join([f"{lat},{lon}" for lat, lon in stops[1:-1]])
        origin = f"{stops[0][0]},{stops[0][1]}"
        destination = f"{stops[-1][0]},{stops[-1][1]}"
        
        if waypoints:
            route_url = (f"{self.google_maps_base}/dir/?api=1"
                        f"&origin={origin}"
                        f"&destination={destination}"
                        f"&waypoints={waypoints}"
                        f"&travelmode={mode}")
        else:
            route_url = self.get_directions_url(
                stops[0][0], stops[0][1],
                stops[-1][0], stops[-1][1],
                mode
            )
        
        return {
            "total_stops": len(stops),
            "total_distance": {
                "meters": round(total_distance_m, 2),
                "kilometers": round(total_distance_m / 1000, 2)
            },
            "total_time": {
                "minutes": total_time_min,
                "hours": round(total_time_min / 60, 2)
            },
            "mode": mode,
            "route_url": route_url,
            "segments": segments
        }
    
    def suggest_transport_mode(self, distance_meters: float) -> str:
        """
        Suggest best transport mode based on distance
        
        Args:
            distance_meters: Distance in meters
        
        Returns:
            Suggested mode
        """
        distance_km = distance_meters / 1000
        
        if distance_km < 1:
            return "walking"
        elif distance_km < 5:
            return "bicycling"
        elif distance_km < 20:
            return "driving"
        else:
            return "transit"


# Singleton instance
_maps_service = None

def get_maps_service() -> MapsService:
    """Get singleton maps service instance"""
    global _maps_service
    if _maps_service is None:
        _maps_service = MapsService()
    return _maps_service
