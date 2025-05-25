"""
The Regiment Engines Module
Contains all engine implementations for automated client management
"""

# TheRegiment - Engines Package
# Phase 3: Onboarding Engine
# Phase 4: Meal Delivery Engine

from .onboarding import OnboardingEngine
from .meal_delivery import MealCompiler, MealDeliveryRunner, MealPlanSelection

__all__ = [
    "OnboardingEngine",
    "MealCompiler", 
    "MealDeliveryRunner",
    "MealPlanSelection"
] 