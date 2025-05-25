"""
Onboarding Engine - Phase 3
Discord-based client onboarding with profile creation and Battle Station finalization
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from src.core.database import get_db_connection
from src.schemas.models import ClientProfileSchema
from src.core.logging.logger import setup_logger

logger = setup_logger("onboarding_engine")

class OnboardingEngine:
    """
    Handles Discord-based client onboarding with profile creation
    """
    
    def __init__(self):
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await get_db_connection()
    
    async def collect_client_data(self, discord_interaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect and validate client data from Discord interaction
        
        Args:
            discord_interaction: Discord form submission data
            
        Returns:
            Validated client data dictionary
        """
        try:
            # Extract form data from Discord interaction
            form_data = discord_interaction.get('data', {})
            user_id = str(discord_interaction.get('user', {}).get('id', ''))
            
            # Validate required fields
            required_fields = ['name', 'email', 'height_cm', 'weight_kg', 'timezone_offset', 'goal']
            for field in required_fields:
                if field not in form_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate data types and ranges
            height_cm = float(form_data['height_cm'])
            weight_kg = float(form_data['weight_kg'])
            
            if not (120 <= height_cm <= 250):
                raise ValueError("Height must be between 120-250 cm")
            
            if not (30 <= weight_kg <= 300):
                raise ValueError("Weight must be between 30-300 kg")
            
            # Validate timezone format (UTC±X)
            timezone_offset = form_data['timezone_offset']
            if not self._validate_timezone_format(timezone_offset):
                raise ValueError("Timezone must be in format UTC±X (e.g., UTC+5, UTC-8)")
            
            # Validate email format
            email = form_data['email']
            if '@' not in email or '.' not in email:
                raise ValueError("Invalid email format")
            
            client_data = {
                'discord_user_id': user_id,
                'name': form_data['name'],
                'email': email,
                'height_cm': height_cm,
                'weight_kg': weight_kg,
                'timezone_offset': timezone_offset,
                'goal': form_data['goal'],
                'start_date': self.calculate_start_date(datetime.utcnow()),
                'paused': False,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info(
                "Client data collected successfully",
                extra={
                    "user_id": user_id,
                    "context": {"action": "data_collection", "status": "success"}
                }
            )
            
            return client_data
            
        except Exception as e:
            logger.error(
                "Failed to collect client data",
                extra={
                    "user_id": discord_interaction.get('user', {}).get('id', 'unknown'),
                    "context": {"action": "data_collection", "error": str(e)}
                }
            )
            raise
    
    def calculate_start_date(self, current_date: datetime) -> str:
        """
        Calculate start date as next Tuesday
        
        Args:
            current_date: Current datetime
            
        Returns:
            ISO 8601 date string for next Tuesday
        """
        # Find next Tuesday (weekday 1, where Monday=0)
        days_ahead = 1 - current_date.weekday()  # Tuesday is weekday 1
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_tuesday = current_date + timedelta(days=days_ahead)
        return next_tuesday.date().isoformat()
    
    async def create_client_profile(self, form_data: Dict[str, Any]) -> str:
        """
        Create client profile in database with retry logic
        
        Args:
            form_data: Validated client data
            
        Returns:
            Client ID
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check if user already exists
                existing_user = await self._check_existing_user(form_data['discord_user_id'])
                if existing_user:
                    raise ValueError("User already exists")
                
                # Validate against schema
                client_profile = ClientProfileSchema(**form_data)
                
                # Insert into database
                query = """
                INSERT INTO client_profiles (
                    discord_user_id, name, email, height_cm, weight_kg,
                    timezone_offset, goal, start_date, paused, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
                """
                
                result = await self.db.fetchrow(
                    query,
                    client_profile.discord_user_id,
                    client_profile.name,
                    client_profile.email,
                    client_profile.height_cm,
                    client_profile.weight_kg,
                    client_profile.timezone_offset,
                    client_profile.goal,
                    client_profile.start_date,
                    client_profile.paused,
                    client_profile.created_at
                )
                
                client_id = str(result['id'])
                
                logger.info(
                    "Client profile created successfully",
                    extra={
                        "user_id": form_data['discord_user_id'],
                        "context": {
                            "action": "profile_creation",
                            "client_id": client_id,
                            "status": "success"
                        }
                    }
                )
                
                return client_id
                
            except Exception as e:
                retry_count += 1
                logger.warning(
                    f"Profile creation attempt {retry_count} failed",
                    extra={
                        "user_id": form_data.get('discord_user_id', 'unknown'),
                        "context": {
                            "action": "profile_creation",
                            "retry": retry_count,
                            "error": str(e)
                        }
                    }
                )
                
                if retry_count >= max_retries:
                    logger.error(
                        "Profile creation failed after max retries",
                        extra={
                            "user_id": form_data.get('discord_user_id', 'unknown'),
                            "context": {
                                "action": "profile_creation",
                                "status": "failed",
                                "retries": max_retries
                            }
                        }
                    )
                    raise
                
                await asyncio.sleep(1)  # Brief delay before retry
    
    async def send_welcome_message(self, user_id: str) -> bool:
        """
        Send welcome message to user (placeholder for Discord integration)
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Success status
        """
        try:
            # This will be implemented when Discord bot is integrated
            # For now, just log the action
            logger.info(
                "Welcome message sent",
                extra={
                    "user_id": user_id,
                    "context": {"action": "welcome_message", "status": "success"}
                }
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send welcome message",
                extra={
                    "user_id": user_id,
                    "context": {"action": "welcome_message", "error": str(e)}
                }
            )
            return False
    
    async def _check_existing_user(self, discord_user_id: str) -> Optional[Dict]:
        """Check if user already exists in database"""
        query = "SELECT id FROM client_profiles WHERE discord_user_id = $1"
        result = await self.db.fetchrow(query, discord_user_id)
        return dict(result) if result else None
    
    def _validate_timezone_format(self, timezone_offset: str) -> bool:
        """
        Validate timezone format (UTC±X)
        
        Args:
            timezone_offset: Timezone string to validate
            
        Returns:
            True if valid format
        """
        if not timezone_offset.startswith('UTC'):
            return False
        
        try:
            offset_part = timezone_offset[3:]  # Remove 'UTC'
            if offset_part.startswith('+') or offset_part.startswith('-'):
                offset_value = int(offset_part[1:])
                return -12 <= offset_value <= 14
        except (ValueError, IndexError):
            pass
        
        return False

# Global instance
onboarding_engine = OnboardingEngine() 