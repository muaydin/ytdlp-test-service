#!/bin/bash

echo "🚂 yt-dlp Railway Deployment Helper"
echo "==================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI is installed"
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
else
    echo "✅ Already logged into Railway"
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Deploy directly from this folder"
echo "2. Initialize Railway project and deploy"
echo "3. Just show deployment instructions"
echo ""

read -p "Choose option (1-3): " option

case $option in
    1)
        echo "🚀 Deploying directly..."
        railway up
        ;;
    2)
        echo "🔗 Initializing Railway project..."
        railway link
        echo "🚀 Deploying..."
        railway up
        ;;
    3)
        echo ""
        echo "📖 Manual Deployment Instructions:"
        echo "1. Push this code to a GitHub repository"
        echo "2. Go to https://railway.app"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select your repository"
        echo "5. Railway will auto-detect and deploy your Python app"
        echo ""
        echo "Or use Railway CLI:"
        echo "  railway login"
        echo "  railway link"
        echo "  railway up"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment initiated!"
echo "📝 After deployment, test your app with:"
echo "   - GET /health (health check)"
echo "   - GET /ytdlp-info (yt-dlp version and test)"
echo "   - POST /test-ytdlp (test with YouTube URL)" 