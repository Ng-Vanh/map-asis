#!/bin/bash

# Quick Start Guide for Map Assistant with Phase 1 Features
# Run this script to test all Phase 1 features

echo "======================================================================"
echo "🚀 MAP ASSISTANT - PHASE 1 QUICK START"
echo "======================================================================"
echo ""

# Check conda environment
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda first."
    exit 1
fi

# Activate environment
echo "📦 Activating conda environment..."
source ~/miniconda3/bin/activate

# Check Python version
echo "🐍 Python version:"
python --version

echo ""
echo "======================================================================"
echo "🧪 RUNNING PHASE 1 TESTS"
echo "======================================================================"
echo ""

# Run Phase 1 tests
python test_phase1.py

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ ALL TESTS PASSED!"
    echo "======================================================================"
    echo ""
    echo "📚 Next steps:"
    echo ""
    echo "1. 🌐 Test Multilingual:"
    echo "   python -c \"from app.services.translation_service import get_translation_service; print(get_translation_service().translate('Tìm quán cafe', 'en'))\""
    echo ""
    echo "2. 🗺️  Test Maps:"
    echo "   python -c \"from app.services.maps_service import get_maps_service; print(get_maps_service().get_place_url(21.0285, 105.8542, 'Hồ Gươm'))\""
    echo ""
    echo "3. 💰 Test Budget:"
    echo "   python -c \"from app.services.budget_service import get_budget_service; print(get_budget_service().estimate_place_cost('restaurant', 2))\""
    echo ""
    echo "4. 🚀 Start Flask API:"
    echo "   python main.py"
    echo ""
    echo "5. 🧪 Test API with curl:"
    echo "   curl -X POST http://localhost:8864/chat -H 'Content-Type: application/json' -d '{\"message\": \"Find cafes near Hoan Kiem Lake\", \"language\": \"en\"}'"
    echo ""
    echo "📖 Documentation:"
    echo "   - Phase 1 Features: PHASE1_FEATURES.md"
    echo "   - API Docs: API_DOCS.md"
    echo "   - Architecture: ARCHITECTURE.md"
    echo ""
else
    echo ""
    echo "❌ Tests failed. Please check the error messages above."
    exit 1
fi
