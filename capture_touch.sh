#!/bin/bash
# Simple touch coordinate capture script

echo "=========================================="
echo "Touch Coordinate Capture"
echo "=========================================="
echo ""
echo "디바이스에서 원하는 위치를 터치하면"
echo "좌표가 출력됩니다."
echo ""
echo "Ctrl+C로 종료할 수 있습니다."
echo ""
echo "=========================================="
echo ""

# Monitor touch events
adb shell getevent | grep -E "ABS_MT_POSITION" | while read line; do
    if echo "$line" | grep -q "0035"; then
        # X coordinate
        x_hex=$(echo "$line" | awk '{print $NF}')
        x_dec=$((16#$x_hex))
        echo "X: $x_dec"
    elif echo "$line" | grep -q "0036"; then
        # Y coordinate
        y_hex=$(echo "$line" | awk '{print $NF}')
        y_dec=$((16#$y_hex))
        echo "Y: $y_dec"
        echo "---"
    fi
done
