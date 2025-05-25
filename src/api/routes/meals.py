"""
TheRegiment - Meal Log API Routes
CRUD operations for meal logs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import MealLogSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_meal_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get meal logs with optional filtering."""
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
            conditions.append(f"date >= ${param_count}")
            params.append(start_date)
        
        if end_date:
            param_count += 1
            conditions.append(f"date <= ${param_count}")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        param_count += 1
        query = f"""
        SELECT user_id, meal_id, date, logged_at, timezone_offset, status
        FROM meal_logs
        {where_clause}
        ORDER BY logged_at DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        meals = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for meal in meals:
            meal_dict = dict(meal)
            # Convert dates to ISO format strings
            if meal_dict.get('date'):
                meal_dict['date'] = meal_dict['date'].isoformat()
            if meal_dict.get('logged_at'):
                meal_dict['logged_at'] = meal_dict['logged_at'].isoformat()
            
            result.append(meal_dict)
        
        log_event(
            level="INFO",
            message="Retrieved meal logs",
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
            message="Failed to retrieve meal logs",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve meal logs")

@router.get("/{user_id}/{meal_id}", response_model=Dict[str, Any])
async def get_meal_log(user_id: str, meal_id: str):
    """Get a specific meal log."""
    try:
        query = """
        SELECT user_id, meal_id, date, logged_at, timezone_offset, status
        FROM meal_logs
        WHERE user_id = $1 AND meal_id = $2
        """
        
        meal = await execute_query(query, user_id, meal_id, fetch_one=True)
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal log not found")
        
        # Convert to dict with proper formatting
        meal_dict = dict(meal)
        if meal_dict.get('date'):
            meal_dict['date'] = meal_dict['date'].isoformat()
        if meal_dict.get('logged_at'):
            meal_dict['logged_at'] = meal_dict['logged_at'].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved meal log",
            context={"user_id": user_id, "meal_id": meal_id}
        )
        
        return meal_dict
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve meal log",
            context={"user_id": user_id, "meal_id": meal_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve meal log")

@router.post("/", response_model=Dict[str, Any])
async def create_meal_log(meal: MealLogSchema):
    """Create a new meal log."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            meal.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO meal_logs (user_id, meal_id, date, logged_at, timezone_offset, status)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING user_id, meal_id
        """
        
        result = await execute_query(
            query,
            meal.user_id,
            meal.meal_id,
            meal.date,
            meal.logged_at,
            meal.timezone_offset,
            meal.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created meal log",
            context={"user_id": meal.user_id, "meal_id": meal.meal_id, "status": meal.status.value}
        )
        
        return {
            "user_id": result["user_id"],
            "meal_id": result["meal_id"],
            "message": "Meal log created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create meal log",
            context={"user_id": meal.user_id, "meal_id": meal.meal_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create meal log")

@router.put("/{user_id}/{meal_id}", response_model=Dict[str, Any])
async def update_meal_log(user_id: str, meal_id: str, meal: MealLogSchema):
    """Update an existing meal log."""
    try:
        # Verify meal log exists
        existing = await execute_query(
            "SELECT user_id FROM meal_logs WHERE user_id = $1 AND meal_id = $2",
            user_id,
            meal_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Meal log not found")
        
        query = """
        UPDATE meal_logs SET
            date = $3, logged_at = $4, timezone_offset = $5, status = $6
        WHERE user_id = $1 AND meal_id = $2
        RETURNING user_id, meal_id
        """
        
        result = await execute_query(
            query,
            user_id,
            meal_id,
            meal.date,
            meal.logged_at,
            meal.timezone_offset,
            meal.status.value,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated meal log",
            context={"user_id": user_id, "meal_id": meal_id}
        )
        
        return {
            "user_id": result["user_id"],
            "meal_id": result["meal_id"],
            "message": "Meal log updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update meal log",
            context={"user_id": user_id, "meal_id": meal_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update meal log")

@router.delete("/{user_id}/{meal_id}", response_model=Dict[str, Any])
async def delete_meal_log(user_id: str, meal_id: str):
    """Delete a meal log."""
    try:
        # Verify meal log exists
        existing = await execute_query(
            "SELECT user_id FROM meal_logs WHERE user_id = $1 AND meal_id = $2",
            user_id,
            meal_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Meal log not found")
        
        await execute_query(
            "DELETE FROM meal_logs WHERE user_id = $1 AND meal_id = $2",
            user_id,
            meal_id
        )
        
        log_event(
            level="INFO",
            message="Deleted meal log",
            context={"user_id": user_id, "meal_id": meal_id}
        )
        
        return {"message": "Meal log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete meal log",
            context={"user_id": user_id, "meal_id": meal_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete meal log")

@router.get("/user/{user_id}/recent", response_model=List[Dict[str, Any]])
async def get_recent_meal_logs(user_id: str, days: int = Query(7, ge=1, le=30)):
    """Get recent meal logs for a specific user."""
    try:
        query = """
        SELECT user_id, meal_id, date, logged_at, timezone_offset, status
        FROM meal_logs
        WHERE user_id = $1 AND date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY logged_at DESC
        """
        
        meals = await execute_query(query % days, user_id, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for meal in meals:
            meal_dict = dict(meal)
            if meal_dict.get('date'):
                meal_dict['date'] = meal_dict['date'].isoformat()
            if meal_dict.get('logged_at'):
                meal_dict['logged_at'] = meal_dict['logged_at'].isoformat()
            
            result.append(meal_dict)
        
        log_event(
            level="INFO",
            message="Retrieved recent meal logs",
            context={"user_id": user_id, "days": days, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve recent meal logs",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve recent meal logs") 