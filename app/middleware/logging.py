"""
Request logging middleware
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from app.core.logging import get_logger

logger = get_logger("middleware.logging")


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        
        # Create request object
        request = Request(scope, receive)
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        response_sent = False
        
        async def send_wrapper(message):
            nonlocal response_sent
            if message["type"] == "http.response.start" and not response_sent:
                response_sent = True
                process_time = time.time() - start_time
                
                # Log response
                status_code = message["status"]
                log_level = "warning" if status_code >= 400 or process_time > 1.0 else "info"
                
                getattr(logger, log_level)(
                    f"Request completed",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "status_code": status_code,
                        "process_time": round(process_time, 4),
                        "client_ip": request.client.host if request.client else None,
                    }
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
