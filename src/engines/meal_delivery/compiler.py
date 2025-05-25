# TheRegiment - Meal Compiler Engine
# Phase 4: Weekly meal plan compilation and shopping list generation

import json
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.core.logging.logger import setup_logger
from src.core.database import get_database_connection
from src.schemas.models import (
    ClientProfileSchema, 
    MealTemplateSchema, 
    MacrosSchema,
    MealDaySchema,
    ShoppingListSchema,
    IngredientSchema
)

logger = setup_logger(__name__)


class MealCompiler:
    """
    Meal Compiler Engine - Compiles weekly meal plans and generates shopping lists.
    
    Triggered weekly (Friday post-selection) to compile meal plans for the upcoming week.
    Handles macro calculation, portion scaling, and shopping list generation.
    """
    
    def __init__(self):
        self.meal_templates_path = Path("data/meal_templates")
        self.compiled_plans_path = Path("data/compiled_plans")
        self.compiled_plans_path.mkdir(parents=True, exist_ok=True)
    
    async def compile_weekly_plan(self, client_id: str, template_id: str, macros: MacrosSchema) -> Dict[str, Any]:
        """
        Compile a weekly meal plan for a client based on template and macro targets.
        
        Args:
            client_id: Discord user ID
            template_id: Meal template ID (template_a, template_b, etc.)
            macros: Client's macro targets
            
        Returns:
            Dict containing compiled weekly meal plan
        """
        try:
            logger.info(f"Compiling weekly plan for client {client_id} with template {template_id}")
            
            # Load meal template
            template = await self._load_meal_template(template_id)
            if not template:
                logger.warning(f"Template {template_id} not found, falling back to template_a")
                template = await self._load_meal_template("template_a")
                if not template:
                    raise Exception("Default template_a not found")
            
            # Calculate portions for each day
            compiled_days = []
            for day in template.days:
                compiled_day = await self._compile_day_meals(day, macros)
                compiled_days.append(compiled_day)
            
            # Generate shopping list
            shopping_list = await self._generate_shopping_list(template.shopping_list, macros)
            
            compiled_plan = {
                "client_id": client_id,
                "template_id": template_id,
                "compiled_at": datetime.utcnow().isoformat(),
                "macros": {
                    "protein": macros.protein,
                    "carbs": macros.carbs,
                    "fats": macros.fats
                },
                "days": compiled_days,
                "shopping_list": shopping_list
            }
            
            # Save compiled plan
            await self._save_compiled_plan(client_id, compiled_plan)
            
            logger.info(f"Successfully compiled weekly plan for client {client_id}")
            return compiled_plan
            
        except Exception as e:
            logger.error(f"Failed to compile weekly plan for client {client_id}: {str(e)}")
            # Fallback to default plan
            return await self._generate_fallback_plan(client_id, macros)
    
    async def calculate_portions(self, macro_targets: MacrosSchema, template_foods: List[Dict]) -> List[Dict]:
        """
        Calculate food portions to meet macro targets.
        
        Args:
            macro_targets: Target macros for the client
            template_foods: List of foods from template
            
        Returns:
            List of foods with calculated portions
        """
        try:
            # This is a simplified calculation - in production would use more sophisticated macro balancing
            total_protein_target = macro_targets.protein
            total_carbs_target = macro_targets.carbs
            total_fats_target = macro_targets.fats
            
            calculated_foods = []
            for food in template_foods:
                # Scale portions based on macro ratios
                # This is placeholder logic - real implementation would use food database
                scaled_grams = food.get("raw_grams", 100)
                
                calculated_foods.append({
                    "food": food["food"],
                    "grams": scaled_grams,
                    "protein": scaled_grams * 0.2,  # Placeholder macro values
                    "carbs": scaled_grams * 0.1,
                    "fats": scaled_grams * 0.05
                })
            
            return calculated_foods
            
        except Exception as e:
            logger.error(f"Failed to calculate portions: {str(e)}")
            return template_foods
    
    async def generate_shopping_list(self, weekly_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate shopping list from compiled weekly plan.
        
        Args:
            weekly_plan: Compiled weekly meal plan
            
        Returns:
            Shopping list with ingredients and instructions
        """
        try:
            ingredient_totals = {}
            
            # Aggregate ingredients across all days
            for day in weekly_plan.get("days", []):
                for meal in day.get("meals", []):
                    for item in meal.get("items", []):
                        food = item["food"]
                        grams = item["grams"]
                        
                        if food in ingredient_totals:
                            ingredient_totals[food] += grams
                        else:
                            ingredient_totals[food] = grams
            
            # Convert to shopping list format
            ingredients = [
                {"food": food, "grams": grams}
                for food, grams in ingredient_totals.items()
            ]
            
            shopping_list = {
                "ingredients": ingredients,
                "instructions": "🔪 Prep all proteins in advance. Store in labeled containers. Follow portion guidelines strictly."
            }
            
            logger.info(f"Generated shopping list with {len(ingredients)} ingredients")
            return shopping_list
            
        except Exception as e:
            logger.error(f"Failed to generate shopping list: {str(e)}")
            return {"ingredients": [], "instructions": "Contact coach for shopping list."}
    
    async def _load_meal_template(self, template_id: str) -> Optional[MealTemplateSchema]:
        """Load meal template from file system."""
        try:
            template_file = self.meal_templates_path / f"{template_id}.json"
            if not template_file.exists():
                return None
            
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            return MealTemplateSchema(**template_data)
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {str(e)}")
            return None
    
    async def _compile_day_meals(self, day: MealDaySchema, macros: MacrosSchema) -> Dict[str, Any]:
        """Compile meals for a single day."""
        compiled_meals = []
        
        for meal in day.meals:
            # Calculate portions for this meal
            calculated_items = await self.calculate_portions(macros, [
                {"food": item.food, "raw_grams": item.raw_grams} 
                for item in meal.items
            ])
            
            compiled_meal = {
                "meal_id": meal.meal_id,
                "items": calculated_items
            }
            compiled_meals.append(compiled_meal)
        
        return {
            "day_index": day.day_index,
            "meals": compiled_meals
        }
    
    async def _generate_shopping_list(self, template_shopping_list: ShoppingListSchema, macros: MacrosSchema) -> Dict[str, Any]:
        """Generate shopping list from template."""
        # Scale shopping list based on macros
        scaled_ingredients = []
        
        for ingredient in template_shopping_list.ingredients:
            # Scale ingredient amounts based on macro targets
            # This is simplified - real implementation would use macro ratios
            scale_factor = 1.0  # Placeholder
            
            scaled_ingredients.append({
                "food": ingredient.food,
                "grams": int(ingredient.grams * scale_factor)
            })
        
        return {
            "ingredients": scaled_ingredients,
            "instructions": template_shopping_list.instructions
        }
    
    async def _save_compiled_plan(self, client_id: str, compiled_plan: Dict[str, Any]) -> None:
        """Save compiled plan to file system."""
        try:
            plan_file = self.compiled_plans_path / f"{client_id}_current.json"
            with open(plan_file, 'w') as f:
                json.dump(compiled_plan, f, indent=2)
            
            logger.info(f"Saved compiled plan for client {client_id}")
            
        except Exception as e:
            logger.error(f"Failed to save compiled plan for client {client_id}: {str(e)}")
    
    async def _generate_fallback_plan(self, client_id: str, macros: MacrosSchema) -> Dict[str, Any]:
        """Generate fallback plan when compilation fails."""
        logger.warning(f"Generating fallback plan for client {client_id}")
        
        # Create basic fallback plan
        fallback_plan = {
            "client_id": client_id,
            "template_id": "template_a",
            "compiled_at": datetime.utcnow().isoformat(),
            "macros": {
                "protein": macros.protein,
                "carbs": macros.carbs,
                "fats": macros.fats
            },
            "days": [],
            "shopping_list": {
                "ingredients": [
                    {"food": "chicken_breast", "grams": 1750},
                    {"food": "rice", "grams": 1200},
                    {"food": "broccoli", "grams": 700}
                ],
                "instructions": "Basic fallback plan. Contact coach for proper meal plan."
            }
        }
        
        return fallback_plan
    
    async def get_compiled_plan(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve compiled plan for a client."""
        try:
            plan_file = self.compiled_plans_path / f"{client_id}_current.json"
            if not plan_file.exists():
                return None
            
            with open(plan_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load compiled plan for client {client_id}: {str(e)}")
            return None 