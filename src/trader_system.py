"""
Trader System
=============
Manages wild trader spawning and trading mechanics.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config.game_balance import TRADER_SETTINGS
from config.traders import TRADER_TYPES, TRADER_INVENTORIES
from src.database import db_manager

logger = logging.getLogger(__name__)

class TraderManager:
    """Manages trader rats and trading operations"""
    
    def __init__(self):
        self.active_traders = {}  # channel_id -> trader data
    
    async def spawn_trader(self, channel_id: str, trader_type: str) -> bool:
        """Spawn a trader rat in a channel"""
        try:
            # Check if there's already a trader in this channel
            if channel_id in self.active_traders:
                return False
            
            # Validate trader type
            if trader_type not in TRADER_TYPES.values():
                logger.error(f"Invalid trader type: {trader_type}")
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
            
            # Store in memory for quick access
            trader_data = {
                'type': 'trader',
                'trader_type': trader_type,
                'spawn_time': datetime.now(),
                'expires_at': expires_at,
                'channel_id': channel_id,
                'caught_by': None
            }
            
            self.active_traders[channel_id] = trader_data
            
            logger.info(f"Spawned {trader_type} trader in channel {channel_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error spawning trader: {e}")
            return False
    
    async def attempt_catch(self, channel_id: str, discord_id: str) -> Tuple[bool, str, Dict]:
        """Attempt to catch a trader"""
        try:
            # Check if there's an active trader
            if channel_id not in self.active_traders:
                return False, "No trader to catch!", {}
            
            trader_data = self.active_traders[channel_id]
            
            # Check if it's expired
            if datetime.now() > trader_data['expires_at']:
                del self.active_traders[channel_id]
                return False, "The trader has left the area.", {}
            
            # Check if already caught
            if trader_data['caught_by']:
                if trader_data['caught_by'] != discord_id:
                    return False, "This trader is already trading with someone else!", {}
                else:
                    # Already caught by this player
                    return True, "You're already trading with this trader!", {'trader_type': trader_data['trader_type']}
            
            # Mark as caught
            trader_data['caught_by'] = discord_id
            trader_data['caught_at'] = datetime.now()
            
            # Update database
            await db_manager.execute("""
                UPDATE active_traders SET caught_by = ? WHERE channel_id = ?
            """, (discord_id, channel_id))
            
            # Get trader name
            trader_names = {
                'basic': 'Basic Trader',
                'rare_goods': 'Rare Goods Trader',
                'key_master': 'Key Master',
                'master_artisan': 'Master Artisan'
            }
            
            trader_name = trader_names.get(trader_data['trader_type'], 'Trader')
            
            # Build response
            response_parts = [f"🏪 You caught a **{trader_name}**!"]
            response_parts.append("Use `!trade` to start trading!")
            
            if trader_data['trader_type'] == 'key_master':
                response_parts.append("🔑 This trader specializes in dungeon keys!")
            elif trader_data['trader_type'] == 'master_artisan':
                response_parts.append("👑 This trader has access to legendary items!")
            
            message = "\n".join(response_parts)
            
            return True, message, {'trader_type': trader_data['trader_type']}
        
        except Exception as e:
            logger.error(f"Error catching trader: {e}")
            return False, "Failed to catch the trader!", {}
    
    def get_trader_inventory(self, trader_type: str) -> Dict:
        """Get inventory for a specific trader type"""
        return TRADER_INVENTORIES.get(trader_type, {})
    
    def get_trader_buy_list(self, trader_type: str) -> List[str]:
        """Get what a trader will buy"""
        from config.traders import TRADER_BUY_LISTS
        return TRADER_BUY_LISTS.get(trader_type, [])
    
    async def cleanup_expired_traders(self):
        """Remove expired traders"""
        current_time = datetime.now()
        expired_channels = []
        
        for channel_id, trader_data in self.active_traders.items():
            if current_time > trader_data['expires_at']:
                expired_channels.append(channel_id)
        
        for channel_id in expired_channels:
            # Remove from database
            await db_manager.execute("""
                DELETE FROM active_traders WHERE channel_id = ?
            """, (channel_id,))
            
            # Remove from memory
            del self.active_traders[channel_id]
            logger.info(f"Cleaned up expired trader in channel {channel_id}")
    
    async def get_trader_for_player(self, player_id: str, channel_id: str) -> Optional[Dict]:
        """Get trader data for a specific player in a channel"""
        if channel_id not in self.active_traders:
            return None
        
        trader_data = self.active_traders[channel_id]
        
        # Check if player is the one who caught this trader
        if trader_data.get('caught_by') == player_id:
            return trader_data
        
        return None

# Global trader manager instance
trader_manager = TraderManager()

# Utility functions
async def get_active_trader_for_player(player_id: str, channel_id: str) -> Optional[Dict]:
    """Get active trader for a specific player"""
    return await trader_manager.get_trader_for_player(player_id, channel_id)

async def cleanup_all_traders():
    """Clean up all expired traders"""
    await trader_manager.cleanup_expired_traders()

async def is_trader_active(channel_id: str) -> bool:
    """Check if there's an active trader in the channel"""
    return channel_id in trader_manager.active_traders

async def get_trader_type(channel_id: str) -> Optional[str]:
    """Get the type of trader in a channel"""
    if channel_id in trader_manager.active_traders:
        return trader_manager.active_traders[channel_id]['trader_type']
    return None