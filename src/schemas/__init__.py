"""
Schema Foundation - Phase 0
Pydantic models sourced from docs/schema_definitions.md
"""

from .models import (
    ClientProfileSchema,
    MealLogSchema,
    TrainingLogSchema,
    CardioLogSchema,
    CheckinLogSchema,
    JobCardSchema,
    TrainingTemplateSchema,
    MealTemplateSchema,
    MacrosSchema,
    GoalEnum,
    StatusEnum,
    TrainingStatusEnum,
    CardioStatusEnum,
    MoodEnum,
    SorenessEnum,
    SleepEnum,
    StressEnum,
    FlagEnum,
    ActionSuggestedEnum
)

__all__ = [
    "ClientProfileSchema",
    "MealLogSchema", 
    "TrainingLogSchema",
    "CardioLogSchema",
    "CheckinLogSchema",
    "JobCardSchema",
    "TrainingTemplateSchema",
    "MealTemplateSchema",
    "MacrosSchema",
    "GoalEnum",
    "StatusEnum",
    "TrainingStatusEnum",
    "CardioStatusEnum",
    "MoodEnum",
    "SorenessEnum",
    "SleepEnum",
    "StressEnum",
    "FlagEnum",
    "ActionSuggestedEnum"
] 