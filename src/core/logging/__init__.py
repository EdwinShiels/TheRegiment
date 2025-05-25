# TheRegiment - Logging Infrastructure
# Structured JSON logging with LST Master format support

from .logger import (
    setup_logger,
    log_event,
    log_missed_event,
    log_engine_failure,
    log_engine_event,
    setup_engine_logger,
    StructuredJSONFormatter,
    LSTMasterFormatter
)

from .validation import (
    validate_log_format,
    enforce_timestamp_format,
    sanitize_user_data
)

from .lst_validation import (
    validate_engine_event_format,
    calculate_client_date,
    VALID_SOURCE_ENGINES,
    VALID_STATUSES
)

__all__ = [
    # System logging (buildspec format)
    "setup_logger",
    "log_event", 
    "log_missed_event",
    "log_engine_failure",
    "StructuredJSONFormatter",
    
    # LST Master format logging
    "log_engine_event",
    "setup_engine_logger", 
    "LSTMasterFormatter",
    
    # Validation functions
    "validate_log_format",
    "enforce_timestamp_format",
    "sanitize_user_data",
    "validate_engine_event_format",
    "calculate_client_date",
    
    # Constants
    "VALID_SOURCE_ENGINES",
    "VALID_STATUSES"
] 