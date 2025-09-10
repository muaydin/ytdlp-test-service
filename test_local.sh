#!/bin/bash

# Test script for yt-dlp service
PORT=${1:-8080}
BASE_URL="http://localhost:$PORT"

echo "🧪 Testing yt-dlp service on port $PORT..."
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
response=$(curl -s "$BASE_URL/health")
if [[ $? -eq 0 ]]; then
    echo "✅ Health check passed"
    echo "$response" | python3 -m json.tool
else
    echo "❌ Health check failed"
fi
echo ""

# Test 2: yt-dlp info
echo "2️⃣ Testing yt-dlp info endpoint..."
response=$(curl -s "$BASE_URL/ytdlp-info")
if [[ $? -eq 0 ]]; then
    echo "✅ yt-dlp info retrieved"
    echo "$response" | python3 -m json.tool
else
    echo "❌ yt-dlp info failed"
fi
echo ""

# Test 3: Metadata extraction
echo "3️⃣ Testing metadata extraction..."
response=$(curl -s -X POST "$BASE_URL/test-ytdlp" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}')
if [[ $? -eq 0 ]]; then
    echo "✅ Metadata extraction successful"
    echo "$response" | python3 -m json.tool
else
    echo "❌ Metadata extraction failed"
fi
echo ""

# Test 4: Terminal command
echo "4️⃣ Testing terminal command endpoint..."
response=$(curl -s -X POST "$BASE_URL/terminal" \
    -H "Content-Type: application/json" \
    -d '{"command": "yt-dlp --version"}')
if [[ $? -eq 0 ]]; then
    echo "✅ Terminal command successful"
    echo "$response" | python3 -m json.tool
else
    echo "❌ Terminal command failed"
fi
echo ""

echo "🎉 Testing complete!"
echo ""
echo "🌐 Open in browser: $BASE_URL"
echo ""
echo "💡 Try these manual tests:"
echo "   curl $BASE_URL/health"
echo "   curl $BASE_URL/ytdlp-info"
echo "   curl -X POST $BASE_URL/test-ytdlp -H 'Content-Type: application/json' -d '{\"url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\"}'" 