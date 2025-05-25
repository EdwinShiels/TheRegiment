"""
TheRegiment - Training Log API Routes
CRUD operations for training logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import TrainingLogSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_training_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    block_id: Optional[str] = Query(None, description="Filter by block ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get training logs with optional filtering."""
    try:
        # Build dynamic query based on filters
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if block_id:
            param_count += 1
            conditions.append(f"block_id = ${param_count}")
            params.append(block_id)
        
        if start_date:
            param_count += 1
            conditions.append(f"timestamp::date >= ${param_count}")
            params.append(start_date)
        
        if end_date:
            param_count += 1
            conditions.append(f"timestamp::date <= ${param_count}")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        param_count += 1
        query = f"""
        SELECT user_id, block_id, day_index, exercise, weight_kg, reps, timestamp, timezone, status
        FROM training_logs
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        training_logs = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for log in training_logs:
            log_dict = dict(log)
            # Convert timestamp to ISO format string
            if log_dict.get('timestamp'):
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            result.append(log_dict)
        
        log_event(
            level="INFO",
            message="Retrieved training logs",
            context={
                "count": len(result),
                "user_id": user_id,
                "block_id": block_id,
                "filters": {"start_date": start_date, "end_date": end_date}
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve training logs",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve training logs")

@router.get("/{user_id}/{block_id}/{day_index}", response_model=List[Dict[str, Any]])
async def get_training_session(user_id: str, block_id: str, day_index: int):
    """Get all training logs for a specific session."""
    try:
        query = """
        SELECT user_id, block_id, day_index, exercise, weight_kg, reps, timestamp, timezone, status
        FROM training_logs
        WHERE user_id = $1 AND block_id = $2 AND day_index = $3
        ORDER BY timestamp ASC
        """
        
        logs = await execute_query(query, user_id, block_id, day_index, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for log in logs:
            log_dict = dict(log)
            if log_dict.get('timestamp'):
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            result.append(log_dict)
        
        log_event(
            level="INFO",
            message="Retrieved training session",
            context={"user_id": user_id, "block_id": block_id, "day_index": day_index, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve training session",
            context={"user_id": user_id, "block_id": block_id, "day_index": day_index, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve training session")

@router.post("/", response_model=Dict[str, Any])
async def create_training_log(training: TrainingLogSchema):
    """Create a new training log."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            training.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO training_logs (user_id, block_id, day_index, exercise, weight_kg, reps, timestamp, timezone, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING user_id, block_id, day_index, exercise
        """
        
        result = await execute_query(
            query,
            training.user_id,
            training.block_id,
            training.day_index,
            training.exercise,
            training.weight_kg,
            training.reps,
            training.timestamp,
            training.timezone,
            training.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created training log",
            context={
                "user_id": training.user_id,
                "exercise": training.exercise,
                "weight_kg": training.weight_kg,
                "reps": training.reps,
                "status": training.status.value
            }
        )
        
        return {
            "user_id": result["user_id"],
            "block_id": result["block_id"],
            "day_index": result["day_index"],
            "exercise": result["exercise"],
            "message": "Training log created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create training log",
            context={"user_id": training.user_id, "exercise": training.exercise, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create training log")

@router.put("/{user_id}/{block_id}/{day_index}/{exercise}", response_model=Dict[str, Any])
async def update_training_log(
    user_id: str, 
    block_id: str, 
    day_index: int, 
    exercise: str, 
    training: TrainingLogSchema
):
    """Update an existing training log."""
    try:
        # Verify training log exists
        existing = await execute_query(
            "SELECT user_id FROM training_logs WHERE user_id = $1 AND block_id = $2 AND day_index = $3 AND exercise = $4",
            user_id,
            block_id,
            day_index,
            exercise,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Training log not found")
        
        query = """
        UPDATE training_logs SET
            weight_kg = $5, reps = $6, timestamp = $7, timezone = $8, status = $9
        WHERE user_id = $1 AND block_id = $2 AND day_index = $3 AND exercise = $4
        RETURNING user_id, block_id, day_index, exercise
        """
        
        result = await execute_query(
            query,
            user_id,
            block_id,
            day_index,
            exercise,
            training.weight_kg,
            training.reps,
            training.timestamp,
            training.timezone,
            training.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated training log",
            context={"user_id": user_id, "exercise": exercise}
        )
        
        return {
            "user_id": result["user_id"],
            "block_id": result["block_id"],
            "day_index": result["day_index"],
            "exercise": result["exercise"],
            "message": "Training log updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update training log",
            context={"user_id": user_id, "exercise": exercise, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update training log")

@router.delete("/{user_id}/{block_id}/{day_index}/{exercise}", response_model=Dict[str, Any])
async def delete_training_log(user_id: str, block_id: str, day_index: int, exercise: str):
    """Delete a training log."""
    try:
        # Verify training log exists
        existing = await execute_query(
            "SELECT user_id FROM training_logs WHERE user_id = $1 AND block_id = $2 AND day_index = $3 AND exercise = $4",
            user_id,
            block_id,
            day_index,
            exercise,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Training log not found")
        
        await execute_query(
            "DELETE FROM training_logs WHERE user_id = $1 AND block_id = $2 AND day_index = $3 AND exercise = $4",
            user_id,
            block_id,
            day_index,
            exercise
        )
        
        log_event(
            level="INFO",
            message="Deleted training log",
            context={"user_id": user_id, "exercise": exercise}
        )
        
        return {"message": "Training log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete training log",
            context={"user_id": user_id, "exercise": exercise, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete training log")

@router.get("/user/{user_id}/recent", response_model=List[Dict[str, Any]])
async def get_recent_training_logs(user_id: str, days: int = Query(7, ge=1, le=30)):
    """Get recent training logs for a specific user."""
    try:
        query = """
        SELECT user_id, block_id, day_index, exercise, weight_kg, reps, timestamp, timezone, status
        FROM training_logs
        WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '%s days'
        ORDER BY timestamp DESC
        """
        
        logs = await execute_query(query % days, user_id, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for log in logs:
            log_dict = dict(log)
            if log_dict.get('timestamp'):
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            result.append(log_dict)
        
        log_event(
            level="INFO",
            message="Retrieved recent training logs",
            context={"user_id": user_id, "days": days, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve recent training logs",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve recent training logs") 