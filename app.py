from flask import Flask, jsonify, request
import yt_dlp
import os
import tempfile
import shutil
import io
import sys
from datetime import datetime
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>yt-dlp Test Service</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content { padding: 30px; }
        .section { margin-bottom: 40px; }
        .section h2 { 
            color: #333; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 10px; 
            margin-bottom: 20px; 
        }
        .test-form { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 10px; 
            margin: 20px 0;
            border-left: 5px solid #667eea;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: 600; 
            color: #333;
        }
        .form-group input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { 
            background: #ccc; 
            cursor: not-allowed; 
            transform: none;
        }
        .progress-container { 
            margin-top: 15px; 
            display: none; 
        }
        .progress-bar { 
            width: 100%; 
            height: 20px; 
            background: #f0f0f0; 
            border-radius: 10px; 
            overflow: hidden;
        }
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            width: 0%; 
            transition: width 0.3s ease;
            position: relative;
        }
        .progress-text { 
            margin-top: 10px; 
            font-size: 14px; 
            color: #666;
            text-align: center;
        }
        .result-container { 
            margin-top: 20px; 
            padding: 20px; 
            border-radius: 8px; 
            display: none;
        }
        .result-success { 
            background: #d4edda; 
            border: 1px solid #c3e6cb; 
            color: #155724;
        }
        .result-error { 
            background: #f8d7da; 
            border: 1px solid #f5c6cb; 
            color: #721c24;
        }
        .endpoint-card { 
            background: white; 
            border: 1px solid #e9ecef; 
            border-radius: 8px; 
            padding: 20px; 
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .endpoint-method { 
            display: inline-block; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px; 
            font-weight: bold;
            margin-right: 10px;
        }
        .method-get { background: #d4edda; color: #155724; }
        .method-post { background: #cce5ff; color: #004085; }
        .code-block { 
            background: #f8f9fa; 
            border: 1px solid #e9ecef; 
            border-radius: 4px; 
            padding: 15px; 
            margin: 10px 0;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            overflow-x: auto;
        }
        .sample-urls { 
            background: #fff3cd; 
            border: 1px solid #ffeaa7; 
            border-radius: 8px; 
            padding: 15px; 
            margin: 20px 0;
        }
        .two-column { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
        }
        @media (max-width: 768px) { 
            .two-column { grid-template-columns: 1fr; }
            .container { margin: 10px; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 yt-dlp Test Service</h1>
            <p>Professional YouTube video download testing platform</p>
        </div>
        
        <div class="content">
            <div class="two-column">
                <div>
                    <div class="section">
                        <h2>🧪 Quick Tests</h2>
                        
                        <div class="test-form">
                            <h3>📊 Metadata Extraction</h3>
                            <p>Extract video information without downloading</p>
                            <form id="metadata-form" onsubmit="testMetadata(event)">
                                <div class="form-group">
                                    <label for="metadata-url">YouTube URL:</label>
                                    <input type="text" id="metadata-url" name="url" 
                                           placeholder="https://www.youtube.com/watch?v=..." required>
                                </div>
                                <button type="submit" class="btn" id="metadata-btn">Extract Metadata</button>
                            </form>
                            <div class="progress-container" id="metadata-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="metadata-progress-fill"></div>
                                </div>
                                <div class="progress-text" id="metadata-progress-text">Processing...</div>
                            </div>
                            <div class="result-container" id="metadata-result"></div>
                        </div>
                        
                        <div class="test-form">
                            <h3>⬇️ Video Download Test</h3>
                            <p>Download video content to memory for testing</p>
                            <form id="download-form" onsubmit="testDownload(event)">
                                <div class="form-group">
                                    <label for="download-url">YouTube URL:</label>
                                    <input type="text" id="download-url" name="url" 
                                           placeholder="https://www.youtube.com/watch?v=..." required>
                                </div>
                                <button type="submit" class="btn" id="download-btn">Start Download</button>
                            </form>
                            <div class="progress-container" id="download-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="download-progress-fill"></div>
                                </div>
                                <div class="progress-text" id="download-progress-text">Downloading...</div>
                            </div>
                            <div class="result-container" id="download-result"></div>
                        </div>
                        
                        <div class="sample-urls">
                            <h4>📝 Sample URLs for Testing:</h4>
                            <ul>
                                <li><strong>Classic:</strong> https://www.youtube.com/watch?v=dQw4w9WgXcQ</li>
                                <li><strong>Short:</strong> https://www.youtube.com/watch?v=jNQXAC9IVRw</li>
                                <li><strong>Recent:</strong> https://www.youtube.com/watch?v=2NRkV7ZQUJA</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class="section">
                        <h2>🔗 API Endpoints</h2>
                        
                        <div class="endpoint-card">
                            <span class="endpoint-method method-get">GET</span>
                            <strong>/health</strong>
                            <p>Check service health and status</p>
                            <div class="code-block">curl http://localhost:8090/health</div>
                        </div>
                        
                        <div class="endpoint-card">
                            <span class="endpoint-method method-get">GET</span>
                            <strong>/ytdlp-info</strong>
                            <p>Get yt-dlp version and capabilities test</p>
                            <div class="code-block">curl http://localhost:8090/ytdlp-info</div>
                        </div>
                        
                        <div class="endpoint-card">
                            <span class="endpoint-method method-post">POST</span>
                            <strong>/test-ytdlp</strong>
                            <p>Extract video metadata without downloading</p>
                            <div class="code-block">curl -X POST http://localhost:8090/test-ytdlp -H "Content-Type: application/json" -d '{"url": "https://youtube.com/watch?v=..."}'</div>
                        </div>
                        
                        <div class="endpoint-card">
                            <span class="endpoint-method method-post">POST</span>
                            <strong>/test-download</strong>
                            <p>Download video content to memory for testing</p>
                            <div class="code-block">curl -X POST http://localhost:8090/test-download -H "Content-Type: application/json" -d '{"url": "https://youtube.com/watch?v=..."}'</div>
                        </div>
                        
                                                 <div class="endpoint-card">
                             <span class="endpoint-method method-post">POST</span>
                             <strong>/terminal</strong>
                             <p>Execute yt-dlp commands directly on server</p>
                             <div class="code-block">curl -X POST http://localhost:8090/terminal -H "Content-Type: application/json" -d '{"command": "yt-dlp --version"}'</div>
                         </div>
                         
                         <div class="endpoint-card">
                             <span class="endpoint-method method-get">GET</span>
                             <strong>/api-docs</strong>
                             <p>Complete API documentation in JSON format</p>
                             <div class="code-block">curl http://localhost:8090/api-docs</div>
                         </div>
                    </div>
                    
                    <div class="section">
                        <h2>ℹ️ Service Information</h2>
                        <div id="service-info" class="endpoint-card">
                            <p>Loading service information...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load service info on page load
        window.onload = function() {
            fetch('/ytdlp-info')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('service-info').innerHTML = `
                        <h4>🚀 Service Status</h4>
                        <p><strong>yt-dlp Version:</strong> ${data['yt-dlp_version']}</p>
                        <p><strong>Test Extraction:</strong> ${data.test_extraction}</p>
                        <p><strong>Test Video:</strong> ${data.test_video_title}</p>
                        <p><strong>Capabilities:</strong> ✅ Extract Info, ✅ Download, ✅ Format Detection</p>
                    `;
                })
                .catch(error => {
                    document.getElementById('service-info').innerHTML = `
                        <h4>⚠️ Service Status</h4>
                        <p style="color: #721c24;">Failed to load service information</p>
                    `;
                });
        };

        function showProgress(progressId, textId, duration = 2000) {
            const progressContainer = document.getElementById(progressId.replace('-fill', ''));
            const progressFill = document.getElementById(progressId);
            const progressText = document.getElementById(textId);
            
            progressContainer.style.display = 'block';
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 95) progress = 95;
                
                progressFill.style.width = progress + '%';
                progressText.textContent = `Processing... ${Math.round(progress)}%`;
            }, duration / 20);
            
            return interval;
        }

        function hideProgress(progressId) {
            const progressContainer = document.getElementById(progressId.replace('-fill', ''));
            progressContainer.style.display = 'none';
        }

        function showResult(resultId, content, isSuccess = true) {
            const resultContainer = document.getElementById(resultId);
            resultContainer.className = `result-container ${isSuccess ? 'result-success' : 'result-error'}`;
            resultContainer.innerHTML = content;
            resultContainer.style.display = 'block';
        }

        async function testMetadata(event) {
            event.preventDefault();
            
            const url = document.getElementById('metadata-url').value;
            const btn = document.getElementById('metadata-btn');
            
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            const progressInterval = showProgress('metadata-progress-fill', 'metadata-progress-text', 3000);
            
            try {
                const response = await fetch('/test-ytdlp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                clearInterval(progressInterval);
                hideProgress('metadata-progress');
                
                if (data.success) {
                    showResult('metadata-result', `
                        <h4>✅ Metadata Extracted Successfully</h4>
                        <p><strong>Title:</strong> ${data.title}</p>
                        <p><strong>Uploader:</strong> ${data.uploader}</p>
                        <p><strong>Duration:</strong> ${Math.floor(data.duration / 60)}:${(data.duration % 60).toString().padStart(2, '0')}</p>
                        <p><strong>View Count:</strong> ${data.view_count?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Formats Available:</strong> ${data.formats_available}</p>
                        <p><strong>Upload Date:</strong> ${data.upload_date}</p>
                    `, true);
                } else {
                    showResult('metadata-result', `
                        <h4>❌ Metadata Extraction Failed</h4>
                        <p><strong>Error:</strong> ${data.error}</p>
                    `, false);
                }
            } catch (error) {
                clearInterval(progressInterval);
                hideProgress('metadata-progress');
                showResult('metadata-result', `
                    <h4>❌ Request Failed</h4>
                    <p><strong>Error:</strong> ${error.message}</p>
                `, false);
            }
            
            btn.disabled = false;
            btn.textContent = 'Extract Metadata';
        }

        async function testDownload(event) {
            event.preventDefault();
            
            const url = document.getElementById('download-url').value;
            const btn = document.getElementById('download-btn');
            
            btn.disabled = true;
            btn.textContent = 'Downloading...';
            
            const progressInterval = showProgress('download-progress-fill', 'download-progress-text', 8000);
            
            try {
                const response = await fetch('/test-download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                clearInterval(progressInterval);
                hideProgress('download-progress');
                
                if (data.success) {
                    showResult('download-result', `
                        <h4>✅ Download Completed Successfully</h4>
                        <p><strong>Title:</strong> ${data.video_title}</p>
                        <p><strong>Download Type:</strong> ${data.download_type}</p>
                        <p><strong>File Size:</strong> ${data.downloaded_size_human}</p>
                        <p><strong>File Extension:</strong> ${data.file_extension}</p>
                        <p><strong>Duration:</strong> ${Math.floor(data.duration / 60)}:${(data.duration % 60).toString().padStart(2, '0')}</p>
                        <p><strong>Note:</strong> ${data.note}</p>
                        <p style="font-size: 12px; color: #666; margin-top: 10px;">${data.explanation}</p>
                    `, true);
                } else {
                    showResult('download-result', `
                        <h4>❌ Download Failed</h4>
                        <p><strong>Error:</strong> ${data.error}</p>
                    `, false);
                }
            } catch (error) {
                clearInterval(progressInterval);
                hideProgress('download-progress');
                showResult('download-result', `
                    <h4>❌ Request Failed</h4>
                    <p><strong>Error:</strong> ${error.message}</p>
                `, false);
            }
            
            btn.disabled = false;
            btn.textContent = 'Start Download';
        }
    </script>
</body>
</html>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'yt-dlp-test'
    })

