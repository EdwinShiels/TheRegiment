🧠 schema_definitions.md
Global Data Contract — Pydantic / JSON Schemas for MonsterCoach

📜 Purpose
This file defines the official schema for every input, output, and log structure across the entire system.
All engines must validate against these before write or execution.
Cursor uses these as ground truth.

🔐 Conventions
All datetime fields = ISO 8601 UTC unless noted

All enums = lowercase snake_case

All booleans = explicit true / false

All logs must include user_id, timestamp, and status

1. ClientProfileSchema
json
Copy
Edit
{
  "user_id": "string",
  "goal": "cut | bulk | recomp",
  "timezone_offset": "UTC±X",
  "start_date": "YYYY-MM-DD",
  "paused": "boolean",
  "height_cm": "integer",
  "weight_kg": "float",
  "training_template_id": "string",
  "meal_template_id": "string",
  "macros": {
    "protein": "integer",
    "carbs": "integer",
    "fats": "integer"
  },
  "cardio_minutes": "integer",
  "cycle_start_date": "YYYY-MM-DD",
  "block_id": "string"
}
2. MealLogSchema
json
Copy
Edit
{
  "user_id": "string",
  "meal_id": "string",
  "date": "YYYY-MM-DD",
  "logged_at": "ISO timestamp",
  "timezone_offset": "UTC±X",
  "status": "completed | missed"
}
3. TrainingLogSchema
json
Copy
Edit
{
  "user_id": "string",
  "block_id": "string",
  "day_index": "integer",
  "exercise": "string",
  "weight_kg": "float",
  "reps": "integer",
  "timestamp": "ISO timestamp",
  "timezone": "UTC±X",
  "status": "completed | missed"
}
4. CardioLogSchema
json
Copy
Edit
{
  "user_id": "string",
  "date": "YYYY-MM-DD",
  "timestamp": "ISO timestamp",
  "assigned_minutes": "integer",
  "actual_minutes": "integer",
  "status": "completed | underperformed | missed"
}
5. CheckinLogSchema
json
Copy
Edit
{
  "user_id": "string",
  "date": "YYYY-MM-DD",
  "timestamp": "ISO timestamp",
  "weight_kg": "float",
  "mood": "great | okay | bad",
  "soreness": "low | medium | high",
  "sleep": "4h | 6h | 8h",
  "stress": "low | medium | high",
  "notes": "string (optional)",
  "status": "completed | missed"
}
6. JobCardSchema
json
Copy
Edit
{
  "user_id": "string",
  "date": "YYYY-MM-DD",
  "timestamp": "ISO timestamp",
  "summary": "string (max 500 chars)",
  "flags": ["soft_compliance", "training_inconsistency", "weight_stall", "non_responding_client", "grit_violation", "flag_parse_error"],
  "action_suggested": "callout | reassign | pause | escalate | none",
  "resolved": "boolean"
}
7. TrainingTemplateSchema (for template builder UI)
json
Copy
Edit
{
  "template_id": "string",
  "block_name": "string",
  "days_per_week": "integer",
  "schedule": [
    {
      "day_index": "integer",
      "day_name": "string",
      "exercises": [
        {
          "exercise": "string",
          "sets": "integer",
          "reps": "integer",
          "rest_seconds": "integer",
          "video_url": "string"
        }
      ]
    }
  ]
}
8. MealTemplateSchema
json
Copy
Edit
{
  "template_id": "string",
  "goal": "cut | bulk | recomp",
  "days": [
    {
      "day_index": "integer",
      "meals": [
        {
          "meal_id": "string",
          "items": [
            { "food": "string", "raw_grams": "integer" }
          ]
        }
      ]
    }
  ],
  "shopping_list": {
    "ingredients": [
      { "food": "string", "grams": "integer" }
    ],
    "instructions": "string"
  }
}
✅ Final Rule:

All engines must reference only the schemas above for all read/write operations.
No new schema can be used unless added here.
Cursor must treat this file as a locked, immutable contract.

