"""
Vercel Serverless Entry Point
Exports the FastAPI app as `app` for Vercel's ASGI adapter.
"""
import sys
import os

# Add the project root to sys.path so `backend` package imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

# Vercel looks for the `app` variable in this module
