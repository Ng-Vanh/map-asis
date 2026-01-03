#!/bin/bash

# Quick Start Guide for Phase 1 Features

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        MAP ASSISTANT - PHASE 1 QUICK START GUIDE              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Phase 1 Features:${NC}"
echo "  ✅ Multilingual Support (Vietnamese & English)"
echo "  ✅ Maps & Navigation Integration"
echo "  ✅ Opening Hours Tracking"
echo "  ✅ Budget Estimation & Filtering"
echo ""

echo -e "${YELLOW}🔍 Quick Tests:${NC}"
echo ""

# Test 1: Multilingual Chat (English)
echo -e "${GREEN}1. Test Multilingual Chat (English):${NC}"
echo ""
echo "curl -X POST http://localhost:8864/chat \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Find romantic cafes with nice views\", \"language\": \"en\"}'"
echo ""

# Test 2: Search with Budget
echo -e "${GREEN}2. Test Budget-based Itinerary:${NC}"
echo ""
echo "curl -X POST http://localhost:8864/plan_itinerary \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"location\": \"Old Quarter\","
echo "    \"duration_hours\": 8,"
echo "    \"num_people\": 2,"
echo "    \"preferences\": {"
echo "      \"budget\": 500000,"
echo "      \"companions\": \"couple\""
echo "    },"
echo "    \"language\": \"vi\""
echo "  }'"
echo ""

# Test 3: Search with Directions
echo -e "${GREEN}3. Test Search with Directions:${NC}"
echo ""
echo "curl -X POST http://localhost:8864/search_places \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"lat\": 21.0285,"
echo "    \"lon\": 105.8542,"
echo "    \"categories\": [\"restaurant\"],"
echo "    \"radius_meters\": 1000,"
echo "    \"language\": \"en\","
echo "    \"user_location\": {\"lat\": 21.0300, \"lon\": 105.8550}"
echo "  }'"
echo ""

echo -e "${YELLOW}📚 Documentation:${NC}"
echo "  - Phase 1 Implementation: PHASE1_IMPLEMENTATION.md"
echo "  - API Documentation: API_DOCS.md"
echo "  - Architecture: ARCHITECTURE.md"
echo ""

echo -e "${YELLOW}🛠️ Data Enrichment (Optional):${NC}"
echo "  cd resource/test_db"
echo "  python enrich_data.py"
echo ""
echo "  Options:"
echo "    1. Enrich CSV with OSM data (slow, rate-limited)"
echo "    2. Add price estimates"
echo "    3. Generate sample enriched data"
echo ""

echo -e "${YELLOW}🧪 Run Tests:${NC}"
echo "  python test_phase1.py"
echo ""

echo -e "${GREEN}✅ Ready to test Phase 1 features!${NC}"
echo ""
