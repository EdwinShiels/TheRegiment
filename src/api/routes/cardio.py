"""
TheRegiment - Cardio Log API Routes
CRUD operations for cardio logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import CardioLogSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_cardio_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get cardio logs with optional filtering."""
    try:
        # Build dynamic query based on filters
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
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
        SELECT user_id, exercise, duration_minutes, distance_km, calories_burned, timestamp, timezone, status
        FROM cardio_logs
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        cardio_logs = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for log in cardio_logs:
            log_dict = dict(log)
            # Convert timestamp to ISO format string
            if log_dict.get('timestamp'):
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            result.append(log_dict)
        
        log_event(
            level="INFO",
            message="Retrieved cardio logs",
            context={
                "count": len(result),
                "user_id": user_id,
                "filters": {"start_date": start_date, "end_date": end_date}
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve cardio logs",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve cardio logs")

@router.get("/{user_id}/{cardio_id}", response_model=Dict[str, Any])
async def get_cardio_log(user_id: str, cardio_id: str):
    """Get a specific cardio log."""
    try:
        query = """
        SELECT user_id, exercise, duration_minutes, distance_km, calories_burned, timestamp, timezone, status
        FROM cardio_logs
        WHERE user_id = $1 AND cardio_id = $2
        """
        
        log = await execute_query(query, user_id, cardio_id, fetch_one=True)
        
        if not log:
            raise HTTPException(status_code=404, detail="Cardio log not found")
        
        # Convert to dict with proper formatting
        result = dict(log)
        if result.get('timestamp'):
            result['timestamp'] = result['timestamp'].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve cardio log")

@router.post("/", response_model=Dict[str, Any])
async def create_cardio_log(cardio: CardioLogSchema):
    """Create a new cardio log."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            cardio.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO cardio_logs (user_id, exercise, duration_minutes, distance_km, calories_burned, timestamp, timezone, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING user_id, exercise, cardio_id
        """
        
        result = await execute_query(
            query,
            cardio.user_id,
            cardio.exercise,
            cardio.duration_minutes,
            cardio.distance_km,
            cardio.calories_burned,
            cardio.timestamp,
            cardio.timezone,
            cardio.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created cardio log",
            context={
                "user_id": cardio.user_id,
                "exercise": cardio.exercise,
                "duration_minutes": cardio.duration_minutes,
                "status": cardio.status.value
            }
        )
        
        return {
            "user_id": result["user_id"],
            "exercise": result["exercise"],
            "cardio_id": result["cardio_id"],
            "message": "Cardio log created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create cardio log",
            context={"user_id": cardio.user_id, "exercise": cardio.exercise, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create cardio log")

@router.put("/{user_id}/{cardio_id}", response_model=Dict[str, Any])
async def update_cardio_log(user_id: str, cardio_id: str, cardio: CardioLogSchema):
    """Update an existing cardio log."""
    try:
        # Verify cardio log exists
        existing = await execute_query(
            "SELECT user_id FROM cardio_logs WHERE user_id = $1 AND cardio_id = $2",
            user_id,
            cardio_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Cardio log not found")
        
        query = """
        UPDATE cardio_logs SET
            exercise = $3, duration_minutes = $4, distance_km = $5, calories_burned = $6,
            timestamp = $7, timezone = $8, status = $9
        WHERE user_id = $1 AND cardio_id = $2
        RETURNING user_id, exercise, cardio_id
        """
        
        result = await execute_query(
            query,
            user_id,
            cardio_id,
            cardio.exercise,
            cardio.duration_minutes,
            cardio.distance_km,
            cardio.calories_burned,
            cardio.timestamp,
            cardio.timezone,
            cardio.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id}
        )
        
        return {
            "user_id": result["user_id"],
            "exercise": result["exercise"],
            "cardio_id": result["cardio_id"],
            "message": "Cardio log updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update cardio log")

@router.delete("/{user_id}/{cardio_id}", response_model=Dict[str, Any])
async def delete_cardio_log(user_id: str, cardio_id: str):
    """Delete a cardio log."""
    try:
        # Verify cardio log exists
        existing = await execute_query(
            "SELECT user_id FROM cardio_logs WHERE user_id = $1 AND cardio_id = $2",
            user_id,
            cardio_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Cardio log not found")
        
        await execute_query(
            "DELETE FROM cardio_logs WHERE user_id = $1 AND cardio_id = $2",
            user_id,
            cardio_id
        )
        
        log_event(
            level="INFO",
            message="Deleted cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id}
        )
        
        return {"message": "Cardio log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete cardio log",
            context={"user_id": user_id, "cardio_id": cardio_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete cardio log")

@router.get("/user/{user_id}/recent", response_model=List[Dict[str, Any]])
async def get_recent_cardio_logs(user_id: str, days: int = Query(7, ge=1, le=30)):
    """Get recent cardio logs for a specific user."""
    try:
        query = """
        SELECT user_id, exercise, duration_minutes, distance_km, calories_burned, timestamp, timezone, status
        FROM cardio_logs
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
            message="Retrieved recent cardio logs",
            context={"user_id": user_id, "days": days, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve recent cardio logs",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve recent cardio logs")

@router.get("/user/{user_id}/stats", response_model=Dict[str, Any])
async def get_cardio_stats(user_id: str, days: int = Query(30, ge=1, le=365)):
    """Get cardio statistics for a specific user."""
    try:
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            SUM(duration_minutes) as total_duration,
            SUM(distance_km) as total_distance,
            SUM(calories_burned) as total_calories,
            AVG(duration_minutes) as avg_duration,
            AVG(distance_km) as avg_distance,
            AVG(calories_burned) as avg_calories
        FROM cardio_logs
        WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '%s days'
        """
        
        stats = await execute_query(query % days, user_id, fetch_one=True)
        
        # Convert to dict with proper formatting
        result = dict(stats) if stats else {}
        
        # Convert None values to 0 for numeric fields
        numeric_fields = ['total_sessions', 'total_duration', 'total_distance', 'total_calories', 
                         'avg_duration', 'avg_distance', 'avg_calories']
        for field in numeric_fields:
            if result.get(field) is None:
                result[field] = 0
        
        log_event(
            level="INFO",
            message="Retrieved cardio stats",
            context={"user_id": user_id, "days": days}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve cardio stats",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve cardio stats") 