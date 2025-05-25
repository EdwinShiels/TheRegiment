# TheRegiment - Meal Delivery Runner
# Phase 4: Daily meal protocol delivery and logging

import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz

from src.core.logging.logger import setup_logger
from src.core.database import get_database_connection
from src.core.utils import timezone_calculator, retry_logic
from src.schemas.models import (
    ClientProfileSchema, 
    MealLogSchema, 
    StatusEnum
)
from .compiler import MealCompiler

logger = setup_logger(__name__)


class MealDeliveryRunner:
    """
    Meal Delivery Runner - Handles daily meal protocol delivery and logging.
    
    Triggered by APScheduler hourly to check for 06:00 client local time.
    Delivers daily meal protocols, handles button interactions, and auto-logs missed meals.
    """
    
    def __init__(self):
        self.compiler = MealCompiler()
    
    async def check_delivery_time(self, client_timezone: str) -> bool:
        """
        Check if it's 06:00 in the client's timezone.
        
        Args:
            client_timezone: Client's timezone offset (e.g., "UTC+2")
            
        Returns:
            True if it's 06:00 client time, False otherwise
        """
        try:
            utc_now = datetime.utcnow()
            client_time = timezone_calculator(client_timezone, utc_now)
            
            # Check if it's 06:00 (within 1 hour window for safety)
            return client_time.hour == 6
            
        except Exception as e:
            logger.error(f"Failed to check delivery time for timezone {client_timezone}: {str(e)}")
            return False
    
    async def send_daily_meal_protocol(self, client_id: str, day_meals: List[Dict[str, Any]]) -> bool:
        """
        Send daily meal protocol to client via Discord.
        
        Args:
            client_id: Discord user ID
            day_meals: List of meals for the day
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Sending daily meal protocol to client {client_id}")
            
            # Format meal message
            message = await self._format_meal_message(day_meals)
            
            # Send via Discord (placeholder - actual Discord integration needed)
            success = await self._send_discord_message(client_id, message, day_meals)
            
            if success:
                logger.info(f"Successfully sent meal protocol to client {client_id}")
                return True
            else:
                logger.error(f"Failed to send meal protocol to client {client_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending meal protocol to client {client_id}: {str(e)}")
            return False
    
    async def handle_meal_button_response(self, interaction: Dict[str, Any]) -> None:
        """
        Handle ✅/❌ button responses from Discord.
        
        Args:
            interaction: Discord interaction data
        """
        try:
            user_id = interaction.get("user_id")
            meal_id = interaction.get("meal_id")
            status = interaction.get("status")  # "completed" or "missed"
            
            if not all([user_id, meal_id, status]):
                logger.error("Invalid interaction data for meal button response")
                return
            
            # Log meal response to database
            await self._log_meal_response(user_id, meal_id, status)
            
            logger.info(f"Logged meal response for user {user_id}, meal {meal_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error handling meal button response: {str(e)}")
    
    async def auto_log_missed_meals(self) -> None:
        """
        Auto-log missed meals for clients who haven't responded by 22:00 local time.
        
        Triggered by scheduler at 22:00 local time for each client.
        """
        try:
            logger.info("Starting auto-log missed meals process")
            
            # Get all active clients
            active_clients = await self._get_active_clients()
            
            for client in active_clients:
                client_id = client["user_id"]
                timezone_offset = client["timezone_offset"]
                
                # Check if it's 22:00 in client's timezone
                if await self._is_missed_meal_time(timezone_offset):
                    await self._check_and_log_missed_meals(client_id)
            
            logger.info("Completed auto-log missed meals process")
            
        except Exception as e:
            logger.error(f"Error in auto-log missed meals: {str(e)}")
    
    async def run_daily_delivery_check(self) -> None:
        """
        Main method called by scheduler to check for meal deliveries.
        
        Checks all active clients and delivers meals if it's 06:00 their time.
        """
        try:
            logger.info("Starting daily meal delivery check")
            
            # Get all active clients
            active_clients = await self._get_active_clients()
            
            for client in active_clients:
                await self._process_client_delivery(client)
            
            logger.info("Completed daily meal delivery check")
            
        except Exception as e:
            logger.error(f"Error in daily delivery check: {str(e)}")
    
    async def _process_client_delivery(self, client: Dict[str, Any]) -> None:
        """Process meal delivery for a single client."""
        try:
            client_id = client["user_id"]
            timezone_offset = client["timezone_offset"]
            paused = client.get("paused", False)
            start_date = client.get("start_date")
            
            # Skip if client is paused
            if paused:
                logger.debug(f"Skipping paused client {client_id}")
                return
            
            # Skip if client hasn't started yet
            if start_date and start_date > date.today():
                logger.debug(f"Skipping client {client_id} - start date in future")
                return
            
            # Check if it's delivery time
            if not await self.check_delivery_time(timezone_offset):
                return
            
            # Get compiled meal plan
            compiled_plan = await self.compiler.get_compiled_plan(client_id)
            if not compiled_plan:
                logger.warning(f"No compiled plan found for client {client_id}")
                await self._log_missed_delivery(client_id, "no_plan")
                return
            
            # Get today's meals
            today_meals = await self._get_today_meals(compiled_plan)
            if not today_meals:
                logger.warning(f"No meals found for today for client {client_id}")
                await self._log_missed_delivery(client_id, "no_meals")
                return
            
            # Send meal protocol
            success = await retry_logic(
                lambda: self.send_daily_meal_protocol(client_id, today_meals),
                max_retries=3
            )
            
            if not success:
                await self._log_missed_delivery(client_id, "delivery_failed")
            
        except Exception as e:
            logger.error(f"Error processing client delivery for {client.get('user_id', 'unknown')}: {str(e)}")
    
    async def _get_active_clients(self) -> List[Dict[str, Any]]:
        """Get all active clients from database."""
        try:
            async with get_database_connection() as conn:
                query = """
                    SELECT user_id, timezone_offset, paused, start_date, meal_template_id
                    FROM client_profiles 
                    WHERE paused = false OR paused IS NULL
                """
                rows = await conn.fetch(query)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get active clients: {str(e)}")
            return []
    
    async def _get_today_meals(self, compiled_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get today's meals from compiled plan."""
        try:
            # Calculate current day index in the 7-day cycle
            cycle_start = datetime.fromisoformat(compiled_plan["compiled_at"]).date()
            today = date.today()
            days_since_start = (today - cycle_start).days
            day_index = days_since_start % 7
            
            # Find today's meals
            for day in compiled_plan.get("days", []):
                if day["day_index"] == day_index:
                    return day["meals"]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get today's meals: {str(e)}")
            return []
    
    async def _format_meal_message(self, day_meals: List[Dict[str, Any]]) -> str:
        """Format meal protocol message for Discord."""
        try:
            message_lines = [
                "🍽️ **DAILY FUEL DROP**",
                f"📅 {date.today().strftime('%A, %B %d')}",
                "",
                "**Today's Mission:**"
            ]
            
            for i, meal in enumerate(day_meals, 1):
                meal_lines = [f"\n**M{i}:**"]
                
                for item in meal.get("items", []):
                    food = item["food"].replace("_", " ").title()
                    grams = item["grams"]
                    meal_lines.append(f"• {grams}g {food}")
                
                message_lines.extend(meal_lines)
            
            message_lines.extend([
                "",
                "✅ = Completed | ❌ = Missed",
                "🎯 **Discipline is non-negotiable.**"
            ])
            
            return "\n".join(message_lines)
            
        except Exception as e:
            logger.error(f"Failed to format meal message: {str(e)}")
            return "🍽️ **DAILY FUEL DROP**\nError loading meal plan. Contact coach."
    
    async def _send_discord_message(self, client_id: str, message: str, day_meals: List[Dict[str, Any]]) -> bool:
        """Send message via Discord with meal buttons."""
        try:
            # This is a placeholder - actual Discord integration would be implemented here
            # The message would include ✅/❌ buttons for each meal
            
            logger.info(f"Discord message sent to {client_id}: {len(message)} chars, {len(day_meals)} meals")
            
            # For now, simulate successful delivery
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord message to {client_id}: {str(e)}")
            return False
    
    async def _log_meal_response(self, user_id: str, meal_id: str, status: str) -> None:
        """Log meal response to database."""
        try:
            # Get client timezone for proper logging
            client = await self._get_client_profile(user_id)
            if not client:
                logger.error(f"Client profile not found for user {user_id}")
                return
            
            timezone_offset = client["timezone_offset"]
            
            # Create meal log entry
            meal_log = MealLogSchema(
                user_id=user_id,
                meal_id=meal_id,
                date=date.today(),
                logged_at=datetime.now(pytz.UTC),
                timezone_offset=timezone_offset,
                status=StatusEnum(status)
            )
            
            # Insert into database
            async with get_database_connection() as conn:
                query = """
                    INSERT INTO meal_logs (user_id, meal_id, date, logged_at, timezone_offset, status)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """
                await conn.execute(
                    query,
                    meal_log.user_id,
                    meal_log.meal_id,
                    meal_log.date,
                    meal_log.logged_at,
                    meal_log.timezone_offset,
                    meal_log.status.value
                )
            
            logger.info(f"Logged meal response: {user_id} - {meal_id} - {status}")
            
        except Exception as e:
            logger.error(f"Failed to log meal response: {str(e)}")
    
    async def _is_missed_meal_time(self, timezone_offset: str) -> bool:
        """Check if it's 22:00 in client's timezone."""
        try:
            utc_now = datetime.utcnow()
            client_time = timezone_calculator(timezone_offset, utc_now)
            return client_time.hour == 22
            
        except Exception as e:
            logger.error(f"Failed to check missed meal time: {str(e)}")
            return False
    
    async def _check_and_log_missed_meals(self, client_id: str) -> None:
        """Check for and log missed meals for a client."""
        try:
            # Get today's meals that haven't been logged
            today = date.today()
            
            async with get_database_connection() as conn:
                # Get meals that should have been logged today
                compiled_plan = await self.compiler.get_compiled_plan(client_id)
                if not compiled_plan:
                    return
                
                today_meals = await self._get_today_meals(compiled_plan)
                
                for meal in today_meals:
                    meal_id = meal["meal_id"]
                    
                    # Check if meal was already logged
                    query = """
                        SELECT COUNT(*) FROM meal_logs 
                        WHERE user_id = $1 AND meal_id = $2 AND date = $3
                    """
                    count = await conn.fetchval(query, client_id, meal_id, today)
                    
                    if count == 0:
                        # Log as missed
                        await self._log_meal_response(client_id, meal_id, "missed")
                        logger.info(f"Auto-logged missed meal: {client_id} - {meal_id}")
            
        except Exception as e:
            logger.error(f"Failed to check and log missed meals for {client_id}: {str(e)}")
    
    async def _get_client_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client profile from database."""
        try:
            async with get_database_connection() as conn:
                query = "SELECT * FROM client_profiles WHERE user_id = $1"
                row = await conn.fetchrow(query, user_id)
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Failed to get client profile for {user_id}: {str(e)}")
            return None
    
    async def _log_missed_delivery(self, client_id: str, reason: str) -> None:
        """Log missed delivery for escalation."""
        try:
            logger.warning(f"Missed delivery for client {client_id}: {reason}")
            
            # This would typically create a job card or alert
            # For now, just log the issue
            
        except Exception as e:
            logger.error(f"Failed to log missed delivery: {str(e)}") 