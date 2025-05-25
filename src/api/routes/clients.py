"""
TheRegiment - Client Profile API Routes
CRUD operations for client profiles
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import date

from ...schemas.models import ClientProfileSchema
from ...core.database import execute_query
from ...core.logging.logger import log_event

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_clients():
    """Get all client profiles."""
    try:
        query = """
        SELECT user_id, goal, timezone_offset, start_date, paused, height_cm, weight_kg,
               training_template_id, meal_template_id, protein, carbs, fats, cardio_minutes,
               cycle_start_date, block_id
        FROM client_profiles
        ORDER BY start_date DESC
        """
        
        clients = await execute_query(query, fetch_all=True)
        
        # Convert to list of dicts with proper formatting
        result = []
        for client in clients:
            client_dict = dict(client)
            # Convert dates to ISO format strings
            if client_dict.get('start_date'):
                client_dict['start_date'] = client_dict['start_date'].isoformat()
            if client_dict.get('cycle_start_date'):
                client_dict['cycle_start_date'] = client_dict['cycle_start_date'].isoformat()
            
            # Structure macros as nested object
            client_dict['macros'] = {
                'protein': client_dict.pop('protein'),
                'carbs': client_dict.pop('carbs'),
                'fats': client_dict.pop('fats')
            }
            
            result.append(client_dict)
        
        log_event(
            level="INFO",
            message="Retrieved all client profiles",
            context={"count": len(result)}
        )
        
        return result
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve client profiles",
            context={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve clients")

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_client(user_id: str):
    """Get a specific client profile by user_id."""
    try:
        query = """
        SELECT user_id, goal, timezone_offset, start_date, paused, height_cm, weight_kg,
               training_template_id, meal_template_id, protein, carbs, fats, cardio_minutes,
               cycle_start_date, block_id
        FROM client_profiles
        WHERE user_id = $1
        """
        
        client = await execute_query(query, user_id, fetch_one=True)
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Convert to dict with proper formatting
        client_dict = dict(client)
        if client_dict.get('start_date'):
            client_dict['start_date'] = client_dict['start_date'].isoformat()
        if client_dict.get('cycle_start_date'):
            client_dict['cycle_start_date'] = client_dict['cycle_start_date'].isoformat()
        
        # Structure macros as nested object
        client_dict['macros'] = {
            'protein': client_dict.pop('protein'),
            'carbs': client_dict.pop('carbs'),
            'fats': client_dict.pop('fats')
        }
        
        log_event(
            level="INFO",
            message="Retrieved client profile",
            context={"user_id": user_id}
        )
        
        return client_dict
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to retrieve client profile",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve client")

@router.post("/", response_model=Dict[str, Any])
async def create_client(client: ClientProfileSchema):
    """Create a new client profile."""
    try:
        query = """
        INSERT INTO client_profiles (
            user_id, goal, timezone_offset, start_date, paused, height_cm, weight_kg,
            training_template_id, meal_template_id, protein, carbs, fats, cardio_minutes,
            cycle_start_date, block_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        RETURNING user_id
        """
        
        result = await execute_query(
            query,
            client.user_id,
            client.goal.value,
            client.timezone_offset,
            client.start_date,
            client.paused,
            client.height_cm,
            client.weight_kg,
            client.training_template_id,
            client.meal_template_id,
            client.macros.protein,
            client.macros.carbs,
            client.macros.fats,
            client.cardio_minutes,
            client.cycle_start_date,
            client.block_id,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Created new client profile",
            context={"user_id": client.user_id}
        )
        
        return {"user_id": result["user_id"], "message": "Client created successfully"}
        
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to create client profile",
            context={"user_id": client.user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create client")

@router.put("/{user_id}", response_model=Dict[str, Any])
async def update_client(user_id: str, client: ClientProfileSchema):
    """Update an existing client profile."""
    try:
        # Verify client exists
        existing = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            user_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Client not found")
        
        query = """
        UPDATE client_profiles SET
            goal = $2, timezone_offset = $3, start_date = $4, paused = $5,
            height_cm = $6, weight_kg = $7, training_template_id = $8,
            meal_template_id = $9, protein = $10, carbs = $11, fats = $12,
            cardio_minutes = $13, cycle_start_date = $14, block_id = $15
        WHERE user_id = $1
        RETURNING user_id
        """
        
        result = await execute_query(
            query,
            user_id,
            client.goal.value,
            client.timezone_offset,
            client.start_date,
            client.paused,
            client.height_cm,
            client.weight_kg,
            client.training_template_id,
            client.meal_template_id,
            client.macros.protein,
            client.macros.carbs,
            client.macros.fats,
            client.cardio_minutes,
            client.cycle_start_date,
            client.block_id,
            fetch_one=True
        )
        
        log_event(
            level="INFO",
            message="Updated client profile",
            context={"user_id": user_id}
        )
        
        return {"user_id": result["user_id"], "message": "Client updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to update client profile",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update client")

@router.delete("/{user_id}", response_model=Dict[str, Any])
async def delete_client(user_id: str):
    """Delete a client profile."""
    try:
        # Verify client exists
        existing = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            user_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete client (this will cascade to related logs due to foreign keys)
        await execute_query(
            "DELETE FROM client_profiles WHERE user_id = $1",
            user_id
        )
        
        log_event(
            level="INFO",
            message="Deleted client profile",
            context={"user_id": user_id}
        )
        
        return {"message": "Client deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to delete client profile",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete client")

@router.post("/{user_id}/pause", response_model=Dict[str, Any])
async def toggle_client_pause(user_id: str, paused: bool):
    """Pause or unpause a client."""
    try:
        # Verify client exists
        existing = await execute_query(
            "SELECT user_id FROM client_profiles WHERE user_id = $1",
            user_id,
            fetch_one=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Client not found")
        
        await execute_query(
            "UPDATE client_profiles SET paused = $2 WHERE user_id = $1",
            user_id,
            paused
        )
        
        log_event(
            level="INFO",
            message=f"Client {'paused' if paused else 'unpaused'}",
            context={"user_id": user_id, "paused": paused}
        )
        
        return {
            "user_id": user_id,
            "paused": paused,
            "message": f"Client {'paused' if paused else 'unpaused'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_event(
            level="ERROR",
            message="Failed to toggle client pause status",
            context={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update pause status") 