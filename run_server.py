import uvicorn
import webbrowser
import time
import socket
import threading
import sys
import os

# Add root directory to sys.path so 'backend' package imports resolve
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app

# Mount frontend static files for local development
# (In production on Vercel, static files are served by Vercel's routing layer)
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

def wait_and_open_browser():
    url = "http://localhost:8000"
    print(f"Waiting for server to start on {url}...")
    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", 8000), timeout=0.5):
                print(f"Server is live! Opening browser at {url}...")
                webbrowser.open(url)
                return
        except (OSError, ConnectionRefusedError):
            time.sleep(0.3)
    print("Server start timeout. Please open http://localhost:8000 manually.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting ECG Signal Analyzer Server on port {port}...")
    
    # Launch browser polling in background thread (local dev only)
    if port == 8000:
        threading.Thread(target=wait_and_open_browser, daemon=True).start()
    
    # Run uvicorn server directly (reload=False prevents Windows subprocess shutdown issue)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

