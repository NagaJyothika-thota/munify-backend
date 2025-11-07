"""
Utility functions for structured logging
"""
from typing import Any, Dict, Optional
from app.core.logging import get_logger

logger = get_logger("utils.logger")


def log_request(
    method: str,
    url: str,
    request_id: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    **kwargs
) -> None:
    """Log HTTP request with structured data"""
    logger.info(
        "HTTP Request",
        extra={
            "event_type": "http_request",
            "request_id": request_id,
            "method": method,
            "url": url,
            "client_ip": client_ip,
            "user_agent": user_agent,
            **kwargs
        }
    )


def log_response(
    method: str,
    url: str,
    status_code: int,
    process_time: float,
    request_id: str,
    **kwargs
) -> None:
    """Log HTTP response with structured data"""
    log_level = "warning" if status_code >= 400 or process_time > 1.0 else "info"
    
    getattr(logger, log_level)(
        "HTTP Response",
        extra={
            "event_type": "http_response",
            "request_id": request_id,
            "method": method,
            "url": url,
            "status_code": status_code,
            "process_time": round(process_time, 4),
            **kwargs
        }
    )


def log_business_event(
    event_type: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    **kwargs
) -> None:
    """Log business events with structured data"""
    logger.info(
        f"Business Event: {event_type}",
        extra={
            "event_type": "business_event",
            "business_event": event_type,
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            **kwargs
        }
    )


def log_error(
    error_type: str,
    error_message: str,
    user_id: Optional[int] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log errors with structured data"""
    logger.error(
        f"Error: {error_type}",
        extra={
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "user_id": user_id,
            "request_id": request_id,
            **kwargs
        },
        exc_info=True
    )


def log_database_operation(
    operation: str,
    table: str,
    record_id: Optional[int] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> None:
    """Log database operations with structured data"""
    logger.debug(
        f"Database Operation: {operation}",
        extra={
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "record_id": record_id,
            "user_id": user_id,
            **kwargs
        }
    )
