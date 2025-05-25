"""
TheRegiment - Template API Routes
CRUD operations for training and meal templates
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from ...schemas.models import TrainingTemplateSchema, MealTemplateSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

# Training Template Routes
@router.get("/training", response_model=List[Dict[str, Any]])
async def get_training_templates(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get training templates with optional filtering."""
    try:
        # Build dynamic query based on filters
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if template_type:
            param_count += 1
            conditions.append(f"template_type = ${param_count}")
            params.append(template_type)
        
        if is_active is not None:
            param_count += 1
            conditions.append(f"is_active = ${param_count}")
            params.append(is_active)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        param_count += 1
        query = f"""
        SELECT template_id, user_id, name, description, template_type, exercises, 
               is_active, created_at, updated_at, timezone
        FROM training_templates
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        templates = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for template in templates:
            template_dict = dict(template)
            # Convert timestamps to ISO format strings
            for field in ['created_at', 'updated_at']:
                if template_dict.get(field):
                    template_dict[field] = template_dict[field].isoformat()
            
            result.append(template_dict)
        
        log_event(
            level="INFO",
            message="Retrieved training templates",
            context={
                "count": len(result),
                "user_id": user_id,
                "filters": {"template_type": template_type, "is_active": is_active}
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve training templates",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve training templates")

@router.get("/training/{user_id}/{template_id}", response_model=Dict[str, Any])
async def get_training_template(user_id: str, template_id: str):
    """Get a specific training template."""
    try:
        query = """
        SELECT template_id, user_id, name, description, template_type, exercises, 
               is_active, created_at, updated_at, timezone
        FROM training_templates
        WHERE user_id = $1 AND template_id = $2
        """
        
        template = await execute_query(query, user_id, template_id, fetch_one=True)
        
        if not template:
            raise HTTPException(status_code=404, detail="Training template not found")
        
        # Convert to dict with proper formatting
        result = dict(template)
        for field in ['created_at', 'updated_at']:
            if result.get(field):
                result[field] = result[field].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved training template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve training template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve training template")

@router.post("/training", response_model=Dict[str, Any])
async def create_training_template(template: TrainingTemplateSchema):
    """Create a new training template."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            template.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO training_templates (user_id, name, description, template_type, exercises, 
                                       is_active, created_at, updated_at, timezone)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING template_id, user_id, name
        """
        
        result = await execute_query(
            query,
            template.user_id,
            template.name,
            template.description,
            template.template_type.value,
            template.exercises,
            template.is_active,
            template.created_at,
            template.updated_at,
            template.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created training template",
            context={
                "user_id": template.user_id,
                "template_id": result["template_id"],
                "name": template.name,
                "template_type": template.template_type.value
            }
        )
        
        return {
            "template_id": result["template_id"],
            "user_id": result["user_id"],
            "name": result["name"],
            "message": "Training template created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create training template",
            context={"user_id": template.user_id, "name": template.name, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create training template")

@router.put("/training/{user_id}/{template_id}", response_model=Dict[str, Any])
async def update_training_template(user_id: str, template_id: str, template: TrainingTemplateSchema):
    """Update an existing training template."""
    try:
        # Verify template exists
        existing = await execute_query(
            "SELECT user_id FROM training_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Training template not found")
        
        query = """
        UPDATE training_templates SET
            name = $3, description = $4, template_type = $5, exercises = $6,
            is_active = $7, updated_at = $8, timezone = $9
        WHERE user_id = $1 AND template_id = $2
        RETURNING template_id, user_id, name
        """
        
        result = await execute_query(
            query,
            user_id,
            template_id,
            template.name,
            template.description,
            template.template_type.value,
            template.exercises,
            template.is_active,
            template.updated_at,
            template.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated training template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return {
            "template_id": result["template_id"],
            "user_id": result["user_id"],
            "name": result["name"],
            "message": "Training template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update training template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update training template")

@router.delete("/training/{user_id}/{template_id}", response_model=Dict[str, Any])
async def delete_training_template(user_id: str, template_id: str):
    """Delete a training template."""
    try:
        # Verify template exists
        existing = await execute_query(
            "SELECT user_id FROM training_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Training template not found")
        
        await execute_query(
            "DELETE FROM training_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id
        )
        
        log_event(
            level="INFO",
            message="Deleted training template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return {"message": "Training template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete training template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete training template")

# Meal Template Routes
@router.get("/meals", response_model=List[Dict[str, Any]])
async def get_meal_templates(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
):
    """Get meal templates with optional filtering."""
    try:
        # Build dynamic query based on filters
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if meal_type:
            param_count += 1
            conditions.append(f"meal_type = ${param_count}")
            params.append(meal_type)
        
        if is_active is not None:
            param_count += 1
            conditions.append(f"is_active = ${param_count}")
            params.append(is_active)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        param_count += 1
        query = f"""
        SELECT template_id, user_id, name, description, meal_type, foods, macros,
               is_active, created_at, updated_at, timezone
        FROM meal_templates
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_count}
        """
        params.append(limit)
        
        templates = await execute_query(query, *params, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for template in templates:
            template_dict = dict(template)
            # Convert timestamps to ISO format strings
            for field in ['created_at', 'updated_at']:
                if template_dict.get(field):
                    template_dict[field] = template_dict[field].isoformat()
            
            result.append(template_dict)
        
        log_event(
            level="INFO",
            message="Retrieved meal templates",
            context={
                "count": len(result),
                "user_id": user_id,
                "filters": {"meal_type": meal_type, "is_active": is_active}
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve meal templates",
            context={"error": str(e), "user_id": user_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve meal templates")

@router.get("/meals/{user_id}/{template_id}", response_model=Dict[str, Any])
async def get_meal_template(user_id: str, template_id: str):
    """Get a specific meal template."""
    try:
        query = """
        SELECT template_id, user_id, name, description, meal_type, foods, macros,
               is_active, created_at, updated_at, timezone
        FROM meal_templates
        WHERE user_id = $1 AND template_id = $2
        """
        
        template = await execute_query(query, user_id, template_id, fetch_one=True)
        
        if not template:
            raise HTTPException(status_code=404, detail="Meal template not found")
        
        # Convert to dict with proper formatting
        result = dict(template)
        for field in ['created_at', 'updated_at']:
            if result.get(field):
                result[field] = result[field].isoformat()
        
        log_event(
            level="INFO",
            message="Retrieved meal template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve meal template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve meal template")

@router.post("/meals", response_model=Dict[str, Any])
async def create_meal_template(template: MealTemplateSchema):
    """Create a new meal template."""
    try:
        # Verify client exists
        client_check = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            template.user_id,
            fetch_one=True
        )
        
        if not client_check:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        INSERT INTO meal_templates (user_id, name, description, meal_type, foods, macros,
                                   is_active, created_at, updated_at, timezone)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING template_id, user_id, name
        """
        
        result = await execute_query(
            query,
            template.user_id,
            template.name,
            template.description,
            template.meal_type.value,
            template.foods,
            template.macros.dict() if template.macros else None,
            template.is_active,
            template.created_at,
            template.updated_at,
            template.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created meal template",
            context={
                "user_id": template.user_id,
                "template_id": result["template_id"],
                "name": template.name,
                "meal_type": template.meal_type.value
            }
        )
        
        return {
            "template_id": result["template_id"],
            "user_id": result["user_id"],
            "name": result["name"],
            "message": "Meal template created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create meal template",
            context={"user_id": template.user_id, "name": template.name, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create meal template")

@router.put("/meals/{user_id}/{template_id}", response_model=Dict[str, Any])
async def update_meal_template(user_id: str, template_id: str, template: MealTemplateSchema):
    """Update an existing meal template."""
    try:
        # Verify template exists
        existing = await execute_query(
            "SELECT user_id FROM meal_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Meal template not found")
        
        query = """
        UPDATE meal_templates SET
            name = $3, description = $4, meal_type = $5, foods = $6, macros = $7,
            is_active = $8, updated_at = $9, timezone = $10
        WHERE user_id = $1 AND template_id = $2
        RETURNING template_id, user_id, name
        """
        
        result = await execute_query(
            query,
            user_id,
            template_id,
            template.name,
            template.description,
            template.meal_type.value,
            template.foods,
            template.macros.dict() if template.macros else None,
            template.is_active,
            template.updated_at,
            template.timezone,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated meal template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return {
            "template_id": result["template_id"],
            "user_id": result["user_id"],
            "name": result["name"],
            "message": "Meal template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update meal template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update meal template")

@router.delete("/meals/{user_id}/{template_id}", response_model=Dict[str, Any])
async def delete_meal_template(user_id: str, template_id: str):
    """Delete a meal template."""
    try:
        # Verify template exists
        existing = await execute_query(
            "SELECT user_id FROM meal_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Meal template not found")
        
        await execute_query(
            "DELETE FROM meal_templates WHERE user_id = $1 AND template_id = $2",
            user_id,
            template_id
        )
        
        log_event(
            level="INFO",
            message="Deleted meal template",
            context={"user_id": user_id, "template_id": template_id}
        )
        
        return {"message": "Meal template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete meal template",
            context={"user_id": user_id, "template_id": template_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete meal template")

@router.get("/user/{user_id}/active", response_model=Dict[str, Any])
async def get_active_templates(user_id: str):
    """Get all active templates for a specific user."""
    try:
        # Get active training templates
        training_query = """
        SELECT template_id, name, description, template_type, exercises, created_at
        FROM training_templates
        WHERE user_id = $1 AND is_active = true
        ORDER BY created_at DESC
        """
        
        training_templates = await execute_query(training_query, user_id, fetch_all=True)
        
        # Get active meal templates
        meal_query = """
        SELECT template_id, name, description, meal_type, foods, macros, created_at
        FROM meal_templates
        WHERE user_id = $1 AND is_active = true
        ORDER BY created_at DESC
        """
        
        meal_templates = await execute_query(meal_query, user_id, fetch_all=True)
        
        # Format results
        training_result = []
        for template in training_templates:
            template_dict = dict(template)
            if template_dict.get('created_at'):
                template_dict['created_at'] = template_dict['created_at'].isoformat()
            training_result.append(template_dict)
        
        meal_result = []
        for template in meal_templates:
            template_dict = dict(template)
            if template_dict.get('created_at'):
                template_dict['created_at'] = template_dict['created_at'].isoformat()
            meal_result.append(template_dict)
        
        result = {
            "training_templates": training_result,
            "meal_templates": meal_result,
            "total_training": len(training_result),
            "total_meals": len(meal_result)
        }
        
        log_event(
            level="INFO",
            message="Retrieved active templates",
            context={
                "user_id": user_id,
                "training_count": len(training_result),
                "meal_count": len(meal_result)
            }
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve active templates",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve active templates") 