"""
Command Registration
==================
Register all bot commands.
"""

import logging
from discord_bot.commands import player_commands, game_commands, dungeon_commands, admin_commands

logger = logging.getLogger(__name__)

async def register_commands(bot):
    """Register all bot commands"""
    try:
        # Add command cogs
        await bot.add_cog(player_commands.PlayerCommands(bot))
        await bot.add_cog(game_commands.GameCommands(bot))
        await bot.add_cog(dungeon_commands.DungeonCommands(bot))
        await bot.add_cog(admin_commands.AdminCommands(bot))
        
        logger.info("All commands registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register commands: {e}")
        raise