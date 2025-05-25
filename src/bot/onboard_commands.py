"""
Discord Bot Onboarding Commands - Phase 3
Handles /onboard slash command and client registration form
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from src.engines.onboarding.engine import onboarding_engine
from src.core.logging.logger import setup_logger

logger = setup_logger("onboard_commands")

class OnboardingModal(discord.ui.Modal, title='Client Registration'):
    """Discord modal for client onboarding form"""
    
    def __init__(self):
        super().__init__()
    
    name = discord.ui.TextInput(
        label='Full Name',
        placeholder='Enter your full name...',
        required=True,
        max_length=100
    )
    
    email = discord.ui.TextInput(
        label='Email Address',
        placeholder='your.email@example.com',
        required=True,
        max_length=100
    )
    
    height_cm = discord.ui.TextInput(
        label='Height (cm)',
        placeholder='e.g., 175',
        required=True,
        max_length=3
    )
    
    weight_kg = discord.ui.TextInput(
        label='Weight (kg)',
        placeholder='e.g., 70.5',
        required=True,
        max_length=5
    )
    
    timezone_offset = discord.ui.TextInput(
        label='Timezone',
        placeholder='e.g., UTC+5, UTC-8',
        required=True,
        max_length=10
    )

class GoalSelectView(discord.ui.View):
    """View for goal selection after initial form submission"""
    
    def __init__(self, form_data: dict):
        super().__init__(timeout=300)  # 5 minute timeout
        self.form_data = form_data
        self.goal = None
    
    @discord.ui.select(
        placeholder="Select your primary goal...",
        options=[
            discord.SelectOption(label="Weight Loss", value="weight_loss", description="Lose body fat and get leaner"),
            discord.SelectOption(label="Muscle Gain", value="muscle_gain", description="Build muscle and strength"),
            discord.SelectOption(label="Body Recomposition", value="recomp", description="Lose fat while gaining muscle"),
            discord.SelectOption(label="Athletic Performance", value="performance", description="Improve sports performance"),
            discord.SelectOption(label="General Health", value="health", description="Overall health and wellness")
        ]
    )
    async def goal_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.goal = select.values[0]
        
        # Add goal to form data
        self.form_data['goal'] = self.goal
        
        # Process the complete onboarding
        await self.process_onboarding(interaction)
    
    async def process_onboarding(self, interaction: discord.Interaction):
        """Process the complete onboarding with all data"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Initialize onboarding engine
            await onboarding_engine.initialize()
            
            # Normalize Discord user ID to user_id for engine compatibility
            self.form_data['user_id'] = str(interaction.user.id)
            
            # Map Discord UI goal values to schema-compliant enum values
            goal_map = {
                "weight_loss": "cut",
                "muscle_gain": "bulk", 
                "recomp": "recomp",
                "performance": "recomp",  # Map performance to recomp
                "health": "recomp"       # Map general health to recomp
            }
            self.form_data["goal"] = goal_map.get(self.form_data["goal"], "recomp")  # default fallback
            
            # Create Discord interaction format
            discord_interaction = {
                'user': {'id': interaction.user.id},
                'data': self.form_data
            }
            
            # Collect and validate client data
            client_data = await onboarding_engine.collect_client_data(discord_interaction)
            
            # Create client profile
            client_id = await onboarding_engine.create_client_profile(client_data)
            
            # Send welcome message
            await onboarding_engine.send_welcome_message(str(interaction.user.id))
            
            # Calculate start date for display
            start_date = client_data['start_date']
            
            # Create success embed
            embed = discord.Embed(
                title="🎯 Welcome to The Regiment!",
                description="Your profile has been created successfully.",
                color=discord.Color.green()
            )
            embed.add_field(name="Client ID", value=client_id, inline=True)
            embed.add_field(name="Start Date", value=f"Next Tuesday ({start_date})", inline=True)
            embed.add_field(name="Goal", value=self.goal.replace('_', ' ').title(), inline=True)
            embed.add_field(
                name="What's Next?",
                value="• Your coach will finalize your profile in Battle Station\n• You'll receive your first meal plan on Friday\n• Training starts on your designated start date",
                inline=False
            )
            embed.set_footer(text="The Regiment - Military-Grade Fitness")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            logger.info(
                "Onboarding completed successfully",
                extra={
                    "user_id": str(interaction.user.id),
                    "context": {
                        "action": "onboarding_complete",
                        "client_id": client_id,
                        "status": "success"
                    }
                }
            )
            
        except ValueError as e:
            # Handle validation errors
            error_embed = discord.Embed(
                title="❌ Registration Error",
                description=f"There was an issue with your registration: {str(e)}",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="What to do?",
                value="Please try the `/onboard` command again with correct information.",
                inline=False
            )
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            
            logger.warning(
                "Onboarding validation error",
                extra={
                    "user_id": str(interaction.user.id),
                    "context": {"action": "onboarding_validation", "error": str(e)}
                }
            )
            
        except Exception as e:
            # Handle unexpected errors
            error_embed = discord.Embed(
                title="⚠️ System Error",
                description="An unexpected error occurred during registration. Please try again later.",
                color=discord.Color.orange()
            )
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            
            logger.error(
                "Onboarding system error",
                extra={
                    "user_id": str(interaction.user.id),
                    "context": {"action": "onboarding_error", "error": str(e)}
                }
            )

