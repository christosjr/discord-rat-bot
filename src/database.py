"""
Database Setup and Configuration
===============================
Database connection and setup for the Discord Rat Bot.
"""

import sqlite3
import asyncio
import logging
from typing import Optional
from config.bot_config import DATABASE_CONFIG

# Import asyncpg only if using PostgreSQL
if DATABASE_CONFIG['type'] == 'postgresql':
    import asyncpg

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self):
        self.connection = None
        self.db_type = DATABASE_CONFIG['type']
        # Ensure database directory exists for SQLite
        if self.db_type == 'sqlite':
            import os
            db_path = DATABASE_CONFIG['database']
            if ':' in db_path:
                # Handle absolute or relative paths properly
                pass
            else:
                # Create database in current directory
                pass
    
    async def connect(self):
        """Connect to the database"""
        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(DATABASE_CONFIG['database'])
                self.connection.row_factory = sqlite3.Row
            elif self.db_type == 'postgresql':
                self.connection = await asyncpg.connect(
                    host=DATABASE_CONFIG['host'],
                    port=DATABASE_CONFIG['port'],
                    user=DATABASE_CONFIG['username'],
                    password=DATABASE_CONFIG['password'],
                    database=DATABASE_CONFIG['name']
                )
            logger.info(f"Connected to {self.db_type} database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            if self.db_type == 'sqlite':
                self.connection.close()
            elif self.db_type == 'postgresql':
                await self.connection.close()
            logger.info("Database connection closed")
    
    async def execute(self, query: str, params: tuple = None):
        """Execute a database query"""
        try:
            # Auto-connect if not connected
            if self.connection is None:
                await self.connect()
                
            if self.db_type == 'sqlite':
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.lastrowid
            elif self.db_type == 'postgresql':
                return await self.connection.execute(query, *params or [])
        except Exception as e:
            logger.error(f"Database execute error: {e}")
            raise
    
    async def fetchone(self, query: str, params: tuple = None):
        """Fetch a single row"""
        try:
            if self.db_type == 'sqlite':
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                return cursor.fetchone()
            elif self.db_type == 'postgresql':
                return await self.connection.fetchrow(query, *params or [])
        except Exception as e:
            logger.error(f"Database fetchone error: {e}")
            raise
    
    async def fetchall(self, query: str, params: tuple = None):
        """Fetch all rows"""
        try:
            if self.db_type == 'sqlite':
                cursor = self.connection.cursor()
                cursor.execute(query, params or ())
                return cursor.fetchall()
            elif self.db_type == 'postgresql':
                return await self.connection.fetch(query, *params or [])
        except Exception as e:
            logger.error(f"Database fetchall error: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

async def setup_database():
    """Setup the database with all required tables"""
    logger.info("Setting up database...")
    
    try:
        # Create tables
        await create_tables()
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

async def create_tables():
    """Create all required database tables"""
    
    # Players table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            discord_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            stat_points INTEGER DEFAULT 0,
            perk_points INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Player stats table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            player_id INTEGER PRIMARY KEY,
            strength INTEGER DEFAULT 5,
            agility INTEGER DEFAULT 5,
            intelligence INTEGER DEFAULT 5,
            vitality INTEGER DEFAULT 5,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Player inventory table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS player_inventory (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Equipment table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            slot TEXT NOT NULL,
            item_id TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Player perks table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS player_perks (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            tree_name TEXT NOT NULL,
            perk_name TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Dungeons table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS dungeons (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            level_requirement INTEGER NOT NULL,
            access_fee INTEGER NOT NULL,
            difficulty_rating INTEGER NOT NULL,
            guaranteed_drops TEXT NOT NULL,
            drop_chances TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Dungeon runs table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS dungeon_runs (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            dungeon_id INTEGER NOT NULL,
            current_floor INTEGER DEFAULT 1,
            max_floors INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id),
            FOREIGN KEY (dungeon_id) REFERENCES dungeons (id)
        )
    """)
    
    # Active traders table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS active_traders (
            id INTEGER PRIMARY KEY,
            channel_id TEXT NOT NULL,
            trader_type TEXT NOT NULL,
            spawn_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            caught_by TEXT,
            FOREIGN KEY (caught_by) REFERENCES players (discord_id)
        )
    """)
    
    # Wild rats table (for tracking spawns)
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS wild_rats (
            id INTEGER PRIMARY KEY,
            channel_id TEXT NOT NULL,
            rat_type TEXT NOT NULL,
            spawn_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            caught_by TEXT,
            FOREIGN KEY (caught_by) REFERENCES players (discord_id)
        )
    """)
    
    # Achievements table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            achievement_type TEXT NOT NULL,
            achievement_id TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Daily quests table
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS daily_quests (
            id INTEGER PRIMARY KEY,
            player_id INTEGER NOT NULL,
            quest_type TEXT NOT NULL,
            quest_data TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            target INTEGER NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    """)
    
    # Game settings table (for server-specific settings)
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS game_settings (
            id INTEGER PRIMARY KEY,
            guild_id TEXT UNIQUE NOT NULL,
            rat_spawn_interval_minutes INTEGER DEFAULT 15,
            trader_spawn_chance_percent INTEGER DEFAULT 15,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Guild spawn settings table (for detailed spawn control)
    await db_manager.execute("""
        CREATE TABLE IF NOT EXISTS guild_spawn_settings (
            id INTEGER PRIMARY KEY,
            guild_id TEXT UNIQUE NOT NULL,
            enabled BOOLEAN DEFAULT TRUE,
            spawn_channel_ids TEXT DEFAULT '[]', -- JSON array of channel IDs
            min_spawn_count INTEGER DEFAULT 2,
            max_spawn_count INTEGER DEFAULT 4,
            spawn_interval_minutes INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    logger.info("All database tables created successfully")

# Utility functions for database operations
async def get_or_create_player(discord_id: str, username: str):
    """Get existing player or create a new one"""
    
    # Check if player exists
    player = await db_manager.fetchone(
        "SELECT * FROM players WHERE discord_id = ?",
        (discord_id,)
    )
    
    if player:
        return dict(player) if player else None
    
    # Create new player
    player_id = await db_manager.execute("""
        INSERT INTO players (discord_id, username)
        VALUES (?, ?)
    """, (discord_id, username))
    
    # Create default stats
    await db_manager.execute("""
        INSERT INTO player_stats (player_id)
        VALUES (?)
    """, (player_id,))
    
    # Return the new player
    player = await db_manager.fetchone(
        "SELECT * FROM players WHERE id = ?",
        (player_id,)
    )
    
    return dict(player) if player else None

async def update_player_xp(discord_id: str, xp_gained: int):
    """Update player XP and level if necessary"""
    from config.game_balance import XP_REQUIREMENTS, STAT_GROWTH
    
    # Get current player data
    player = await db_manager.fetchone(
        "SELECT * FROM players WHERE discord_id = ?",
        (discord_id,)
    )
    
    if not player:
        return False
    
    player = dict(player)
    new_xp = player['xp'] + xp_gained
    new_level = player['level']
    
    # Check for level up
    while new_level < 100 and new_xp >= XP_REQUIREMENTS.get(new_level + 1, float('inf')):
        new_level += 1
    
    # Calculate stat and perk points earned
    level_diff = new_level - player['level']
    stat_points_gained = level_diff * STAT_GROWTH['stat_points_per_level']
    perk_points_gained = level_diff * STAT_GROWTH['perk_points_per_level']
    
    # Update player
    await db_manager.execute("""
        UPDATE players 
        SET level = ?, xp = ?, stat_points = stat_points + ?, perk_points = perk_points + ?, updated_at = CURRENT_TIMESTAMP
        WHERE discord_id = ?
    """, (new_level, new_xp, stat_points_gained, perk_points_gained, discord_id))
    
    return new_level > player['level']  # Return True if leveled up