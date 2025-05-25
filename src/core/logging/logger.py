# TheRegiment - Structured JSON Logger
# ISO 8601 UTC timestamp enforcement with schema validation

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .validation import validate_log_format, enforce_timestamp_format, sanitize_user_data


class StructuredJSONFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs with ISO 8601 UTC timestamps."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        timestamp = enforce_timestamp_format(datetime.now(timezone.utc))
        
        log_entry = {
            "timestamp": timestamp,
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', str(uuid.uuid4())),
        }
        
        # Add optional fields if present
        if hasattr(record, 'context'):
            log_entry["context"] = sanitize_user_data(record.context)
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
            
        if hasattr(record, 'engine_name'):
            log_entry["engine_name"] = record.engine_name
            
        if hasattr(record, 'event_type'):
            log_entry["event_type"] = record.event_type
            
        if hasattr(record, 'status'):
            log_entry["status"] = record.status
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Validate log format before output
        validate_log_format(log_entry)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(module_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured JSON logger for a module.
    
    Args:
        module_name: Name of the module/engine requesting logger
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If log_level is invalid
        PermissionError: If log directory cannot be created
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log_level: {log_level}. Must be one of {valid_levels}")
    
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
    except PermissionError as e:
        raise PermissionError(f"Cannot create log directory: {e}")
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    file_handler = logging.FileHandler(log_dir / f"{module_name}.log")
    file_handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_event(
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    module_name: str = "system",
    trace_id: Optional[str] = None
) -> None:
    """
    Log a structured event with context.
    
    Args:
        level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        message: Human readable description
        context: Structured data object (will be sanitized)
        user_id: Client identifier (if applicable)
        module_name: Module/engine name
        trace_id: Request/operation tracking ID
        
    Raises:
        ValueError: If level is invalid
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
    
    logger = logging.getLogger(module_name)
    log_level = getattr(logging, level.upper())
    
    # Create log record with extra fields
    extra = {
        "trace_id": trace_id or str(uuid.uuid4())
    }
    
    if context is not None:
        extra["context"] = context
        
    if user_id is not None:
        extra["user_id"] = user_id
    
    logger.log(log_level, message, extra=extra)


def log_missed_event(user_id: str, event_type: str, timestamp: datetime) -> None:
    """
    Log a missed event with status: missed.
    
    Args:
        user_id: Client identifier
        event_type: Type of missed event (meal, training, checkin, cardio)
        timestamp: When the event was supposed to occur
        
    Raises:
        ValueError: If timestamp format is invalid
    """
    # Validate and format timestamp
    formatted_timestamp = enforce_timestamp_format(timestamp)
    
    context = {
        "missed_at": formatted_timestamp,
        "event_type": event_type
    }
    
    logger = logging.getLogger("missed_events")
    extra = {
        "user_id": user_id,
        "event_type": event_type,
        "status": "missed",
        "context": context,
        "trace_id": str(uuid.uuid4())
    }
    
    logger.warning(f"Missed {event_type} event for user {user_id}", extra=extra)


def log_engine_failure(engine_name: str, error: Exception, context: Dict[str, Any]) -> None:
    """
    Log engine failure with error context.
    
    Args:
        engine_name: Name of the failing engine
        error: Exception that occurred
        context: Additional context about the failure
        
    Raises:
        None - This function must never fail
    """
    try:
        logger = logging.getLogger("engine_failures")
        
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **sanitize_user_data(context)
        }
        
        extra = {
            "engine_name": engine_name,
            "context": error_context,
            "status": "failed",
            "trace_id": str(uuid.uuid4())
        }
        
        logger.error(f"Engine failure in {engine_name}: {error}", extra=extra, exc_info=True)
        
    except Exception as log_error:
        # Fallback logging to prevent silent failures
        fallback_message = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "CRITICAL",
            "module": "logger_fallback",
            "message": f"Logger failure while logging engine error: {log_error}",
            "original_engine": engine_name,
            "original_error": str(error)
        }
        print(json.dumps(fallback_message), file=sys.stderr)


def log_engine_event(
    user_id: str,
    source_engine: str,
    status: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None,
    timezone_offset: Optional[str] = None
) -> None:
    """
    Log engine event in LST Master unified format.
    
    Args:
        user_id: Client identifier (Discord ID)
        source_engine: Engine identifier (meal, training, checkin, cardio)
        status: Event status (completed, missed, underperformed, failed)
        data: Engine-specific payload
        timestamp: Event timestamp (defaults to current UTC)
        timezone_offset: Client timezone offset for date calculation (e.g. "UTC+2")
        
    Raises:
        ValueError: If parameters are invalid
    """
    from .lst_validation import validate_engine_event_format, calculate_client_date
    
    # Use current time if not provided
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    # Ensure timestamp is UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)
    
    # Format timestamp as ISO 8601 UTC
    formatted_timestamp = timestamp.isoformat().replace('+00:00', 'Z')
    
    # Calculate client-local date
    client_date = calculate_client_date(timestamp, timezone_offset)
    
    # Create LST Master format log entry
    log_entry = {
        "user_id": user_id,
        "date": client_date,
        "timestamp": formatted_timestamp,
        "source_engine": source_engine,
        "status": status,
        "data": data
    }
    
    # Validate LST Master format
    validate_engine_event_format(log_entry)
    
    # Get logger for the specific engine
    logger = logging.getLogger(f"engine_{source_engine}")
    
    # Create log record with LST format as context
    extra = {
        "lst_format": log_entry,
        "user_id": user_id,
        "source_engine": source_engine,
        "status": status,
        "trace_id": str(uuid.uuid4())
    }
    
    # Log with appropriate level based on status
    if status == "failed":
        log_level = logging.ERROR
    elif status in ["missed", "underperformed"]:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    
    message = f"Engine event: {source_engine} - {status}"
    logger.log(log_level, message, extra=extra)


class LSTMasterFormatter(logging.Formatter):
    """Formatter for LST Master unified log format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record in LST Master format if available."""
        if hasattr(record, 'lst_format'):
            # Use LST Master format directly with Unicode support
            return json.dumps(record.lst_format, ensure_ascii=False)
        else:
            # Fallback to standard JSON format
            return StructuredJSONFormatter().format(record)


def setup_engine_logger(engine_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logger for engine events using LST Master format.
    
    Args:
        engine_name: Name of the engine (meal, training, checkin, cardio)
        log_level: Logging level
        
    Returns:
        Configured logger for engine events
    """
    logger_name = f"engine_{engine_name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with LST Master formatting and UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LSTMasterFormatter())
    # Set encoding to UTF-8 for Unicode support on Windows
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8')
    logger.addHandler(console_handler)
    
    # File handler with LST Master formatting and UTF-8 encoding
    file_handler = logging.FileHandler(log_dir / f"engine_{engine_name}.log", encoding='utf-8')
    file_handler.setFormatter(LSTMasterFormatter())
    logger.addHandler(file_handler)
    
    logger.propagate = False
    return logger 