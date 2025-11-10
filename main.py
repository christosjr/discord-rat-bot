#!/usr/bin/env python3
"""
Discord Rat Bot - Main Entry Point
=================================

Entry point for the Discord Rat Catching Bot with full game implementation.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from discord_bot.client import RatBotClient
from src.database import setup_database
from config.bot_config import BOT_CONFIG


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )


async def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Setup database
    try:
        await setup_database()
        logger.info("Database setup completed")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)
    
    # Create and run bot
    async with RatBotClient() as client:
        logger.info("Starting Discord Rat Bot...")
        try:
            await client.start(BOT_CONFIG['token'])
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shutdown requested by user")
    except Exception as e:
        print(f"Bot failed: {e}")
        sys.exit(1)