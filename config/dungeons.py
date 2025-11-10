"""
Dungeon Configuration
====================
All dungeon definitions with different types and mechanics.
Easy to add new dungeons by editing this file.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random

class DungeonType(Enum):
    GENERIC = "generic"
    FIRE = "fire"
    ICE = "ice" 
    LIGHTNING = "lightning"
    EARTH = "earth"
    WIND = "wind"
    DARK = "dark"
    LIGHT = "light"
    POISON = "poison"
    UNDEAD = "undead"
    CRYSTAL = "crystal"
    DRAGON = "dragon"
    VOID = "void"
    TEMPORAL = "temporal"

class DungeonDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"

class DungeonTheme(Enum):
    CAVERNS = "caverns"
    FOREST = "forest"
    SWAMP = "swamp"
    MOUNTAIN = "mountain"
    RUINS = "ruins"
    TEMPLE = "temple"
    DUNGEON = "dungeon"
    REALM = "realm"

@dataclass
class Enemy:
    name: str
    health: int
    attack: int
    defense: int
    special_ability: str = ""
    element: str = "none"
    resistance: Dict[str, int] = None  # element -> resistance percentage
    
    def __post_init__(self):
        if self.resistance is None:
            self.resistance = {}

@dataclass
class Dungeon:
    id: str
    name: str
    description: str
    dungeon_type: DungeonType
    difficulty: DungeonDifficulty
    theme: DungeonTheme
    level_requirement: int
    access_fee: int
    max_floors: int
    floor_enemies: Dict[int, List[Enemy]]  # floor -> list of enemies
    boss_enemy: Enemy = None
    guaranteed_drops: List[str] = None
    drop_chances: Dict[str, int] = None  # item -> chance percentage
    special_mechanics: List[str] = None
    death_penalty: int = 10  # XP loss percentage
    completion_xp_bonus: int = 0

# Initialize default values
Dungeon.__dataclass_fields__['guaranteed_drops'].default_factory = list
Dungeon.__dataclass_fields__['drop_chances'].default_factory = dict
Dungeon.__dataclass_fields__['special_mechanics'].default_factory = list

# Common enemy templates
ENEMY_TEMPLATES = {
    # Basic enemies
    "sewer_rat_enemy": Enemy(
        name="Sewer Rat",
        health=30,
        attack=8,
        defense=2,
        element="none"
    ),
    
    "giant_rat_enemy": Enemy(
        name="Giant Rat",
        health=50,
        attack=12,
        defense=4,
        element="none"
    ),
    
    "rat_pack_enemy": Enemy(
        name="Rat Pack",
        health=40,
        attack=10,
        defense=3,
        special_ability="Pack Attack: 50% chance to attack twice",
        element="none"
    ),
    
    # Fire-type enemies
    "flame_rat_enemy": Enemy(
        name="Flame Rat",
        health=45,
        attack=15,
        defense=5,
        special_ability="Burn: 20% chance to ignite attacker",
        element="fire",
        resistance={"fire": 50, "ice": -25}  # Fire resistant, weak to ice
    ),
    
    "ember_rat_enemy": Enemy(
        name="Ember Rat",
        health=60,
        attack=18,
        defense=6,
        special_ability="Ignite: Burns the entire area",
        element="fire",
        resistance={"fire": 70, "ice": -50}
    ),
    
    "phoenix_rat_enemy": Enemy(
        name="Phoenix Rat",
        health=80,
        attack=25,
        defense=8,
        special_ability="Rebirth: Revives with 50% health when defeated",
        element="fire",
        resistance={"fire": 90, "ice": -75}
    ),
    
    # Ice-type enemies  
    "frost_rat_enemy": Enemy(
        name="Frost Rat",
        health=40,
        attack=10,
        defense=8,
        special_ability="Freeze: 25% chance to freeze attacker",
        element="ice",
        resistance={"ice": 50, "fire": -25}
    ),
    
    "crystal_rat_enemy": Enemy(
        name="Crystal Rat",
        health=70,
        attack=20,
        defense=15,
        special_ability="Crystal Shield: 30% damage reduction",
        element="ice",
        resistance={"ice": 80, "fire": -50}
    ),
    
    # Undead enemies
    "skeleton_rat_enemy": Enemy(
        name="Skeleton Rat",
        health=35,
        attack=12,
        defense=6,
        special_ability="Bone Throw: Ranged attack",
        element="undead",
        resistance={"undead": 50, "light": -50}  # Weak to light
    ),
    
    "zombie_rat_enemy": Enemy(
        name="Zombie Rat",
        health=60,
        attack=14,
        defense=4,
        special_ability="Infection: Spreads disease",
        element="undead",
        resistance={"undead": 60, "fire": 25, "light": -75}
    ),
    
    "lich_rat_enemy": Enemy(
        name="Lich Rat",
        health=100,
        attack=30,
        defense=12,
        special_ability="Death Curse: Curses the entire party",
        element="undead",
        resistance={"undead": 80, "fire": 50, "light": -100}
    ),
    
    # Dragon enemies
    "dragon_whelp_enemy": Enemy(
        name="Dragon Whelp",
        health=120,
        attack=35,
        defense=20,
        special_ability="Fire Breath: Area attack",
        element="fire",
        resistance={"fire": 80, "ice": -50, "physical": 50}
    ),
    
    "ancient_dragon_enemy": Enemy(
        name="Ancient Dragon Rat",
        health=200,
        attack=50,
        defense=30,
        special_ability="Dragon's Wrath: Devastating area attack",
        element="fire",
        resistance={"fire": 95, "ice": -75, "physical": 75}
    )
}

# Dungeon definitions
DUNGEONS = {
    # Early Game Dungeons (Levels 1-15)
    "sewer_crawl": Dungeon(
        id="sewer_crawl",
        name="Sewer Crawl",
        description="A basic dungeon in the city sewers. Good for beginners.",
        dungeon_type=DungeonType.GENERIC,
        difficulty=DungeonDifficulty.EASY,
        theme=DungeonTheme.CAVERNS,
        level_requirement=1,
        access_fee=0,  # Free for first dungeon
        max_floors=3,
        floor_enemies={
            1: [ENEMY_TEMPLATES["sewer_rat_enemy"]],
            2: [ENEMY_TEMPLATES["sewer_rat_enemy"], ENEMY_TEMPLATES["giant_rat_enemy"]],
            3: [ENEMY_TEMPLATES["rat_pack_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["giant_rat_enemy"],
        guaranteed_drops=["leather_vest", "wooden_dagger", "copper_ring"],
        drop_chances={"flame_dagger": 10, "fire_ring": 5},
        completion_xp_bonus=100
    ),
    
    "burning_pits": Dungeon(
        id="burning_pits",
        name="Burning Pits",
        description="A fiery dungeon where fire rats have made their home.",
        dungeon_type=DungeonType.FIRE,
        difficulty=DungeonDifficulty.EASY,
        theme=DungeonTheme.CAVERNS,
        level_requirement=5,
        access_fee=50,
        max_floors=4,
        floor_enemies={
            1: [ENEMY_TEMPLATES["sewer_rat_enemy"], ENEMY_TEMPLATES["flame_rat_enemy"]],
            2: [ENEMY_TEMPLATES["flame_rat_enemy"], ENEMY_TEMPLATES["flame_rat_enemy"]],
            3: [ENEMY_TEMPLATES["ember_rat_enemy"], ENEMY_TEMPLATES["flame_rat_enemy"]],
            4: [ENEMY_TEMPLATES["flame_rat_enemy"], ENEMY_TEMPLATES["ember_rat_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["ember_rat_enemy"],
        guaranteed_drops=["flame_vest", "flame_dagger", "fire_ring"],
        drop_chances={"fire_staff": 15, "phoenix_mail": 5},
        special_mechanics=["Fire resistance required for best results"],
        death_penalty=5
    ),
    
    "frost_cavern": Dungeon(
        id="frost_cavern",
        name="Frost Cavern",
        description="A cold dungeon filled with ice rats and crystal formations.",
        dungeon_type=DungeonType.ICE,
        difficulty=DungeonDifficulty.MEDIUM,
        theme=DungeonTheme.CAVERNS,
        level_requirement=10,
        access_fee=100,
        max_floors=5,
        floor_enemies={
            1: [ENEMY_TEMPLATES["frost_rat_enemy"]],
            2: [ENEMY_TEMPLATES["frost_rat_enemy"], ENEMY_TEMPLATES["crystal_rat_enemy"]],
            3: [ENEMY_TEMPLATES["crystal_rat_enemy"], ENEMY_TEMPLATES["frost_rat_enemy"]],
            4: [ENEMY_TEMPLATES["crystal_rat_enemy"], ENEMY_TEMPLATES["crystal_rat_enemy"]],
            5: [ENEMY_TEMPLATES["crystal_rat_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["crystal_rat_enemy"],
        guaranteed_drops=["frost_vest", "frost_blade", "ice_shield"],
        drop_chances={"ice_staff": 20, "crystal_sword": 10},
        special_mechanics=["Ice spells are more effective", "Crystal formations can provide cover"],
        death_penalty=10
    ),
    
    # Mid Game Dungeons (Levels 16-35)
    "undead_catacombs": Dungeon(
        id="undead_catacombs",
        name="Undead Catacombs",
        description="Ancient catacombs haunted by undead rats. Light magic is effective here.",
        dungeon_type=DungeonType.UNDEAD,
        difficulty=DungeonDifficulty.MEDIUM,
        theme=DungeonTheme.RUINS,
        level_requirement=15,
        access_fee=200,
        max_floors=6,
        floor_enemies={
            1: [ENEMY_TEMPLATES["skeleton_rat_enemy"]],
            2: [ENEMY_TEMPLATES["skeleton_rat_enemy"], ENEMY_TEMPLATES["zombie_rat_enemy"]],
            3: [ENEMY_TEMPLATES["zombie_rat_enemy"], ENEMY_TEMPLATES["skeleton_rat_enemy"]],
            4: [ENEMY_TEMPLATES["zombie_rat_enemy"], ENEMY_TEMPLATES["zombie_rat_enemy"]],
            5: [ENEMY_TEMPLATES["skeleton_rat_enemy"], ENEMY_TEMPLATES["zombie_rat_enemy"]],
            6: [ENEMY_TEMPLATES["zombie_rat_enemy"], ENEMY_TEMPLATES["skeleton_rat_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["lich_rat_enemy"],
        guaranteed_drops=["bone_armor", "undead_slayer", "holy_ring"],
        drop_chances={"light_staff": 15, "phoenix_mail": 8},
        special_mechanics=["Light spells deal double damage", "Undead are vulnerable to fire"],
        death_penalty=15
    ),
    
    "dragon_lair": Dungeon(
        id="dragon_lair",
        name="Dragon's Lair",
        description="The dangerous lair of a dragon. Requires powerful equipment.",
        dungeon_type=DungeonType.DRAGON,
        difficulty=DungeonDifficulty.HARD,
        theme=DungeonTheme.CAVERNS,
        level_requirement=25,
        access_fee=500,
        max_floors=7,
        floor_enemies={
            1: [ENEMY_TEMPLATES["flame_rat_enemy"], ENEMY_TEMPLATES["ember_rat_enemy"]],
            2: [ENEMY_TEMPLATES["ember_rat_enemy"], ENEMY_TEMPLATES["ember_rat_enemy"]],
            3: [ENEMY_TEMPLATES["phoenix_rat_enemy"], ENEMY_TEMPLATES["ember_rat_enemy"]],
            4: [ENEMY_TEMPLATES["phoenix_rat_enemy"], ENEMY_TEMPLATES["phoenix_rat_enemy"]],
            5: [ENEMY_TEMPLATES["dragon_whelp_enemy"]],
            6: [ENEMY_TEMPLATES["dragon_whelp_enemy"], ENEMY_TEMPLATES["phoenix_rat_enemy"]],
            7: [ENEMY_TEMPLATES["dragon_whelp_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["ancient_dragon_enemy"],
        guaranteed_drops=["dragon_scale", "fire_resist_armor", "dragon_slayer"],
        drop_chances={"phoenix_mail": 25, "void_boots": 10},
        special_mechanics=["Extreme fire resistance required", "Lava traps on some floors"],
        death_penalty=25
    ),
    
    # Late Game Dungeons (Levels 36+)
    "void_realm": Dungeon(
        id="void_realm",
        name="Void Realm",
        description="A reality-bending dungeon from beyond the void. Extremely dangerous.",
        dungeon_type=DungeonType.VOID,
        difficulty=DungeonDifficulty.EXTREME,
        theme=DungeonTheme.REALM,
        level_requirement=40,
        access_fee=2000,
        max_floors=10,
        floor_enemies={
            1: [ENEMY_TEMPLATES["shadow_rat_enemy"]],
            2: [ENEMY_TEMPLATES["shadow_rat_enemy"], ENEMY_TEMPLATES["void_rat_enemy"]],
            3: [ENEMY_TEMPLATES["void_rat_enemy"]],
            4: [ENEMY_TEMPLATES["void_rat_enemy"], ENEMY_TEMPLATES["shadow_rat_enemy"]],
            5: [ENEMY_TEMPLATES["void_rat_enemy"], ENEMY_TEMPLATES["void_rat_enemy"]],
            6: [ENEMY_TEMPLATES["time_rat_enemy"]],
            7: [ENEMY_TEMPLATES["time_rat_enemy"], ENEMY_TEMPLATES["void_rat_enemy"]],
            8: [ENEMY_TEMPLATES["time_rat_enemy"], ENEMY_TEMPLATES["time_rat_enemy"]],
            9: [ENEMY_TEMPLATES["time_rat_enemy"], ENEMY_TEMPLATES["void_rat_enemy"]],
            10: [ENEMY_TEMPLATES["time_rat_enemy"], ENEMY_TEMPLATES["void_rat_enemy"]]
        },
        boss_enemy=ENEMY_TEMPLATES["time_rat_enemy"],
        guaranteed_drops=["void_crystal", "reality_anchor", "time_manipulator"],
        drop_chances={"ring_of_power": 20, "dragon_slayer": 15},
        special_mechanics=["Reality constantly shifts", "Time flows differently", "Standard rules may not apply"],
        death_penalty=50,
        completion_xp_bonus=1000
    )
}

# Dungeon key requirements for locked dungeons
DUNGEON_KEYS = {
    "burning_pits": {
        "name": "Fire Dungeon Key",
        "price": 100,
        "description": "Opens access to fire-based dungeons"
    },
    "frost_cavern": {
        "name": "Ice Dungeon Key", 
        "price": 250,
        "description": "Opens access to ice-based dungeons"
    },
    "undead_catacombs": {
        "name": "Undead Dungeon Key",
        "price": 500,
        "description": "Opens access to undead dungeons"
    },
    "dragon_lair": {
        "name": "Dragon Dungeon Key",
        "price": 2000,
        "description": "Opens access to dragon dungeons"
    },
    "void_realm": {
        "name": "Void Dungeon Key",
        "price": 10000,
        "description": "Opens access to the most dangerous dungeons"
    }
}

# All dungeons in one place
ALL_DUNGEONS = DUNGEONS

def get_dungeon_by_id(dungeon_id: str) -> Dungeon:
    """Get a dungeon by its ID"""
    return ALL_DUNGEONS.get(dungeon_id)

def get_available_dungeons_for_level(level: int) -> List[Dungeon]:
    """Get all dungeons a player of this level can access"""
    available = []
    for dungeon in ALL_DUNGEONS.values():
        if level >= dungeon.level_requirement:
            available.append(dungeon)
    return available

def get_dungeon_recommendations(player_level: int, recent_dungeons: List[str] = None) -> List[Dungeon]:
    """Get recommended dungeons for a player"""
    available = get_available_dungeons_for_level(player_level)
    if not recent_dungeons:
        return available[:3]  # First 3 available
    
    # Recommend dungeons not recently completed
    recommendations = [d for d in available if d.id not in recent_dungeons]
    return recommendations[:3] if recommendations else available[:3]