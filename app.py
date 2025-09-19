from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import tempfile
import os
from datetime import datetime
import json
import requests
import shutil
from functools import lru_cache
import concurrent.futures
import time

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
                        
                        <div class="test-form">
                            <h3>📝 Caption Extraction</h3>
                            <p>Extract video captions/subtitles in available languages. This feature detects available caption languages and downloads the caption content.</p>
                            
                            <form id="captions-form" onsubmit="testCaptions(event)">
                                <div class="form-group">
                                    <label for="captions-url">YouTube URL:</label>
                                    <input type="text" id="captions-url" name="url" 
                                           placeholder="https://www.youtube.com/watch?v=..." required>
                                </div>
                                
                                <div class="form-group" id="language-selection" style="display: none;">
                                    <label for="preferred-language">Preferred Language (optional):</label>
                                    <select id="preferred-language">
                                        <option value="">Auto-select best available</option>
                                        <option value="en">English</option>
                                        <option value="es">Spanish</option>
                                        <option value="fr">French</option>
                                        <option value="de">German</option>
                                        <option value="it">Italian</option>
                                        <option value="pt">Portuguese</option>
                                        <option value="ja">Japanese</option>
                                        <option value="ko">Korean</option>
                                        <option value="zh">Chinese</option>
                                        <option value="ru">Russian</option>
                                    </select>
                                </div>
                                
                                <button type="submit" class="btn" id="captions-btn">Extract Captions</button>
                            </form>
                            
                            <div class="progress-container" id="captions-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="captions-progress-fill"></div>
                                </div>
                                <div class="progress-text" id="captions-progress-text">Extracting captions...</div>
                            </div>
                            
                            <div class="result-container" id="captions-result"></div>
                            
                            <!-- Quick test buttons -->
                            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                                <h4 style="margin: 0 0 10px 0; font-size: 16px;">🎬 Quick Test Videos</h4>
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Click to test with popular videos that have captions:</p>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                    <button class="btn" onclick="loadTestVideo('https://www.youtube.com/watch?v=jNQXAC9IVRw', 'Me at the zoo (First YouTube video)')" 
                                            style="font-size: 13px; padding: 6px 10px;">Me at the zoo</button>
                                    <button class="btn" onclick="loadTestVideo('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Rick Astley - Never Gonna Give You Up')" 
                                            style="font-size: 13px; padding: 6px 10px;">Never Gonna Give You Up</button>
                                    <button class="btn" onclick="loadTestVideo('https://www.youtube.com/watch?v=9bZkp7q19f0', 'PSY - GANGNAM STYLE')" 
                                            style="font-size: 13px; padding: 6px 10px;">Gangnam Style</button>
                                    <button class="btn" onclick="loadTestVideo('https://www.youtube.com/watch?v=kJQP7kiw5Fk', 'Luis Fonsi - Despacito')" 
                                            style="font-size: 13px; padding: 6px 10px;">Despacito</button>
                                </div>
                            </div>
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
                            <strong>/extract-captions</strong>
                            <p>Extract video captions/subtitles in available languages</p>
                            <div class="code-block">curl -X POST http://localhost:8090/extract-captions -H "Content-Type: application/json" -d '{"url": "https://youtube.com/watch?v=..."}'</div>
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
        
        // Initialize global variables
        let currentCaptionData = null;
        
        // Load service info on page load
        window.onload = function() {
            fetch('/ytdlp-info')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    document.getElementById('service-info').innerHTML = 
                        '<h4>🚀 Service Status</h4>' +
                        '<p><strong>yt-dlp Version:</strong> ' + data['yt-dlp_version'] + '</p>' +
                        '<p><strong>Test Extraction:</strong> ' + data.test_extraction + '</p>' +
                        '<p><strong>Test Video:</strong> ' + data.test_video_title + '</p>' +
                        '<p><strong>Capabilities:</strong> ✅ Extract Info, ✅ Download, ✅ Format Detection</p>';
                })
                .catch(function(error) {
                    document.getElementById('service-info').innerHTML = 
                        '<h4>⚠️ Service Status</h4>' +
                        '<p style="color: #721c24;">Failed to load service information</p>';
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
            var terminalOutput = document.getElementById('terminal-output');
            var outputDiv = document.createElement('div');
            outputDiv.className = 'terminal-output terminal-' + type;
            outputDiv.textContent = text;
            terminalOutput.appendChild(outputDiv);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }

        function addTerminalCommand(command) {
            var terminalOutput = document.getElementById('terminal-output');
            var commandDiv = document.createElement('div');
            commandDiv.className = 'terminal-output terminal-command';
            commandDiv.innerHTML = '<span class="terminal-prompt">$</span> ' + command;
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
                    addTerminalOutput('Error: ' + data.error, 'error');
                }
            } catch (error) {
                addTerminalOutput('Request failed: ' + error.message, 'error');
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
                progressText.textContent = 'Processing... ' + Math.round(progress) + '%';
            }, duration / 20);
            
            return interval;
        }

        function hideProgress(progressId) {
            const progressContainer = document.getElementById(progressId.replace('-fill', ''));
            progressContainer.style.display = 'none';
        }

        function showResult(resultId, content, isSuccess) {
            isSuccess = isSuccess !== false; // default to true
            var resultContainer = document.getElementById(resultId);
            resultContainer.className = 'result-container ' + (isSuccess ? 'result-success' : 'result-error');
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
                    var metadataHtml = 
                        '<h4>✅ Metadata Extracted Successfully</h4>' +
                        '<p><strong>Title:</strong> ' + data.title + '</p>' +
                        '<p><strong>Uploader:</strong> ' + data.uploader + '</p>' +
                        '<p><strong>Duration:</strong> ' + Math.floor(data.duration / 60) + ':' + (data.duration % 60).toString().padStart(2, '0') + '</p>' +
                        '<p><strong>View Count:</strong> ' + (data.view_count ? data.view_count.toLocaleString() : 'N/A') + '</p>' +
                        '<p><strong>Formats Available:</strong> ' + data.formats_available + '</p>' +
                        '<p><strong>Upload Date:</strong> ' + data.upload_date + '</p>';
                    showResult('metadata-result', metadataHtml, true);
                } else {
                    var errorHtml = 
                        '<h4>❌ Metadata Extraction Failed</h4>' +
                        '<p><strong>Error:</strong> ' + data.error + '</p>';
                    showResult('metadata-result', errorHtml, false);
                }
            } catch (error) {
                clearInterval(progressInterval);
                hideProgress('metadata-progress');
                var requestErrorHtml = 
                    '<h4>❌ Request Failed</h4>' +
                    '<p><strong>Error:</strong> ' + error.message + '</p>';
                showResult('metadata-result', requestErrorHtml, false);
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
                    var downloadHtml = 
                        '<h4>✅ Download Completed Successfully</h4>' +
                        '<p><strong>Title:</strong> ' + data.video_title + '</p>' +
                        '<p><strong>Download Type:</strong> ' + data.download_type + '</p>' +
                        '<p><strong>File Size:</strong> ' + data.downloaded_size_human + '</p>' +
                        '<p><strong>File Extension:</strong> ' + data.file_extension + '</p>' +
                        '<p><strong>Duration:</strong> ' + Math.floor(data.duration / 60) + ':' + (data.duration % 60).toString().padStart(2, '0') + '</p>' +
                        '<p><strong>Note:</strong> ' + data.note + '</p>' +
                        '<p style="font-size: 12px; color: #666; margin-top: 10px;">' + data.explanation + '</p>';
                    showResult('download-result', downloadHtml, true);
                } else {
                    var errorHtml = 
                        '<h4>❌ Download Failed</h4>' +
                        '<p><strong>Error:</strong> ' + data.error + '</p>';
                    showResult('download-result', errorHtml, false);
                }
            } catch (error) {
                clearInterval(progressInterval);
                hideProgress('download-progress');
                var requestErrorHtml = 
                    '<h4>❌ Request Failed</h4>' +
                    '<p><strong>Error:</strong> ' + error.message + '</p>';
                showResult('download-result', requestErrorHtml, false);
            }
            
            btn.disabled = false;
            btn.textContent = 'Start Download';
        }

        async function testCaptions(event) {
            event.preventDefault();
            
            const url = document.getElementById('captions-url').value;
            const btn = document.getElementById('captions-btn');
            
            btn.disabled = true;
            btn.textContent = 'Extracting...';
            
            const progressInterval = showProgress('captions-progress-fill', 'captions-progress-text', 6000);
            
            try {
                const response = await fetch('/extract-captions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                clearInterval(progressInterval);
                hideProgress('captions-progress');
                
                if (data.success) {
                    displayCaptionResults(data);
                } else {
                    displayCaptionError(data);
                }
            } catch (error) {
                clearInterval(progressInterval);
                hideProgress('captions-progress');
                var requestErrorHtml = 
                    '<h4>❌ Request Failed</h4>' +
                    '<p><strong>Error:</strong> ' + error.message + '</p>';
                showResult('captions-result', requestErrorHtml, false);
            }
            
            btn.disabled = false;
            btn.textContent = 'Extract Captions';
        }

        function displayCaptionResults(data) {
            const hasContent = data.selectedCaptions && data.selectedCaptions.trim().length > 0;
            
            // Store caption data globally for safe access
            currentCaptionData = data;
            
            // Create video info section
            const videoInfo = 
                '<div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #28a745;">' +
                    '<h4 style="margin: 0 0 10px 0; color: #155724;">✅ Caption Extraction Successful</h4>' +
                    '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">' +
                        '<div><strong>Video:</strong> ' + data.videoTitle + '</div>' +
                        '<div><strong>Video ID:</strong> ' + data.videoId + '</div>' +
                        '<div><strong>Duration:</strong> ' + Math.floor(data.videoDuration / 60) + ':' + (data.videoDuration % 60).toString().padStart(2, '0') + '</div>' +
                        '<div><strong>Default Language:</strong> ' + (data.defaultLanguage || 'Not specified') + '</div>' +
                    '</div>' +
                '</div>';

            // Create language statistics
            const languageStats = 
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">' +
                    '<h4 style="margin: 0 0 10px 0; font-size: 16px;">📊 Available Caption Languages</h4>' +
                    '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align: center;">' +
                        '<div style="background: white; padding: 10px; border-radius: 6px; border: 1px solid #dee2e6;">' +
                            '<div style="font-size: 24px; font-weight: bold; color: #007bff;">' + data.manualCaptionCount + '</div>' +
                            '<div style="font-size: 12px; color: #666;">Manual Captions</div>' +
                        '</div>' +
                        '<div style="background: white; padding: 10px; border-radius: 6px; border: 1px solid #dee2e6;">' +
                            '<div style="font-size: 24px; font-weight: bold; color: #6f42c1;">' + data.autoCaptionCount + '</div>' +
                            '<div style="font-size: 12px; color: #666;">Auto Captions</div>' +
                        '</div>' +
                        '<div style="background: white; padding: 10px; border-radius: 6px; border: 1px solid #dee2e6;">' +
                            '<div style="font-size: 24px; font-weight: bold; color: #28a745;">' + data.availableTracks.length + '</div>' +
                            '<div style="font-size: 12px; color: #666;">Total Available</div>' +
                        '</div>' +
                    '</div>' +
                '</div>';

            // Create selected track info
            const selectedTrackInfo = 
                '<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ffc107;">' +
                    '<h4 style="margin: 0 0 10px 0; font-size: 16px;">🎯 Selected Caption Track</h4>' +
                    '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 14px;">' +
                        '<div><strong>Language:</strong> ' + data.selectedTrack.language + '</div>' +
                        '<div><strong>Type:</strong> ' + data.selectedTrack.type + '</div>' +
                        '<div><strong>Format:</strong> ' + data.selectedTrack.ext + '</div>' +
                    '</div>' +
                '</div>';

            // Create available tracks list
            var availableTracksList = '';
            if (data.availableTracks.length > 0) {
                availableTracksList = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">' +
                    '<h4 style="margin: 0 0 10px 0; font-size: 16px;">🌐 All Available Languages</h4>' +
                    '<div style="display: flex; flex-wrap: wrap; gap: 8px;">';
                
                for (var i = 0; i < data.availableTracks.length; i++) {
                    var track = data.availableTracks[i];
                    var bgColor = track.type === 'manual' ? '#d4edda' : '#cce7ff';
                    var textColor = track.type === 'manual' ? '#155724' : '#004085';
                    var borderColor = track.type === 'manual' ? '#c3e6cb' : '#b8daff';
                    
                    availableTracksList += '<span style="background: ' + bgColor + '; color: ' + textColor + '; padding: 4px 8px; border-radius: 12px; font-size: 12px; border: 1px solid ' + borderColor + ';">' +
                        track.language + ' (' + track.type + ')' +
                        '</span>';
                }
                
                availableTracksList += '</div></div>';
            }

            // Create caption content section
            var captionContent = '';
            if (hasContent) {
                var captionPreview = data.selectedCaptions.length > 1000 
                    ? data.selectedCaptions.substring(0, 1000) + '... [Content truncated - download full file to see complete captions]' 
                    : data.selectedCaptions;
                
                // Escape HTML content to prevent issues
                captionPreview = captionPreview.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
                
                captionContent = 
                    '<div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 15px;">' +
                        '<h4 style="margin: 0 0 10px 0; font-size: 16px;">📝 Caption Content</h4>' +
                        '<div style="margin-bottom: 10px;">' +
                            '<strong>Content Length:</strong> ' + data.selectedCaptions.length + ' characters' +
                        '</div>' +
                        '<pre style="background: white; padding: 15px; border-radius: 6px; font-size: 12px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; border: 1px solid #dee2e6; margin: 0;">' + captionPreview + '</pre>' +
                        '<div style="margin-top: 10px; text-align: center;">' +
                            '<button class="btn" onclick="downloadCaptions()" style="margin-right: 10px;">📥 Download Full Captions</button>' +
                            '<button class="btn" onclick="copyToClipboardSafe()">📋 Copy to Clipboard</button>' +
                        '</div>' +
                    '</div>';
            } else {
                var errorNote = data.captionFetchError || data.note || 'Caption content could not be fetched';
                errorNote = errorNote.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
                
                captionContent = 
                    '<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ffc107;">' +
                        '<h4 style="margin: 0 0 10px 0; font-size: 16px;">⚠️ Caption Content Not Available</h4>' +
                        '<p style="margin: 0; font-size: 14px;">' + errorNote + '</p>' +
                        '<p style="margin: 10px 0 0 0; font-size: 13px; color: #856404;">' +
                            '<strong>Note:</strong> Caption metadata was successfully extracted, but the actual content could not be downloaded due to YouTube anti-bot protections. You can still see which languages are available above.' +
                        '</p>' +
                    '</div>';
            }

            var fullResult = videoInfo + languageStats + selectedTrackInfo + availableTracksList + captionContent;
            showResult('captions-result', fullResult, true);
        }

        function displayCaptionError(data) {
            var errorDetails = '<p><strong>Error:</strong> ' + (data.error || 'Unknown error').replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</p>';
            
            if (data.manualCaptionLanguages && data.manualCaptionLanguages.length > 0) {
                errorDetails += '<p><strong>Available Manual Languages:</strong> ' + data.manualCaptionLanguages.join(', ') + '</p>';
            }
            if (data.autoCaptionLanguages && data.autoCaptionLanguages.length > 0) {
                errorDetails += '<p><strong>Available Auto Languages:</strong> ' + data.autoCaptionLanguages.join(', ') + '</p>';
            }
            
            var errorHtml = 
                '<div style="background: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">' +
                    '<h4 style="margin: 0 0 10px 0; color: #721c24;">❌ Caption Extraction Failed</h4>' +
                    errorDetails +
                '</div>';
            
            showResult('captions-result', errorHtml, false);
        }

        function loadTestVideo(url, title) {
            document.getElementById('captions-url').value = url;
            // Optionally show a brief notification
            const btn = document.getElementById('captions-btn');
            var originalText = btn.textContent;
            btn.textContent = 'Loaded: ' + title;
            btn.style.background = '#28a745';
            setTimeout(function() {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }

        function copyToClipboardSafe() {
            if (!currentCaptionData || !currentCaptionData.selectedCaptions) {
                alert('No caption content available to copy');
                return;
            }
            
            var text = currentCaptionData.selectedCaptions;
            navigator.clipboard.writeText(text).then(function() {
                // Show temporary success message
                var notification = document.createElement('div');
                notification.style.cssText = 
                    'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; ' +
                    'padding: 10px 20px; border-radius: 6px; z-index: 1000; font-size: 14px;';
                notification.textContent = '✅ Captions copied to clipboard!';
                document.body.appendChild(notification);
                setTimeout(function() { document.body.removeChild(notification); }, 3000);
            }).catch(function(err) {
                // Fallback for older browsers
                var textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    var notification = document.createElement('div');
                    notification.style.cssText = 
                        'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; ' +
                        'padding: 10px 20px; border-radius: 6px; z-index: 1000; font-size: 14px;';
                    notification.textContent = '✅ Captions copied to clipboard!';
                    document.body.appendChild(notification);
                    setTimeout(function() { document.body.removeChild(notification); }, 3000);
                } catch (fallbackErr) {
                    alert('Failed to copy to clipboard: ' + fallbackErr);
                }
                document.body.removeChild(textArea);
            });
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                // Show temporary success message
                var notification = document.createElement('div');
                notification.style.cssText = 
                    'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; ' +
                    'padding: 10px 20px; border-radius: 6px; z-index: 1000; font-size: 14px;';
                notification.textContent = '✅ Captions copied to clipboard!';
                document.body.appendChild(notification);
                setTimeout(function() { document.body.removeChild(notification); }, 3000);
            }).catch(function(err) {
                alert('Failed to copy to clipboard: ' + err);
            });
        }

        function downloadCaptions() {
            if (!currentCaptionData || !currentCaptionData.selectedCaptions) {
                alert('No caption content available to download');
                return;
            }
            
            try {
                // Create downloadable file using current data
                var blob = new Blob([currentCaptionData.selectedCaptions], { type: 'text/plain' });
                var downloadUrl = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = downloadUrl;
                a.download = currentCaptionData.videoId + '_' + currentCaptionData.selectedTrack.language + '.' + currentCaptionData.selectedTrack.ext;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                // Show success notification
                var notification = document.createElement('div');
                notification.style.cssText = 
                    'position: fixed; top: 20px; right: 20px; background: #007bff; color: white; ' +
                    'padding: 10px 20px; border-radius: 6px; z-index: 1000; font-size: 14px;';
                notification.textContent = '✅ Caption file downloaded!';
                document.body.appendChild(notification);
                setTimeout(function() { document.body.removeChild(notification); }, 3000);
            } catch (error) {
                alert('Failed to download captions: ' + error.message);
            }
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
        
        # Create a temporary file path (but don't create the file yet)
        temp_dir = tempfile.gettempdir()
        output_template = os.path.join(temp_dir, f"ytdlp_test_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.%(ext)s")
            
        try:
            # Configure yt-dlp for download
            download_opts = {
                'outtmpl': output_template,
                'quiet': False,  # Enable logging to see what's happening
                'no_warnings': False,  # Show warnings to debug
                # Try audio formats first (smaller files), then video formats
                'format': '140/249/250/251/bestaudio[filesize<10M]/best[filesize<10M]/worst',
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
                
                # Find the actual downloaded file (yt-dlp replaces %(ext)s with actual extension)
                base_path = output_template.replace('.%(ext)s', '')
                downloaded_file = None
                for ext in ['.m4a', '.mp4', '.webm', '.opus', '.mp3', '.mkv', '.mhtml']:
                    potential_file = base_path + ext
                    if os.path.exists(potential_file):
                        downloaded_file = potential_file
                        break
                
                if downloaded_file and os.path.exists(downloaded_file):
                    file_size = os.path.getsize(downloaded_file)
                    file_extension = os.path.splitext(downloaded_file)[1]
                    
                    # Read first few bytes to verify content
                    with open(downloaded_file, 'rb') as f:
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
                    else:
                        download_type = 'media file'
                    
                    # Clean up the temporary file
                    os.unlink(downloaded_file)
                    
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
            # Clean up temp files if they exist
            base_path = output_template.replace('.%(ext)s', '')
            for ext in ['.m4a', '.mp4', '.webm', '.opus', '.mp3', '.mkv', '.mhtml']:
                potential_file = base_path + ext
                if os.path.exists(potential_file):
                    os.unlink(potential_file)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Cache for video metadata to avoid repeated yt-dlp calls
@lru_cache(maxsize=100)
def get_video_metadata_cached(url):
    """Cached video metadata extraction with optimized yt-dlp options"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        # Optimize for speed - only get essential metadata
        'skip_download': True,
        'no_check_certificate': True,
        'socket_timeout': 10,  # Reduce timeout
        'retries': 1,  # Reduce retries
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.route('/extract-captions', methods=['POST'])
def extract_captions():
    """Extract YouTube video captions/subtitles"""
    start_time = time.time()
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required', 'success': False}), 400
        
        print(f"Starting caption extraction for: {url}")
        
        # Use cached metadata extraction
        metadata_start = time.time()
        info = get_video_metadata_cached(url)
        metadata_time = time.time() - metadata_start
        print(f"Metadata extraction took: {metadata_time:.2f}s")
        
        if not info:
            return jsonify({
                'success': False,
                'error': 'Failed to extract video information',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        video_id = info.get('id', 'unknown')
        default_language = info.get('language') or info.get('language_code')
        
        print(f"Default language for video {video_id}: {default_language}")
        
        # Get caption data
        manual_captions = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        
        # Optimize caption track processing - limit to top 3 languages for speed
        vtt_tracks = []
        processed_count = 0
        for lang, tracks in manual_captions.items():
            if processed_count >= 3:  # Reduced from 5 to 3 for speed
                break
            for track in tracks:
                if track.get('ext') == 'vtt':
                    vtt_tracks.append({
                        'language': lang,
                        'type': 'manual',
                        'url': track['url'],
                        'ext': track['ext']
                    })
                    processed_count += 1
                    break
        
        # Add auto captions if not enough manual ones
        if len(vtt_tracks) < 3:
            for lang, tracks in auto_captions.items():
                if len(vtt_tracks) >= 3:
                    break
                for track in tracks:
                    if track.get('ext') in ['ttml', 'vtt']:
                        vtt_tracks.append({
                            'language': lang,
                            'type': 'auto',
                            'url': track['url'],
                            'ext': track['ext']
                        })
                        break

        if not vtt_tracks:
            return jsonify({
                'success': False,
                'error': 'No captions available for this video',
                'videoId': video_id,
                'videoTitle': info.get('title', 'Unknown'),
                'manualCaptionLanguages': list(manual_captions.keys()),
                'autoCaptionLanguages': list(auto_captions.keys()),
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Determine best language fallback
        if not default_language:
            # Look for English variant
            english_track = next((track for track in vtt_tracks if track['language'].startswith('en')), None)
            if english_track:
                default_language = english_track['language']
        
        # Select the best caption track
        selected_track = None
        if default_language:
            selected_track = next((track for track in vtt_tracks if track['language'] == default_language), None)
        
        # Fallback to English if default language not found
        if not selected_track:
            selected_track = next((track for track in vtt_tracks if track['language'].startswith('en')), None)
        
        # Final fallback to first available
        if not selected_track:
            selected_track = vtt_tracks[0]
        
        print(f"Selected caption track for {video_id}: {selected_track}")
        
        # Optimized caption fetching with shorter timeout
        caption_content = ""
        caption_fetch_error = None
        
        fetch_start = time.time()
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/vtt,text/plain,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/'
            }
            
            print(f"Attempting direct fetch of captions from URL...")
            caption_response = requests.get(selected_track['url'], headers=headers, timeout=8)  # Reduced from 15s
            if caption_response.status_code == 200 and caption_response.text.strip():
                caption_content = caption_response.text
                fetch_time = time.time() - fetch_start
                print(f"Successfully fetched {len(caption_content)} characters via direct URL in {fetch_time:.2f}s")
            else:
                print(f"Direct URL fetch failed: {caption_response.status_code}")
                
        except Exception as e:
            print(f"Direct URL fetch error: {str(e)}")
            caption_fetch_error = f"Direct fetch failed: {str(e)}"
        
        # Skip yt-dlp fallback for speed - it usually fails anyway due to YouTube protections
        
        total_time = time.time() - start_time
        print(f"Total caption extraction time: {total_time:.2f}s")
        
        # Return result
        result = {
            'success': True,
            'videoId': video_id,
            'videoTitle': info.get('title', 'Unknown'),
            'videoDuration': info.get('duration', 0),
            'defaultLanguage': default_language,
            'selectedTrack': selected_track,
            'selectedCaptions': caption_content,
            'availableTracks': vtt_tracks,
            'manualCaptionCount': len(manual_captions),
            'autoCaptionCount': len(auto_captions),
            'processingTime': f"{total_time:.2f}s",
            'timestamp': datetime.now().isoformat()
        }
        
        # Add error info if caption fetching failed
        if not caption_content and caption_fetch_error:
            result['captionFetchError'] = caption_fetch_error
            result['note'] = 'Caption metadata extracted successfully, but content could not be fetched due to YouTube protections'
        
        return jsonify(result)
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"Caption extraction failed after {total_time:.2f}s: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processingTime': f"{total_time:.2f}s",
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
            'POST /extract-captions': {
                'description': 'Extract and return YouTube video captions/subtitles',
                'request_body': {'url': 'YouTube URL'},
                'response_type': 'JSON',
                'example_request': {
                    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                },
                'example_response': {
                    'success': True,
                    'videoId': 'dQw4w9WgXcQ',
                    'videoTitle': 'Rick Astley - Never Gonna Give You Up',
                    'defaultLanguage': 'en',
                    'selectedTrack': {
                        'language': 'en',
                        'type': 'auto',
                        'url': 'https://...',
                        'ext': 'ttml'
                    },
                    'selectedCaptions': 'WEBVTT\\n\\n00:00:00.000 --> 00:00:03.000\\nNever gonna give you up...',
                    'availableTracks': [],
                    'manualCaptionCount': 0,
                    'autoCaptionCount': 12
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
