import torch
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import json
import os


EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
import requests
class QdrantPlaceSearch:
    """Qdrant search for place details using semantic search"""
    
    def __init__(
        self, 
        qdrant_url: str = QDRANT_HOST,
        qdrant_port: int = QDRANT_PORT,
        collection_name: str = QDRANT_COLLECTION,
        embedding_service_url: str = EMBEDDING_SERVICE_URL
    ):
        """
        Initialize Qdrant search client
        
        Args:
            qdrant_url: Qdrant server URL
            qdrant_port: Qdrant server port
            collection_name: Collection name in Qdrant
            embedding_model: Pre-loaded embedding model (optional)
        """
        self.client = QdrantClient(host=qdrant_url, port=qdrant_port)
        self.collection_name = collection_name
        self.embedding_service_url = embedding_service_url
        
        print(f"✓ Embedding service: {embedding_service_url}")
        print(f"✓ Connected to Qdrant: {qdrant_url}:{qdrant_port}")
        print(f"✓ Using collection: {collection_name}")
    
    def _get_embedding(self, text: str):
        resp = requests.post(self.embedding_service_url, json={"texts": [text]}, timeout=10)
        resp.raise_for_status()
        return resp.json()["embeddings"][0]
    
    def search_place_details(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Tìm kiếm thông tin chi tiết địa điểm bằng semantic search
        
        Args:
            query: Câu truy vấn (VD: "tìm thông tin chi tiết Hồ Tây")
            top_k: Số lượng kết quả trả về
            score_threshold: Ngưỡng điểm tương đồng tối thiểu (0-1)
            
        Returns:
            List các địa điểm với thông tin chi tiết và score
        """
        # Encode query
        query_vector = self._get_embedding(query)
        
        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results
        results = []
        for hit in search_result:
            result = {
                'place_id': hit.id,
                'score': hit.score,
                'payload': hit.payload
            }
            results.append(result)
        
        return results
    
    
    def print_search_results(self, results: List[Dict], title: str = "KẾT QUẢ TÌM KIẾM"):
        print(f"\n{'='*80}")
        print(f"{title}")
        print(f"{'='*80}")
        
        if not results:
            print("Không tìm thấy kết quả nào.")
            return
        
        print(f"Tìm thấy {len(results)} địa điểm:\n")
        
        for i, result in enumerate(results, 1):
            payload = result['payload']
            score = result.get('score', 0)
            
            print(f"{i}. {payload.get('name', 'N/A')}")
            print(f"   Độ liên quan: {score:.3f}")
            print(f"    Place ID: {result['place_id']}")
            
            # Basic info
           
            print(payload["text"])
            print("-" * 80)



if __name__ == "__main__":
    try:
        searcher = QdrantPlaceSearch()
        
        # Search
        results = searcher.search_place_details(
            query="Lăng Bác",
            top_k=3,
            score_threshold=0.0
        )

        searcher.print_search_results(results, "Thông tin Search")


    except Exception as e: 
        print(f"\nLỗi: {str(e)}")
        print(" Đảm bảo Qdrant server đang chạy và collection 'map_assistant' tồn tại")