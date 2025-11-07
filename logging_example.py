"""
Example of how to use the new logging system
"""
from app.core.logging import setup_logging, get_logger
from app.utils.logger import log_business_event, log_error, log_database_operation

# Setup logging
setup_logging()

# Get a logger
logger = get_logger("example")

def example_usage():
    """Example of how to use different logging methods"""
    
    # Basic logging
    logger.info("This is a basic info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Structured logging for business events
    log_business_event(
        "user_login",
        user_id=123,
        entity_type="user",
        login_method="email"
    )
    
    # Structured logging for database operations
    log_database_operation(
        "update",
        "users",
        record_id=123,
        user_id=456,
        fields_updated=["email", "last_login"]
    )
    
    # Structured logging for errors
    try:
        # Some operation that might fail
        raise ValueError("Something went wrong")
    except Exception as e:
        log_error(
            "operation_failed",
            str(e),
            user_id=123,
            operation="example_operation"
        )

if __name__ == "__main__":
    example_usage()
