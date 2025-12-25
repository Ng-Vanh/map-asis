#!/bin/bash

# 🚀 QUICK START SCRIPT - Map Assistant
# Hướng dẫn nhanh để chạy và test hệ thống

echo "=================================="
echo "MAP ASSISTANT - QUICK START"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓${NC} $service_name is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is NOT running on port $port"
        return 1
    fi
}

echo "📋 Checking prerequisites..."
echo ""

# Check Neo4j
echo "1. Neo4j (Port 7687):"
check_service "Neo4j" 7687
NEO4J_STATUS=$?

# Check Qdrant
echo ""
echo "2. Qdrant (Port 6333):"
check_service "Qdrant" 6333
QDRANT_STATUS=$?

# Check Embedding Service
echo ""
echo "3. Embedding Service (Port 8080):"
check_service "Embedding Service" 8080
EMBEDDING_STATUS=$?

# Check Flask API
echo ""
echo "4. Flask API (Port 8864):"
check_service "Flask API" 8864
API_STATUS=$?

echo ""
echo "=================================="

# If all services running
if [ $NEO4J_STATUS -eq 0 ] && [ $QDRANT_STATUS -eq 0 ] && [ $EMBEDDING_STATUS -eq 0 ] && [ $API_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Tất cả services đang chạy!${NC}"
    echo ""
    echo "🧪 Bạn có thể chạy tests:"
    echo "   python test_services.py"
    echo ""
    echo "📖 Xem documentation:"
    echo "   API_DOCS.md - API documentation"
    echo "   README.md - Overview"
    echo "   EXAMPLES.py - Use cases"
    echo ""
    exit 0
fi

# If some services not running
echo -e "${YELLOW}⚠ Một số services chưa chạy!${NC}"
echo ""
echo "🔧 Hướng dẫn khởi động:"
echo ""

if [ $NEO4J_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Neo4j:${NC}"
    echo "   neo4j start"
    echo "   # hoặc"
    echo "   systemctl start neo4j"
    echo ""
fi

if [ $QDRANT_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Qdrant:${NC}"
    echo "   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant"
    echo ""
fi

if [ $EMBEDDING_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Embedding Service:${NC}"
    echo "   cd serve/"
    echo "   bash serve.sh"
    echo "   # hoặc"
    echo "   python embed_service.py"
    echo ""
fi

if [ $API_STATUS -ne 0 ]; then
    echo -e "${YELLOW}Flask API:${NC}"
    echo "   python main.py"
    echo ""
fi

echo "=================================="
echo ""
echo "📚 Sau khi tất cả services đã chạy:"
echo "   1. Test APIs: python test_services.py"
echo "   2. Xem docs: cat API_DOCS.md"
echo "   3. Thử examples: cat EXAMPLES.py"
echo ""
