# TheRegiment - Meal Plan Selection Engine
# Phase 4: Weekly meal plan selection and deadline management

import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any

from src.core.logging.logger import setup_logger
from src.core.database import get_database_connection
from src.core.utils import timezone_calculator, retry_logic
from src.schemas.models import ClientProfileSchema, MacrosSchema
from .compiler import MealCompiler

logger = setup_logger(__name__)


class MealPlanSelection:
    """
    Meal Plan Selection Engine - Handles weekly meal plan selection.
    
    Triggered Friday 21:00 client time to prompt plan selection.
    Manages deadline enforcement and fallback to template_a.
    """
    
    def __init__(self):
        self.compiler = MealCompiler()
        self.available_plans = ["template_a", "template_b", "template_c", "template_d"]
    
    async def send_plan_selection_prompt(self, client_id: str) -> bool:
        """
        Send plan selection prompt to client via Discord.
        
        Args:
            client_id: Discord user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Sending plan selection prompt to client {client_id}")
            
            # Format selection message
            message = await self._format_selection_message()
            
            # Send via Discord with plan buttons
            success = await self._send_selection_message(client_id, message)
            
            if success:
                logger.info(f"Successfully sent plan selection to client {client_id}")
                return True
            else:
                logger.error(f"Failed to send plan selection to client {client_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending plan selection to client {client_id}: {str(e)}")
            return False
    
    async def handle_plan_choice(self, interaction: Dict[str, Any], plan_id: str) -> None:
        """
        Handle plan selection from Discord interaction.
        
        Args:
            interaction: Discord interaction data
            plan_id: Selected plan ID (template_a, template_b, etc.)
        """
        try:
            user_id = interaction.get("user_id")
            
            if not user_id:
                logger.error("Invalid interaction data for plan choice")
                return
            
            if plan_id not in self.available_plans:
                logger.error(f"Invalid plan selection: {plan_id}")
                await self._send_invalid_plan_message(user_id)
                return
            
            # Update client profile with selected plan
            await self._update_client_meal_template(user_id, plan_id)
            
            # Get client profile for compilation
            client = await self._get_client_profile(user_id)
            if not client:
                logger.error(f"Client profile not found for {user_id}")
                return
            
            # Compile new meal plan
            macros = MacrosSchema(
                protein=client["macros"]["protein"],
                carbs=client["macros"]["carbs"],
                fats=client["macros"]["fats"]
            )
            
            await self.compiler.compile_weekly_plan(user_id, plan_id, macros)
            
            # Send confirmation
            await self._send_plan_confirmation(user_id, plan_id)
            
            logger.info(f"Plan selection completed for user {user_id}: {plan_id}")
            
        except Exception as e:
            logger.error(f"Error handling plan choice: {str(e)}")
    
    async def apply_default_plan_if_missed(self, client_id: str) -> None:
        """
        Apply default plan (template_a) if no selection made by deadline.
        
        Args:
            client_id: Discord user ID
        """
        try:
            logger.info(f"Checking for missed plan selection: {client_id}")
            
            # Check if client made a selection this week
            selection_made = await self._check_recent_plan_selection(client_id)
            
            if not selection_made:
                logger.info(f"No plan selection found, applying default for {client_id}")
                
                # Apply template_a as default
                await self._update_client_meal_template(client_id, "template_a")
                
                # Get client profile for compilation
                client = await self._get_client_profile(client_id)
                if client:
                    macros = MacrosSchema(
                        protein=client["macros"]["protein"],
                        carbs=client["macros"]["carbs"],
                        fats=client["macros"]["fats"]
                    )
                    
                    await self.compiler.compile_weekly_plan(client_id, "template_a", macros)
                    
                    # Send default plan notification
                    await self._send_default_plan_notification(client_id)
                
                logger.info(f"Applied default plan for client {client_id}")
            
        except Exception as e:
            logger.error(f"Error applying default plan for {client_id}: {str(e)}")
    
    async def run_friday_selection_check(self) -> None:
        """
        Main method called by scheduler on Friday 21:00 to send plan selections.
        
        Checks all active clients and sends plan selection prompts.
        """
        try:
            logger.info("Starting Friday plan selection check")
            
            # Get all active clients
            active_clients = await self._get_active_clients()
            
            for client in active_clients:
                await self._process_client_selection(client)
            
            logger.info("Completed Friday plan selection check")
            
        except Exception as e:
            logger.error(f"Error in Friday selection check: {str(e)}")
    
    async def run_deadline_enforcement(self) -> None:
        """
        Enforce plan selection deadline and apply defaults where needed.
        
        Called after the Friday 21:00 deadline has passed.
        """
        try:
            logger.info("Starting plan selection deadline enforcement")
            
            # Get all active clients
            active_clients = await self._get_active_clients()
            
            for client in active_clients:
                client_id = client["user_id"]
                await self.apply_default_plan_if_missed(client_id)
            
            logger.info("Completed deadline enforcement")
            
        except Exception as e:
            logger.error(f"Error in deadline enforcement: {str(e)}")
    
    async def _process_client_selection(self, client: Dict[str, Any]) -> None:
        """Process plan selection for a single client."""
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
            
            # Check if it's selection time (Friday 21:00)
            if not await self._is_selection_time(timezone_offset):
                return
            
            # Send plan selection prompt
            success = await retry_logic(
                lambda: self.send_plan_selection_prompt(client_id),
                max_retries=3
            )
            
            if not success:
                logger.error(f"Failed to send plan selection to {client_id}")
            
        except Exception as e:
            logger.error(f"Error processing client selection for {client.get('user_id', 'unknown')}: {str(e)}")
    
    async def _get_active_clients(self) -> List[Dict[str, Any]]:
        """Get all active clients from database."""
        try:
            async with get_database_connection() as conn:
                query = """
                    SELECT user_id, timezone_offset, paused, start_date, meal_template_id, macros
                    FROM client_profiles 
                    WHERE paused = false OR paused IS NULL
                """
                rows = await conn.fetch(query)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get active clients: {str(e)}")
            return []
    
    async def _is_selection_time(self, timezone_offset: str) -> bool:
        """Check if it's Friday 21:00 in client's timezone."""
        try:
            utc_now = datetime.utcnow()
            client_time = timezone_calculator(timezone_offset, utc_now)
            
            # Check if it's Friday (weekday 4) and 21:00
            return client_time.weekday() == 4 and client_time.hour == 21
            
        except Exception as e:
            logger.error(f"Failed to check selection time: {str(e)}")
            return False
    
    async def _format_selection_message(self) -> str:
        """Format plan selection message for Discord."""
        try:
            message_lines = [
                "🎯 **WEEKLY PLAN SELECTION**",
                f"📅 Week of {(date.today() + timedelta(days=1)).strftime('%B %d')}",
                "",
                "**Choose your battle plan for next week:**",
                "",
                "🥩 **Plan A** - High Protein Focus",
                "🍚 **Plan B** - Balanced Macros", 
                "🥑 **Plan C** - Higher Fats",
                "💪 **Plan D** - Performance Focus",
                "",
                "⏰ **Deadline: Tonight 21:00**",
                "❌ No selection = Plan A assigned",
                "",
                "🎯 **Choose wisely. No changes after deadline.**"
            ]
            
            return "\n".join(message_lines)
            
        except Exception as e:
            logger.error(f"Failed to format selection message: {str(e)}")
            return "🎯 **WEEKLY PLAN SELECTION**\nError loading plan options. Contact coach."
    
    async def _send_selection_message(self, client_id: str, message: str) -> bool:
        """Send selection message via Discord with plan buttons."""
        try:
            # This is a placeholder - actual Discord integration would be implemented here
            # The message would include A/B/C/D buttons for plan selection
            
            logger.info(f"Plan selection message sent to {client_id}: {len(message)} chars")
            
            # For now, simulate successful delivery
            return True
            
        except Exception as e:
            logger.error(f"Failed to send selection message to {client_id}: {str(e)}")
            return False
    
    async def _send_invalid_plan_message(self, user_id: str) -> None:
        """Send invalid plan selection message."""
        try:
            message = "❌ Invalid plan selection. Please choose A, B, C, or D."
            # Send via Discord
            logger.info(f"Sent invalid plan message to {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send invalid plan message: {str(e)}")
    
    async def _send_plan_confirmation(self, user_id: str, plan_id: str) -> None:
        """Send plan selection confirmation."""
        try:
            plan_name = plan_id.replace("template_", "Plan ").upper()
            message = f"✅ **{plan_name} SELECTED**\n\nYour meal plan is locked in. Shopping list drops Saturday 06:00."
            
            # Send via Discord
            logger.info(f"Sent plan confirmation to {user_id}: {plan_id}")
            
        except Exception as e:
            logger.error(f"Failed to send plan confirmation: {str(e)}")
    
    async def _send_default_plan_notification(self, client_id: str) -> None:
        """Send default plan assignment notification."""
        try:
            message = (
                "⚠️ **PLAN A ASSIGNED**\n\n"
                "No selection received by deadline.\n"
                "Plan A has been automatically assigned.\n\n"
                "Shopping list drops Saturday 06:00."
            )
            
            # Send via Discord
            logger.info(f"Sent default plan notification to {client_id}")
            
        except Exception as e:
            logger.error(f"Failed to send default plan notification: {str(e)}")
    
    async def _update_client_meal_template(self, user_id: str, template_id: str) -> None:
        """Update client's meal template in database."""
        try:
            async with get_database_connection() as conn:
                query = """
                    UPDATE client_profiles 
                    SET meal_template_id = $1, cycle_start_date = $2
                    WHERE user_id = $3
                """
                # Set cycle start to next Saturday
                next_saturday = date.today() + timedelta(days=(5 - date.today().weekday()) % 7)
                
                await conn.execute(query, template_id, next_saturday, user_id)
            
            logger.info(f"Updated meal template for {user_id}: {template_id}")
            
        except Exception as e:
            logger.error(f"Failed to update meal template for {user_id}: {str(e)}")
    
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
    
    async def _check_recent_plan_selection(self, client_id: str) -> bool:
        """Check if client made a plan selection this week."""
        try:
            # Check if cycle_start_date was updated this week
            async with get_database_connection() as conn:
                query = """
                    SELECT cycle_start_date FROM client_profiles 
                    WHERE user_id = $1
                """
                row = await conn.fetchrow(query, client_id)
                
                if not row:
                    return False
                
                cycle_start = row["cycle_start_date"]
                today = date.today()
                
                # Check if cycle start is within the next 7 days (indicating recent selection)
                return cycle_start >= today and cycle_start <= today + timedelta(days=7)
                
        except Exception as e:
            logger.error(f"Failed to check recent plan selection for {client_id}: {str(e)}")
            return False 