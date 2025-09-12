# Load testing script for yt-dlp scaling
for i in {1..5}; do
  echo "Request $i:"
  curl -X POST http://51.159.205.195/test-download \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
    --max-time 30 &
done
wait
echo "All requests completed. Check scaling with: kubectl get hpa -n ytdlp-namespace"