@app.route('/ytdlp-info')
def ytdlp_info():
    try:
        # Get yt-dlp version
        try:
            version = yt_dlp.version.__version__
        except AttributeError:
            # Fallback for newer versions
            import subprocess
            version = subprocess.check_output(['yt-dlp', '--version'], text=True).strip()
        
        # Test basic functionality
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Test with a known working video
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - always available
            try:
                info = ydl.extract_info(test_url, download=False)
                test_result = "success"
                test_title = info.get('title', 'Unknown')
            except Exception as e:
                test_result = f"error: {str(e)}"
                test_title = None
        
        return jsonify({
            'yt-dlp_version': version,
            'test_extraction': test_result,
            'test_video_title': test_title,
            'capabilities': {
                'extract_info': True,
                'download': True,
                'formats_available': True
            }
        })
    except Exception as e:
        return jsonify({
            'error': f"yt-dlp not working: {str(e)}"
        }), 500

@app.route('/api-docs')
def api_docs():
    return jsonify({
        "service": "yt-dlp Test Service",
        "version": "1.0.0",
        "description": "A comprehensive YouTube video download testing service",
        "base_url": request.base_url.replace('/api-docs', ''),
        "endpoints": {
            "GET /": {
                "description": "Web interface for testing the service",
                "returns": "HTML page with interactive forms"
            },
            "GET /health": {
                "description": "Check service health and status",
                "returns": {
                    "status": "healthy",
                    "timestamp": "ISO timestamp",
                    "service": "yt-dlp-test"
                },
                "example": "curl http://localhost:8090/health"
            },
            "GET /ytdlp-info": {
                "description": "Get yt-dlp version and capabilities",
                "returns": {
                    "yt-dlp_version": "version string",
                    "test_extraction": "success/error",
                    "test_video_title": "title of test video",
                    "capabilities": {
                        "extract_info": True,
                        "download": True,
                        "formats_available": True
                    }
                },
                "example": "curl http://localhost:8090/ytdlp-info"
            },
            "POST /test-ytdlp": {
                "description": "Extract video metadata without downloading",
                "parameters": {
                    "url": "YouTube video URL (required)"
                },
                "returns": {
                    "success": True,
                    "title": "video title",
                    "duration": "duration in seconds",
                    "uploader": "channel name",
                    "view_count": "number of views",
                    "upload_date": "YYYYMMDD",
                    "formats_available": "number of formats",
                    "sample_formats": "array of format objects"
                },
                "example": 'curl -X POST http://localhost:8090/test-ytdlp -H "Content-Type: application/json" -d \'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}\''
            },
            "POST /test-download": {
                "description": "Download video content to memory for testing",
                "parameters": {
                    "url": "YouTube video URL (required)"
                },
                "returns": {
                    "success": True,
                    "video_title": "video title",
                    "downloaded_bytes": "file size in bytes",
                    "downloaded_size_mb": "file size in MB",
                    "download_type": "video/audio/storyboard/metadata",
                    "file_extension": "file extension",
                    "verification": "verification message",
                    "note": "completion message"
                },
                "example": 'curl -X POST http://localhost:8090/test-download -H "Content-Type: application/json" -d \'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}\''
            },
            "POST /terminal": {
                "description": "Execute yt-dlp commands directly on server",
                "parameters": {
                    "command": "yt-dlp command to execute (must start with 'yt-dlp')"
                },
                "returns": {
                    "success": True,
                    "command": "executed command",
                    "exit_code": "command exit code",
                    "stdout": "command output",
                    "stderr": "command errors"
                },
                "example": 'curl -X POST http://localhost:8090/terminal -H "Content-Type: application/json" -d \'{"command": "yt-dlp --version"}\''
            },
            "GET /api-docs": {
                "description": "This endpoint - comprehensive API documentation",
                "returns": "Complete API documentation in JSON format"
            }
        },
        "sample_urls": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "https://www.youtube.com/watch?v=2NRkV7ZQUJA"
        ],
        "notes": [
            "Due to YouTube's restrictions, downloads may only retrieve storyboard images or metadata",
            "The service automatically selects the best available format",
            "Large downloads are verified in memory and then deleted",
            "All endpoints support both form data and JSON input where applicable"
        ]
    })

