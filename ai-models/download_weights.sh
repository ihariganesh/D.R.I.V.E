#!/bin/bash
# Download YOLO v8 model weights

echo "📥 Downloading YOLO v8 weights..."
echo "=================================="

# Create weights directory
mkdir -p weights
cd weights

# Download YOLOv8 nano (lightweight, fast)
echo "Downloading YOLOv8 nano..."
wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Optional: Download larger models
read -p "Download YOLOv8 small (better accuracy)? (y/n): " download_small
if [ "$download_small" = "y" ]; then
    echo "Downloading YOLOv8 small..."
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
fi

read -p "Download YOLOv8 medium (best balance)? (y/n): " download_medium
if [ "$download_medium" = "y" ]; then
    echo "Downloading YOLOv8 medium..."
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
fi

echo ""
echo "✅ Download complete!"
echo ""
echo "Downloaded models:"
ls -lh *.pt

echo ""
echo "Update your .env file:"
echo "YOLO_MODEL_PATH=./ai-models/weights/yolov8n.pt"
