# Test LST Master Logging Implementation
# Validates Phase 1 compliance with buildspec and LST Master requirements

import pytest
from datetime import datetime, timezone
from src.core.logging import log_engine_event, calculate_client_date, validate_engine_event_format


def test_log_engine_event_meal():
    """Test meal engine event logging."""
    user_id = "123456789012345678"
    source_engine = "meal"
    status = "completed"
    data = {"meal_id": "planC_meal3"}
    
    # Should not raise any exceptions
    log_engine_event(user_id, source_engine, status, data)


def test_log_engine_event_training():
    """Test training engine event logging."""
    user_id = "123456789012345678"
    source_engine = "training"
    status = "completed"
    data = {
        "exercise_id": "ex_dl_001",
        "exercise_name": "Deadlift",
        "weight_kg": 140.0,
        "reps": 6,
        "block_id": "steel_block_b",
        "day_index": 13
    }
    
    # Should not raise any exceptions
    log_engine_event(user_id, source_engine, status, data)


def test_log_engine_event_checkin():
    """Test checkin engine event logging."""
    user_id = "123456789012345678"
    source_engine = "checkin"
    status = "completed"
    data = {
        "weight": 93.8,
        "mood": "😐",
        "soreness": "🟡",
        "stress": "⚡",
        "sleep": "🔥",
        "notes": "Feeling okay but a bit tight in the back."
    }
    
    # Should not raise any exceptions
    log_engine_event(user_id, source_engine, status, data)


def test_log_engine_event_cardio():
    """Test cardio engine event logging."""
    user_id = "123456789012345678"
    source_engine = "cardio"
    status = "underperformed"
    data = {
        "assigned_minutes": 30,
        "actual_minutes": 24
    }
    
    # Should not raise any exceptions
    log_engine_event(user_id, source_engine, status, data)


def test_calculate_client_date():
    """Test client date calculation from UTC timestamp and timezone offset."""
    utc_time = datetime(2025, 1, 27, 22, 0, 0, tzinfo=timezone.utc)
    
    # UTC+2 should advance to next day
    date_utc_plus2 = calculate_client_date(utc_time, "UTC+2")
    assert date_utc_plus2 == "2025-01-28"
    
    # UTC-5 should stay same day
    date_utc_minus5 = calculate_client_date(utc_time, "UTC-5")
    assert date_utc_minus5 == "2025-01-27"
    
    # No offset should use UTC
    date_utc = calculate_client_date(utc_time)
    assert date_utc == "2025-01-27"


def test_validate_engine_event_format():
    """Test LST Master format validation."""
    valid_log = {
        "user_id": "123456789012345678",
        "date": "2025-01-27",
        "timestamp": "2025-01-27T22:00:00Z",
        "source_engine": "meal",
        "status": "completed",
        "data": {"meal_id": "planC_meal3"}
    }
    
    # Should not raise any exceptions
    validate_engine_event_format(valid_log)


def test_invalid_source_engine():
    """Test validation rejects invalid source engines."""
    invalid_log = {
        "user_id": "123456789012345678",
        "date": "2025-01-27",
        "timestamp": "2025-01-27T22:00:00Z",
        "source_engine": "invalid_engine",
        "status": "completed",
        "data": {"meal_id": "planC_meal3"}
    }
    
    with pytest.raises(ValueError, match="Invalid source_engine"):
        validate_engine_event_format(invalid_log)


def test_invalid_status():
    """Test validation rejects invalid statuses."""
    invalid_log = {
        "user_id": "123456789012345678",
        "date": "2025-01-27",
        "timestamp": "2025-01-27T22:00:00Z",
        "source_engine": "meal",
        "status": "invalid_status",
        "data": {"meal_id": "planC_meal3"}
    }
    
    with pytest.raises(ValueError, match="Invalid status"):
        validate_engine_event_format(invalid_log)


def test_missing_required_fields():
    """Test validation rejects logs missing required fields."""
    incomplete_log = {
        "user_id": "123456789012345678",
        "timestamp": "2025-01-27T22:00:00Z",
        "source_engine": "meal",
        "status": "completed"
        # Missing date and data fields
    }
    
    with pytest.raises(ValueError, match="Missing required LST Master fields"):
        validate_engine_event_format(incomplete_log)


def test_invalid_user_id_format():
    """Test validation rejects invalid user ID formats."""
    invalid_log = {
        "user_id": "invalid_id",
        "date": "2025-01-27",
        "timestamp": "2025-01-27T22:00:00Z",
        "source_engine": "meal",
        "status": "completed",
        "data": {"meal_id": "planC_meal3"}
    }
    
    with pytest.raises(ValueError, match="user_id must be Discord snowflake format"):
        validate_engine_event_format(invalid_log) 