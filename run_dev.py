"""
Run the FastAPI application in development mode with minimal logging
"""
import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "127.0.0.1")  # Use 127.0.0.1 for Windows compatibility
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # Auto-reload for development
        log_level="warning",  # Only show warnings and errors
        access_log=True  # Disable access logs for cleaner output
    )
