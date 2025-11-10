"""
Rat Types Configuration
======================
All different rat types and their properties.
Easy to add new rats by editing this file.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ElementType(Enum):
    NONE = "none"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    EARTH = "earth"
    WIND = "wind"
    DARK = "dark"
    LIGHT = "light"
    POISON = "poison"

@dataclass
class RatType:
    name: str
    rarity: Rarity
    element: ElementType
    base_xp: int
    base_gold: int
    loot_table: Dict[str, int]  # item_id -> weight
    special_ability: str = ""
    description: str = ""
    spawn_conditions: Dict = None

# Wild rat types - can appear anywhere
WILD_RATS = {
    # Common Rats (70% of spawns)
    "sewer_rat": RatType(
        name="Sewer Rat",
        rarity=Rarity.COMMON,
        element=ElementType.NONE,
        base_xp=10,
        base_gold=5,
        loot_table={
            "basic_net": 30,
            "leather_boots": 20,
            "copper_ring": 25,
            "small_health_potion": 15,
            "rat_essence": 10
        },
        description="A common rat found in dark places. Offers basic rewards."
    ),
    
    "garden_rat": RatType(
        name="Garden Rat", 
        rarity=Rarity.COMMON,
        element=ElementType.EARTH,
        base_xp=12,
        base_gold=6,
        loot_table={
            "basic_net": 35,
            "garden_boots": 15,
            "nature_ring": 20,
            "herb": 20,
            "rat_essence": 10
        },
        description="A nature-loving rat. Slightly more rewarding than sewer rats."
    ),
    
    "city_rat": RatType(
        name="City Rat",
        rarity=Rarity.COMMON, 
        element=ElementType.NONE,
        base_xp=15,
        base_gold=8,
        loot_table={
            "basic_net": 30,
            "urban_boots": 20,
            "city_ring": 25,
            "coin_pouch": 15,
            "rat_essence": 10
        },
        description="An urban rat that's seen a thing or two. Better rewards than rural rats."
    ),
    
    # Uncommon Rats (25% of spawns)
    "fire_rat": RatType(
        name="Fire Rat",
        rarity=Rarity.UNCOMMON,
        element=ElementType.FIRE,
        base_xp=25,
        base_gold=15,
        loot_table={
            "fire_net": 25,
            "flame_boots": 20,
            "fire_ring": 25,
            "fire_crystal": 15,
            "flame_essence": 10,
            "fire_spell": 5
        },
        description="A rat with a fiery personality. Drops fire-related equipment."
    ),
    
    "ice_rat": RatType(
        name="Ice Rat",
        rarity=Rarity.UNCOMMON,
        element=ElementType.ICE,
        base_xp=25,
        base_gold=15,
        loot_table={
            "ice_net": 25,
            "frost_boots": 20,
            "frost_ring": 25,
            "ice_crystal": 15,
            "frost_essence": 10,
            "frost_spell": 5
        },
        description="A cold-blooded rat. Drops ice-related equipment."
    ),
    
    "lightning_rat": RatType(
        name="Lightning Rat",
        rarity=Rarity.UNCOMMON,
        element=ElementType.LIGHTNING,
        base_xp=30,
        base_gold=18,
        loot_table={
            "storm_net": 25,
            "storm_boots": 20,
            "storm_ring": 25,
            "storm_crystal": 15,
            "storm_essence": 10,
            "lightning_spell": 5
        },
        description="A fast rat that crackles with electricity."
    ),
    
    # Rare Rats (4.5% of spawns)
    "crystal_rat": RatType(
        name="Crystal Rat",
        rarity=Rarity.RARE,
        element=ElementType.LIGHT,
        base_xp=50,
        base_gold=40,
        loot_table={
            "crystal_net": 20,
            "crystal_boots": 25,
            "crystal_ring": 20,
            "large_crystal": 20,
            "crystal_essence": 10,
            "prism_spell": 5
        },
        description="A rat made partially of crystal. Very rare and valuable."
    ),
    
    "shadow_rat": RatType(
        name="Shadow Rat",
        rarity=Rarity.RARE,
        element=ElementType.DARK,
        base_xp=55,
        base_gold=45,
        loot_table={
            "shadow_net": 20,
            "shadow_boots": 25,
            "shadow_ring": 20,
            "shadow_crystal": 20,
            "dark_essence": 10,
            "stealth_spell": 5
        },
        description="A rat that seems to blend with the shadows."
    ),
    
    "ancient_rat": RatType(
        name="Ancient Rat",
        rarity=Rarity.RARE,
        element=ElementType.NONE,
        base_xp=60,
        base_gold=50,
        loot_table={
            "ancient_net": 15,
            "ancient_boots": 25,
            "ancient_ring": 25,
            "ancient_relic": 20,
            "wisdom_essence": 10,
            "time_spell": 5
        },
        description="A rat that's lived through many ages. Possesses ancient knowledge."
    ),
    
    # Epic Rats (0.49% of spawns)
    "dragon_rat": RatType(
        name="Dragon Rat",
        rarity=Rarity.EPIC,
        element=ElementType.FIRE,
        base_xp=100,
        base_gold=200,
        loot_table={
            "dragon_net": 10,
            "dragon_boots": 30,
            "dragon_ring": 25,
            "dragon_scale": 20,
            "dragon_essence": 10,
            "fire_breath_spell": 5
        },
        description="A rat with draconic heritage. Extremely dangerous but rewarding."
    ),
    
    "phoenix_rat": RatType(
        name="Phoenix Rat",
        rarity=Rarity.EPIC,
        element=ElementType.FIRE,
        base_xp=120,
        base_gold=250,
        loot_table={
            "phoenix_net": 5,
            "phoenix_boots": 25,
            "phoenix_ring": 30,
            "phoenix_feather": 25,
            "life_essence": 10,
            "revival_spell": 5
        },
        description="A mythical rat that rises from ashes. Can bring good fortune."
    ),
    
    # Legendary Rats (0.01% of spawns)
    "void_rat": RatType(
        name="Void Rat",
        rarity=Rarity.LEGENDARY,
        element=ElementType.DARK,
        base_xp=200,
        base_gold=1000,
        loot_table={
            "void_net": 1,
            "void_boots": 20,
            "void_ring": 25,
            "void_crystal": 30,
            "void_essence": 20,
            "reality_warp_spell": 4
        },
        description="A rat from beyond the void. Possesses reality-bending abilities."
    ),
    
    "time_rat": RatType(
        name="Time Rat",
        rarity=Rarity.LEGENDARY,
        element=ElementType.NONE,
        base_xp=250,
        base_gold=1500,
        loot_table={
            "time_net": 1,
            "temporal_boots": 20,
            "temporal_ring": 25,
            "time_crystal": 30,
            "temporal_essence": 20,
            "time_manipulation_spell": 4
        },
        description="A rat that exists outside of time. Can alter the flow of events."
    )
}

# Location-specific rats (appear in specific locations)
LOCATION_RATS = {
    "forest": {
        "tree_rat": RatType(
            name="Tree Rat",
            rarity=Rarity.UNCOMMON,
            element=ElementType.EARTH,
            base_xp=30,
            base_gold=20,
            loot_table={
                "wooden_boots": 30,
                "branch_weapon": 25,
                "forest_ring": 25,
                "wood_essence": 20
            }
        ),
        "camouflage_rat": RatType(
            name="Camouflage Rat",
            rarity=Rarity.RARE,
            element=ElementType.EARTH,
            base_xp=70,
            base_gold=60,
            loot_table={
                "stealth_boots": 25,
                "nature_sword": 20,
                "forest_mastery_ring": 25,
                "camouflage_essence": 20,
                "invisibility_spell": 10
            }
        )
    },
    "cave": {
        "crystal_rat_variant": RatType(
            name="Deep Crystal Rat",
            rarity=Rarity.RARE,
            element=ElementType.LIGHT,
            base_xp=80,
            base_gold=70,
            loot_table={
                "deep_crystal_boots": 25,
                "crystal_blade": 20,
                "crystal_mastery_ring": 25,
                "pure_crystal": 20,
                "crystal_vision_spell": 10
            }
        )
    }
}

# Special event rats
EVENT_RATS = {
    "holiday_santa_rat": RatType(
        name="Santa Rat",
        rarity=Rarity.LEGENDARY,
        element=ElementType.LIGHT,
        base_xp=500,
        base_gold=5000,
        loot_table={
            "santa_hat": 30,
            "christmas_boots": 25,
            "holiday_ring": 25,
            "christmas_crystal": 15,
            "gift_essence": 5
        },
        description="🎄 A magical rat that only appears during the holidays!",
        spawn_conditions={"event": "christmas", "time": "december"}
    ),
    
    "halloween_spook_rat": RatType(
        name="Spooky Rat",
        rarity=Rarity.EPIC,
        element=ElementType.DARK,
        base_xp=150,
        base_gold=300,
        loot_table={
            "spooky_costume": 30,
            "halloween_boots": 25,
            "fright_ring": 25,
            "pumpkin_crystal": 15,
            "fright_essence": 5
        },
        description="🎃 A rat that loves Halloween! BOO!",
        spawn_conditions={"event": "halloween", "time": "october"}
    )
}

# All rats in one place
ALL_RATS = {**WILD_RATS, **LOCATION_RATS, **EVENT_RATS}