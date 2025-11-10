"""
Configuration Tests
==================
Test all configuration files for validity and completeness.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_bot_config():
    """Test bot configuration"""
    from config.bot_config import BOT_CONFIG, DATABASE_CONFIG
    
    # Check required environment variables
    assert 'DISCORD_BOT_TOKEN' in os.environ, "DISCORD_BOT_TOKEN not in environment"
    
    # Check bot config structure
    assert 'token' in BOT_CONFIG
    assert 'command_prefix' in BOT_CONFIG
    assert 'activity_name' in BOT_CONFIG
    
    # Check database config
    assert 'type' in DATABASE_CONFIG
    assert DATABASE_CONFIG['type'] in ['sqlite', 'postgresql']

def test_game_balance():
    """Test game balance configuration"""
    from config.game_balance import (
        XP_REQUIREMENTS, XP_REWARDS, WILD_RAT_RATES, 
        STARTING_STATS, INVENTORY_LIMITS
    )
    
    # Check XP requirements
    assert 1 in XP_REQUIREMENTS
    assert XP_REQUIREMENTS[1] == 0
    assert len(XP_REQUIREMENTS) > 10
    
    # Check XP rewards are positive
    for reward in XP_REWARDS.values():
        assert reward > 0
    
    # Check wild rat rates sum to 100%
    total_rate = sum(WILD_RAT_RATES.values())
    assert abs(total_rate - 100.0) < 0.1, f"Wild rat rates should sum to 100%, got {total_rate}%"
    
    # Check starting stats
    assert STARTING_STATS['level'] == 1
    assert STARTING_STATS['gold'] > 0
    
    # Check inventory limits
    assert INVENTORY_LIMITS['base_rat_slots'] > 0
    assert INVENTORY_LIMITS['base_item_slots'] > 0

def test_rat_types():
    """Test rat types configuration"""
    from config.rat_types import ALL_RATS, WILD_RATS, EVENT_RATS
    
    # Check that we have various rat types
    assert len(ALL_RATS) > 0
    assert len(WILD_RATS) > 0
    
    # Check rarities are represented
    rat_rarities = {rat.rarity.value for rat in ALL_RATS.values()}
    expected_rarities = {'common', 'uncommon', 'rare', 'epic', 'legendary'}
    assert expected_rarities.issubset(rat_rarities), f"Missing rarities: {expected_rarities - rat_rarities}"
    
    # Check that rats have required attributes
    for rat_id, rat in ALL_RATS.items():
        assert rat.name, f"Rat {rat_id} missing name"
        assert rat.base_xp > 0, f"Rat {rat_id} has invalid XP"
        assert rat.base_gold >= 0, f"Rat {rat_id} has invalid gold"
        assert rat.loot_table, f"Rat {rat_id} missing loot table"

def test_equipment():
    """Test equipment configuration"""
    from config.equipment import ALL_EQUIPMENT, WEAPONS, ARMOR, ACCESSORIES
    
    # Check that we have equipment
    assert len(ALL_EQUIPMENT) > 0
    assert len(WEAPONS) > 0
    assert len(ARMOR) > 0
    
    # Check equipment slots
    from config.equipment import EquipmentSlot
    expected_slots = {slot.value for slot in EquipmentSlot}
    used_slots = {equipment.slot.value for equipment in ALL_EQUIPMENT.values()}
    assert expected_slots.issubset(used_slots), f"Missing equipment slots: {expected_slots - used_slots}"
    
    # Check loot tables
    from config.equipment import LOOT_TABLES
    for rarity, loot_table in LOOT_TABLES.items():
        assert len(loot_table) > 0, f"Loot table for {rarity} is empty"

def test_dungeons():
    """Test dungeon configuration"""
    from config.dungeons import ALL_DUNGEONS, DUNGEON_KEYS
    
    # Check that we have dungeons
    assert len(ALL_DUNGEONS) > 0
    
    # Check dungeon keys
    for dungeon_id, key_info in DUNGEON_KEYS.items():
        assert 'name' in key_info
        assert 'price' in key_info
        assert key_info['price'] > 0
    
    # Check dungeon structure
    for dungeon_id, dungeon in ALL_DUNGEONS.items():
        assert dungeon.name, f"Dungeon {dungeon_id} missing name"
        assert dungeon.level_requirement > 0, f"Dungeon {dungeon_id} has invalid level requirement"
        assert dungeon.access_fee >= 0, f"Dungeon {dungeon_id} has invalid access fee"
        assert dungeon.max_floors > 0, f"Dungeon {dungeon_id} has invalid floor count"
        assert len(dungeon.floor_enemies) > 0, f"Dungeon {dungeon_id} missing enemies"

def test_traders():
    """Test trader configuration"""
    from config.traders import TRADER_TYPES, TRADER_INVENTORIES
    
    # Check trader types
    assert len(TRADER_TYPES) > 0
    
    # Check inventories
    for trader_type, inventory in TRADER_INVENTORIES.items():
        assert len(inventory) > 0, f"Inventory for {trader_type} is empty"
        
        for item_id, item_data in inventory.items():
            assert item_data.price > 0, f"Item {item_id} has invalid price"
            assert item_data.stock >= 0, f"Item {item_id} has invalid stock"

def test_environment_variables():
    """Test that required environment variables are handled properly"""
    from config.bot_config import BOT_CONFIG
    
    # For testing, we allow missing token but warn about it
    if 'DISCORD_BOT_TOKEN' not in os.environ:
        import warnings
        warnings.warn("DISCORD_BOT_TOKEN not set - this is OK for testing")
    
    # Check that other config loads without errors
    assert BOT_CONFIG['command_prefix'] == '!'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])