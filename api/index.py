"""
Vercel Serverless Function entrypoint.
Imports and exports the Flask application from app.py.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app

# Vercel entrypoint handler
app = app
