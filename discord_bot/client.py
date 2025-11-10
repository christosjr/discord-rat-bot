"""
Discord Bot Client
================
Main Discord client setup and event handling.
"""

import asyncio
import logging
import os
import signal
from typing import Optional

import discord
from discord.ext import commands, tasks

from config.bot_config import BOT_CONFIG
from src.database import db_manager
from src.catch_system import wild_rat_manager
from discord_bot.commands import register_commands

logger = logging.getLogger(__name__)

class RatBotClient(commands.Bot):
    """Main Discord bot client"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        
        super().__init__(
            command_prefix=BOT_CONFIG['command_prefix'],
            intents=intents,
            case_insensitive=True,
            help_command=None
        )
        
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def setup_hook(self):
        """Setup the bot when it starts"""
        logger.info("Setting up Discord bot...")
        
        # Connect to database
        await db_manager.connect()
        
        # Set bot reference in wild_rat_manager
        wild_rat_manager.bot = self
        
        # Register commands
        await register_commands(self)
        
        # Start background tasks
        if not self.rat_spawning_task.is_running():
            self.rat_spawning_task.start()
        
        logger.info("Bot setup completed")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot is ready! Logged in as {self.user} (ID: {self.user.id})")
        
        # Set bot activity
        activity = discord.Activity(
            name=BOT_CONFIG['activity_name'],
            type=BOT_CONFIG['activity_type']
        )
        await self.change_presence(activity=activity)
        
        # Start rat spawning
        await wild_rat_manager.start_spawning()
        
        self.running = True
        logger.info("Bot is now online and running!")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Check for mention commands
        if self.user in message.mentions and len(message.mentions) == 1:
            if message.content.strip() == f"<@{self.user.id}>":
                # Bot was mentioned alone, show help
                help_text = """
🐭 **Discord Rat Bot** 🐭

**Quick Start:**
• `!create` - Create your character
• `!catch` - Catch wild rats
• `!stats` - View your character
• `!inventory` - See your items
• `!dungeon` - Enter a dungeon

**Need help?** Use `!help` for all commands!
                """
                await message.channel.send(help_text)
                return
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Use `!help [command]` for usage.")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument! Check your input and try again.")
            return
        
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command!")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command on cooldown! Try again in {error.retry_after:.1f} seconds.")
            return
        
        # Log unexpected errors
        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while executing this command.")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new server"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Create default settings for the guild
        await db_manager.execute("""
            INSERT OR IGNORE INTO game_settings (guild_id, rat_spawn_interval_minutes, trader_spawn_chance_percent, enabled)
            VALUES (?, ?, ?, ?)
        """, (str(guild.id), 15, 15, True))
        
        # Send welcome message
        try:
            system_channel = guild.system_channel
            if system_channel:
                welcome_message = f"""
🐭 **Welcome to {guild.name}!** 🐭

I'm the Discord Rat Bot! I'm here to bring you an exciting rat-catching adventure.

**Quick Start:**
• `!create` - Create your character and get started
• `!help` - See all available commands
• `!stats` - View your character information

Enjoy catching rats and exploring dungeons! 🎮
                """
                await system_channel.send(welcome_message)
        except Exception as e:
            logger.error(f"Failed to send welcome message to {guild.name}: {e}")
    
    async def close(self):
        """Close the bot gracefully"""
        logger.info("Shutting down bot...")
        
        # Stop background tasks
        if self.rat_spawning_task.is_running():
            self.rat_spawning_task.cancel()
        
        # Stop rat spawning
        await wild_rat_manager.stop_spawning()
        
        # Disconnect from database
        await db_manager.disconnect()
        
        # Call parent close
        await super().close()
        
        self.running = False
        self.shutdown_event.set()
    
    @tasks.loop(minutes=1)
    async def rat_spawning_task(self):
        """Background task for rat spawning"""
        try:
            # This task manages global rat spawning across all channels
            # In a more advanced implementation, you might want to track
            # per-channel timing and spawn rates
            
            logger.debug("Rat spawning task running...")
            
        except Exception as e:
            logger.error(f"Error in rat spawning task: {e}")

# Global bot instance
bot = RatBotClient()

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}")
    asyncio.create_task(bot.close())

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Utility functions for external use
def get_bot() -> Optional[RatBotClient]:
    """Get the bot instance"""
    return bot if bot.running else None

async def send_dm(user: discord.User, message: str):
    """Send a DM to a user"""
    try:
        await user.send(message)
    except discord.Forbidden:
        logger.warning(f"Could not send DM to {user}")
    except Exception as e:
        logger.error(f"Error sending DM to {user}: {e}")