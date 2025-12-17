from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from app.database.neo4j import Neo4jSpatialQuery
from app.database.qdrant import QdrantPlaceSearch
from app.models.model import AIService

import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_AUTH = (
    os.getenv("NEO4J_USER", "neo4j"),
    os.getenv("NEO4J_PASSWORD", "12345678")
)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)

neo4j_query = Neo4jSpatialQuery(uri=NEO4J_URI, auth=NEO4J_AUTH)
qdrant_search = QdrantPlaceSearch(
    qdrant_url=QDRANT_HOST,
    qdrant_port=QDRANT_PORT,
    collection_name="map_assistant_v2"
)
ai_service = AIService()

def get_info_details(name):
    res_qdrant = qdrant_search.search_place_details(
        query=name,
        top_k=2
    )
    data = ""
    for item in res_qdrant:
        summary = item.get("payload", {}).get("summary", "")
        data += f"{summary}\n"

    ai_response = ai_service.generate_response(
        user_message=f"Can you provide detailed information about the place named '{name}'?",
        data_extend=data
    )
    return jsonify({"response": ai_response})

