# TheRegiment - Pydantic Schema Models
# Exact implementation of docs/schema_definitions.md

from datetime import date, datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


# Enums for schema validation
class GoalEnum(str, Enum):
    cut = "cut"
    bulk = "bulk"
    recomp = "recomp"


class StatusEnum(str, Enum):
    completed = "completed"
    missed = "missed"


class TrainingStatusEnum(str, Enum):
    completed = "completed"
    missed = "missed"


class CardioStatusEnum(str, Enum):
    completed = "completed"
    underperformed = "underperformed"
    missed = "missed"


class MoodEnum(str, Enum):
    great = "great"
    okay = "okay"
    bad = "bad"


class SorenessEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SleepEnum(str, Enum):
    four_hours = "4h"
    six_hours = "6h"
    eight_hours = "8h"


class StressEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class FlagEnum(str, Enum):
    soft_compliance = "soft_compliance"
    training_inconsistency = "training_inconsistency"
    weight_stall = "weight_stall"
    non_responding_client = "non_responding_client"
    grit_violation = "grit_violation"
    flag_parse_error = "flag_parse_error"


class ActionSuggestedEnum(str, Enum):
    callout = "callout"
    reassign = "reassign"
    pause = "pause"
    escalate = "escalate"
    none = "none"


# Schema Models
class MacrosSchema(BaseModel):
    """Macronutrient breakdown schema."""
    protein: int
    carbs: int
    fats: int


class ClientProfileSchema(BaseModel):
    """Client profile schema matching docs/schema_definitions.md exactly."""
    user_id: str
    goal: GoalEnum
    timezone_offset: str = Field(..., regex=r"^UTC[±]\d{1,2}$")
    start_date: date
    paused: bool
    height_cm: int = Field(..., gt=0, le=300)
    weight_kg: float = Field(..., gt=0, le=500)
    training_template_id: str
    meal_template_id: str
    macros: MacrosSchema
    cardio_minutes: int = Field(..., ge=0, le=300)
    cycle_start_date: date
    block_id: str

    @validator('timezone_offset')
    def validate_timezone_offset(cls, v):
        """Validate timezone offset format."""
        if not v.startswith('UTC'):
            raise ValueError('Timezone offset must start with UTC')
        return v


class MealLogSchema(BaseModel):
    """Meal log schema matching docs/schema_definitions.md exactly."""
    user_id: str
    meal_id: str
    date: date
    logged_at: datetime
    timezone_offset: str = Field(..., regex=r"^UTC[±]\d{1,2}$")
    status: StatusEnum

    @validator('logged_at')
    def validate_logged_at(cls, v):
        """Ensure timestamp is timezone-aware."""
        if v.tzinfo is None:
            raise ValueError('logged_at must include timezone information')
        return v


class TrainingLogSchema(BaseModel):
    """Training log schema matching docs/schema_definitions.md exactly."""
    user_id: str
    block_id: str
    day_index: int = Field(..., ge=0)
    exercise: str
    weight_kg: float = Field(..., gt=0, le=1000)
    reps: int = Field(..., gt=0, le=100)
    timestamp: datetime
    timezone: str = Field(..., regex=r"^UTC[±]\d{1,2}$")
    status: TrainingStatusEnum

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is timezone-aware."""
        if v.tzinfo is None:
            raise ValueError('timestamp must include timezone information')
        return v


class CardioLogSchema(BaseModel):
    """Cardio log schema matching docs/schema_definitions.md exactly."""
    user_id: str
    date: date
    timestamp: datetime
    assigned_minutes: int = Field(..., ge=0, le=300)
    actual_minutes: int = Field(..., ge=0, le=300)
    status: CardioStatusEnum

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is timezone-aware."""
        if v.tzinfo is None:
            raise ValueError('timestamp must include timezone information')
        return v


class CheckinLogSchema(BaseModel):
    """Check-in log schema matching docs/schema_definitions.md exactly."""
    user_id: str
    date: date
    timestamp: datetime
    weight_kg: float = Field(..., gt=0, le=500)
    mood: MoodEnum
    soreness: SorenessEnum
    sleep: SleepEnum
    stress: StressEnum
    notes: Optional[str] = Field(None, max_length=250)
    status: StatusEnum

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is timezone-aware."""
        if v.tzinfo is None:
            raise ValueError('timestamp must include timezone information')
        return v


class JobCardSchema(BaseModel):
    """Job card schema matching docs/schema_definitions.md exactly."""
    user_id: str
    date: date
    timestamp: datetime
    summary: str = Field(..., max_length=500)
    flags: List[FlagEnum]
    action_suggested: ActionSuggestedEnum
    resolved: bool

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is timezone-aware."""
        if v.tzinfo is None:
            raise ValueError('timestamp must include timezone information')
        return v


class ExerciseSchema(BaseModel):
    """Exercise schema for training templates."""
    exercise: str
    sets: int = Field(..., gt=0, le=20)
    reps: int = Field(..., gt=0, le=100)
    rest_seconds: int = Field(..., ge=0, le=600)
    video_url: str


class TrainingDaySchema(BaseModel):
    """Training day schema for templates."""
    day_index: int = Field(..., ge=0, le=6)
    day_name: str
    exercises: List[ExerciseSchema]


class TrainingTemplateSchema(BaseModel):
    """Training template schema matching docs/schema_definitions.md exactly."""
    template_id: str
    block_name: str
    days_per_week: int = Field(..., gt=0, le=7)
    schedule: List[TrainingDaySchema]


class MealItemSchema(BaseModel):
    """Meal item schema for meal templates."""
    food: str
    raw_grams: int = Field(..., gt=0, le=2000)


class MealSchema(BaseModel):
    """Meal schema for meal templates."""
    meal_id: str
    items: List[MealItemSchema]


class MealDaySchema(BaseModel):
    """Meal day schema for templates."""
    day_index: int = Field(..., ge=0, le=6)
    meals: List[MealSchema]


class IngredientSchema(BaseModel):
    """Ingredient schema for shopping lists."""
    food: str
    grams: int = Field(..., gt=0, le=10000)


class ShoppingListSchema(BaseModel):
    """Shopping list schema for meal templates."""
    ingredients: List[IngredientSchema]
    instructions: str


class MealTemplateSchema(BaseModel):
    """Meal template schema matching docs/schema_definitions.md exactly."""
    template_id: str
    goal: GoalEnum
    days: List[MealDaySchema]
    shopping_list: ShoppingListSchema 