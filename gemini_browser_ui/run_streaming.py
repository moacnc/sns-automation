#!/usr/bin/env python3
"""
Gemini Browser UI - Real-time Streaming Version
Uses Server-Sent Events (SSE) for real-time progress updates
"""

import os
import sys
import threading
import queue
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from loguru import logger

# Configure logging first
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from computer_use_wrapper import GeminiComputerUseAgent

# Load environment from project root (parent directory)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
logger.info(f"📁 Loading .env from: {env_path}")

# Flask app
app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)

# Global state
agent = None
execution_lock = threading.Lock()
current_task = {
    'status': 'idle',  # idle, executing, completed, error
    'prompt': None,
    'result': None,
    'progress': []
}

# Queue for progress events
progress_queues = {}  # session_id -> queue


def get_agent():
    """Get or create agent (runs in main thread)"""
    global agent

    if agent is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        logger.info("🚀 Initializing Gemini Computer Use Agent...")
        agent = GeminiComputerUseAgent(api_key=api_key)
        logger.info("✓ Gemini Computer Use Agent initialized")

    return agent


def progress_callback(event):
    """
    Callback for progress events from agent
    Broadcasts to all connected clients
    """
    # Add to all queues
    for q in progress_queues.values():
        try:
            q.put(event)
        except:
            pass


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index_streaming.html')


@app.route('/api/status')
def get_status():
    """Get browser and task status"""
    try:
        agent_instance = get_agent()

        # Browser is closed after each task (normal behavior)
        browser_running = (agent_instance.page is not None and
                          agent_instance.context is not None)

        return jsonify({
            'browser_ready': True,  # Agent is always ready to accept new tasks
            'browser_running': browser_running,
            'url': agent_instance.page.url if browser_running else 'Ready - Click Send to start new task',
            'task_status': current_task['status'],
            'task_prompt': current_task['prompt']
        })
    except Exception as e:
        return jsonify({
            'browser_ready': False,
            'browser_running': False,
            'error': str(e),
            'task_status': 'error'
        }), 500


@app.route('/api/progress/<session_id>')
def stream_progress(session_id):
    """Server-Sent Events endpoint for real-time progress"""
    import json

    def generate():
        # Create queue for this client
        q = queue.Queue()
        progress_queues[session_id] = q

        try:
            # Send initial connection message (properly JSON-encoded)
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Progress stream connected'})}\n\n"

            # Stream progress events
            while True:
                try:
                    event = q.get(timeout=30)  # 30s timeout for keepalive
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    # Send keepalive (properly JSON-encoded)
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
        finally:
            # Cleanup
            if session_id in progress_queues:
                del progress_queues[session_id]

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/execute', methods=['POST'])
def execute_task():
    """Execute Gemini Computer Use task in background thread"""
    global current_task

    # Check if already executing
    if current_task['status'] == 'executing':
        return jsonify({
            'status': 'error',
            'error': 'Another task is already running'
        }), 409

    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return jsonify({'status': 'error', 'error': 'Empty prompt'}), 400

        logger.info(f"🎯 Executing: {prompt}")

        # Update task status
        current_task = {
            'status': 'executing',
            'prompt': prompt,
            'result': None,
            'progress': []
        }

        # Execute in background thread
        def run_task():
            global current_task
            agent_instance = None

            try:
                agent_instance = get_agent()

                # Set progress callback
                agent_instance.progress_callback = progress_callback

                # Always start fresh browser for this task (solves thread issues)
                logger.info("🚀 Starting new browser window for this task...")
                progress_callback({
                    'type': 'info',
                    'message': '🚀 브라우저 창을 여는 중...'
                })
                agent_instance.start_browser(headless=False)
                logger.info("✅ Browser window opened!")
                logger.info("🖥️  You should see Chrome window on your screen!")
                progress_callback({
                    'type': 'info',
                    'message': '✅ 브라우저 준비 완료!'
                })

                # Execute task with autonomous execution (max 50 rounds)
                result = agent_instance.execute_task(prompt, max_steps=50)

                # Update task status
                current_task = {
                    'status': 'completed' if result.get('status') == 'success' else 'error',
                    'prompt': prompt,
                    'result': result,
                    'progress': result.get('actions', [])
                }

                # Send completion event
                progress_callback({
                    'type': 'completed',
                    'result': result
                })

                logger.info(f"✅ Task completed: {result.get('status')}")

            except Exception as e:
                logger.error(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

                current_task = {
                    'status': 'error',
                    'prompt': prompt,
                    'result': {'error': str(e)},
                    'progress': []
                }

                progress_callback({
                    'type': 'error',
                    'message': f'❌ 오류: {str(e)}'
                })

            finally:
                # CRITICAL: Always close browser after task to prevent thread issues
                if agent_instance:
                    logger.info("🧹 Closing browser to prevent thread conflicts...")
                    progress_callback({
                        'type': 'info',
                        'message': '🧹 브라우저 정리 중...'
                    })
                    agent_instance.close_browser()
                    logger.info("✅ Browser closed - ready for next task")

        # Start background thread
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()

        return jsonify({
            'status': 'started',
            'message': 'Task execution started'
        })

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/stop', methods=['POST'])
def stop_task():
    """Stop currently executing task"""
    try:
        agent_instance = get_agent()
        agent_instance.stop_task()

        logger.info("🛑 Stop requested")

        return jsonify({
            'status': 'success',
            'message': 'Stop signal sent'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/task_status')
def get_task_status():
    """Get current task status (for polling)"""
    return jsonify(current_task)


@app.route('/api/screenshot')
def get_screenshot():
    """Get current browser screenshot"""
    try:
        agent_instance = get_agent()
        screenshot_path = agent_instance.take_screenshot()

        # Read and return as base64
        import base64
        with open(screenshot_path, 'rb') as f:
            screenshot_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'screenshot': screenshot_data,
            'url': agent_instance.page.url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def cleanup():
    """Cleanup on shutdown"""
    global agent
    if agent:
        logger.info("Cleaning up...")
        agent.close_browser()
        agent = None


if __name__ == '__main__':
    import atexit
    atexit.register(cleanup)

    logger.info("=" * 60)
    logger.info("🌐 Gemini Browser UI - Real-time Streaming Version")
    logger.info("=" * 60)
    logger.info(f"📍 Server: http://localhost:8080")
    logger.info(f"🔑 API Key: {os.getenv('GEMINI_API_KEY', 'NOT SET')[:20]}...")
    logger.info("=" * 60)

    # Initialize browser on startup
    try:
        get_agent()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")

    try:
        # Run with threading support for SSE
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        cleanup()
