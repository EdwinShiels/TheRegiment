"""
TheRegiment - Check-in Log API Routes
CRUD operations for check-in logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import CheckinLogSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_checkin_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get check-in logs with optional filtering."""
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
        SELECT user_id, weight_kg, body_fat_percentage, muscle_mass_kg, mood, energy_level, 
               sleep_hours, stress_level, notes, timestamp, timezone, status
        FROM checkin_logs
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        checkin_logs = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for log in checkin_logs:
            log_dict = dict(log)
            # Convert timestamp to ISO format string
            if log_dict.get('timestamp'):
                log_dict['timestamp'] = log_dict['timestamp'].isoformat()
            
            result.append(log_dict)
        
        log_event(
            level="INFO",
            message="Retrieved check-in logs",
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
            message="Failed to retrieve check-in logs",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve check-in logs")

@router.get("/{user_id}/{checkin_id}", response_model=Dict[str, Any])
async def get_checkin_log(user_id: str, checkin_id: str):
    """Get a specific check-in log."""
    try:
        query = """
        SELECT user_id, weight_kg, body_fat_percentage, muscle_mass_kg, mood, energy_level, 
               sleep_hours, stress_level, notes, timestamp, timezone, status
        FROM checkin_logs
        WHERE user_id = $1 AND checkin_id = $2
        """
        
        log = await execute_query(query, user_id, checkin_id, fetch_one=True)
        
        if not log:
            raise HTTPException(status_code=404, detail="Check-in log not found")
        
        # Convert to dict with proper formatting
        result = dict(log)
        if result.get('timestamp'):
            result['timestamp'] = result['timestamp'].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve check-in log")

@router.post("/", response_model=Dict[str, Any])
async def create_checkin_log(checkin: CheckinLogSchema):
    """Create a new check-in log."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            checkin.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO checkin_logs (user_id, weight_kg, body_fat_percentage, muscle_mass_kg, mood, 
                                 energy_level, sleep_hours, stress_level, notes, timestamp, timezone, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING user_id, checkin_id
        """
        
        result = await execute_query(
            query,
            checkin.user_id,
            checkin.weight_kg,
            checkin.body_fat_percentage,
            checkin.muscle_mass_kg,
            checkin.mood.value if checkin.mood else None,
            checkin.energy_level.value if checkin.energy_level else None,
            checkin.sleep_hours,
            checkin.stress_level.value if checkin.stress_level else None,
            checkin.notes,
            checkin.timestamp,
            checkin.timezone,
            checkin.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created check-in log",
            context={
                "user_id": checkin.user_id,
                "weight_kg": checkin.weight_kg,
                "mood": checkin.mood.value if checkin.mood else None,
                "status": checkin.status.value
            }
        )
        
        return {
            "user_id": result["user_id"],
            "checkin_id": result["checkin_id"],
            "message": "Check-in log created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create check-in log",
            context={"user_id": checkin.user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create check-in log")

@router.put("/{user_id}/{checkin_id}", response_model=Dict[str, Any])
async def update_checkin_log(user_id: str, checkin_id: str, checkin: CheckinLogSchema):
    """Update an existing check-in log."""
    try:
        # Verify check-in log exists
        existing = await execute_query(
            "SELECT user_id FROM checkin_logs WHERE user_id = $1 AND checkin_id = $2",
            user_id,
            checkin_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Check-in log not found")
        
        query = """
        UPDATE checkin_logs SET
            weight_kg = $3, body_fat_percentage = $4, muscle_mass_kg = $5, mood = $6,
            energy_level = $7, sleep_hours = $8, stress_level = $9, notes = $10,
            timestamp = $11, timezone = $12, status = $13
        WHERE user_id = $1 AND checkin_id = $2
        RETURNING user_id, checkin_id
        """
        
        result = await execute_query(
            query,
            user_id,
            checkin_id,
            checkin.weight_kg,
            checkin.body_fat_percentage,
            checkin.muscle_mass_kg,
            checkin.mood.value if checkin.mood else None,
            checkin.energy_level.value if checkin.energy_level else None,
            checkin.sleep_hours,
            checkin.stress_level.value if checkin.stress_level else None,
            checkin.notes,
            checkin.timestamp,
            checkin.timezone,
            checkin.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id}
        )
        
        return {
            "user_id": result["user_id"],
            "checkin_id": result["checkin_id"],
            "message": "Check-in log updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update check-in log")

@router.delete("/{user_id}/{checkin_id}", response_model=Dict[str, Any])
async def delete_checkin_log(user_id: str, checkin_id: str):
    """Delete a check-in log."""
    try:
        # Verify check-in log exists
        existing = await execute_query(
            "SELECT user_id FROM checkin_logs WHERE user_id = $1 AND checkin_id = $2",
            user_id,
            checkin_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Check-in log not found")
        
        await execute_query(
            "DELETE FROM checkin_logs WHERE user_id = $1 AND checkin_id = $2",
            user_id,
            checkin_id
        )
        
        log_event(
            level="INFO",
            message="Deleted check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id}
        )
        
        return {"message": "Check-in log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete check-in log",
            context={"user_id": user_id, "checkin_id": checkin_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete check-in log")

@router.get("/user/{user_id}/recent", response_model=List[Dict[str, Any]])
async def get_recent_checkin_logs(user_id: str, days: int = Query(7, ge=1, le=30)):
    """Get recent check-in logs for a specific user."""
    try:
        query = """
        SELECT user_id, weight_kg, body_fat_percentage, muscle_mass_kg, mood, energy_level, 
               sleep_hours, stress_level, notes, timestamp, timezone, status
        FROM checkin_logs
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
            message="Retrieved recent check-in logs",
            context={"user_id": user_id, "days": days, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve recent check-in logs",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve recent check-in logs")

@router.get("/user/{user_id}/latest", response_model=Dict[str, Any])
async def get_latest_checkin(user_id: str):
    """Get the most recent check-in log for a specific user."""
    try:
        query = """
        SELECT user_id, weight_kg, body_fat_percentage, muscle_mass_kg, mood, energy_level, 
               sleep_hours, stress_level, notes, timestamp, timezone, status
        FROM checkin_logs
        WHERE user_id = $1
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        log = await execute_query(query, user_id, fetch_one=True)
        
        if not log:
            raise HTTPException(status_code=404, detail="No check-in logs found for user")
        
        # Convert to dict with proper formatting
        result = dict(log)
        if result.get('timestamp'):
            result['timestamp'] = result['timestamp'].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved latest check-in log",
            context={"user_id": user_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve latest check-in log",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve latest check-in log")

@router.get("/user/{user_id}/trends", response_model=Dict[str, Any])
async def get_checkin_trends(user_id: str, days: int = Query(30, ge=7, le=365)):
    """Get check-in trends for a specific user."""
    try:
        query = """
        SELECT 
            COUNT(*) as total_checkins,
            AVG(weight_kg) as avg_weight,
            AVG(body_fat_percentage) as avg_body_fat,
            AVG(muscle_mass_kg) as avg_muscle_mass,
            AVG(sleep_hours) as avg_sleep_hours,
            MIN(weight_kg) as min_weight,
            MAX(weight_kg) as max_weight,
            MIN(timestamp) as first_checkin,
            MAX(timestamp) as last_checkin
        FROM checkin_logs
        WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '%s days'
        """
        
        trends = await execute_query(query % days, user_id, fetch_one=True)
        
        # Convert to dict with proper formatting
        result = dict(trends) if trends else {}
        
        # Convert None values to 0 for numeric fields
        numeric_fields = ['total_checkins', 'avg_weight', 'avg_body_fat', 'avg_muscle_mass', 
                         'avg_sleep_hours', 'min_weight', 'max_weight']
        for field in numeric_fields:
            if result.get(field) is None:
                result[field] = 0
        
        # Convert timestamps to ISO format
        for field in ['first_checkin', 'last_checkin']:
            if result.get(field):
                result[field] = result[field].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved check-in trends",
            context={"user_id": user_id, "days": days}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve check-in trends",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve check-in trends") 