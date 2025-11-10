"""
Game Balance Configuration
=========================
All game balance values and progression curves.
Easy to adjust without code changes.
"""

from typing import Dict, List, Tuple

# XP progression - exponential growth
XP_REQUIREMENTS = {
    1: 0,      # Starting level
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    10: 2500,
    20: 10000,
    30: 25000,
    40: 50000,
    50: 100000,
    60: 200000,
    70: 400000,
    80: 800000,
    90: 1600000,
    100: 3200000
}

# XP rewards for different activities
XP_REWARDS = {
    'catch_common': 10,
    'catch_uncommon': 25,
    'catch_rare': 50,
    'catch_epic': 100,
    'catch_legendary': 200,
    'dungeon_completion': 500,
    'daily_quest': 100,
    'achievement': 250
}

# Wild rat spawn rates (percentages)
WILD_RAT_RATES = {
    'common': 70.0,
    'uncommon': 25.0,
    'rare': 4.5,
    'epic': 0.49,
    'legendary': 0.01
}

# Rat spawn timing
SPAWN_SETTINGS = {
    'min_interval_minutes': 10,
    'max_interval_minutes': 20,
    'trader_spawn_chance_percent': 15,
    'trader_spawn_interval_hours': 2,
    'trader_duration_minutes': 2
}

# Starting player stats
STARTING_STATS = {
    'level': 1,
    'xp': 0,
    'gold': 100,
    'stat_points': 0,
    'perk_points': 0,
    'strength': 5,
    'agility': 5,
    'intelligence': 5,
    'vitality': 5
}

# Stat growth per level
STAT_GROWTH = {
    'stat_points_per_level': 3,
    'perk_points_per_level': 1,
    'perk_points_dungeon_bonus': {
        'easy': 1,
        'medium': 2,
        'hard': 3,
        'extreme': 5
    }
}

# Inventory limits
INVENTORY_LIMITS = {
    'base_rat_slots': 50,
    'base_item_slots': 25,
    'expansion_cost_base': 100,
    'expansion_cost_increment': 50,
    'slots_per_expansion': 10
}

# Combat system
COMBAT_SETTINGS = {
    'base_damage_variance': 0.2,  # ±20% damage variance
    'critical_hit_chance_base': 0.05,  # 5% base crit
    'critical_hit_multiplier': 1.5,
    'dungeon_death_xp_penalty_percent': 10,
    'max_dungeon_floor_boss_chance': 0.3  # 30% chance of boss at final floor
}

# Trader system
TRADER_SETTINGS = {
    'spawn_rates': {
        'basic': 0.70,      # 70% of traders
        'rare_goods': 0.20, # 20% of traders
        'key_master': 0.08, # 8% of traders
        'master_artisan': 0.02 # 2% of traders
    },
    'restock_interval_hours': {
        'basic': 2,
        'rare_goods': 6,
        'key_master': 24,
        'master_artisan': 168  # Weekly
    },
    'price_markup': {
        'basic': 1.0,       # No markup
        'rare_goods': 1.2,  # 20% markup
        'key_master': 1.5,  # 50% markup
        'master_artisan': 2.0  # 100% markup
    }
}

# Death penalties by activity
DEATH_PENALTIES = {
    'dungeon': {
        'xp_loss_percent': 10,
        'gold_loss_percent': 0,
        'item_loss_chance': 0,
        'key_refund': True
    },
    'rare_encounter': {
        'xp_loss_percent': 5,
        'gold_loss_percent': 0,
        'item_loss_chance': 0
    }
}

# Achievement thresholds
ACHIEVEMENT_THRESHOLDS = {
    'rats_caught': [10, 50, 100, 500, 1000, 5000],
    'levels_gained': [5, 10, 25, 50, 75, 100],
    'dungeons_completed': [1, 5, 10, 25, 50, 100],
    'gold_earned': [1000, 5000, 10000, 50000, 100000, 500000]
}

# Rate limiting
RATE_LIMITS = {
    'catch_attempts_per_minute': 10,
    'dungeon_entries_per_hour': 5,
    'trade_per_minute': 3,
    'perk_allocation_per_minute': 2
}