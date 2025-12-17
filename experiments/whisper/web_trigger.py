#!/usr/bin/env python3
"""
Simple web server for phone-triggered voice control
"""
from flask import Flask, render_template_string
import threading
import queue

app = Flask(__name__)
trigger_queue = queue.Queue()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Voice Control</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            text-align: center;
            width: 100%;
            max-width: 400px;
        }
        h1 {
            color: white;
            margin-bottom: 20px;
            font-size: 28px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .instructions {
            color: rgba(255,255,255,0.9);
            font-size: 14px;
            margin-bottom: 30px;
            line-height: 1.5;
        }
        #triggerBtn {
            width: 220px;
            height: 220px;
            border-radius: 50%;
            border: none;
            background: white;
            color: #667eea;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: all 0.2s ease;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }
        #triggerBtn:active {
            transform: scale(0.95);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }
        #triggerBtn.triggered {
            background: #4ade80;
            color: white;
        }
        .status {
            margin-top: 30px;
            color: white;
            font-size: 18px;
            min-height: 30px;
        }
        .emoji {
            font-size: 72px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Lamp Control</h1>
        <div class="instructions">
            Tap to start recording<br>
            (Your Mac will use iPhone mic)
        </div>
        <button id="triggerBtn" onclick="trigger()">
            <div class="emoji">🎙️</div>
            TAP<br>TO<br>RECORD
        </button>
        <div class="status" id="status">Ready</div>
    </div>

    <script>
        async function trigger() {
            const btn = document.getElementById('triggerBtn');
            const status = document.getElementById('status');

            btn.classList.add('triggered');
            btn.innerHTML = '<div class="emoji">🔴</div>RECORDING';
            status.textContent = 'Speak your command...';

            // Add haptic feedback if supported
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }

            try {
                const response = await fetch('/trigger', {method: 'POST'});
                const data = await response.json();

                status.textContent = 'Command sent!';

                setTimeout(() => {
                    btn.classList.remove('triggered');
                    btn.innerHTML = '<div class="emoji">🎙️</div>TAP<br>TO<br>RECORD';
                    status.textContent = 'Ready';
                }, 2500);
            } catch (error) {
                status.textContent = 'Error: ' + error.message;
                setTimeout(() => {
                    btn.classList.remove('triggered');
                    btn.innerHTML = '<div class="emoji">🎙️</div>TAP<br>TO<br>RECORD';
                    status.textContent = 'Ready';
                }, 2000);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/trigger', methods=['POST'])
def trigger():
    trigger_queue.put('TRIGGER')
    return {'status': 'triggered'}

def run_server(host='0.0.0.0', port=5000):
    """Run Flask server in background thread"""
    app.run(host=host, port=port, debug=False, use_reloader=False)

def start_server(host='0.0.0.0', port=5000):
    """Start web server in background thread"""
    thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    thread.start()
    return trigger_queue

def wait_for_trigger(trigger_queue):
    """Block until trigger received from web interface"""
    trigger_queue.get()
