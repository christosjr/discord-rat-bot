"""
Equipment Configuration
=====================
All equipment items, weapons, and spells.
Easy to add new equipment by editing this file.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random

class EquipmentSlot(Enum):
    WEAPON = "weapon"
    HEAD = "head"
    BODY = "body"
    RING = "ring"
    TAIL_RING = "tail_ring"
    NECK = "neck"
    BOOTS = "boots"

class EquipmentRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EquipmentType(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"
    ARMOR = "armor"
    ACCESSORY = "accessory"

@dataclass
class Equipment:
    id: str
    name: str
    slot: EquipmentSlot
    rarity: EquipmentRarity
    equipment_type: EquipmentType
    element: str = "none"  # fire, ice, lightning, etc.
    stats: Dict[str, int] = None
    special_effect: str = ""
    description: str = ""
    level_requirement: int = 1
    price: int = 0

# Initialize default stats
Equipment.__dataclass_fields__['stats'].default_factory = dict

# Weapons
WEAPONS = {
    # Basic Weapons
    "wooden_dagger": Equipment(
        id="wooden_dagger",
        name="Wooden Dagger",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.MELEE,
        stats={"attack": 5, "speed": 2},
        description="A simple dagger made of wood. Better than nothing."
    ),
    
    "iron_sword": Equipment(
        id="iron_sword", 
        name="Iron Sword",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.MELEE,
        stats={"attack": 8, "strength": 1},
        description="A reliable iron sword. Good for beginners."
    ),
    
    "basic_bow": Equipment(
        id="basic_bow",
        name="Basic Bow", 
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.RANGED,
        stats={"ranged_attack": 6, "agility": 1},
        description="A simple wooden bow. Allows ranged attacks."
    ),
    
    "training_staff": Equipment(
        id="training_staff",
        name="Training Staff",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.COMMON, 
        equipment_type=EquipmentType.MAGIC,
        stats={"magic_attack": 5, "intelligence": 2},
        description="A staff for practicing magic spells."
    ),
    
    # Fire Weapons
    "flame_dagger": Equipment(
        id="flame_dagger",
        name="Flame Dagger",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.MELEE,
        element="fire",
        stats={"attack": 12, "fire_damage": 5},
        special_effect="Ignite: 20% chance to burn enemy for 3 turns",
        description="A dagger that burns with eternal flame."
    ),
    
    "fire_bow": Equipment(
        id="fire_bow",
        name="Fire Bow",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.RANGED,
        element="fire", 
        stats={"ranged_attack": 10, "fire_damage": 4},
        special_effect="Flame Arrows: All attacks deal fire damage",
        description="A bow that shoots flaming arrows."
    ),
    
    "fire_staff": Equipment(
        id="fire_staff",
        name="Fire Staff",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.MAGIC,
        element="fire",
        stats={"magic_attack": 12, "fire_spell_power": 8},
        special_effect="Fire Mastery: +20% fire spell effectiveness",
        description="A staff that channels fire magic."
    ),
    
    # Ice Weapons  
    "frost_blade": Equipment(
        id="frost_blade",
        name="Frost Blade",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.MELEE,
        element="ice",
        stats={"attack": 11, "ice_damage": 5},
        special_effect="Freeze: 25% chance to freeze enemy for 2 turns",
        description="A blade that cuts with winter's chill."
    ),
    
    "ice_staff": Equipment(
        id="ice_staff",
        name="Ice Staff",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.MAGIC,
        element="ice",
        stats={"magic_attack": 12, "ice_spell_power": 8},
        special_effect="Ice Mastery: +20% ice spell effectiveness",
        description="A staff that commands ice magic."
    ),
    
    # Epic Weapons
    "crystal_sword": Equipment(
        id="crystal_sword",
        name="Crystal Sword",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.EPIC,
        equipment_type=EquipmentType.MELEE,
        stats={"attack": 25, "magic_attack": 10, "all_stats": 3},
        special_effect="Crystal Clear: 30% chance to pierce all resistances",
        level_requirement=20,
        description="A sword made of pure crystal. Radiates magical energy."
    ),
    
    "dragon_slayer": Equipment(
        id="dragon_slayer",
        name="Dragon Slayer",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.LEGENDARY,
        equipment_type=EquipmentType.MELEE,
        stats={"attack": 50, "critical_chance": 15, "vs_dragon": 100},
        special_effect="Dragon Bane: 200% damage against dragon-type enemies",
        level_requirement=50,
        description="A legendary weapon forged to slay dragons."
    )
}

# Armor
ARMOR = {
    # Basic Armor
    "leather_vest": Equipment(
        id="leather_vest",
        name="Leather Vest",
        slot=EquipmentSlot.BODY,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.ARMOR,
        stats={"defense": 3, "agility": 1},
        description="Simple leather protection. Lightweight and flexible."
    ),
    
    "cloth_robe": Equipment(
        id="cloth_robe",
        name="Cloth Robe",
        slot=EquipmentSlot.BODY,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.ARMOR,
        stats={"magic_resist": 5, "intelligence": 2},
        description="A simple robe for magical practitioners."
    ),
    
    "leather_boots": Equipment(
        id="leather_boots",
        name="Leather Boots",
        slot=EquipmentSlot.BOOTS,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.ARMOR,
        stats={"speed": 2, "agility": 1},
        description="Basic boots for moving quietly and quickly."
    ),
    
    # Fire Armor
    "flame_vest": Equipment(
        id="flame_vest",
        name="Flame Vest",
        slot=EquipmentSlot.BODY,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.ARMOR,
        element="fire",
        stats={"defense": 8, "fire_resist": 10, "fire_damage": 3},
        special_effect="Fire Ward: -50% fire damage taken",
        description="Armor woven with fire-resistant materials."
    ),
    
    # Epic Armor
    "phoenix_mail": Equipment(
        id="phoenix_mail",
        name="Phoenix Mail",
        slot=EquipmentSlot.BODY,
        rarity=EquipmentRarity.EPIC,
        equipment_type=EquipmentType.ARMOR,
        stats={"defense": 20, "fire_resist": 15, "vitality": 5},
        special_effect="Rising Again: Revive with 50% health once per dungeon",
        level_requirement=25,
        description="Armor that grants the power of the phoenix."
    )
}

# Accessories
ACCESSORIES = {
    # Rings
    "copper_ring": Equipment(
        id="copper_ring",
        name="Copper Ring",
        slot=EquipmentSlot.RING,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.ACCESSORY,
        stats={"all_stats": 1},
        description="A simple ring that provides a small boost to all stats."
    ),
    
    "fire_ring": Equipment(
        id="fire_ring",
        name="Fire Ring",
        slot=EquipmentSlot.RING,
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.ACCESSORY,
        element="fire",
        stats={"fire_damage": 5, "intelligence": 2},
        special_effect="Fire Bolt: Cast a fire bolt once per day",
        description="A ring that channels fire magic."
    ),
    
    "ring_of_power": Equipment(
        id="ring_of_power",
        name="Ring of Power",
        slot=EquipmentSlot.RING,
        rarity=EquipmentRarity.LEGENDARY,
        equipment_type=EquipmentType.ACCESSORY,
        stats={"all_stats": 10, "xp_bonus": 25},
        special_effect="Power Surge: Double all stats for 5 turns once per day",
        level_requirement=40,
        description="The One Ring... or maybe just a very powerful ring."
    ),
    
    # Tail Rings
    "basic_tail_ring": Equipment(
        id="basic_tail_ring",
        name="Basic Tail Ring",
        slot=EquipmentSlot.TAIL_RING,
        rarity=EquipmentRarity.COMMON,
        equipment_type=EquipmentType.ACCESSORY,
        stats={"luck": 1},
        description="A small ring for your cat's tail. Cute and lucky!"
    )
}

# Spells (magical equipment)
SPELLS = {
    "fire_bolt": Equipment(
        id="fire_bolt",
        name="Fire Bolt",
        slot=EquipmentSlot.WEAPON,  # Spells go in weapon slot
        rarity=EquipmentRarity.UNCOMMON,
        equipment_type=EquipmentType.MAGIC,
        element="fire",
        stats={"spell_power": 10},
        special_effect="Active: Deal 15 fire damage (3 turn cooldown)",
        description="A basic fire spell. Can be cast during combat."
    ),
    
    "ice_shield": Equipment(
        id="ice_shield",
        name="Ice Shield",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.RARE,
        equipment_type=EquipmentType.MAGIC,
        element="ice", 
        stats={"defense": 8, "ice_resist": 15},
        special_effect="Active: Gain 50% damage reduction for 5 turns (5 turn cooldown)",
        description="A protective ice spell that creates a barrier."
    ),
    
    "lightning_storm": Equipment(
        id="lightning_storm",
        name="Lightning Storm",
        slot=EquipmentSlot.WEAPON,
        rarity=EquipmentRarity.EPIC,
        equipment_type=EquipmentType.MAGIC,
        element="lightning",
        stats={"spell_power": 25, "agility": 5},
        special_effect="Active: Deal 30 lightning damage to all enemies (10 turn cooldown)",
        description="A powerful lightning spell that affects all foes."
    )
}

# All equipment combined
ALL_EQUIPMENT = {**WEAPONS, **ARMOR, **ACCESSORIES, **SPELLS}

# Loot tables for different rat rarities
LOOT_TABLES = {
    "common": {
        "leather_vest": 20,
        "wooden_dagger": 15,
        "basic_bow": 10,
        "copper_ring": 25,
        "leather_boots": 20,
        "basic_tail_ring": 10
    },
    "uncommon": {
        "flame_dagger": 15,
        "fire_bow": 10,
        "fire_staff": 12,
        "flame_vest": 15,
        "fire_ring": 20,
        "frost_blade": 15,
        "ice_staff": 13
    },
    "rare": {
        "crystal_sword": 10,
        "ice_shield": 15,
        "fire_ring": 25,
        "phoenix_mail": 15,
        "lightning_storm": 20,
        "ring_of_power": 5
    },
    "epic": {
        "crystal_sword": 15,
        "phoenix_mail": 20,
        "lightning_storm": 25,
        "ring_of_power": 10
    },
    "legendary": {
        "dragon_slayer": 30,
        "ring_of_power": 40,
        "phoenix_mail": 30
    }
}

def get_random_loot(rarity: str) -> List[str]:
    """Get random loot based on rarity"""
    table = LOOT_TABLES.get(rarity, LOOT_TABLES["common"])
    items = []
    for item_id, weight in table.items():
        if random.randint(1, 100) <= weight:
            items.append(item_id)
    return items