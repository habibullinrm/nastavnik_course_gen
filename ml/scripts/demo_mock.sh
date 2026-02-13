#!/bin/bash
# Quick demo of mock mode vs real mode timing

echo "=========================================="
echo "🎭 Mock Mode Demo"
echo "=========================================="
echo ""

echo "This script demonstrates the speed difference between:"
echo "  • Real mode: 2-5 minutes (actual DeepSeek API calls)"
echo "  • Mock mode: 2-5 seconds (pre-saved responses)"
echo ""

echo "Running mock pipeline..."
echo ""

# Set mock mode
export MOCK_LLM=true

# Time the execution
START=$(date +%s)

python3 scripts/run_pipeline_mock.py

END=$(date +%s)
DURATION=$((END - START))

echo ""
echo "=========================================="
echo "⏱️  Mock mode completed in ${DURATION}s"
echo "=========================================="
echo ""
echo "Compare with real mode: ~180-300s (60-100x slower)"
echo ""
echo "Mock mode is perfect for:"
echo "  ✅ Testing validators"
echo "  ✅ CI/CD pipelines"
echo "  ✅ Development without API key"
echo "  ✅ Offline work"
echo ""
