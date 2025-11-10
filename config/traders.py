"""
Trader Configuration
===================
Defines all trader types and their inventory.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random

@dataclass
class TraderItem:
    item_id: str
    price: int
    stock: int
    description: str = ""

class TraderType(Enum):
    BASIC = "basic"
    RARE_GOODS = "rare_goods"
    KEY_MASTER = "key_master"
    MASTER_ARTISAN = "master_artisan"

# Trader inventories - what they sell
TRADER_INVENTORIES = {
    TraderType.BASIC: {
        "basic_net": TraderItem("basic_net", 15, 10),
        "leather_vest": TraderItem("leather_vest", 25, 5),
        "copper_ring": TraderItem("copper_ring", 10, 15),
        "leather_boots": TraderItem("leather_boots", 20, 8),
        "basic_tail_ring": TraderItem("basic_tail_ring", 5, 20),
        "wooden_dagger": TraderItem("wooden_dagger", 30, 3),
        "basic_bow": TraderItem("basic_bow", 35, 3),
        "training_staff": TraderItem("training_staff", 30, 3),
        "small_health_potion": TraderItem("small_health_potion", 5, 50),
        "rat_essence": TraderItem("rat_essence", 3, 100)
    },
    
    TraderType.RARE_GOODS: {
        "flame_dagger": TraderItem("flame_dagger", 150, 2),
        "fire_bow": TraderItem("fire_bow", 180, 2),
        "fire_staff": TraderItem("fire_staff", 200, 2),
        "frost_blade": TraderItem("frost_blade", 120, 2),
        "ice_staff": TraderItem("ice_staff", 150, 2),
        "flame_vest": TraderItem("flame_vest", 250, 1),
        "fire_ring": TraderItem("fire_ring", 100, 3),
        "crystal_sword": TraderItem("crystal_sword", 500, 1),
        "ice_shield": TraderItem("ice_shield", 300, 1),
        "fire_bolt": TraderItem("fire_bolt", 80, 5),
        "large_health_potion": TraderItem("large_health_potion", 25, 10),
        "magic_dust": TraderItem("magic_dust", 15, 20)
    },
    
    TraderType.KEY_MASTER: {
        "fire_dungeon_key": TraderItem("fire_dungeon_key", 500, 3),
        "ice_dungeon_key": TraderItem("ice_dungeon_key", 750, 2),
        "undead_dungeon_key": TraderItem("undead_dungeon_key", 1500, 1),
        "dragon_dungeon_key": TraderItem("dragon_dungeon_key", 5000, 1),
        "void_dungeon_key": TraderItem("void_dungeon_key", 20000, 1),
        "rare_crystal": TraderItem("rare_crystal", 200, 5),
        "master_key": TraderItem("master_key", 1000, 1)  # Opens any locked dungeon once
    },
    
    TraderType.MASTER_ARTISAN: {
        "dragon_slayer": TraderItem("dragon_slayer", 5000, 1),
        "phoenix_mail": TraderItem("phoenix_mail", 3000, 2),
        "ring_of_power": TraderItem("ring_of_power", 8000, 1),
        "lightning_storm": TraderItem("lightning_storm", 2000, 3),
        "custom_equipment_blueprint": TraderItem("custom_equipment_blueprint", 10000, 1),
        "legendary_crystal": TraderItem("legendary_crystal", 1000, 5),
        "void_equipment_material": TraderItem("void_equipment_material", 2000, 3),
        "time_crystal": TraderItem("time_crystal", 5000, 1)
    }
}

# What traders will buy from players (at 50% value)
TRADER_BUY_LISTS = {
    TraderType.BASIC: [
        "wooden_dagger", "basic_bow", "training_staff", "leather_vest", "copper_ring",
        "leather_boots", "basic_tail_ring", "small_health_potion", "rat_essence"
    ],
    
    TraderType.RARE_GOODS: [
        "flame_dagger", "fire_bow", "fire_staff", "frost_blade", "ice_staff",
        "flame_vest", "fire_ring", "crystal_sword", "ice_shield", "fire_bolt",
        "large_health_potion", "magic_dust"
    ],
    
    TraderType.KEY_MASTER: [
        "fire_dungeon_key", "ice_dungeon_key", "undead_dungeon_key", 
        "dragon_dungeon_key", "void_dungeon_key", "master_key"
    ],
    
    TraderType.MASTER_ARTISAN: [
        "dragon_slayer", "phoenix_mail", "ring_of_power", "lightning_storm",
        "legendary_crystal", "void_equipment_material", "time_crystal"
    ]
}

# Trader names and descriptions
TRADER_NAMES = {
    TraderType.BASIC: "Barter Rat",
    TraderType.RARE_GOODS: "Renaissance Rat",
    TraderType.KEY_MASTER: "Keykeeper Rat",
    TraderType.MASTER_ARTISAN: "Master Artisan Rat"
}

TRADER_DESCRIPTIONS = {
    TraderType.BASIC: "A friendly rat that deals in basic supplies and equipment.",
    TraderType.RARE_GOODS: "A sophisticated rat with access to rare and magical items.",
    TraderType.KEY_MASTER: "A mysterious rat that specializes in dungeon keys.",
    TraderType.MASTER_ARTISAN: "An ancient rat with access to the most legendary items."
}

# Dungeon keys mapping
DUNGEON_KEYS = {
    "fire_dungeon_key": {"dungeon": "burning_pits", "name": "Fire Dungeon Key"},
    "ice_dungeon_key": {"dungeon": "frost_cavern", "name": "Ice Dungeon Key"},
    "undead_dungeon_key": {"dungeon": "undead_catacombs", "name": "Undead Dungeon Key"},
    "dragon_dungeon_key": {"dungeon": "dragon_lair", "name": "Dragon Dungeon Key"},
    "void_dungeon_key": {"dungeon": "void_realm", "name": "Void Dungeon Key"},
    "master_key": {"dungeon": "any_locked", "name": "Master Key"}
}

# All trader types for easy access
TRADER_TYPES = {
    'basic': TraderType.BASIC,
    'rare_goods': TraderType.RARE_GOODS,
    'key_master': TraderType.KEY_MASTER,
    'master_artisan': TraderType.MASTER_ARTISAN
}

def get_trader_inventory(trader_type: str) -> Dict[str, TraderItem]:
    """Get inventory for a specific trader type"""
    trader_enum = TRADER_TYPES.get(trader_type)
    if trader_enum:
        return TRADER_INVENTORIES.get(trader_enum, {})
    return {}

def get_trader_buy_list(trader_type: str) -> List[str]:
    """Get what a trader will buy"""
    trader_enum = TRADER_TYPES.get(trader_type)
    if trader_enum:
        return TRADER_BUY_LISTS.get(trader_enum, [])
    return []

def get_random_special_offer(trader_type: str) -> Optional[Dict]:
    """Get a random special offer from a trader"""
    from config.equipment import ALL_EQUIPMENT
    
    inventory = get_trader_inventory(trader_type)
    if not inventory:
        return None
    
    # Special offers are high-value items with limited stock
    special_items = [
        item_id for item_id, item in inventory.items()
        if 'legendary' in item_id.lower() or 'epic' in item_id.lower()
    ]
    
    if special_items:
        item_id = random.choice(special_items)
        item = inventory[item_id]
        return {
            'item_id': item_id,
            'original_price': item.price,
            'special_price': int(item.price * 0.7),  # 30% off
            'stock': 1,  # Only one available
            'description': f"Special offer! 30% off {ALL_EQUIPMENT[item_id].name}!"
        }
    
    return None