# api/index.py - Vercel entry point
import sys
import os
from pathlib import Path

# Add the project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from app.main import app

# Vercel requires this to be named 'app'
application = app