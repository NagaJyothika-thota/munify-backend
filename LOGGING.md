# Logging System

This project implements a comprehensive, standards-compliant logging system following Python and FastAPI best practices.

## Features

- **Structured Logging**: JSON-formatted logs with consistent fields
- **Log Rotation**: Automatic log file rotation (10MB max, 5 backups)
- **Environment-based Configuration**: Different log levels for dev/prod
- **Request Tracing**: Unique request IDs for tracking requests across services
- **Business Event Logging**: Structured logging for business operations
- **Error Tracking**: Comprehensive error logging with stack traces

## Log Files

- `logs/app.log`: All application logs
- `logs/error.log`: Error-level logs only

## Usage

### Basic Logging

```python
from app.core.logging import get_logger

logger = get_logger("your.module.name")
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
```

### Structured Logging

```python
from app.utils.logger import log_business_event, log_error, log_database_operation

# Business events
log_business_event(
    "user_created",
    user_id=123,
    entity_type="user",
    additional_data="value"
)

# Database operations
log_database_operation(
    "create",
    "users",
    record_id=123,
    user_id=456
)

# Errors
log_error(
    "validation_failed",
    "Invalid email format",
    user_id=123,
    field="email"
)
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Something unexpected happened but the program is still working
- **ERROR**: A serious problem occurred
- **CRITICAL**: A very serious error occurred

## Configuration

Logging is configured in `app/core/logging.py` and can be customized by:

1. **Environment Variables**: Set `DEBUG=false` for production
2. **Log Levels**: Modify the `log_level` variable
3. **Handlers**: Add/remove console/file handlers
4. **Formatters**: Customize log message format

## Request Logging

All HTTP requests are automatically logged with:
- Request ID for tracing
- Method, URL, status code
- Processing time
- Client IP and user agent

## Best Practices

1. **Use structured logging** for business events
2. **Include context** (user_id, request_id, etc.)
3. **Log at appropriate levels** (don't log everything as ERROR)
4. **Use unique request IDs** for tracing
5. **Log errors with stack traces** using `exc_info=True`

## Example Log Output

```
2024-01-15 10:30:15 [INFO] app.main: Request started
2024-01-15 10:30:15 [INFO] app.services.project: Business Event: project_creation_started
2024-01-15 10:30:15 [DEBUG] app.services.project: Database Operation: create
2024-01-15 10:30:15 [INFO] app.services.project: Business Event: project_created
2024-01-15 10:30:15 [INFO] app.main: Request completed
```