class OnboardingCommands(commands.Cog):
    """Cog for onboarding-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="onboard", description="Register as a new client with The Regiment")
    async def onboard(self, interaction: discord.Interaction):
        """
        /onboard slash command - Client registration form
        Rate limited to 1 onboard per user lifetime
        """
        try:
            # Check if user already exists
            await onboarding_engine.initialize()
            existing_user = await onboarding_engine._check_existing_user(str(interaction.user.id))
            
            if existing_user:
                embed = discord.Embed(
                    title="⚠️ Already Registered",
                    description="You are already registered with The Regiment.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Need Help?",
                    value="Contact your coach if you need to update your profile.",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                logger.info(
                    "Duplicate onboarding attempt",
                    extra={
                        "user_id": str(interaction.user.id),
                        "context": {"action": "duplicate_onboard"}
                    }
                )
                return
            
            # Show onboarding modal
            modal = OnboardingModal()
            await interaction.response.send_modal(modal)
            
            # Wait for modal submission
            await modal.wait()
            
            if modal.name.value and modal.email.value and modal.height_cm.value and modal.weight_kg.value and modal.timezone_offset.value:
                # Validate basic input formats
                try:
                    height = float(modal.height_cm.value)
                    weight = float(modal.weight_kg.value)
                    
                    if not (120 <= height <= 250):
                        raise ValueError("Height must be between 120-250 cm")
                    
                    if not (30 <= weight <= 300):
                        raise ValueError("Weight must be between 30-300 kg")
                    
                    if '@' not in modal.email.value or '.' not in modal.email.value:
                        raise ValueError("Invalid email format")
                    
                    # Prepare form data
                    form_data = {
                        'name': modal.name.value,
                        'email': modal.email.value,
                        'height_cm': modal.height_cm.value,
                        'weight_kg': modal.weight_kg.value,
                        'timezone_offset': modal.timezone_offset.value
                    }
                    
                    # Show goal selection
                    view = GoalSelectView(form_data)
                    
                    embed = discord.Embed(
                        title="🎯 Select Your Goal",
                        description="Please select your primary fitness goal to complete registration.",
                        color=discord.Color.blue()
                    )
                    
                    # Send goal selection as followup (since modal already responded)
                    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                    
                except ValueError as e:
                    error_embed = discord.Embed(
                        title="❌ Invalid Input",
                        description=f"Please check your input: {str(e)}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(
                "Onboard command error",
                extra={
                    "user_id": str(interaction.user.id),
                    "context": {"action": "onboard_command", "error": str(e)}
                }
            )
            
            if not interaction.response.is_done():
                error_embed = discord.Embed(
                    title="⚠️ System Error",
                    description="An error occurred. Please try again later.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=error_embed, ephemeral=True)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(OnboardingCommands(bot)) 