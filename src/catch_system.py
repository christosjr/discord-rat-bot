"""
Wild Rat Catching System
=======================
Handles wild rat spawning, catching, and rewards.
"""

import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config.game_balance import WILD_RAT_RATES, SPAWN_SETTINGS, XP_REWARDS
from config.rat_types import ALL_RATS, Rarity
from src.database import db_manager
from src.player import Player

logger = logging.getLogger(__name__)

class WildRatManager:
    """Manages wild rat spawning and catching"""
    
    def __init__(self):
        self.active_spawns = {}  # channel_id -> spawn data
        self.spawn_timer = None
        self.bot = None  # Will be set by the bot client
    
    async def start_spawning(self):
        """Start the automatic rat spawning system"""
        logger.info("Starting wild rat spawning system")
        self.spawn_timer = asyncio.create_task(self._spawn_loop())
    
    async def stop_spawning(self):
        """Stop the spawning system"""
        if self.spawn_timer:
            self.spawn_timer.cancel()
            logger.info("Stopped wild rat spawning system")
    
    async def _spawn_loop(self):
        """Main spawning loop - spawns rats in all configured channels every 3 minutes"""
        while True:
            try:
                await self._check_and_cleanup_expired_spawns()
                await self._spawn_rats_in_all_channels()
                await asyncio.sleep(180)  # Check every 3 minutes (180 seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in spawn loop: {e}")
                await asyncio.sleep(180)

    async def _spawn_rats_in_all_channels(self):
        """Spawn rats in all configured channels based on guild settings"""
        try:
            # Get all guild spawn settings from database
            guild_settings = await db_manager.fetchall("""
                SELECT guild_id, spawn_channel_ids, min_spawn_count, max_spawn_count, 
                       spawn_interval_minutes, enabled 
                FROM guild_spawn_settings 
                WHERE enabled = 1
            """)
            
            for settings in guild_settings:
                if not self.bot:
                    continue
                    
                try:
                    # Parse channel IDs from JSON
                    import json
                    channel_ids = json.loads(settings['spawn_channel_ids'])
                    
                    # Get min/max spawn counts
                    min_spawn = settings['min_spawn_count'] or 2
                    max_spawn = settings['max_spawn_count'] or 4
                    
                    # Choose random number of rats to spawn
                    spawn_count = random.randint(min_spawn, max_spawn)
                    
                    # Choose random channels to spawn in
                    if len(channel_ids) >= spawn_count:
                        selected_channels = random.sample(channel_ids, spawn_count)
                    else:
                        selected_channels = channel_ids
                    
                    # Spawn rats in selected channels
                    for channel_id in selected_channels:
                        # Check if channel already has a rat
                        if channel_id not in self.active_spawns:
                            success = await self.spawn_wild_rat(channel_id)
                            if success:
                                # Send message to channel
                                try:
                                    channel = self.bot.get_channel(int(channel_id))
                                    if channel:
                                        await channel.send("🐭 A wild rat has appeared! Use `!catch` to try and catch it!")
                                        logger.info(f"Spawned rat in channel {channel_id} for guild {settings['guild_id']}")
                                except Exception as e:
                                    logger.error(f"Error sending spawn message to channel {channel_id}: {e}")
                
                except Exception as e:
                    logger.error(f"Error spawning rats for guild {settings['guild_id']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in _spawn_rats_in_all_channels: {e}")
    
    async def _check_and_cleanup_expired_spawns(self):
        """Remove expired rat spawns"""
        current_time = datetime.now()
        expired_channels = []
        
        for channel_id, spawn_data in self.active_spawns.items():
            if current_time > spawn_data['expires_at']:
                expired_channels.append(channel_id)
        
        for channel_id in expired_channels:
            del self.active_spawns[channel_id]
            logger.info(f"Cleaned up expired rat spawn in channel {channel_id}")
    
    async def spawn_wild_rat(self, channel_id: str) -> bool:
        """Spawn a wild rat in a specific channel"""
        try:
            # Check if there's already an active rat in this channel
            if channel_id in self.active_spawns:
                return False
            
            # Decide if it's a trader or normal rat
            trader_chance = SPAWN_SETTINGS['trader_spawn_chance_percent']
            is_trader = random.randint(1, 100) <= trader_chance
            
            if is_trader:
                return await self._spawn_trader(channel_id)
            else:
                return await self._spawn_normal_rat(channel_id)
        
        except Exception as e:
            logger.error(f"Error spawning wild rat: {e}")
            return False
    
    async def _spawn_normal_rat(self, channel_id: str) -> bool:
        """Spawn a normal wild rat"""
        try:
            # Select rat type based on rarity distribution
            rat_type = self._select_rat_by_rarity()
            if not rat_type:
                return False
            
            # Create spawn data
            spawn_duration = 60  # 1 minute to catch
            expires_at = datetime.now() + timedelta(seconds=spawn_duration)
            
            spawn_data = {
                'type': 'normal',
                'rat_type': rat_type.name,
                'spawn_time': datetime.now(),
                'expires_at': expires_at,
                'channel_id': channel_id
            }
            
            # Store in database for persistence
            await db_manager.execute("""
                INSERT INTO wild_rats (channel_id, rat_type, expires_at)
                VALUES (?, ?, ?)
            """, (channel_id, rat_type.name, expires_at))
            
            # Store in memory for quick access
            self.active_spawns[channel_id] = spawn_data
            
            logger.info(f"Spawned {rat_type.name} in channel {channel_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error spawning normal rat: {e}")
            return False
    
    async def _spawn_trader(self, channel_id: str) -> bool:
        """Spawn a trader rat"""
        try:
            from config.traders import TRADER_TYPES
            from config.game_balance import TRADER_SETTINGS
            
            # Select trader type based on rates
            trader_type = self._select_trader_type()
            if not trader_type:
                return False
            
            # Set duration based on trader type
            duration_map = {
                'basic': 60,        # 1 minute
                'rare_goods': 90,   # 1.5 minutes
                'key_master': 120,  # 2 minutes
                'master_artisan': 300  # 5 minutes
            }
            
            spawn_duration = duration_map.get(trader_type, 60)
            expires_at = datetime.now() + timedelta(seconds=spawn_duration)
            
            # Store in database
            await db_manager.execute("""
                INSERT INTO active_traders (channel_id, trader_type, expires_at)
                VALUES (?, ?, ?)
            """, (channel_id, trader_type, expires_at))
            
            # Store in memory
            spawn_data = {
                'type': 'trader',
                'trader_type': trader_type,
                'spawn_time': datetime.now(),
                'expires_at': expires_at,
                'channel_id': channel_id
            }
            
            self.active_spawns[channel_id] = spawn_data
            
            logger.info(f"Spawned {trader_type} trader in channel {channel_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error spawning trader: {e}")
            return False
    
    def _select_rat_by_rarity(self):
        """Select a rat type based on rarity distribution"""
        roll = random.randint(1, 10000) / 100  # Convert to percentage with 2 decimal places
        
        cumulative = 0
        for rarity, rate in WILD_RAT_RATES.items():
            cumulative += rate
            if roll <= cumulative:
                # Find a rat of this rarity
                available_rats = [
                    rat for rat in ALL_RATS.values() 
                    if rat.rarity.value == rarity
                ]
                if available_rats:
                    return random.choice(available_rats)
        
        # Fallback to common rat
        common_rats = [rat for rat in ALL_RATS.values() if rat.rarity == Rarity.COMMON]
        return random.choice(common_rats) if common_rats else None
    
    def _select_trader_type(self):
        """Select a trader type based on spawn rates"""
        from config.game_balance import TRADER_SETTINGS
        
        rates = TRADER_SETTINGS['spawn_rates']
        roll = random.random()
        
        cumulative = 0
        for trader_type, rate in rates.items():
            cumulative += rate
            if roll <= cumulative:
                return trader_type
        
        return 'basic'  # Fallback
    
    async def attempt_catch(self, channel_id: str, discord_id: str) -> Tuple[bool, str, Dict]:
        """Attempt to catch a rat in the channel"""
        try:
            # Check if there's an active spawn
            if channel_id not in self.active_spawns:
                return False, "No wild rat to catch!", {}
            
            spawn_data = self.active_spawns[channel_id]
            
            # Check if it's expired
            if datetime.now() > spawn_data['expires_at']:
                del self.active_spawns[channel_id]
                return False, "Too late! The rat has escaped.", {}
            
            # Get player
            player = await Player.get_by_discord_id(discord_id)
            if not player:
                return False, "You need to set up your character first!", {}
            
            if spawn_data['type'] == 'trader':
                return await self._catch_trader(spawn_data, player)
            else:
                return await self._catch_normal_rat(spawn_data, player)
        
        except Exception as e:
            logger.error(f"Error in attempt_catch: {e}")
            return False, "An error occurred while trying to catch the rat.", {}
    
    async def _catch_normal_rat(self, spawn_data: Dict, player: Player) -> Tuple[bool, str, Dict]:
        """Handle catching a normal wild rat"""
        try:
            rat_name = spawn_data['rat_type']
            rat_data = ALL_RATS.get(rat_name)
            
            if not rat_data:
                return False, "This rat type doesn't exist!", {}
            
            # Award XP and gold
            xp_reward = rat_data.base_xp
            gold_reward = rat_data.base_gold
            
            await player.add_gold(gold_reward)
            
            # Calculate XP gain
            from src.database import update_player_xp
            leveled_up = await update_player_xp(player.discord_id, xp_reward)
            
            # Generate loot
            loot = self._generate_loot(rat_data.rarity.value)
            loot_messages = []
            
            for item_id in loot:
                success = await player.add_to_inventory(item_id, 'equipment', 1)
                if success:
                    from config.equipment import ALL_EQUIPMENT
                    item_data = ALL_EQUIPMENT.get(item_id)
                    if item_data:
                        loot_messages.append(f"🎁 {item_data.name}")
            
            # Remove from active spawns
            channel_id = spawn_data['channel_id']
            if channel_id in self.active_spawns:
                del self.active_spawns[channel_id]
            
            # Remove from database
            await db_manager.execute("""
                DELETE FROM wild_rats WHERE channel_id = ? AND rat_type = ?
            """, (channel_id, rat_name))
            
            # Build response message
            response_parts = [f"🎯 You caught a **{rat_data.name}**!"]
            response_parts.append(f"💰 +{gold_reward} gold")
            response_parts.append(f"⭐ +{xp_reward} XP")
            
            if loot_messages:
                response_parts.append("**Loot obtained:**")
                response_parts.extend(loot_messages)
            
            if leveled_up:
                response_parts.append("🎉 **LEVEL UP!**")
            
            message = "\n".join(response_parts)
            
            result_data = {
                'rat_data': rat_data,
                'loot': loot,
                'xp_gained': xp_reward,
                'gold_gained': gold_reward,
                'leveled_up': leveled_up
            }
            
            return True, message, result_data
        
        except Exception as e:
            logger.error(f"Error catching normal rat: {e}")
            return False, "Failed to catch the rat!", {}
    
    async def _catch_trader(self, spawn_data: Dict, player: Player) -> Tuple[bool, str, Dict]:
        """Handle catching a trader rat"""
        # For now, just mark that player caught the trader
        # The actual trading will be handled by a separate command
        
        channel_id = spawn_data['channel_id']
        trader_type = spawn_data['trader_type']
        
        # Update database to mark as caught
        await db_manager.execute("""
            UPDATE active_traders SET caught_by = ? WHERE channel_id = ?
        """, (player.discord_id, channel_id))
        
        # Update spawn data
        self.active_spawns[channel_id]['caught_by'] = player.discord_id
        self.active_spawns[channel_id]['caught_at'] = datetime.now()
        
        trader_names = {
            'basic': 'Basic Trader',
            'rare_goods': 'Rare Goods Trader', 
            'key_master': 'Key Master',
            'master_artisan': 'Master Artisan'
        }
        
        message = f"🏪 You caught a **{trader_names.get(trader_type, 'Trader')}**! Use `!trade` to start trading."
        
        return True, message, {'trader_type': trader_type}
    
    def _generate_loot(self, rarity: str) -> List[str]:
        """Generate loot based on rat rarity"""
        from config.equipment import LOOT_TABLES
        
        loot_table = LOOT_TABLES.get(rarity, LOOT_TABLES['common'])
        loot = []
        
        for item_id, chance in loot_table.items():
            if random.randint(1, 100) <= chance:
                loot.append(item_id)
        
        return loot

# Global rat manager instance
wild_rat_manager = WildRatManager()

# Utility functions
async def check_and_spawn_rat(channel_id: str) -> Optional[str]:
    """Check if we should spawn a rat in a channel and do it"""
    try:
        # Check if there's already a rat in this channel
        if channel_id in wild_rat_manager.active_spawns:
            return None
        
        # Random chance to spawn (1% per check)
        if random.randint(1, 100) <= 1:
            success = await wild_rat_manager.spawn_wild_rat(channel_id)
            if success:
                return "wild_rat_spawned"
        return None
    
    except Exception as e:
        logger.error(f"Error checking for rat spawn: {e}")
        return None

async def get_channel_spawn_info(channel_id: str) -> Optional[Dict]:
    """Get information about active spawn in a channel"""
    return wild_rat_manager.active_spawns.get(channel_id)