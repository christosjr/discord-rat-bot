"""
Dungeon System
=============
Manages dungeon exploration, combat, and progression.
"""

import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config.dungeons import ALL_DUNGEONS, DUNGEON_KEYS
from config.game_balance import COMBAT_SETTINGS
from config.equipment import get_random_loot
from src.database import db_manager
from src.player import Player

logger = logging.getLogger(__name__)

class DungeonManager:
    """Manages dungeon runs and combat"""
    
    def __init__(self):
        self.active_runs = {}  # player_id -> run data
    
    async def create_run(self, player_id: int, dungeon_id: str) -> Optional[Dict]:
        """Create a new dungeon run"""
        try:
            dungeon = ALL_DUNGEONS.get(dungeon_id)
            if not dungeon:
                return None
            
            # Create run in database
            run_id = await db_manager.execute("""
                INSERT INTO dungeon_runs (player_id, dungeon_id, max_floors, status)
                VALUES (?, ?, ?, 'active')
            """, (player_id, dungeon_id, dungeon.max_floors))
            
            # Store in memory
            run_data = {
                'id': run_id,
                'player_id': player_id,
                'dungeon_id': dungeon_id,
                'current_floor': 1,
                'max_floors': dungeon.max_floors,
                'status': 'active',
                'player_hp': 100,  # Will be set based on actual player stats
                'enemies': []
            }
            
            self.active_runs[player_id] = run_data
            
            # Initialize first floor
            await self._initialize_floor(run_data)
            
            return run_data
        
        except Exception as e:
            logger.error(f"Error creating dungeon run: {e}")
            return None
    
    async def get_active_run(self, player_discord_id: str) -> Optional[Dict]:
        """Get active dungeon run for player"""
        # First check memory
        for run_data in self.active_runs.values():
            if str(run_data['player_id']) == player_discord_id:
                return run_data
        
        # Check database
        run_data = await db_manager.fetchone("""
            SELECT dr.*, d.name as dungeon_name FROM dungeon_runs dr
            JOIN players p ON dr.player_id = p.id
            WHERE p.discord_id = ? AND dr.status = 'active'
        """, (player_discord_id,))
        
        if run_data:
            run_dict = dict(run_data)
            self.active_runs[run_dict['player_id']] = run_dict
            return run_dict
        
        return None
    
    async def _initialize_floor(self, run_data: Dict):
        """Initialize enemies for current floor"""
        dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
        if not dungeon or run_data['current_floor'] not in dungeon.floor_enemies:
            return
        
        # Get enemy templates for this floor
        enemy_templates = dungeon.floor_enemies[run_data['current_floor']]
        
        # Create actual enemies for this run
        enemies = []
        for template in enemy_templates:
            # Copy enemy data and add run-specific modifications
            enemy = {
                'name': template.name,
                'health': template.health,
                'max_health': template.health,
                'attack': template.attack,
                'defense': template.defense,
                'element': template.element,
                'resistance': template.resistance,
                'special_ability': template.special_ability,
                'is_boss': False
            }
            enemies.append(enemy)
        
        # Check if this is a boss floor
        if run_data['current_floor'] == dungeon.max_floors and dungeon.boss_enemy:
            boss = {
                'name': dungeon.boss_enemy.name,
                'health': dungeon.boss_enemy.health,
                'max_health': dungeon.boss_enemy.health,
                'attack': dungeon.boss_enemy.attack,
                'defense': dungeon.boss_enemy.defense,
                'element': dungeon.boss_enemy.element,
                'resistance': dungeon.boss_enemy.resistance,
                'special_ability': dungeon.boss_enemy.special_ability,
                'is_boss': True
            }
            enemies = [boss]
        
        run_data['enemies'] = enemies
    
    async def process_combat_action(self, player_discord_id: str, action: str) -> Optional[Dict]:
        """Process a combat action"""
        try:
            # Get player and run
            player = await Player.get_by_discord_id(player_discord_id)
            if not player:
                return None
            
            run_data = await self.get_active_run(player_discord_id)
            if not run_data:
                return None
            
            dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
            if not dungeon:
                return None
            
            # Get combat stats
            combat_stats = player.get_combat_stats()
            if 'player_hp' not in run_data:
                run_data['player_hp'] = combat_stats['health']
            
            # Process action
            if action == 'attack':
                return await self._process_attack(player, run_data, combat_stats)
            elif action == 'defend':
                return await self._process_defend(player, run_data, combat_stats)
            elif action == 'cast':
                return await self._process_cast(player, run_data, combat_stats)
            elif action == 'flee':
                return await self._process_flee(player, run_data, combat_stats)
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error processing combat action: {e}")
            return None
    
    async def _process_attack(self, player: Player, run_data: Dict, combat_stats: Dict) -> Dict:
        """Process an attack action"""
        if not run_data['enemies']:
            return {'error': 'No enemies to attack'}
        
        # Get first enemy
        enemy = run_data['enemies'][0]
        
        # Calculate damage
        base_damage = combat_stats['attack']
        damage_variance = random.uniform(1 - COMBAT_SETTINGS['base_damage_variance'], 
                                       1 + COMBAT_SETTINGS['base_damage_variance'])
        final_damage = int(base_damage * damage_variance)
        
        # Apply critical hit
        crit_chance = combat_stats['critical_chance'] / 100
        is_critical = random.random() < crit_chance
        if is_critical:
            final_damage = int(final_damage * COMBAT_SETTINGS['critical_hit_multiplier'])
        
        # Apply enemy defense
        final_damage = max(1, final_damage - enemy['defense'])
        
        # Deal damage to enemy
        enemy['health'] -= final_damage
        
        # Enemy attacks back
        enemy_damage = max(1, enemy['attack'] - combat_stats['defense'])
        run_data['player_hp'] -= enemy_damage
        
        result = {
            'action': 'attack',
            'damage_dealt': final_damage,
            'damage_taken': enemy_damage,
            'enemy_hp': enemy['health'],
            'player_hp': run_data['player_hp'],
            'is_critical': is_critical,
            'enemies_defeated': 0,
            'loot': []
        }
        
        # Check if enemy is defeated
        if enemy['health'] <= 0:
            result['enemies_defeated'] = 1
            run_data['enemies'].pop(0)  # Remove defeated enemy
            
            # Generate loot
            rarity = self._determine_loot_rarity(run_data, enemy['is_boss'])
            loot = get_random_loot(rarity)
            result['loot'] = loot
            
            # Add loot to player
            for item_id in loot:
                await player.add_to_inventory(item_id, 'equipment', 1)
        
        # Check if floor is cleared
        if not run_data['enemies']:
            result['floor_cleared'] = True
            await self._advance_to_next_floor(run_data)
        
        # Check if dungeon is completed
        if run_data['current_floor'] > run_data['max_floors']:
            result['dungeon_completed'] = True
            await self._complete_dungeon(player, run_data, result)
        
        return result
    
    async def _process_defend(self, player: Player, run_data: Dict, combat_stats: Dict) -> Dict:
        """Process a defend action"""
        if not run_data['enemies']:
            return {'error': 'No enemies to defend from'}
        
        enemy = run_data['enemies'][0]
        
        # Reduced damage when defending
        enemy_damage = max(1, int((enemy['attack'] - combat_stats['defense']) * 0.5))
        run_data['player_hp'] -= enemy_damage
        
        return {
            'action': 'defend',
            'damage_taken': enemy_damage,
            'player_hp': run_data['player_hp'],
            'defended': True
        }
    
    async def _process_cast(self, player: Player, run_data: Dict, combat_stats: Dict) -> Dict:
        """Process a cast spell action"""
        # Simplified magic attack
        if combat_stats['mana'] < 10:
            return {'error': 'Not enough mana'}
        
        if not run_data['enemies']:
            return {'error': 'No enemies to cast at'}
        
        enemy = run_data['enemies'][0]
        
        # Use mana
        mana_cost = 10
        spell_damage = combat_stats['magic_attack'] * 1.2  # 20% bonus for spells
        
        # Apply enemy magic resistance
        if 'magic' in enemy['resistance']:
            spell_damage = int(spell_damage * (1 - enemy['resistance']['magic'] / 100))
        
        final_damage = max(1, int(spell_damage))
        enemy['health'] -= final_damage
        
        # Enemy counter-attacks
        enemy_damage = max(1, enemy['attack'] - combat_stats['defense'])
        run_data['player_hp'] -= enemy_damage
        
        result = {
            'action': 'cast',
            'spell_damage': final_damage,
            'damage_taken': enemy_damage,
            'mana_cost': mana_cost,
            'enemy_hp': enemy['health'],
            'player_hp': run_data['player_hp'],
            'enemies_defeated': 0,
            'loot': []
        }
        
        # Check if enemy is defeated
        if enemy['health'] <= 0:
            result['enemies_defeated'] = 1
            run_data['enemies'].pop(0)
            
            # Generate better loot for magic kills
            rarity = self._determine_loot_rarity(run_data, enemy['is_boss'])
            loot = get_random_loot(rarity)
            result['loot'] = loot
            
            for item_id in loot:
                await player.add_to_inventory(item_id, 'equipment', 1)
        
        # Check floor/dungeon completion
        if not run_data['enemies']:
            result['floor_cleared'] = True
            await self._advance_to_next_floor(run_data)
        
        if run_data['current_floor'] > run_data['max_floors']:
            result['dungeon_completed'] = True
            await self._complete_dungeon(player, run_data, result)
        
        return result
    
    async def _process_flee(self, player: Player, run_data: Dict, combat_stats: Dict) -> Dict:
        """Process a flee action"""
        # Flee chance based on speed vs enemy
        if not run_data['enemies']:
            return {'error': 'No enemies to flee from'}
        
        enemy = run_data['enemies'][0]
        flee_chance = min(0.8, combat_stats['speed'] / (combat_stats['speed'] + enemy['attack']))
        
        if random.random() < flee_chance:
            # Successful flee
            await self._end_dungeon_run(run_data, 'fled')
            return {
                'action': 'flee',
                'successful': True,
                'message': 'You successfully fled from the dungeon!'
            }
        else:
            # Failed flee, enemy attacks
            enemy_damage = max(1, enemy['attack'] - combat_stats['defense'])
            run_data['player_hp'] -= enemy_damage
            
            return {
                'action': 'flee',
                'successful': False,
                'damage_taken': enemy_damage,
                'player_hp': run_data['player_hp']
            }
    
    def _determine_loot_rarity(self, run_data: Dict, is_boss: bool) -> str:
        """Determine loot rarity based on dungeon and floor"""
        dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
        if not dungeon:
            return 'common'
        
        # Bosses drop better loot
        if is_boss:
            return dungeon.difficulty.value
        
        # Higher floors and harder dungeons drop better loot
        floor_multiplier = run_data['current_floor'] / run_data['max_floors']
        
        if dungeon.difficulty.value == 'easy':
            return 'common' if floor_multiplier < 0.5 else 'uncommon'
        elif dungeon.difficulty.value == 'medium':
            return 'uncommon' if floor_multiplier < 0.7 else 'rare'
        elif dungeon.difficulty.value == 'hard':
            return 'rare' if floor_multiplier < 0.8 else 'epic'
        else:  # extreme
            return 'epic' if floor_multiplier < 0.9 else 'legendary'
    
    async def _advance_to_next_floor(self, run_data: Dict):
        """Advance to the next floor"""
        run_data['current_floor'] += 1
        run_data['enemies'] = []
        
        # Update database
        await db_manager.execute("""
            UPDATE dungeon_runs SET current_floor = ? WHERE id = ?
        """, (run_data['current_floor'], run_data['id']))
        
        # Initialize new floor
        await self._initialize_floor(run_data)
    
    async def _complete_dungeon(self, player: Player, run_data: Dict, result: Dict):
        """Complete a dungeon run"""
        # Award completion rewards
        dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
        if not dungeon:
            return
        
        # Completion XP
        from src.database import update_player_xp
        completion_xp = dungeon.completion_xp_bonus
        if completion_xp > 0:
            await update_player_xp(player.discord_id, completion_xp)
            result['xp_gained'] = completion_xp
        
        # Guaranteed drops
        if dungeon.guaranteed_drops:
            result['completion_rewards'] = []
            for item_id in dungeon.guaranteed_drops:
                await player.add_to_inventory(item_id, 'equipment', 1)
                result['completion_rewards'].append(f"✅ {item_id}")
        
        await self._end_dungeon_run(run_data, 'completed')
    
    async def _end_dungeon_run(self, run_data: Dict, final_status: str):
        """End a dungeon run"""
        # Update database
        await db_manager.execute("""
            UPDATE dungeon_runs SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (final_status, run_data['id']))
        
        # Remove from memory
        if run_data['player_id'] in self.active_runs:
            del self.active_runs[run_data['player_id']]
    
    async def handle_player_death(self, player_discord_id: str) -> Dict:
        """Handle player death in dungeon"""
        run_data = await self.get_active_run(player_discord_id)
        if not run_data:
            return {}
        
        # Get player for death penalty calculation
        player = await Player.get_by_discord_id(player_discord_id)
        if not player:
            return {}
        
        dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
        if not dungeon:
            return {}
        
        # Calculate death penalty
        xp_loss = int(player.xp * dungeon.death_penalty / 100)
        gold_loss = min(player.gold, int(player.gold * 0.1))  # 10% gold loss
        
        # Apply penalties
        from src.database import update_player_xp
        await update_player_xp(player_discord_id, -xp_loss)  # Negative XP
        if gold_loss > 0:
            await player.spend_gold(gold_loss)
        
        # End run
        await self._end_dungeon_run(run_data, 'died')
        
        return {
            'xp_lost': xp_loss,
            'gold_lost': gold_loss
        }

# Global dungeon manager instance
dungeon_manager = DungeonManager()

# Utility functions
async def get_player_active_dungeon(player_discord_id: str) -> Optional[Dict]:
    """Get active dungeon for player"""
    return await dungeon_manager.get_active_run(player_discord_id)

async def is_player_in_dungeon(player_discord_id: str) -> bool:
    """Check if player is currently in a dungeon"""
    return await dungeon_manager.get_active_run(player_discord_id) is not None