# TheRegiment - Log Validation & Sanitization
# Schema enforcement and PII protection for structured logs

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Union


# PII patterns to sanitize
PII_PATTERNS = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
    'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
    'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
}

# Required log entry fields
REQUIRED_FIELDS = {"timestamp", "level", "module", "message", "trace_id"}

# Valid log levels
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# Valid event statuses
VALID_STATUSES = {"completed", "failed", "missed", "pending", "skipped"}


def validate_log_format(log_entry: Dict[str, Any]) -> None:
    """
    Validate log entry against required schema format.
    
    Args:
        log_entry: Log entry dictionary to validate
        
    Raises:
        ValueError: If log entry format is invalid
        TypeError: If log entry is not a dictionary
    """
    if not isinstance(log_entry, dict):
        raise TypeError(f"Log entry must be a dictionary, got {type(log_entry)}")
    
    # Check required fields
    missing_fields = REQUIRED_FIELDS - set(log_entry.keys())
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Validate log level
    if log_entry["level"] not in VALID_LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_entry['level']}. Must be one of {VALID_LOG_LEVELS}")
    
    # Validate timestamp format
    try:
        enforce_timestamp_format(log_entry["timestamp"])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid timestamp format: {e}")
    
    # Validate trace_id is string
    if not isinstance(log_entry["trace_id"], str):
        raise ValueError(f"trace_id must be string, got {type(log_entry['trace_id'])}")
    
    # Validate module name
    if not isinstance(log_entry["module"], str) or not log_entry["module"].strip():
        raise ValueError("module must be non-empty string")
    
    # Validate message
    if not isinstance(log_entry["message"], str):
        raise ValueError(f"message must be string, got {type(log_entry['message'])}")
    
    # Validate optional fields if present
    if "user_id" in log_entry:
        _validate_user_id(log_entry["user_id"])
    
    if "status" in log_entry:
        if log_entry["status"] not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {log_entry['status']}. Must be one of {VALID_STATUSES}")
    
    if "context" in log_entry:
        _validate_context(log_entry["context"])
    
    # Validate JSON serializability
    try:
        json.dumps(log_entry)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Log entry is not JSON serializable: {e}")


def enforce_timestamp_format(timestamp: Union[str, datetime]) -> str:
    """
    Enforce ISO 8601 UTC timestamp format with explicit offset.
    
    Args:
        timestamp: Timestamp as string or datetime object
        
    Returns:
        Formatted ISO 8601 UTC timestamp string
        
    Raises:
        ValueError: If timestamp format is invalid
        TypeError: If timestamp is not string or datetime
    """
    if isinstance(timestamp, str):
        # Validate existing string format
        try:
            parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Ensure UTC timezone
            if parsed.tzinfo is None:
                raise ValueError("Timestamp must include timezone information")
            # Convert to UTC and format with explicit offset
            utc_time = parsed.astimezone(timezone.utc)
            return utc_time.isoformat().replace('+00:00', '+00:00')
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {timestamp}. Must be ISO 8601 UTC with offset. Error: {e}")
    
    elif isinstance(timestamp, datetime):
        # Convert datetime to UTC string
        if timestamp.tzinfo is None:
            # Assume naive datetime is UTC
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        else:
            # Convert to UTC
            timestamp = timestamp.astimezone(timezone.utc)
        
        return timestamp.isoformat().replace('+00:00', '+00:00')
    
    else:
        raise TypeError(f"Timestamp must be string or datetime, got {type(timestamp)}")


def sanitize_user_data(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize context data to remove PII and ensure safe logging.
    
    Args:
        context: Context dictionary to sanitize
        
    Returns:
        Sanitized context dictionary
        
    Raises:
        TypeError: If context is not a dictionary
    """
    if not isinstance(context, dict):
        raise TypeError(f"Context must be a dictionary, got {type(context)}")
    
    sanitized = {}
    
    for key, value in context.items():
        # Sanitize key names (no PII in keys)
        clean_key = _sanitize_string(str(key))
        
        # Sanitize values based on type
        if isinstance(value, str):
            sanitized[clean_key] = _sanitize_string(value)
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[clean_key] = sanitize_user_data(value)
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[clean_key] = [
                _sanitize_string(str(item)) if isinstance(item, str) else item
                for item in value
            ]
        elif isinstance(value, (int, float, bool, type(None))):
            # Safe primitive types
            sanitized[clean_key] = value
        else:
            # Convert other types to string and sanitize
            sanitized[clean_key] = _sanitize_string(str(value))
    
    # Validate final context is JSON serializable
    try:
        json.dumps(sanitized)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Sanitized context is not JSON serializable: {e}")
    
    return sanitized


def _sanitize_string(text: str) -> str:
    """
    Remove PII patterns from string.
    
    Args:
        text: String to sanitize
        
    Returns:
        Sanitized string with PII replaced
    """
    sanitized = text
    
    # Replace PII patterns with placeholders
    for pii_type, pattern in PII_PATTERNS.items():
        sanitized = pattern.sub(f'[{pii_type.upper()}_REDACTED]', sanitized)
    
    return sanitized


def _validate_user_id(user_id: Any) -> None:
    """
    Validate user_id format matches client_profiles schema.
    
    Args:
        user_id: User ID to validate
        
    Raises:
        ValueError: If user_id format is invalid
    """
    if not isinstance(user_id, str):
        raise ValueError(f"user_id must be string, got {type(user_id)}")
    
    if not user_id.strip():
        raise ValueError("user_id cannot be empty")
    
    # Discord user ID format validation (snowflake - 17-19 digits)
    if not re.match(r'^\d{17,19}$', user_id):
        raise ValueError(f"user_id must be Discord snowflake format (17-19 digits), got: {user_id}")


def _validate_context(context: Any) -> None:
    """
    Validate context field structure.
    
    Args:
        context: Context to validate
        
    Raises:
        ValueError: If context format is invalid
    """
    if not isinstance(context, dict):
        raise ValueError(f"context must be dictionary, got {type(context)}")
    
    # Check for nested depth limit (prevent deeply nested objects)
    max_depth = 5
    if _get_dict_depth(context) > max_depth:
        raise ValueError(f"context nesting too deep (max {max_depth} levels)")
    
    # Validate all values are JSON serializable
    try:
        json.dumps(context)
    except (TypeError, ValueError) as e:
        raise ValueError(f"context contains non-serializable data: {e}")


def _get_dict_depth(d: Dict[str, Any], depth: int = 0) -> int:
    """
    Calculate maximum nesting depth of dictionary.
    
    Args:
        d: Dictionary to analyze
        depth: Current depth level
        
    Returns:
        Maximum depth found
    """
    if not isinstance(d, dict) or not d:
        return depth
    
    return max(_get_dict_depth(v, depth + 1) if isinstance(v, dict) else depth + 1 
               for v in d.values()) 