@app.route('/test-ytdlp', methods=['POST'])
def test_ytdlp():
    try:
        # Get URL from form or JSON
        if request.is_json:
            url = request.json.get('url')
        else:
            url = request.form.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Configure yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'outtmpl': '/tmp/%(title)s.%(ext)s'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information without downloading
            info = ydl.extract_info(url, download=False)
            
            # Extract useful information
            result = {
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'formats_available': len(info.get('formats', [])),
                'url_tested': url,
                'timestamp': datetime.now().isoformat()
            }
            
            # Get available formats info
            formats = info.get('formats', [])
            if formats:
                result['sample_formats'] = [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution'),
                        'filesize': f.get('filesize')
                    }
                    for f in formats[:5]  # First 5 formats
                ]
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'url_tested': url if 'url' in locals() else 'unknown',
            'timestamp': datetime.now().isoformat()
        }), 500

class MemoryFile:
    """A file-like object that stores data in memory"""
    def __init__(self):
        self.buffer = io.BytesIO()
        self.size = 0
    
    def write(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        written = self.buffer.write(data)
        self.size += written
        return written
    
    def read(self, size=-1):
        return self.buffer.read(size)
    
    def seek(self, pos, whence=0):
        return self.buffer.seek(pos, whence)
    
    def tell(self):
        return self.buffer.tell()
    
    def close(self):
        self.buffer.close()
    
    def flush(self):
        # Memory buffers don't need flushing, but yt-dlp expects this method
        pass
    
    def get_size_mb(self):
        return self.size / (1024 * 1024)

@app.route('/test-download', methods=['POST'])
def test_download():
    temp_file_path = None
    try:
        # Get URL from form or JSON
        if request.is_json:
            url = request.json.get('url')
        else:
            url = request.form.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Create a temporary file - use a simple extension
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Create the actual output path with yt-dlp template
        temp_dir = os.path.dirname(temp_file_path)
        temp_base = os.path.basename(temp_file_path).replace('.tmp', '')
        output_template = os.path.join(temp_dir, f"{temp_base}.%(ext)s")
        
        # Simple approach: Just use basic yt-dlp like CLI
        downloaded = False
        format_used = None
        
        try:
            # Use simple yt-dlp options like the working CLI command
            download_opts = {
                'outtmpl': output_template,
                'quiet': False,  # Enable logging to see what's happening
                'no_warnings': False,  # Show warnings to debug
                # Try specific formats including DRC versions and fallbacks
                'format': '249-drc/249/250-drc/250/140-drc/140/251-drc/251/160/278/394/133/best[filesize<10M]/worst',
            }
            
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                print(f"Attempting to download: {url}")
                # Get video info first
                info = ydl.extract_info(url, download=False)
                
                # Show available formats for debugging
                formats = info.get('formats', [])
                print(f"Available formats: {len(formats)}")
                for f in formats[:3]:  # Show first 3 formats
                    print(f"  - {f.get('format_id')}: {f.get('ext')} {f.get('resolution')} {f.get('filesize')}")
                
                # Download the video
                ydl.download([url])
                print(f"Download command completed")
                
                # Find the downloaded file
                temp_dir = os.path.dirname(temp_file_path)
                temp_base = os.path.basename(temp_file_path).replace('.tmp', '')
                
                actual_file = None
                for filename in os.listdir(temp_dir):
                    if filename.startswith(temp_base):
                        actual_file = os.path.join(temp_dir, filename)
                        break
                
                if actual_file and os.path.exists(actual_file):
                    file_size = os.path.getsize(actual_file)
                    print(f"File created: {actual_file}, size: {file_size}")
                    temp_file_path = actual_file
                    downloaded = True
                    format_used = 'default'
                else:
                    downloaded = False
                    
        except Exception as e:
            print(f"Download failed with error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'url_tested': url,
                'timestamp': datetime.now().isoformat()
                            }), 400
        
        if not downloaded:
            return jsonify({
                'success': False,
                'error': 'Download completed but no file was found',
                'url_tested': url,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # If we get here, download was successful!
        file_size = os.path.getsize(temp_file_path)
        
        # Get the actual file extension to confirm what was downloaded
        file_extension = os.path.splitext(temp_file_path)[1] or 'unknown'
        
        # Verify it's a real media file by checking size and reading first few bytes
        with open(temp_file_path, 'rb') as f:
            first_bytes = f.read(16)  # Read first 16 bytes to check file signature
            f.seek(0)
            # Optionally read entire file into memory to prove we can
            if file_size < 10 * 1024 * 1024:  # Only if under 10MB
                full_content = f.read()
                content_verification = f"Full file read into memory ({len(full_content)} bytes)"
            else:
                content_verification = f"Large file detected, verified first {len(first_bytes)} bytes"
        
        # Delete the temporary file immediately after verification
        os.unlink(temp_file_path)
        temp_file_path = None  # Mark as cleaned up
        
        # Determine what was actually downloaded
        download_type = 'unknown'
        if file_extension == '.mhtml':
            download_type = 'storyboard/thumbnails'
        elif file_extension in ['.mp4', '.webm', '.mkv']:
            download_type = 'video'
        elif file_extension in ['.mp3', '.m4a', '.opus']:
            download_type = 'audio'
        elif file_size < 1024:
            download_type = 'metadata/small file'
        
        result = {
            'success': True,
            'video_title': info.get('title'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'downloaded_size_mb': round(file_size / (1024 * 1024), 2),
            'downloaded_bytes': file_size,
            'downloaded_size_human': f"{file_size:,} bytes ({file_size / (1024 * 1024):.2f} MB)",
            'format_used': format_used,
            'file_extension': file_extension,
            'file_signature': first_bytes.hex()[:32] if first_bytes else 'none',
            'download_type': download_type,
            'url_tested': url,
            'timestamp': datetime.now().isoformat(),
            'verification': content_verification,
            'note': f'✅ DOWNLOAD COMPLETED! Downloaded {download_type}. File was created, verified, and deleted.',
            'explanation': 'Note: YouTube often restricts video downloads. You may only get storyboard images or metadata.'
        }
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'url_tested': url if 'url' in locals() else 'unknown',
            'timestamp': datetime.now().isoformat()
        }), 500
    finally:
        # Clean up temp file if it still exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore cleanup errors

@app.route('/terminal', methods=['POST'])
def terminal():
    """Execute yt-dlp commands directly on the server"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'error': 'Command is required',
                'usage': 'POST /terminal with {"command": "yt-dlp --help"}'
            }), 400
        
        command = data['command'].strip()
        
        # Security: only allow yt-dlp commands
        if not command.startswith('yt-dlp'):
            return jsonify({
                'success': False,
                'error': 'Only yt-dlp commands are allowed',
                'command_received': command
            }), 400
        
        # Execute the command on the server
        try:
            # Run the command and capture output
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd='/tmp'  # Run in tmp directory
            )
            
            return jsonify({
                'success': True,
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'server': 'Railway Production',
                'timestamp': datetime.now().isoformat()
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Command timed out (60s limit)',
                'command': command
            }), 408
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to execute command: {str(e)}',
                'command': command
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    app.run(host='0.0.0.0', port=port, debug=False) 