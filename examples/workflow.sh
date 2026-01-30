#!/bin/bash
# Example workflow: Check context, compress if needed, then proceed

SCRIPT_DIR="$(dirname "$0")/../scripts"
HISTORY_FILE="${1:-examples/sample_history.json}"
THRESHOLD="${2:-0.7}"

echo "🧠 Memory Manager Workflow"
echo "=========================="
echo ""

# Step 1: Check current token count
echo "Step 1: Checking token count..."
RESULT=$(python3 "$SCRIPT_DIR/token_counter.py" --file "$HISTORY_FILE")
echo "$RESULT" | python3 -m json.tool

PERCENT=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['percent'])")
WARNING=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['warning'])")

echo ""
echo "Current usage: ${PERCENT} (${WARNING})"
echo ""

# Step 2: Check if compression needed
echo "Step 2: Checking threshold (${THRESHOLD})..."
python3 "$SCRIPT_DIR/token_counter.py" --file "$HISTORY_FILE" --threshold "$THRESHOLD" --quiet
EXIT_CODE=$?

if [ $EXIT_CODE -eq 1 ]; then
    echo "⚠️  Threshold exceeded! Compression recommended."
    echo ""
    
    # Step 3: Compress (dry-run first)
    echo "Step 3: Running compression (dry-run)..."
    python3 "$SCRIPT_DIR/compressor.py" --input "$HISTORY_FILE" --keep-recent 3 --dry-run
    echo ""
    
    echo "To actually compress, run:"
    echo "  python3 $SCRIPT_DIR/compressor.py --input $HISTORY_FILE --output compressed.json --keep-recent 3"
else
    echo "✅ Under threshold. Safe to proceed."
fi

echo ""
echo "Done!"
