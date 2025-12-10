from flask import Flask
from flask_session import Session
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import register_routes

load_dotenv()

app = Flask(__name__, template_folder="../templates")
app.secret_key = os.getenv("FLASK_SECRET", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

register_routes(app)

# For Vercel serverless functions
