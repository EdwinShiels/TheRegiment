# Demo: LST Master Logging Format
# Shows Phase 1 compliance with buildspec and LST Master requirements

from datetime import datetime, timezone
from src.core.logging import log_engine_event, setup_engine_logger

def demo_lst_logging():
    """Demonstrate LST Master format logging for all engine types."""
    
    print("🔍 LST Master Logging Format Demo")
    print("=" * 50)
    
    # Setup engine loggers
    meal_logger = setup_engine_logger("meal")
    training_logger = setup_engine_logger("training") 
    checkin_logger = setup_engine_logger("checkin")
    cardio_logger = setup_engine_logger("cardio")
    
    user_id = "123456789012345678"
    timezone_offset = "UTC+2"
    
    print("\n📝 Logging meal completion...")
    log_engine_event(
        user_id=user_id,
        source_engine="meal",
        status="completed",
        data={"meal_id": "planC_meal3"},
        timezone_offset=timezone_offset
    )
    
    print("\n🏋️ Logging training session...")
    log_engine_event(
        user_id=user_id,
        source_engine="training", 
        status="completed",
        data={
            "exercise_id": "ex_dl_001",
            "exercise_name": "Deadlift",
            "weight_kg": 140.0,
            "reps": 6,
            "block_id": "steel_block_b",
            "day_index": 13
        },
        timezone_offset=timezone_offset
    )
    
    print("\n📊 Logging check-in...")
    log_engine_event(
        user_id=user_id,
        source_engine="checkin",
        status="completed", 
        data={
            "weight": 93.8,
            "mood": "😐",
            "soreness": "🟡", 
            "stress": "⚡",
            "sleep": "🔥",
            "notes": "Feeling okay but a bit tight in the back."
        },
        timezone_offset=timezone_offset
    )
    
    print("\n🏃 Logging cardio underperformance...")
    log_engine_event(
        user_id=user_id,
        source_engine="cardio",
        status="underperformed",
        data={
            "assigned_minutes": 30,
            "actual_minutes": 24
        },
        timezone_offset=timezone_offset
    )
    
    print("\n❌ Logging missed meal...")
    log_engine_event(
        user_id=user_id,
        source_engine="meal",
        status="missed",
        data={"meal_id": "planC_meal1"},
        timezone_offset=timezone_offset
    )
    
    print("\n✅ LST Master logging demo complete!")
    print("Check logs/ directory for engine-specific log files.")

if __name__ == "__main__":
    demo_lst_logging() 