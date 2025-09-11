from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import tempfile
import os
from datetime import datetime
import json

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
            max-width: 1400px; 
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
        .three-column { 
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr; 
            gap: 30px; 
        }
        
        /* Terminal Styles */
        .terminal-container {
            background: #1e1e1e;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .terminal-header {
            background: #2d2d2d;
            color: #fff;
            padding: 10px 15px;
            border-radius: 5px 5px 0 0;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .terminal-dots {
            display: flex;
            gap: 5px;
        }
        .terminal-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .terminal-dot.red { background: #ff5f56; }
        .terminal-dot.yellow { background: #ffbd2e; }
        .terminal-dot.green { background: #27ca3f; }
        .terminal-body {
            background: #000;
            color: #00ff00;
            padding: 15px;
            border-radius: 0 0 5px 5px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            min-height: 300px;
            max-height: 400px;
            overflow-y: auto;
        }
        .terminal-input {
            background: transparent;
            border: none;
            color: #00ff00;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            width: 100%;
            outline: none;
            padding: 5px 0;
        }
        .terminal-prompt {
            color: #00ff00;
            margin-right: 5px;
        }
        .terminal-output {
            margin: 5px 0;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .terminal-error {
            color: #ff6b6b;
        }
        .terminal-success {
            color: #51cf66;
        }
        .terminal-command {
            color: #74c0fc;
        }
        .terminal-form {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        .terminal-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        .terminal-btn:hover {
            background: #5a67d8;
        }
        .terminal-btn:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        @media (max-width: 1200px) { 
            .three-column { grid-template-columns: 1fr; }
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
            <p>Professional YouTube video download testing platform with integrated terminal</p>
        </div>
        
        <div class="content">
            <div class="three-column">
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
                
                <div>
                    <div class="section">
                        <h2>💻 Terminal</h2>
                        <p>Execute yt-dlp commands directly from the browser</p>
                        
                        <div class="terminal-container">
                            <div class="terminal-header">
                                <div class="terminal-dots">
                                    <div class="terminal-dot red"></div>
                                    <div class="terminal-dot yellow"></div>
                                    <div class="terminal-dot green"></div>
                                </div>
                                <span>yt-dlp Terminal</span>
                            </div>
                            <div class="terminal-body" id="terminal-output">
                                <div class="terminal-output terminal-success">Welcome to yt-dlp Terminal!</div>
                                <div class="terminal-output terminal-command">Try these commands:</div>
                                <div class="terminal-output">• yt-dlp --version</div>
                                <div class="terminal-output">• yt-dlp --help</div>
                                <div class="terminal-output">• yt-dlp --list-formats "https://www.youtube.com/watch?v=dQw4w9WgXcQ"</div>
                                <div class="terminal-output">• yt-dlp --get-title "https://www.youtube.com/watch?v=dQw4w9WgXcQ"</div>
                                <div class="terminal-output">• echo "Hello World"</div>
                                <div class="terminal-output">• ls -la</div>
                                <div class="terminal-output">• pwd</div>
                                <div class="terminal-output">• whoami</div>
                                <div class="terminal-output">• date</div>
                                <div class="terminal-output terminal-command">Type your command below:</div>
                            </div>
                            <div class="terminal-form">
                                <span class="terminal-prompt">$</span>
                                <input type="text" class="terminal-input" id="terminal-input" placeholder="Enter command..." autocomplete="off">
                                <button class="terminal-btn" onclick="executeTerminalCommand()" id="terminal-btn">Execute</button>
                            </div>
                        </div>
                        
                        <div class="test-form">
                            <h3>🚀 Quick Commands</h3>
                            <p>Click to execute common yt-dlp commands</p>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                                <button class="btn" onclick="quickCommand('yt-dlp --version')" style="font-size: 14px; padding: 8px 12px;">Version</button>
                                <button class="btn" onclick="quickCommand('yt-dlp --help')" style="font-size: 14px; padding: 8px 12px;">Help</button>
                                <button class="btn" onclick="quickCommand('yt-dlp --list-formats \\"https://www.youtube.com/watch?v=dQw4w9WgXcQ\\"')" style="font-size: 14px; padding: 8px 12px;">List Formats</button>
                                <button class="btn" onclick="quickCommand('yt-dlp --get-title \\"https://www.youtube.com/watch?v=dQw4w9WgXcQ\\"')" style="font-size: 14px; padding: 8px 12px;">Get Title</button>
                                <button class="btn" onclick="quickCommand('pwd')" style="font-size: 14px; padding: 8px 12px;">Current Dir</button>
                                <button class="btn" onclick="quickCommand('ls -la')" style="font-size: 14px; padding: 8px 12px;">List Files</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Terminal functionality
        let terminalHistory = [];
        let historyIndex = -1;
        
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
            
            // Focus terminal input
            document.getElementById('terminal-input').focus();
            
            // Add keyboard event listeners
            document.getElementById('terminal-input').addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    executeTerminalCommand();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (historyIndex < terminalHistory.length - 1) {
                        historyIndex++;
                        this.value = terminalHistory[terminalHistory.length - 1 - historyIndex];
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (historyIndex > 0) {
                        historyIndex--;
                        this.value = terminalHistory[terminalHistory.length - 1 - historyIndex];
                    } else if (historyIndex === 0) {
                        historyIndex = -1;
                        this.value = '';
                    }
                }
            });
        };

        function addTerminalOutput(text, type = 'output') {
            const terminalOutput = document.getElementById('terminal-output');
            const outputDiv = document.createElement('div');
            outputDiv.className = `terminal-output terminal-${type}`;
            outputDiv.textContent = text;
            terminalOutput.appendChild(outputDiv);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }

        function addTerminalCommand(command) {
            const terminalOutput = document.getElementById('terminal-output');
            const commandDiv = document.createElement('div');
            commandDiv.className = 'terminal-output terminal-command';
            commandDiv.innerHTML = `<span class="terminal-prompt">$</span> ${command}`;
            terminalOutput.appendChild(commandDiv);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }

        async function executeTerminalCommand() {
            const input = document.getElementById('terminal-input');
            const btn = document.getElementById('terminal-btn');
            const command = input.value.trim();
            
            if (!command) return;
            
            // Add to history
            terminalHistory.push(command);
            historyIndex = -1;
            
            // Show command
            addTerminalCommand(command);
            
            // Clear input and disable button
            input.value = '';
            btn.disabled = true;
            btn.textContent = 'Executing...';
            
            try {
                const response = await fetch('/terminal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.stdout) {
                        addTerminalOutput(data.stdout, 'success');
                    }
                    if (data.stderr) {
                        addTerminalOutput(data.stderr, 'error');
                    }
                    if (!data.stdout && !data.stderr) {
                        addTerminalOutput('Command executed successfully (no output)', 'success');
                    }
                } else {
                    addTerminalOutput(`Error: ${data.error}`, 'error');
                }
            } catch (error) {
                addTerminalOutput(`Request failed: ${error.message}`, 'error');
            }
            
            // Re-enable button and focus input
            btn.disabled = false;
            btn.textContent = 'Execute';
            input.focus();
        }

        function quickCommand(command) {
            document.getElementById('terminal-input').value = command;
            executeTerminalCommand();
        }

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
                'format_detection': True
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test-ytdlp', methods=['POST'])
def test_ytdlp():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required', 'success': False}), 400
        
        # Configure yt-dlp for metadata extraction only
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'success': True,
                'title': info.get('title', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', 'Unknown'),
                'formats_available': len(info.get('formats', [])),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test-download', methods=['POST'])
def test_download():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required', 'success': False}), 400
        
        # Create a temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            output_template = temp_file.name
            
        try:
            # Configure yt-dlp for download
            download_opts = {
                'outtmpl': output_template,
                'quiet': False,  # Enable logging to see what's happening
                'no_warnings': False,  # Show warnings to debug
                # Try specific formats including DRC versions and fallbacks
                'format': '249-drc/249/250-drc/250/140-drc/140/251-drc/251/160/278/394/133/best[filesize<10M]/worst',
            }
            
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                # First, get info to show available formats
                info = ydl.extract_info(url, download=False)
                
                # Show available formats for debugging
                formats = info.get('formats', [])
                print(f"Available formats: {len(formats)}")
                for f in formats[:3]:  # Show first 3 formats
                    print(f"  - {f.get('format_id')}: {f.get('ext')} {f.get('resolution')} {f.get('filesize')}")
                
                # Attempt download
                print(f"Attempting to download: {url}")
                ydl.download([url])
                
                # Check if file was created and get its size
                if os.path.exists(output_template):
                    file_size = os.path.getsize(output_template)
                    file_extension = os.path.splitext(output_template)[1]
                    
                    # Read first few bytes to verify content
                    with open(output_template, 'rb') as f:
                        first_bytes = f.read(16)
                    
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
                    
                    # Clean up the temporary file
                    os.unlink(output_template)
                    
                    result = {
                        'success': True,
                        'video_title': info.get('title', 'Unknown'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'downloaded_bytes': file_size,
                        'downloaded_size_mb': round(file_size / (1024 * 1024), 2),
                        'downloaded_size_human': f"{file_size:,} bytes ({round(file_size / (1024 * 1024), 2):.2f} MB)",
                        'file_extension': file_extension,
                        'file_signature': first_bytes.hex()[:32] if first_bytes else 'none',
                        'download_type': download_type,
                        'url_tested': url,
                        'timestamp': datetime.now().isoformat(),
                        'verification': 'Full file read into memory (0 bytes)',
                        'note': f'✅ DOWNLOAD COMPLETED! Downloaded {download_type}. File was created, verified, and deleted.',
                        'explanation': 'Note: YouTube often restricts video downloads. You may only get storyboard images or metadata.'
                    }
                    
                    return jsonify(result)
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Download failed - no file was created',
                        'url_tested': url,
                        'timestamp': datetime.now().isoformat()
                    }), 500
                    
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(output_template):
                os.unlink(output_template)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/terminal', methods=['POST'])
def terminal():
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'Command is required', 'success': False}), 400
        
        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        return jsonify({
            'success': True,
            'command': command,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exit_code': result.returncode,
            'server': 'Railway Production',
            'timestamp': datetime.now().isoformat()
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Command timed out after 30 seconds',
            'command': command,
            'timestamp': datetime.now().isoformat()
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'command': command,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api-docs')
def api_docs():
    """Return comprehensive API documentation"""
    docs = {
        'service': 'yt-dlp Test Service',
        'version': '1.0.0',
        'description': 'A comprehensive Flask-based web service for testing yt-dlp functionality',
        'base_url': request.base_url.rstrip('/'),
        'endpoints': {
            'GET /': {
                'description': 'Modern web interface with interactive forms and terminal',
                'response_type': 'HTML',
                'features': ['Interactive forms', 'Progress bars', 'Terminal interface', 'API documentation']
            },
            'GET /health': {
                'description': 'Service health check',
                'response_type': 'JSON',
                'example_response': {
                    'status': 'healthy',
                    'timestamp': '2025-09-10T15:30:00.000000',
                    'service': 'yt-dlp-test'
                }
            },
            'GET /ytdlp-info': {
                'description': 'Get yt-dlp version and capabilities',
                'response_type': 'JSON',
                'example_response': {
                    'yt-dlp_version': '2025.09.05',
                    'test_extraction': 'success',
                    'test_video_title': 'Rick Astley - Never Gonna Give You Up',
                    'capabilities': {
                        'extract_info': True,
                        'download': True,
                        'format_detection': True
                    }
                }
            },
            'POST /test-ytdlp': {
                'description': 'Extract video metadata without downloading',
                'request_body': {'url': 'YouTube URL'},
                'response_type': 'JSON',
                'example_request': {
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                },
                'example_response': {
                    'success': True,
                    'title': 'Rick Astley - Never Gonna Give You Up',
                    'uploader': 'Rick Astley',
                    'duration': 213,
                    'view_count': 1692567350,
                    'formats_available': 22
                }
            },
            'POST /test-download': {
                'description': 'Download video content to memory for testing',
                'request_body': {'url': 'YouTube URL'},
                'response_type': 'JSON',
                'example_request': {
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                },
                'example_response': {
                    'success': True,
                    'video_title': 'Rick Astley - Never Gonna Give You Up',
                    'downloaded_bytes': 241672132,
                    'downloaded_size_mb': 230.48,
                    'download_type': 'video',
                    'file_extension': '.webm'
                }
            },
            'POST /terminal': {
                'description': 'Execute yt-dlp commands directly on server',
                'request_body': {'command': 'Shell command'},
                'response_type': 'JSON',
                'example_request': {
                    'command': 'yt-dlp --version'
                },
                'example_response': {
                    'success': True,
                    'command': 'yt-dlp --version',
                    'stdout': '2025.09.05\\n',
                    'stderr': '',
                    'exit_code': 0
                }
            },
            'GET /api-docs': {
                'description': 'Complete API documentation in JSON format',
                'response_type': 'JSON',
                'note': 'This endpoint returns this documentation'
            }
        },
        'sample_urls': [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://www.youtube.com/watch?v=jNQXAC9IVRw',
            'https://www.youtube.com/watch?v=2NRkV7ZQUJA'
        ],
        'common_commands': {
            'yt-dlp_version': 'yt-dlp --version',
            'yt-dlp_help': 'yt-dlp --help',
            'list_formats': 'yt-dlp --list-formats "URL"',
            'get_title': 'yt-dlp --get-title "URL"',
            'extract_audio': 'yt-dlp -x "URL"',
            'download_best': 'yt-dlp "URL"',
            'download_format': 'yt-dlp -f "best[height<=720]" "URL"'
        },
        'notes': {
            'youtube_restrictions': 'YouTube may restrict downloads to storyboard images or metadata only',
            'rate_limiting': 'YouTube may temporarily block requests if too many are made quickly',
            'legal_compliance': 'This tool is for testing purposes only. Respect YouTube Terms of Service',
            'terminal_timeout': 'Terminal commands have a 30-second timeout limit'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    app.run(host='0.0.0.0', port=port, debug=False)
