"""
System Tests
============
Test core game systems and database operations.
"""

import pytest
import asyncio
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Set up a temporary database for testing"""
    # Create a temporary database file
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_file.close()
    
    # Set up database configuration to use our temp file
    os.environ['DATABASE_TYPE'] = 'sqlite'
    os.environ['DATABASE_NAME'] = db_file.name
    
    # Import and setup database
    from src.database import setup_database, db_manager
    await setup_database()
    
    yield db_file.name
    
    # Cleanup
    try:
        os.unlink(db_file.name)
    except:
        pass

@pytest.mark.asyncio
async def test_player_creation(test_db):
    """Test player creation and basic operations"""
    from src.player import Player
    from src.database import get_or_create_player
    
    # Test creating a new player
    player_data = await get_or_create_player("test_user_123", "TestUser")
    assert player_data is not None
    assert player_data['username'] == "TestUser"
    assert player_data['level'] == 1
    assert player_data['gold'] == 100
    
    # Test getting existing player
    player = await Player.get_by_discord_id("test_user_123")
    assert player is not None
    assert player.username == "TestUser"
    assert player.level == 1
    
    # Test stats
    assert player.stats.strength == 5
    assert player.stats.agility == 5
    assert player.stats.intelligence == 5
    assert player.stats.vitality == 5

@pytest.mark.asyncio
async def test_inventory_operations(test_db):
    """Test inventory management"""
    from src.player import Player
    from config.equipment import ALL_EQUIPMENT
    
    # Create a player
    player = await Player.create("test_inventory_user", "InventoryUser")
    assert player is not None
    
    # Test adding items
    success = await player.add_to_inventory("wooden_dagger", "equipment", 1)
    assert success
    assert len(player.inventory) == 1
    assert player.inventory[0]['item_id'] == "wooden_dagger"
    
    # Test getting inventory count
    count = player.get_inventory_count("wooden_dagger")
    assert count == 1
    
    # Test removing items
    success = await player.remove_from_inventory("wooden_dagger", 1)
    assert success
    assert len(player.inventory) == 0
    assert player.get_inventory_count("wooden_dagger") == 0

@pytest.mark.asyncio
async def test_equipment_system(test_db):
    """Test equipment system"""
    from src.player import Player
    
    # Create a player
    player = await Player.create("test_equipment_user", "EquipmentUser")
    assert player is not None
    
    # Add equipment to inventory
    await player.add_to_inventory("wooden_dagger", "equipment", 1)
    await player.add_to_inventory("leather_vest", "equipment", 1)
    
    # Test equipping items
    success = await player.equip_item("wooden_dagger")
    assert success
    assert player.equipment.weapon is not None
    assert player.equipment.weapon['item_id'] == "wooden_dagger"
    
    success = await player.equip_item("leather_vest")
    assert success
    assert player.equipment.body is not None
    assert player.equipment.body['item_id'] == "leather_vest"
    
    # Test that equipment affects stats
    total_stats = player.get_total_stats()
    assert total_stats['attack'] > 0  # Should have attack from weapon
    assert total_stats['defense'] > 0  # Should have defense from armor

@pytest.mark.asyncio
async def test_catch_system_basic(test_db):
    """Test basic catch system functionality"""
    from src.catch_system import WildRatManager
    from src.player import Player
    from config.rat_types import ALL_RATS
    
    # Create a player
    player = await Player.create("test_catch_user", "CatchUser")
    assert player is not None
    
    # Create rat manager
    rat_manager = WildRatManager()
    
    # Test spawning a rat
    success = await rat_manager.spawn_wild_rat("test_channel_123")
    assert success
    
    # Test that rat was spawned
    spawn_info = rat_manager.active_spawns.get("test_channel_123")
    assert spawn_info is not None
    assert spawn_info['type'] == 'normal'
    assert 'rat_type' in spawn_info
    
    # Test catching the rat
    success, message, data = await rat_manager.attempt_catch("test_channel_123", "test_catch_user")
    assert success
    assert "caught" in message.lower()
    assert 'rat_data' in data
    assert 'loot' in data

@pytest.mark.asyncio
async def test_trader_system_basic(test_db):
    """Test basic trader system functionality"""
    from src.trader_system import TraderManager
    from src.player import Player
    
    # Create a player
    player = await Player.create("test_trader_user", "TraderUser")
    assert player is not None
    
    # Create trader manager
    trader_manager = TraderManager()
    
    # Test spawning a trader
    success = await trader_manager.spawn_trader("test_trader_channel", "basic")
    assert success
    
    # Test catching the trader
    success, message, data = await trader_manager.attempt_catch("test_trader_channel", "test_trader_user")
    assert success
    assert "trader" in message.lower()
    assert 'trader_type' in data
    assert data['trader_type'] == 'basic'

@pytest.mark.asyncio
async def test_dungeon_system_basic(test_db):
    """Test basic dungeon system functionality"""
    from src.dungeon_system import DungeonManager
    from src.player import Player
    from config.dungeons import ALL_DUNGEONS
    
    # Create a player
    player = await Player.create("test_dungeon_user", "DungeonUser")
    assert player is not None
    
    # Create dungeon manager
    dungeon_manager = DungeonManager()
    
    # Get a test dungeon
    test_dungeon = None
    for dungeon in ALL_DUNGEONS.values():
        if dungeon.level_requirement <= player.level:
            test_dungeon = dungeon
            break
    
    assert test_dungeon is not None, "No suitable test dungeon found"
    
    # Test creating a dungeon run
    run_data = await dungeon_manager.create_run(player.id, test_dungeon.id)
    assert run_data is not None
    assert run_data['current_floor'] == 1
    assert run_data['max_floors'] == test_dungeon.max_floors
    
    # Test getting active run
    active_run = await dungeon_manager.get_active_run(str(player.discord_id))
    assert active_run is not None
    assert active_run['dungeon_id'] == test_dungeon.id

@pytest.mark.asyncio
async def test_xp_and_leveling(test_db):
    """Test XP and leveling system"""
    from src.database import update_player_xp
    from src.player import Player
    from config.game_balance import XP_REQUIREMENTS
    
    # Create a player
    player = await Player.create("test_level_user", "LevelUser")
    assert player is not None
    
    # Test XP gain
    leveled_up = await update_player_xp("test_level_user", 100)
    assert leveled_up == True  # Should level up from 1 to 2
    
    # Get updated player
    player = await Player.get_by_discord_id("test_level_user")
    assert player.level == 2
    assert player.xp == 100
    assert player.stat_points > 0  # Should have gained stat points
    assert player.perk_points > 0  # Should have gained perk points

def test_configuration_integrity():
    """Test that all configurations work together properly"""
    from config.equipment import ALL_EQUIPMENT, get_random_loot
    from config.rat_types import ALL_RATS
    from config.dungeons import ALL_DUNGEONS
    from config.traders import TRADER_INVENTORIES
    
    # Test that equipment exists for all rarities mentioned in loot tables
    from config.equipment import LOOT_TABLES
    for rarity, loot_table in LOOT_TABLES.items():
        for item_id in loot_table.keys():
            assert item_id in ALL_EQUIPMENT, f"Item {item_id} in loot table but not in equipment"
    
    # Test that rats reference valid equipment
    for rat in ALL_RATS.values():
        for item_id in rat.loot_table.keys():
            assert item_id in ALL_EQUIPMENT, f"Rat {rat.name} references unknown item {item_id}"
    
    # Test that dungeon enemies exist
    for dungeon in ALL_DUNGEONS.values():
        for floor, enemies in dungeon.floor_enemies.items():
            for enemy in enemies:
                assert enemy.name, f"Dungeon {dungeon.name} floor {floor} has enemy without name"
                assert enemy.health > 0, f"Enemy {enemy.name} has invalid health"
                assert enemy.attack >= 0, f"Enemy {enemy.name} has invalid attack"
                assert enemy.defense >= 0, f"Enemy {enemy.name} has invalid defense"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])