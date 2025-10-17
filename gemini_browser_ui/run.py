#!/usr/bin/env python3
"""
Gemini Browser UI - Simple HTTP Polling Version
No SocketIO, no threading issues - just simple HTTP requests

Features:
- AI-powered browser control with Gemini 2.5 Computer Use API
- Real-time browser view and control
- Natural language command interface
- Environment variable configuration
"""

import os
import sys
import threading
import time
import signal
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from loguru import logger

# Configure logging first
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO")
)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from computer_use_wrapper import GeminiComputerUseAgent
except ImportError as e:
    logger.error(f"❌ Failed to import GeminiComputerUseAgent: {e}")
    logger.error("Make sure computer_use_wrapper.py exists in the same directory")
    sys.exit(1)

# Load environment from both local and parent directory
project_root = Path(__file__).parent.parent
env_paths = [
    Path(__file__).parent / '.env',  # Local .env first
    project_root / '.env'             # Parent .env as fallback
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
        logger.info(f"📁 Loaded .env from: {env_path}")
        break
else:
    logger.warning("⚠️  No .env file found, using environment variables")

# Configuration from environment
PORT = int(os.getenv('PORT', 8080))
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
MAX_STEPS = int(os.getenv('MAX_STEPS', 50))

# Flask app
app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.urandom(24)

# Session configuration for Cloud Run (client-side secure cookies)
# Cloud Run is stateless, so we use Flask's default secure cookie sessions
# instead of filesystem/redis sessions that don't work across instances
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Security settings for production (Cloud Run uses HTTPS)
is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
app.config['SESSION_COOKIE_SECURE'] = is_production  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Note: We don't use Flask-Session extension for Cloud Run
# Flask's built-in session (secure cookies) is sufficient and works across instances

CORS(app)

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Global state
agent = None
execution_lock = threading.Lock()
current_task = {
    'status': 'idle',  # idle, executing, completed, error
    'prompt': None,
    'result': None,
    'progress': [],
    'realtime_messages': []  # Real-time Gemini messages
}


def get_agent():
    """Get or create agent (runs in main thread)"""
    global agent

    if agent is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in environment")
            logger.info("💡 Get your API key from: https://aistudio.google.com/apikey")
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        logger.info("🚀 Initializing Gemini Computer Use Agent...")
        try:
            agent = GeminiComputerUseAgent(api_key=api_key)
            logger.info("✅ Gemini Computer Use Agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise

    return agent


@app.route('/')
def index():
    """Serve main page - require login"""
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    response = app.make_response(render_template('index_polling.html'))
    # Prevent caching to avoid loading old versions
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')


@app.route('/auth/google')
def auth_google():
    """Redirect to Google OAuth"""
    # Use environment variable for redirect URI (required for Cloud Run)
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
    if not redirect_uri:
        # Fallback to dynamic URL generation for local development
        redirect_uri = url_for('auth_google_callback', _external=True)

    logger.info(f"🔐 OAuth redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def auth_google_callback():
    """Google OAuth callback"""
    try:
        # Get access token (Authlib automatically uses the redirect_uri from authorize_redirect)
        token = google.authorize_access_token()

        # Get user info
        user_info = token.get('userinfo')

        if user_info:
            # Store user info in session
            session['user'] = {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'sub': user_info.get('sub')  # Google user ID
            }

            logger.info(f"✅ User logged in: {user_info.get('email')}")

            return redirect(url_for('index'))
        else:
            logger.error("❌ Failed to get user info from Google")
            return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"❌ OAuth callback error: {e}")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Logout user"""
    if 'user' in session:
        logger.info(f"👋 User logged out: {session['user'].get('email')}")
        session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/moa-architecture')
def moa_architecture():
    """MOA AI Architecture page - require login"""
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    response = app.make_response(render_template('moa_ai_architecture.html'))
    # Prevent caching to avoid loading old versions
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/user')
def get_user():
    """Get current user info"""
    if 'user' in session:
        return jsonify({
            'logged_in': True,
            'user': session['user']
        })
    else:
        return jsonify({
            'logged_in': False
        }), 401


@app.route('/api/status')
def get_status():
    """Get browser and task status"""
    try:
        agent_instance = get_agent()

        # Check if browser is actually running
        browser_ready = (agent_instance.browser is not None and
                        agent_instance.page is not None)

        return jsonify({
            'browser_ready': True,  # Agent is always ready to accept tasks
            'browser_running': browser_ready,
            'url': agent_instance.page.url if agent_instance.page else 'Click Send to start browser',
            'task_status': current_task['status'],
            'task_prompt': current_task['prompt'],
            'headless': HEADLESS,
            'max_steps': MAX_STEPS
        })
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return jsonify({
            'browser_ready': False,
            'browser_running': False,
            'error': str(e),
            'task_status': 'error'
        }), 500


@app.route('/api/execute', methods=['POST'])
def execute_task():
    """Execute Gemini Computer Use task"""
    global current_task

    # Check if already executing
    if not execution_lock.acquire(blocking=False):
        logger.warning("⚠️  Task rejected: Another task is already running")
        return jsonify({
            'status': 'error',
            'error': 'Another task is already running. Please wait for the current task to complete.'
        }), 409

    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'error': 'Invalid JSON data'}), 400

        prompt = data.get('prompt', '').strip()
        max_steps_override = data.get('max_steps', MAX_STEPS)

        if not prompt:
            return jsonify({'status': 'error', 'error': 'Empty prompt provided'}), 400

        logger.info(f"🎯 Executing task: {prompt}")
        logger.info(f"⚙️  Max steps: {max_steps_override}")

        # Update task status
        current_task = {
            'status': 'executing',
            'prompt': prompt,
            'result': None,
            'progress': [],
            'realtime_messages': [],
            'start_time': time.time()
        }

        # Get agent first
        agent_instance = get_agent()

        # Create a thread-safe message list for this specific request
        from queue import Queue
        message_queue = Queue()

        # Define progress callback without closure issues
        def progress_callback(update):
            """Callback to receive real-time progress from agent"""
            try:
                message = {
                    'timestamp': time.time(),
                    'type': update.get('type', 'info'),
                    'message': update.get('message', ''),
                    'round': update.get('round')
                }
                # Use queue instead of direct list append to avoid thread issues
                message_queue.put(message)
                # Also append to current_task for polling
                current_task['realtime_messages'].append(message)
                logger.debug(f"Progress update: {update.get('message', '')}")
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

        # Set progress callback
        agent_instance.progress_callback = progress_callback

        # Always restart browser to avoid greenlet thread issues
        # Close existing browser if any
        if agent_instance.page is not None or agent_instance.context is not None:
            logger.info("🔄 Closing existing browser to avoid thread conflicts...")
            try:
                agent_instance.close_browser()
            except Exception as e:
                logger.warning(f"⚠️  Error closing browser: {e}")

        # Start fresh browser for this request
        logger.info(f"🚀 Starting browser (headless={HEADLESS})...")
        agent_instance.start_browser(headless=HEADLESS)
        logger.info("✅ Browser started successfully!")
        if not HEADLESS:
            logger.info("🖥️  Browser window should be visible on your screen")

        try:
            # Execute task with HYBRID mode (Google Search Grounding + Computer Use)
            # This avoids bot detection by using official Google Search API
            result = agent_instance.execute_hybrid_task(prompt, max_steps=max_steps_override)
        finally:
            # ALWAYS clear callback after task completion to prevent thread issues
            agent_instance.progress_callback = None
            # Force garbage collection of callback closure
            del progress_callback
            import gc
            gc.collect()

            # ALWAYS close browser after task completion
            logger.info("🧹 Closing browser after task completion...")
            try:
                agent_instance.close_browser()
                logger.info("✅ Browser closed successfully")
            except Exception as e:
                logger.warning(f"⚠️  Error closing browser: {e}")

        # Calculate execution time
        execution_time = time.time() - current_task['start_time']

        # Update task status
        current_task = {
            'status': 'completed' if result.get('status') == 'success' else 'error',
            'prompt': prompt,
            'result': result,
            'progress': result.get('actions', []),
            'realtime_messages': current_task['realtime_messages'],  # Keep messages
            'execution_time': execution_time
        }

        logger.info(f"✅ Task completed: {result.get('status')} (took {execution_time:.2f}s)")

        # Add execution metadata to result
        result['execution_time'] = execution_time
        result['steps_taken'] = len(result.get('actions', []))

        return jsonify(result)

    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        # Clear callback and close browser on error
        try:
            agent_instance = get_agent()
            agent_instance.progress_callback = None
            agent_instance.close_browser()
            logger.info("✅ Browser closed after validation error")
        except:
            pass

        current_task = {
            'status': 'error',
            'prompt': current_task.get('prompt'),
            'result': {'error': str(e)},
            'progress': []
        }
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"❌ Execution error: {e}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Traceback:\n{error_trace}")

        # Clear callback and close browser on error
        try:
            agent_instance = get_agent()
            agent_instance.progress_callback = None
            agent_instance.close_browser()
            logger.info("✅ Browser closed after execution error")
        except:
            pass

        current_task = {
            'status': 'error',
            'prompt': current_task.get('prompt'),
            'result': {'error': str(e), 'traceback': error_trace},
            'progress': [],
            'realtime_messages': current_task.get('realtime_messages', [])
        }

        return jsonify({
            'status': 'error',
            'error': str(e),
            'details': error_trace if os.getenv('DEBUG') else None
        }), 500

    finally:
        execution_lock.release()


@app.route('/api/task_status')
def get_task_status():
    """Get current task status (for polling)"""
    return jsonify(current_task)


@app.route('/api/stop', methods=['POST'])
def stop_task():
    """Stop the currently executing task"""
    global agent

    if current_task.get('status') != 'executing':
        return jsonify({
            'status': 'error',
            'error': 'No task is currently executing'
        }), 400

    try:
        agent_instance = get_agent()
        agent_instance.should_stop = True
        logger.info("🛑 Stop requested by user")

        return jsonify({
            'status': 'success',
            'message': 'Stop signal sent to agent'
        })
    except Exception as e:
        logger.error(f"❌ Failed to stop task: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/screenshot')
def get_screenshot():
    """Get current browser screenshot"""
    try:
        agent_instance = get_agent()

        if not agent_instance.page:
            return jsonify({'error': 'Browser not started yet'}), 400

        screenshot_path = agent_instance.take_screenshot()

        # Read and return as base64
        import base64
        with open(screenshot_path, 'rb') as f:
            screenshot_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'screenshot': screenshot_data,
            'url': agent_instance.page.url,
            'title': agent_instance.page.title()
        })
    except Exception as e:
        logger.error(f"❌ Screenshot failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cdp_url')
def get_cdp_url():
    """Get CDP endpoint URL for embedding browser (fallback to screenshot mode)"""
    # Playwright doesn't easily expose CDP for embedding
    # User will see the real browser window instead
    return jsonify({
        'cdp_url': None,
        'message': 'Using screenshot mode - real browser window is visible'
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'agent_initialized': agent is not None,
        'browser_running': agent.page is not None if agent else False,
        'port': PORT,
        'headless': HEADLESS
    })


@app.route('/api/info')
def get_info():
    """Get server information"""
    return jsonify({
        'server': 'Gemini Browser UI',
        'version': '1.0.0',
        'port': PORT,
        'headless': HEADLESS,
        'max_steps': MAX_STEPS,
        'template': 'index_polling.html',
        'api_key_set': bool(os.getenv('GEMINI_API_KEY'))
    })


def cleanup():
    """Cleanup on shutdown"""
    global agent
    if agent:
        logger.info("🧹 Cleaning up resources...")
        try:
            agent.close_browser()
            logger.info("✅ Browser closed successfully")
        except Exception as e:
            logger.error(f"⚠️  Error during cleanup: {e}")
        finally:
            agent = None


def validate_environment():
    """Validate environment variables and dependencies"""
    issues = []

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        issues.append("❌ GEMINI_API_KEY not set")
        issues.append("   Get your key from: https://aistudio.google.com/apikey")
    else:
        logger.info(f"✅ GEMINI_API_KEY found ({api_key[:10]}...)")

    # Check template files
    template_path = Path(__file__).parent / 'frontend' / 'templates' / 'index_polling.html'
    if not template_path.exists():
        issues.append(f"❌ Template not found: {template_path}")
    else:
        logger.info(f"✅ Template found: {template_path.name}")

    # Check port availability
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', PORT))
    sock.close()
    if result == 0:
        issues.append(f"⚠️  Port {PORT} is already in use")
        issues.append(f"   Kill existing process: lsof -ti:{PORT} | xargs kill -9")
        issues.append(f"   Or use different port: PORT=8081 python run.py")

    return issues


def signal_handler(signum, _):
    """Handle shutdown signals gracefully"""
    logger.info(f"\n⚠️  Received signal {signum}")
    cleanup()
    sys.exit(0)


if __name__ == '__main__':
    import atexit
    atexit.register(cleanup)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Print banner
    logger.info("=" * 70)
    logger.info("🌐 Gemini Browser UI - AI-Powered Browser Automation")
    logger.info("=" * 70)
    logger.info(f"📍 Server URL:    http://localhost:{PORT}")
    logger.info(f"🔧 Headless Mode: {HEADLESS}")
    logger.info(f"📊 Max Steps:     {MAX_STEPS}")
    logger.info(f"🔑 API Key:       {os.getenv('GEMINI_API_KEY', 'NOT SET')[:15]}...")
    logger.info("=" * 70)

    # Validate environment
    logger.info("🔍 Validating environment...")
    issues = validate_environment()

    if issues:
        logger.error("\n⚠️  Environment validation failed:")
        for issue in issues:
            logger.error(f"   {issue}")

        # Only exit if API key is missing
        if not os.getenv('GEMINI_API_KEY'):
            logger.error("\n❌ Cannot start without GEMINI_API_KEY")
            sys.exit(1)
        else:
            logger.warning("\n⚠️  Continuing despite warnings...\n")
    else:
        logger.info("✅ Environment validation passed\n")

    # Initialize agent on startup (lazy initialization)
    logger.info("🚀 Starting server...")
    logger.info(f"💡 Agent will be initialized on first request")
    logger.info(f"🌐 Open http://localhost:{PORT} in your browser\n")

    try:
        # Run Flask with threading to allow parallel requests (status polling while executing)
        # Callback issues are now handled by proper cleanup after each task
        # Enable debug mode in development for auto-reload of templates and code
        is_dev = os.getenv('ENVIRONMENT', 'development') == 'development'
        app.run(host='0.0.0.0', port=PORT, debug=is_dev, threaded=True, use_reloader=is_dev)
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        cleanup()
    except Exception as e:
        logger.error(f"\n❌ Server error: {e}")
        cleanup()
        sys.exit(1)
