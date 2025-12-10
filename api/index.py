import sys
import os

# Set up the path to import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Now import Flask app
from flask import Flask
from flask_session import Session
from routes import register_routes

# Create Flask app
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

register_routes(app)

# For Vercel: export the app instance


