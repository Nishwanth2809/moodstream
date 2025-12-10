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
    from routes import register_routes

    # Load environment variables
    load_dotenv()

    # Create Flask app
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
    app.config["SESSION_TYPE"] = "filesystem"
    
    # Initialize session
    Session(app)
    
    # Register routes
    register_routes(app)

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



