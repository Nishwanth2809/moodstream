import sys
import os
from pathlib import Path

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from flask import Flask
    from flask_session import Session
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Create Flask app with minimal setup
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
    app.config["SESSION_TYPE"] = "filesystem"
    
    # Initialize session
    Session(app)
    
    # Lazy load routes - only when needed
    _routes_registered = False
    
    @app.before_request
    def register_routes_on_first_request():
        global _routes_registered
        if not _routes_registered:
            try:
                from routes import register_routes
                register_routes(app)
                _routes_registered = True
            except Exception as e:
                print(f"Error registering routes: {e}")
                import traceback
                traceback.print_exc()

except Exception as e:
    import traceback
    print(f"Error initializing app: {e}")
    print(traceback.format_exc())
    
    # Create a minimal error app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"<h1>Error initializing app</h1><pre>{traceback.format_exc()}</pre>", 500




