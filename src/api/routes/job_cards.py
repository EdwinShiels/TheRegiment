"""
TheRegiment - Job Card API Routes
CRUD operations for job cards
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import JobCardSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_job_cards(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get job cards with optional filtering."""
    try:
        # Build dynamic query based on filters
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)
        
        if priority:
            param_count += 1
            conditions.append(f"priority = ${param_count}")
            params.append(priority)
        
        if start_date:
            param_count += 1
            conditions.append(f"created_at::date >= ${param_count}")
            params.append(start_date)
        
        if end_date:
            param_count += 1
            conditions.append(f"created_at::date <= ${param_count}")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        param_count += 1
        query = f"""
        SELECT job_id, user_id, title, description, priority, status, due_date, 
               created_at, updated_at, completed_at, timezone
        FROM job_cards
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        job_cards = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for card in job_cards:
            card_dict = dict(card)
            # Convert timestamps to ISO format strings
            for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
                if card_dict.get(field):
                    card_dict[field] = card_dict[field].isoformat()
            
            result.append(card_dict)
        
        log_event(
            level="INFO",
            message="Retrieved job cards",
            context={
                "count": len(result),
                "user_id": user_id,
                "filters": {"status": status, "priority": priority, "start_date": start_date, "end_date": end_date}
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve job cards",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve job cards")

@router.get("/{user_id}/{job_id}", response_model=Dict[str, Any])
async def get_job_card(user_id: str, job_id: str):
    """Get a specific job card."""
    try:
        query = """
        SELECT job_id, user_id, title, description, priority, status, due_date, 
               created_at, updated_at, completed_at, timezone
        FROM job_cards
        WHERE user_id = $1 AND job_id = $2
        """
        
        card = await execute_query(query, user_id, job_id, fetch_one=True)
        
        if not card:
            raise HTTPException(status_code=404, detail="Job card not found")
        
        # Convert to dict with proper formatting
        result = dict(card)
        for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
            if result.get(field):
                result[field] = result[field].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved job card",
            context={"user_id": user_id, "job_id": job_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve job card",
            context={"user_id": user_id, "job_id": job_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve job card")

@router.post("/", response_model=Dict[str, Any])
async def create_job_card(job_card: JobCardSchema):
    """Create a new job card."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            job_card.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO job_cards (user_id, title, description, priority, status, due_date, 
                              created_at, updated_at, timezone)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING job_id, user_id, title
        """
        
        result = await execute_query(
            query,
            job_card.user_id,
            job_card.title,
            job_card.description,
            job_card.priority.value,
            job_card.status.value,
            job_card.due_date,
            job_card.created_at,
            job_card.updated_at,
            job_card.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created job card",
            context={
                "user_id": job_card.user_id,
                "job_id": result["job_id"],
                "title": job_card.title,
                "priority": job_card.priority.value,
                "status": job_card.status.value
            }
        )
        
        return {
            "job_id": result["job_id"],
            "user_id": result["user_id"],
            "title": result["title"],
            "message": "Job card created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create job card",
            context={"user_id": job_card.user_id, "title": job_card.title, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create job card")

@router.put("/{user_id}/{job_id}", response_model=Dict[str, Any])
async def update_job_card(user_id: str, job_id: str, job_card: JobCardSchema):
    """Update an existing job card."""
    try:
        # Verify job card exists
        existing = await execute_query(
            "SELECT user_id FROM job_cards WHERE user_id = $1 AND job_id = $2",
            user_id,
            job_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Job card not found")
        
        query = """
        UPDATE job_cards SET
            title = $3, description = $4, priority = $5, status = $6, due_date = $7,
            updated_at = $8, completed_at = $9, timezone = $10
        WHERE user_id = $1 AND job_id = $2
        RETURNING job_id, user_id, title
        """
        
        result = await execute_query(
            query,
            user_id,
            job_id,
            job_card.title,
            job_card.description,
            job_card.priority.value,
            job_card.status.value,
            job_card.due_date,
            job_card.updated_at,
            job_card.completed_at,
            job_card.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated job card",
            context={"user_id": user_id, "job_id": job_id}
        )
        
        return {
            "job_id": result["job_id"],
            "user_id": result["user_id"],
            "title": result["title"],
            "message": "Job card updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update job card",
            context={"user_id": user_id, "job_id": job_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update job card")

@router.delete("/{user_id}/{job_id}", response_model=Dict[str, Any])
async def delete_job_card(user_id: str, job_id: str):
    """Delete a job card."""
    try:
        # Verify job card exists
        existing = await execute_query(
            "SELECT user_id FROM job_cards WHERE user_id = $1 AND job_id = $2",
            user_id,
            job_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Job card not found")
        
        await execute_query(
            "DELETE FROM job_cards WHERE user_id = $1 AND job_id = $2",
            user_id,
            job_id
        )
        
        log_event(
            level="INFO",
            message="Deleted job card",
            context={"user_id": user_id, "job_id": job_id}
        )
        
        return {"message": "Job card deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete job card",
            context={"user_id": user_id, "job_id": job_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete job card")

@router.patch("/{user_id}/{job_id}/status", response_model=Dict[str, Any])
async def update_job_card_status(user_id: str, job_id: str, status: str):
    """Update the status of a job card."""
    try:
        # Verify job card exists
        existing = await execute_query(
            "SELECT user_id FROM job_cards WHERE user_id = $1 AND job_id = $2",
            user_id,
            job_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Job card not found")
        
        # Set completed_at if status is completed
        completed_at = datetime.utcnow() if status.lower() == 'completed' else None
        
        query = """
        UPDATE job_cards SET
            status = $3, updated_at = $4, completed_at = $5
        WHERE user_id = $1 AND job_id = $2
        RETURNING job_id, user_id, title, status
        """
        
        result = await execute_query(
            query,
            user_id,
            job_id,
            status,
            datetime.utcnow(),
            completed_at,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated job card status",
            context={"user_id": user_id, "job_id": job_id, "status": status}
        )
        
        return {
            "job_id": result["job_id"],
            "user_id": result["user_id"],
            "title": result["title"],
            "status": result["status"],
            "message": "Job card status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update job card status",
            context={"user_id": user_id, "job_id": job_id, "status": status, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update job card status")

@router.get("/user/{user_id}/active", response_model=List[Dict[str, Any]])
async def get_active_job_cards(user_id: str):
    """Get active job cards for a specific user."""
    try:
        query = """
        SELECT job_id, user_id, title, description, priority, status, due_date, 
               created_at, updated_at, completed_at, timezone
        FROM job_cards
        WHERE user_id = $1 AND status NOT IN ('completed', 'cancelled')
        ORDER BY priority DESC, created_at ASC
        """
        
        cards = await execute_query(query, user_id, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for card in cards:
            card_dict = dict(card)
            for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
                if card_dict.get(field):
                    card_dict[field] = card_dict[field].isoformat()
            
            result.append(card_dict)
        
        log_event(
            level="INFO",
            message="Retrieved active job cards",
            context={"user_id": user_id, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve active job cards",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve active job cards")

@router.get("/user/{user_id}/overdue", response_model=List[Dict[str, Any]])
async def get_overdue_job_cards(user_id: str):
    """Get overdue job cards for a specific user."""
    try:
        query = """
        SELECT job_id, user_id, title, description, priority, status, due_date, 
               created_at, updated_at, completed_at, timezone
        FROM job_cards
        WHERE user_id = $1 AND due_date < NOW() AND status NOT IN ('completed', 'cancelled')
        ORDER BY due_date ASC
        """
        
        cards = await execute_query(query, user_id, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for card in cards:
            card_dict = dict(card)
            for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
                if card_dict.get(field):
                    card_dict[field] = card_dict[field].isoformat()
            
            result.append(card_dict)
        
        log_event(
            level="INFO",
            message="Retrieved overdue job cards",
            context={"user_id": user_id, "count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve overdue job cards",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve overdue job cards")

@router.get("/user/{user_id}/stats", response_model=Dict[str, Any])
async def get_job_card_stats(user_id: str, days: int = Query(30, ge=1, le=365)):
    """Get job card statistics for a specific user."""
    try:
        query = """
        SELECT 
            COUNT(*) as total_cards,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_cards,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_cards,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_cards,
            COUNT(CASE WHEN due_date < NOW() AND status NOT IN ('completed', 'cancelled') THEN 1 END) as overdue_cards,
            AVG(CASE WHEN completed_at IS NOT NULL THEN EXTRACT(EPOCH FROM (completed_at - created_at))/86400 END) as avg_completion_days
        FROM job_cards
        WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
        """
        
        stats = await execute_query(query % days, user_id, fetch_one=True)
        
        # Convert to dict with proper formatting
        result = dict(stats) if stats else {}
        
        # Convert None values to 0 for numeric fields
        numeric_fields = ['total_cards', 'completed_cards', 'in_progress_cards', 'pending_cards', 'overdue_cards']
        for field in numeric_fields:
            if result.get(field) is None:
                result[field] = 0
        
        # Round average completion days
        if result.get('avg_completion_days'):
            result['avg_completion_days'] = round(float(result['avg_completion_days']), 2)
        else:
            result['avg_completion_days'] = 0
        
        log_event(
            level="INFO",
            message="Retrieved job card stats",
            context={"user_id": user_id, "days": days}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve job card stats",
            context={"user_id": user_id, "days": days, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve job card stats") 