"""
Windows-compatible production runner for FastAPI
"""
import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Windows-compatible settings
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Use localhost instead of 0.0.0.0
        port=8000,
        reload=False,
        log_level="info",
        workers=1,  # Single worker for Windows compatibility
        access_log=True
    )
