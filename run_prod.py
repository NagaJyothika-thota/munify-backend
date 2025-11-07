"""
Run the FastAPI application in production mode with full logging
"""
import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "127.0.0.1")  # Use 127.0.0.1 for Windows compatibility
    port = int(os.getenv("PORT", "8000"))
    
    # Check if running on Windows
    is_windows = os.name == 'nt'
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # No auto-reload in production
        log_level="info",
        workers=1 if is_windows else 4  # Single worker on Windows, multiple on Unix
    )
