"""
Player Commands
===============
Commands for character creation and management.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio

from src.player import Player
from src.database import get_or_create_player
from config.game_balance import STARTING_STATS

class PlayerCommands(commands.Cog):
    """Player character management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='create', aliases=['start', 'new'])
    async def create_character(self, ctx, *, character_name: str = None):
        """Create a new character with optional name"""
        try:
            # Check if player already exists
            existing_player = await Player.get_by_discord_id(str(ctx.author.id))
            if existing_player:
                await ctx.send("❌ You already have a character! Use `!stats` to view your character.")
                return
            
            # Create new character with name and random cat emoji
            player_data = await get_or_create_player(str(ctx.author.id), ctx.author.name, character_name)
            if not player_data:
                await ctx.send("❌ Failed to create character. Please try again.")
                return
            
            # Get the created player's data for display
            player = Player(player_data)
            
            # Send welcome message with cat theme
            embed = discord.Embed(
                title=f"{player.cat_emoji} Welcome to Rat Catching Adventure!",
                description=f"Your cat `{player.name}` has been created successfully!",
                color=0x00ff00
            )
            
            # Use cat-themed stats display
            embed.add_field(name="🏆 Level", value=f"{STARTING_STATS['level']}", inline=True)
            embed.add_field(name="💰 Gold", value=f"{STARTING_STATS['gold']}", inline=True)
            embed.add_field(name="⭐ XP", value=f"{STARTING_STATS['xp']}", inline=True)
            embed.add_field(name="💪 Strength", value=f"{STARTING_STATS['strength']}", inline=True)
            embed.add_field(name="🏃 Agility", value=f"{STARTING_STATS['agility']}", inline=True)
            embed.add_field(name="🧠 Intelligence", value=f"{STARTING_STATS['intelligence']}", inline=True)
            embed.add_field(name="❤️ Vitality", value=f"{STARTING_STATS['vitality']}", inline=True)
            
            embed.add_field(
                name="🎮 Next Steps",
                value="1. Use `!catch` to catch wild rats\n2. Use `!stats` to view your character\n3. Use `!help` to see all commands",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error creating character: {e}")
    
    @commands.command(name='stats', aliases=['stat', 'character'])
    async def view_stats(self, ctx):
        """View your character stats"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            # Get current level progress
            current_xp, needed_xp = player.get_level_progress()
            
            # Get total stats including equipment
            total_stats = player.get_total_stats()
            combat_stats = player.get_combat_stats()
            
            # Create embed with cat theme
            embed = discord.Embed(
                title=f"{player.cat_emoji} {player.name}'s Profile",
                description="A proud cat in the rat-catching world!",
                color=0x0099ff
            )
            
            # Basic info
            embed.add_field(name="🏆 Level", value=str(player.level), inline=True)
            embed.add_field(name="💰 Gold", value=str(player.gold), inline=True)
            embed.add_field(name="⭐ XP", value=f"{current_xp}/{needed_xp}", inline=True)
            
            # Progress bar
            progress_bar = "▓" * int((current_xp / needed_xp) * 10) + "░" * (10 - int((current_xp / needed_xp) * 10))
            embed.add_field(name="XP Progress", value=progress_bar, inline=False)
            
            # Stat points
            embed.add_field(name="📈 Stat Points", value=str(player.stat_points), inline=True)
            embed.add_field(name="🌟 Perk Points", value=str(player.perk_points), inline=True)
            
            # Base stats with cat theme
            embed.add_field(name="💪 Purr Strength", value=str(total_stats['strength']), inline=True)
            embed.add_field(name="🏃 Leaping Agility", value=str(total_stats['agility']), inline=True)
            embed.add_field(name="🧠 Cat Intelligence", value=str(total_stats['intelligence']), inline=True)
            embed.add_field(name="❤️ Nine Lives Vitality", value=str(total_stats['vitality']), inline=True)
            
            # Combat stats with cat theme
            embed.add_field(name="⚔️ Paw Combat", value=str(combat_stats['attack']), inline=True)
            embed.add_field(name="🏹 Claw Marksman", value=str(combat_stats['ranged_attack']), inline=True)
            embed.add_field(name="🪄 Cat Magic", value=str(combat_stats['magic_attack']), inline=True)
            embed.add_field(name="🛡️ Fur Shield", value=str(combat_stats['defense']), inline=True)
            embed.add_field(name="⚡ Reflex Speed", value=str(combat_stats['speed']), inline=True)
            embed.add_field(name="❤️ Purr Health", value=str(combat_stats['health']), inline=True)
            embed.add_field(name="🔮 Purr Magic", value=str(combat_stats['mana']), inline=True)
            embed.add_field(name="💥 Whiskers Critical", value=f"{combat_stats['critical_chance']}%", inline=True)
            
            # Equipment slots
            equipment_text = []
            slot_emojis = {
                'weapon': '⚔️',
                'head': '🪖',
                'body': '🛡️', 
                'ring': '💍',
                'tail_ring': '💍',
                'neck': '📿',
                'boots': '👢'
            }
            
            for slot_name, equipment_item in player.equipment.__dict__.items():
                if equipment_item:
                    # Check if it's a dict with 'data' or a direct object
                    if isinstance(equipment_item, dict) and 'data' in equipment_item:
                        item_name = equipment_item['data'].name
                    elif hasattr(equipment_item, 'name'):
                        item_name = equipment_item.name
                    else:
                        item_name = str(equipment_item)
                    equipment_text.append(f"{slot_emojis.get(slot_name, '📦')} **{slot_name.replace('_', ' ').title()}:** {item_name}")
                else:
                    equipment_text.append(f"{slot_emojis.get(slot_name, '📦')} **{slot_name.replace('_', ' ').title()}:** [Empty]")
            
            if equipment_text:
                embed.add_field(name="👕 Equipment", value="\n".join(equipment_text), inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error viewing stats: {e}")
    
    @commands.command(name='inventory', aliases=['inv', 'items'])
    async def view_inventory(self, ctx, page: int = 1):
        """View your inventory"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            if not player.inventory:
                await ctx.send("📦 Your inventory is empty. Catch some rats to get items!")
                return
            
            # Paginate inventory (10 items per page)
            items_per_page = 10
            total_pages = (len(player.inventory) + items_per_page - 1) // items_per_page
            page = max(1, min(page, total_pages))
            
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_items = player.inventory[start_idx:end_idx]
            
            # Create embed
            embed = discord.Embed(
                title=f"📦 {ctx.author.display_name}'s Inventory",
                description=f"Page {page} of {total_pages}",
                color=0x9966cc
            )
            
            # Show equipment slots
            equipment_text = []
            for slot_name, equipment_item in player.equipment.__dict__.items():
                if equipment_item and 'data' in equipment_item:
                    equipment_text.append(f"**{slot_name.title()}:** {equipment_item['data'].name}")
                else:
                    equipment_text.append(f"**{slot_name.title()}:** Empty")
            
            embed.add_field(name="👕 Equipment", value="\n".join(equipment_text), inline=False)
            
            # Show inventory items
            items_text = []
            for item in page_items:
                from config.equipment import ALL_EQUIPMENT
                item_data = ALL_EQUIPMENT.get(item['item_id'])
                if item_data:
                    items_text.append(f"• **{item_data.name}** x{item['quantity']}")
                else:
                    items_text.append(f"• **{item['item_id']}** x{item['quantity']}")
            
            if items_text:
                embed.add_field(name="🎒 Items", value="\n".join(items_text), inline=False)
            else:
                embed.add_field(name="🎒 Items", value="No items on this page", inline=False)
            
            # Show inventory capacity
            from config.game_balance import INVENTORY_LIMITS
            base_slots = INVENTORY_LIMITS['base_item_slots']
            used_slots = len([item for item in player.inventory if item['quantity'] > 0])
            embed.add_field(name="📊 Storage", value=f"{used_slots}/{base_slots} slots used", inline=True)
            
            # Navigation help
            if total_pages > 1:
                embed.set_footer(text=f"Use !inventory {page + 1} for next page")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error viewing inventory: {e}")
    
    @commands.command(name='allocate', aliases=['alloc'])
    async def allocate_stat_point(self, ctx, stat: str = None):
        """Allocate a stat point"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            if player.stat_points <= 0:
                await ctx.send("❌ You don't have any stat points! Level up to earn more.")
                return
            
            if not stat:
                # Show current stats and available points
                total_stats = player.get_total_stats()
                
                embed = discord.Embed(
                    title="📈 Allocate Stat Points",
                    description=f"You have **{player.stat_points}** stat points to allocate",
                    color=0xff6600
                )
                
                embed.add_field(name="💪 Strength", value=str(total_stats['strength']), inline=True)
                embed.add_field(name="🏃 Agility", value=str(total_stats['agility']), inline=True)
                embed.add_field(name="🧠 Intelligence", value=str(total_stats['intelligence']), inline=True)
                embed.add_field(name="❤️ Vitality", value=str(total_stats['vitality']), inline=True)
                
                embed.add_field(
                    name="📋 Usage",
                    value="`!allocate strength` - Allocate to Strength\n`!allocate agility` - Allocate to Agility\n`!allocate intelligence` - Allocate to Intelligence\n`!allocate vitality` - Allocate to Vitality",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            # Validate stat name
            stat = stat.lower()
            if stat not in ['strength', 'agility', 'intelligence', 'vitality']:
                await ctx.send("❌ Invalid stat! Use: strength, agility, intelligence, or vitality")
                return
            
            # Allocate point
            success = await player.allocate_stat_point(stat)
            if success:
                stat_name = stat.title()
                await ctx.send(f"✅ Allocated 1 point to {stat_name}! Use `!stats` to see the changes.")
            else:
                await ctx.send("❌ Failed to allocate stat point.")
            
        except Exception as e:
            await ctx.send(f"❌ Error allocating stat point: {e}")
    
    @commands.command(name='help', aliases=['h', 'commands'])
    async def show_help(self, ctx, command: str = None):
        """Show help information"""
        try:
            if not command:
                # General help
                embed = discord.Embed(
                    title="🐭 Discord Rat Bot Help",
                    description="A Discord bot for rat catching adventures!",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="🎆 Getting Started",
                    value="`!create [name]` - Create your cat character\n`!catch` - Catch wild rats\n`!stats` - View your cat's profile\n`!inventory` - See your items",
                    inline=False
                )
                
                embed.add_field(
                    name="⚔️ Combat & Progression",
                    value="`!dungeon` - Enter a dungeon\n`!stats` - View your stats\n`!allocate` - Allocate stat points\n`!perks` - Manage perks",
                    inline=False
                )
                
                embed.add_field(
                    name="💰 Economy",
                    value="`!trade` - Trade with wild rats\n`!shop` - View available shops\n`!sell` - Sell items for gold",
                    inline=False
                )
                
                embed.add_field(
                    name="🏆 Other",
                    value="`!achievements` - View achievements\n`!daily` - Check daily quests\n`!help [command]` - Get help for specific command",
                    inline=False
                )
                
                embed.add_field(
                    name="🔗 Links",
                    value="Need more help? Check the documentation or ask on the support server!",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                # Command-specific help
                command = command.lower()
                help_texts = {
                    'create': "**!create [name]** - Create a new cat character\nAliases: !start, !new\nCreates your character with a random cat emoji.\nOptionally provide a name, otherwise uses your Discord name.",
                    'catch': "**!catch** - Catch wild rats\nThe bot will occasionally spawn wild rats. Be the first to catch them for rewards!",
                    'stats': "**!stats** - View character stats\nAliases: !stat, !character\nShows your level, stats, equipment, and progress.",
                    'inventory': "**!inventory [page]** - View your inventory\nAliases: !inv, !items\nShows your equipment and items. Use page number to navigate.",
                    'allocate': "**!allocate [stat]** - Allocate stat points\nAlias: !alloc\nAllocate stat points to strength, agility, intelligence, or vitality.",
                    'dungeon': "**!dungeon** - Enter a dungeon\nStarts a dungeon run with turn-based combat against rats.",
                    'help': "**!help [command]** - Show help\nAliases: !h, !commands\nShows this help message or help for a specific command."
                }
                
                help_text = help_texts.get(command, f"No help available for '{command}'")
                await ctx.send(help_text)
            
        except Exception as e:
            await ctx.send(f"❌ Error showing help: {e}")