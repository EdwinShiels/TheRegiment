# TheRegiment - LST Master Log Format Validation
# Validates engine events against LST Master unified log structure

import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

# Valid source engines as per LST Master
VALID_SOURCE_ENGINES = {"meal", "training", "checkin", "cardio"}

# Valid event statuses as per LST Master
VALID_STATUSES = {"completed", "missed", "underperformed", "failed"}

# Required fields for LST Master format
LST_REQUIRED_FIELDS = {"user_id", "date", "timestamp", "source_engine", "status", "data"}


def validate_engine_event_format(log_entry: Dict[str, Any]) -> None:
    """
    Validate log entry against LST Master unified format.
    
    Args:
        log_entry: Log entry dictionary to validate
        
    Raises:
        ValueError: If log entry format is invalid
        TypeError: If log entry is not a dictionary
    """
    if not isinstance(log_entry, dict):
        raise TypeError(f"Log entry must be a dictionary, got {type(log_entry)}")
    
    # Check required fields
    missing_fields = LST_REQUIRED_FIELDS - set(log_entry.keys())
    if missing_fields:
        raise ValueError(f"Missing required LST Master fields: {missing_fields}")
    
    # Validate user_id (Discord snowflake format)
    if not isinstance(log_entry["user_id"], str):
        raise ValueError(f"user_id must be string, got {type(log_entry['user_id'])}")
    
    if not re.match(r'^\d{17,19}$', log_entry["user_id"]):
        raise ValueError(f"user_id must be Discord snowflake format (17-19 digits), got: {log_entry['user_id']}")
    
    # Validate date format (YYYY-MM-DD)
    if not isinstance(log_entry["date"], str):
        raise ValueError(f"date must be string, got {type(log_entry['date'])}")
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', log_entry["date"]):
        raise ValueError(f"date must be YYYY-MM-DD format, got: {log_entry['date']}")
    
    # Validate timestamp format (ISO 8601 UTC)
    if not isinstance(log_entry["timestamp"], str):
        raise ValueError(f"timestamp must be string, got {type(log_entry['timestamp'])}")
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$', log_entry["timestamp"]):
        raise ValueError(f"timestamp must be ISO 8601 UTC format ending with Z, got: {log_entry['timestamp']}")
    
    # Validate source_engine
    if log_entry["source_engine"] not in VALID_SOURCE_ENGINES:
        raise ValueError(f"Invalid source_engine: {log_entry['source_engine']}. Must be one of {VALID_SOURCE_ENGINES}")
    
    # Validate status
    if log_entry["status"] not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {log_entry['status']}. Must be one of {VALID_STATUSES}")
    
    # Validate data field
    if not isinstance(log_entry["data"], dict):
        raise ValueError(f"data must be dictionary, got {type(log_entry['data'])}")
    
    # Validate engine-specific data structure
    _validate_engine_data(log_entry["source_engine"], log_entry["data"])


def calculate_client_date(utc_timestamp: datetime, timezone_offset: str = None) -> str:
    """
    Calculate client-local date from UTC timestamp and timezone offset.
    
    Args:
        utc_timestamp: UTC timestamp
        timezone_offset: Client timezone offset (e.g. "UTC+2", "UTC-5")
        
    Returns:
        Client-local date in YYYY-MM-DD format
        
    Raises:
        ValueError: If timezone_offset format is invalid
    """
    if timezone_offset is None:
        # Default to UTC if no offset provided
        client_time = utc_timestamp
    else:
        # Parse timezone offset
        if not isinstance(timezone_offset, str):
            raise ValueError(f"timezone_offset must be string, got {type(timezone_offset)}")
        
        # Match UTC±X format
        match = re.match(r'^UTC([+-])(\d{1,2})$', timezone_offset)
        if not match:
            raise ValueError(f"timezone_offset must be UTC±X format, got: {timezone_offset}")
        
        sign, hours = match.groups()
        offset_hours = int(hours)
        
        if offset_hours > 14:
            raise ValueError(f"timezone_offset hours must be ≤14, got: {offset_hours}")
        
        # Calculate offset
        if sign == '+':
            offset = timedelta(hours=offset_hours)
        else:
            offset = timedelta(hours=-offset_hours)
        
        # Apply offset to get client local time
        client_time = utc_timestamp + offset
    
    # Return date in YYYY-MM-DD format
    return client_time.strftime('%Y-%m-%d')


def _validate_engine_data(source_engine: str, data: Dict[str, Any]) -> None:
    """
    Validate engine-specific data structure as per LST Master examples.
    
    Args:
        source_engine: Engine identifier
        data: Data payload to validate
        
    Raises:
        ValueError: If data structure is invalid for the engine
    """
    if source_engine == "meal":
        # Meal data: {meal_id: string}
        if "meal_id" not in data:
            raise ValueError("Meal data must contain 'meal_id' field")
        if not isinstance(data["meal_id"], str):
            raise ValueError(f"meal_id must be string, got {type(data['meal_id'])}")
    
    elif source_engine == "training":
        # Training data: {exercise_id, exercise_name, weight_kg, reps, block_id, day_index}
        required_fields = {"exercise_id", "exercise_name", "weight_kg", "reps", "block_id", "day_index"}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Training data missing required fields: {missing}")
        
        # Type validation
        if not isinstance(data["exercise_id"], str):
            raise ValueError(f"exercise_id must be string, got {type(data['exercise_id'])}")
        if not isinstance(data["exercise_name"], str):
            raise ValueError(f"exercise_name must be string, got {type(data['exercise_name'])}")
        if not isinstance(data["weight_kg"], (int, float)):
            raise ValueError(f"weight_kg must be number, got {type(data['weight_kg'])}")
        if not isinstance(data["reps"], int):
            raise ValueError(f"reps must be integer, got {type(data['reps'])}")
        if not isinstance(data["block_id"], str):
            raise ValueError(f"block_id must be string, got {type(data['block_id'])}")
        if not isinstance(data["day_index"], int):
            raise ValueError(f"day_index must be integer, got {type(data['day_index'])}")
    
    elif source_engine == "checkin":
        # Checkin data: {weight, mood, soreness, stress, sleep, notes?}
        required_fields = {"weight", "mood", "soreness", "stress", "sleep"}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Checkin data missing required fields: {missing}")
        
        # Type validation
        if not isinstance(data["weight"], (int, float)):
            raise ValueError(f"weight must be number, got {type(data['weight'])}")
        if not isinstance(data["mood"], str):
            raise ValueError(f"mood must be string, got {type(data['mood'])}")
        if not isinstance(data["soreness"], str):
            raise ValueError(f"soreness must be string, got {type(data['soreness'])}")
        if not isinstance(data["stress"], str):
            raise ValueError(f"stress must be string, got {type(data['stress'])}")
        if not isinstance(data["sleep"], str):
            raise ValueError(f"sleep must be string, got {type(data['sleep'])}")
        
        # Notes is optional
        if "notes" in data and not isinstance(data["notes"], str):
            raise ValueError(f"notes must be string, got {type(data['notes'])}")
    
    elif source_engine == "cardio":
        # Cardio data: {assigned_minutes, actual_minutes}
        required_fields = {"assigned_minutes", "actual_minutes"}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Cardio data missing required fields: {missing}")
        
        # Type validation
        if not isinstance(data["assigned_minutes"], int):
            raise ValueError(f"assigned_minutes must be integer, got {type(data['assigned_minutes'])}")
        if not isinstance(data["actual_minutes"], int):
            raise ValueError(f"actual_minutes must be integer, got {type(data['actual_minutes'])}") 