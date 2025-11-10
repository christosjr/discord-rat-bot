"""
Player Class and Operations
===========================
Core player management and operations.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.game_balance import STARTING_STATS, STAT_GROWTH
from config.equipment import ALL_EQUIPMENT
from config.rat_types import ALL_RATS
from src.database import db_manager

logger = logging.getLogger(__name__)

@dataclass
class PlayerStats:
    strength: int = 5
    agility: int = 5
    intelligence: int = 5
    vitality: int = 5

@dataclass
class PlayerEquipment:
    weapon: Optional[Dict] = None
    head: Optional[Dict] = None
    body: Optional[Dict] = None
    ring: Optional[Dict] = None
    tail_ring: Optional[Dict] = None
    neck: Optional[Dict] = None
    boots: Optional[Dict] = None

class Player:
    """Player class representing a Discord user in the game"""
    
    def __init__(self, data: Dict):
        self.id = data['id']
        self.discord_id = data['discord_id']
        self.username = data['username']
        self.level = data['level']
        self.xp = data['xp']
        self.stat_points = data['stat_points']
        self.perk_points = data['perk_points']
        self.gold = data['gold']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
        # Will be loaded separately
        self.stats = None
        self.inventory = []
        self.equipment = PlayerEquipment()
        self.perks = []
    
    @classmethod
    async def create(cls, discord_id: str, username: str):
        """Create a new player"""
        from src.database import get_or_create_player
        
        data = await get_or_create_player(discord_id, username)
        if data:
            player = cls(data)
            await player.load_full_data()
            return player
        return None
    
    @classmethod
    async def get_by_discord_id(cls, discord_id: str):
        """Get player by Discord ID"""
        player_data = await db_manager.fetchone(
            "SELECT * FROM players WHERE discord_id = ?",
            (discord_id,)
        )
        
        if player_data:
            player = cls(dict(player_data))
            await player.load_full_data()
            return player
        return None
    
    async def load_full_data(self):
        """Load all player data (stats, inventory, equipment, perks)"""
        await self._load_stats()
        await self._load_inventory()
        await self._load_equipment()
        await self._load_perks()
    
    async def _load_stats(self):
        """Load player stats"""
        stats_data = await db_manager.fetchone(
            "SELECT * FROM player_stats WHERE player_id = ?",
            (self.id,)
        )
        
        if stats_data:
            self.stats = PlayerStats(
                strength=stats_data['strength'],
                agility=stats_data['agility'],
                intelligence=stats_data['intelligence'],
                vitality=stats_data['vitality']
            )
        else:
            self.stats = PlayerStats()
            # Create default stats
            await db_manager.execute("""
                INSERT INTO player_stats (player_id, strength, agility, intelligence, vitality)
                VALUES (?, ?, ?, ?, ?)
            """, (self.id, 5, 5, 5, 5))
    
    async def _load_inventory(self):
        """Load player inventory"""
        inventory_data = await db_manager.fetchall(
            "SELECT * FROM player_inventory WHERE player_id = ?",
            (self.id,)
        )
        
        self.inventory = []
        for item in inventory_data:
            self.inventory.append({
                'id': item['id'],
                'item_id': item['item_id'],
                'item_type': item['item_type'],
                'quantity': item['quantity']
            })
    
    async def _load_equipment(self):
        """Load player equipment"""
        equipment_data = await db_manager.fetchall(
            "SELECT * FROM equipment WHERE player_id = ?",
            (self.id,)
        )
        
        for item in equipment_data:
            equipment_info = ALL_EQUIPMENT.get(item['item_id'])
            if equipment_info:
                equipment_item = {
                    'id': item['id'],
                    'item_id': item['item_id'],
                    'slot': item['slot'],
                    'data': equipment_info
                }
                
                # Set equipment in correct slot
                slot = item['slot']
                if hasattr(self.equipment, slot):
                    setattr(self.equipment, slot, equipment_item)
    
    async def _load_perks(self):
        """Load player perks"""
        perk_data = await db_manager.fetchall(
            "SELECT * FROM player_perks WHERE player_id = ?",
            (self.id,)
        )
        
        self.perks = []
        for perk in perk_data:
            self.perks.append({
                'tree_name': perk['tree_name'],
                'perk_name': perk['perk_name']
            })
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get total stats including equipment bonuses"""
        base_stats = {
            'strength': self.stats.strength,
            'agility': self.stats.agility,
            'intelligence': self.stats.intelligence,
            'vitality': self.stats.vitality
        }
        
        # Add equipment bonuses
        for slot_name, equipment_item in self.equipment.__dict__.items():
            if equipment_item and 'data' in equipment_item:
                equipment_data = equipment_item['data']
                if hasattr(equipment_data, 'stats') and equipment_data.stats:
                    for stat_name, bonus in equipment_data.stats.items():
                        base_stats[stat_name] = base_stats.get(stat_name, 0) + bonus
        
        return base_stats
    
    def get_combat_stats(self) -> Dict[str, int]:
        """Get combat-relevant stats"""
        total_stats = self.get_total_stats()
        
        return {
            'attack': total_stats.get('strength', 0) * 2 + total_stats.get('attack', 0),
            'ranged_attack': total_stats.get('agility', 0) * 2 + total_stats.get('ranged_attack', 0),
            'magic_attack': total_stats.get('intelligence', 0) * 2 + total_stats.get('magic_attack', 0),
            'defense': total_stats.get('vitality', 0) + total_stats.get('defense', 0),
            'speed': total_stats.get('agility', 0) + total_stats.get('speed', 0),
            'health': total_stats.get('vitality', 0) * 10 + 100,
            'mana': total_stats.get('intelligence', 0) * 5 + 50,
            'critical_chance': min(total_stats.get('agility', 0) // 5, 20) + total_stats.get('critical_chance', 0)
        }
    
    async def allocate_stat_point(self, stat_name: str) -> bool:
        """Allocate a stat point to a specific stat"""
        if self.stat_points <= 0:
            return False
        
        if stat_name not in ['strength', 'agility', 'intelligence', 'vitality']:
            return False
        
        # Update database
        await db_manager.execute(f"""
            UPDATE player_stats SET {stat_name} = {stat_name} + 1 WHERE player_id = ?
        """, (self.id,))
        
        # Update local data
        current_value = getattr(self.stats, stat_name)
        setattr(self.stats, stat_name, current_value + 1)
        self.stat_points -= 1
        
        return True
    
    async def add_to_inventory(self, item_id: str, item_type: str, quantity: int = 1) -> bool:
        """Add item to inventory"""
        try:
            item_id_db = await db_manager.execute("""
                INSERT INTO player_inventory (player_id, item_id, item_type, quantity)
                VALUES (?, ?, ?, ?)
            """, (self.id, item_id, item_type, quantity))
            
            # Update local inventory
            self.inventory.append({
                'id': item_id_db,
                'item_id': item_id,
                'item_type': item_type,
                'quantity': quantity
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to add item to inventory: {e}")
            return False
    
    async def remove_from_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        try:
            # Find item in inventory
            for i, item in enumerate(self.inventory):
                if item['item_id'] == item_id and item['quantity'] >= quantity:
                    if item['quantity'] == quantity:
                        # Remove completely
                        await db_manager.execute("""
                            DELETE FROM player_inventory WHERE id = ?
                        """, (item['id'],))
                        del self.inventory[i]
                    else:
                        # Reduce quantity
                        await db_manager.execute("""
                            UPDATE player_inventory SET quantity = quantity - ? WHERE id = ?
                        """, (quantity, item['id']))
                        item['quantity'] -= quantity
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to remove item from inventory: {e}")
            return False
    
    async def equip_item(self, item_id: str) -> bool:
        """Equip an item from inventory"""
        try:
            # Find item in inventory
            item_to_equip = None
            for item in self.inventory:
                if item['item_id'] == item_id:
                    item_to_equip = item
                    break
            
            if not item_to_equip:
                return False
            
            # Get equipment data
            equipment_data = ALL_EQUIPMENT.get(item_id)
            if not equipment_data:
                return False
            
            slot = equipment_data.slot.value
            
            # Check if slot is occupied
            current_equipment = getattr(self.equipment, slot)
            if current_equipment:
                # Unequip current item
                await self.unequip_item(slot)
            
            # Equip new item
            await db_manager.execute("""
                INSERT INTO equipment (player_id, slot, item_id)
                VALUES (?, ?, ?)
            """, (self.id, slot, item_id))
            
            # Remove from inventory
            await self.remove_from_inventory(item_id, 1)
            
            # Update local equipment
            equipment_item = {
                'id': db_manager.connection.lastrowid if hasattr(db_manager.connection, 'lastrowid') else 0,
                'item_id': item_id,
                'slot': slot,
                'data': equipment_data
            }
            setattr(self.equipment, slot, equipment_item)
            
            return True
        except Exception as e:
            logger.error(f"Failed to equip item: {e}")
            return False
    
    async def unequip_item(self, slot: str) -> bool:
        """Unequip an item from a slot"""
        try:
            current_equipment = getattr(self.equipment, slot)
            if not current_equipment:
                return False
            
            # Add back to inventory
            await self.add_to_inventory(current_equipment['item_id'], 'equipment', 1)
            
            # Remove from equipment table
            await db_manager.execute("""
                DELETE FROM equipment WHERE player_id = ? AND slot = ?
            """, (self.id, slot))
            
            # Update local equipment
            setattr(self.equipment, slot, None)
            
            return True
        except Exception as e:
            logger.error(f"Failed to unequip item: {e}")
            return False
    
    async def add_gold(self, amount: int) -> bool:
        """Add gold to player"""
        try:
            await db_manager.execute("""
                UPDATE players SET gold = gold + ? WHERE id = ?
            """, (amount, self.id))
            self.gold += amount
            return True
        except Exception as e:
            logger.error(f"Failed to add gold: {e}")
            return False
    
    async def spend_gold(self, amount: int) -> bool:
        """Spend gold if player has enough"""
        if self.gold < amount:
            return False
        
        try:
            await db_manager.execute("""
                UPDATE players SET gold = gold - ? WHERE id = ?
            """, (amount, self.id))
            self.gold -= amount
            return True
        except Exception as e:
            logger.error(f"Failed to spend gold: {e}")
            return False
    
    async def add_perk(self, tree_name: str, perk_name: str) -> bool:
        """Add a perk to the player"""
        try:
            await db_manager.execute("""
                INSERT INTO player_perks (player_id, tree_name, perk_name)
                VALUES (?, ?, ?)
            """, (self.id, tree_name, perk_name))
            
            self.perks.append({
                'tree_name': tree_name,
                'perk_name': perk_name
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to add perk: {e}")
            return False
    
    def has_perk(self, tree_name: str, perk_name: str) -> bool:
        """Check if player has a specific perk"""
        for perk in self.perks:
            if perk['tree_name'] == tree_name and perk['perk_name'] == perk_name:
                return True
        return False
    
    def get_inventory_count(self, item_id: str) -> int:
        """Get total quantity of an item in inventory"""
        total = 0
        for item in self.inventory:
            if item['item_id'] == item_id:
                total += item['quantity']
        return total
    
    def can_afford(self, cost: int) -> bool:
        """Check if player can afford a cost"""
        return self.gold >= cost
    
    def get_level_progress(self) -> Tuple[int, int]:
        """Get current XP and XP needed for next level"""
        from config.game_balance import XP_REQUIREMENTS
        
        current_xp = self.xp
        next_level_xp = XP_REQUIREMENTS.get(self.level + 1, current_xp)
        current_level_xp = XP_REQUIREMENTS.get(self.level, current_xp)
        
        return current_xp - current_level_xp, next_level_xp - current_level_xp