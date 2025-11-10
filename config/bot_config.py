"""
Discord Bot Configuration
========================
Core bot settings and Discord API configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_CONFIG = {
    'token': os.getenv('DISCORD_BOT_TOKEN'),
    'application_id': os.getenv('DISCORD_APPLICATION_ID'),
    'command_prefix': '!',
    'activity_name': 'Catching rats',
    'activity_type': 0,  # 0 = Playing
    'intents': {
        'message_content': True,
        'members': True,
        'presences': True
    }
}

# Validate required environment variables
required_vars = ['DISCORD_BOT_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# Validate token format
token = os.getenv('DISCORD_BOT_TOKEN')
if token:
    if not token.startswith(('MTM', 'OTM', 'NDE', 'NDU', 'NDI', 'NDk', 'NDc', 'NDQ', 'NDM', 'OQ', 'Mt', 'OT', 'ND')):
        raise ValueError("Invalid Discord bot token format. Token should start with MT, OT, ND, or MQ")
    if len(token) < 50:
        raise ValueError("Discord bot token appears to be too short. Please check the token format.")
else:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is not set or is empty")

# Database configuration
DATABASE_CONFIG = {
    'type': 'sqlite',  # 'sqlite' or 'postgresql'
    'database': 'rat_bot.db',
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', '5432')),
    'username': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'name': os.getenv('DATABASE_NAME', 'rat_bot')
}

# Rate limiting
RATE_LIMITS = {
    'commands_per_minute': 30,
    'catch_attempts_per_minute': 5,
    'dungeon_entries_per_hour': 10
}

# Bot settings
BOT_SETTINGS = {
    'auto_restart': True,
    'log_level': 'INFO',
    'max_message_length': 1900,  # Discord limit is 2000
    'database_backup_interval_hours': 24
}