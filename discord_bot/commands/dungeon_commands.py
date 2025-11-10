"""
Dungeon Commands
===============
Commands for dungeon exploration and combat.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio
import random

from src.player import Player
from src.dungeon_system import dungeon_manager
from config.dungeons import ALL_DUNGEONS, DUNGEON_KEYS

class DungeonCommands(commands.Cog):
    """Dungeon exploration commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='dungeon', aliases=['dungeon-enter', 'enter-dungeon'])
    async def enter_dungeon(self, ctx, dungeon_name: str = None):
        """Enter a dungeon"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            if not dungeon_name:
                # Show available dungeons
                await self._show_available_dungeons(ctx, player)
                return
            
            # Check if already in a dungeon
            existing_run = await dungeon_manager.get_active_run(str(ctx.author.id))
            if existing_run:
                await ctx.send("❌ You're already in a dungeon! Use `!dungeon continue` to continue.")
                return
            
            # Find dungeon
            dungeon = None
            for d in ALL_DUNGEONS.values():
                if dungeon_name.lower() in d.name.lower() or dungeon_name.lower() == d.id:
                    dungeon = d
                    break
            
            if not dungeon:
                available_names = [d.name for d in ALL_DUNGEONS.values() if player.level >= d.level_requirement]
                await ctx.send(f"❌ Dungeon '{dungeon_name}' not found!\nAvailable dungeons: {', '.join(available_names)}")
                return
            
            # Check level requirement
            if player.level < dungeon.level_requirement:
                await ctx.send(f"❌ You need to be level {dungeon.level_requirement} to enter {dungeon.name}!")
                return
            
            # Check access fee
            if player.gold < dungeon.access_fee:
                await ctx.send(f"❌ You need {dungeon.access_fee} gold to enter {dungeon.name}!")
                return
            
            # Check if dungeon requires a key
            if dungeon.id in DUNGEON_KEYS:
                # This is a locked dungeon, check for key
                key_item_id = f"{dungeon.id.replace('_', '_')}_key"
                if player.get_inventory_count(key_item_id) <= 0:
                    key_info = DUNGEON_KEYS[dungeon.id]
                    await ctx.send(f"🔑 {dungeon.name} is locked! You need a {key_info['name']} (costs {key_info['price']} gold) from a Key Master trader.")
                    return
            
            # Pay entrance fee (if not using key)
            if dungeon.access_fee > 0:
                success = await player.spend_gold(dungeon.access_fee)
                if not success:
                    await ctx.send("❌ Failed to pay entrance fee!")
                    return
            
            # Create dungeon run
            run_data = await dungeon_manager.create_run(player.id, dungeon.id)
            if not run_data:
                await ctx.send("❌ Failed to create dungeon run!")
                return
            
            # Show dungeon introduction
            await self._show_dungeon_intro(ctx, dungeon, run_data)
            
        except Exception as e:
            await ctx.send(f"❌ Error entering dungeon: {e}")
    
    @commands.command(name='dungeon-continue', aliases=['dc', 'continue'])
    async def continue_dungeon(self, ctx):
        """Continue current dungeon run"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet!")
                return
            
            # Get active run
            run_data = await dungeon_manager.get_active_run(str(ctx.author.id))
            if not run_data:
                await ctx.send("❌ You're not in a dungeon! Use `!dungeon` to enter one.")
                return
            
            # Get dungeon data
            dungeon = ALL_DUNGEONS.get(run_data['dungeon_id'])
            if not dungeon:
                await ctx.send("❌ Dungeon data not found!")
                return
            
            # Show current floor
            await self._show_dungeon_floor(ctx, player, dungeon, run_data)
            
        except Exception as e:
            await ctx.send(f"❌ Error continuing dungeon: {e}")
    
    @commands.command(name='dungeon-attack', aliases=['attack', 'fight'])
    async def attack_enemy(self, ctx, action: str = None):
        """Attack in a dungeon"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet!")
                return
            
            # Get active run
            run_data = await dungeon_manager.get_active_run(str(ctx.author.id))
            if not run_data:
                await ctx.send("❌ You're not in a dungeon!")
                return
            
            if not action:
                await ctx.send("❌ Please specify an action: attack, defend, cast, or flee")
                return
            
            # Process combat action
            result = await dungeon_manager.process_combat_action(str(ctx.author.id), action.lower())
            if not result:
                await ctx.send("❌ Failed to process combat action!")
                return
            
            # Show combat result
            await self._show_combat_result(ctx, result)
            
        except Exception as e:
            await ctx.send(f"❌ Error in combat: {e}")
    
    async def _show_available_dungeons(self, ctx, player):
        """Show available dungeons for the player"""
        embed = discord.Embed(
            title="🏰 Available Dungeons",
            description="Choose a dungeon to enter!",
            color=0x8b4513
        )
        
        available_dungeons = [d for d in ALL_DUNGEONS.values() if player.level >= d.level_requirement]
        
        if not available_dungeons:
            embed.add_field(
                name="No Dungeons Available",
                value="Level up to unlock your first dungeon!",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        dungeon_texts = []
        for dungeon in available_dungeons:
            # Check if locked
            if dungeon.id in DUNGEON_KEYS:
                key_info = DUNGEON_KEYS[dungeon.id]
                dungeon_texts.append(
                    f"**{dungeon.name}** 🔑\n"
                    f"Level {dungeon.level_requirement} | {dungeon.difficulty.value.title()}\n"
                    f"Requires: {key_info['name']}\n"
                    f"Floors: {dungeon.max_floors}"
                )
            else:
                dungeon_texts.append(
                    f"**{dungeon.name}**\n"
                    f"Level {dungeon.level_requirement} | {dungeon.difficulty.value.title()}\n"
                    f"Fee: {dungeon.access_fee} gold | Floors: {dungeon.max_floors}"
                )
        
        embed.add_field(
            name="🏰 Dungeons",
            value="\n\n".join(dungeon_texts),
            inline=False
        )
        
        embed.add_field(
            name="📋 Usage",
            value="`!dungeon [dungeon_name]` - Enter a dungeon\n"
                  "`!dungeon-continue` - Continue current dungeon",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _show_dungeon_intro(self, ctx, dungeon, run_data):
        """Show dungeon introduction"""
        embed = discord.Embed(
            title=f"🏰 {dungeon.name}",
            description=dungeon.description,
            color=0x8b4513
        )
        
        embed.add_field(name="🎯 Difficulty", value=dungeon.difficulty.value.title(), inline=True)
        embed.add_field(name="📊 Floors", value=str(dungeon.max_floors), inline=True)
        embed.add_field(name="💀 Death Penalty", value=f"{dungeon.death_penalty}% XP loss", inline=True)
        
        # Show first enemies
        if 1 in dungeon.floor_enemies:
            enemies = dungeon.floor_enemies[1]
            enemy_names = [enemy.name for enemy in enemies]
            embed.add_field(name="👹 Floor 1 Enemies", value="\n".join(enemy_names), inline=False)
        
        embed.add_field(
            name="⚔️ Combat",
            value="Use `!dungeon-continue` to start exploring!\n"
                  "During combat: `attack`, `defend`, `cast`, or `flee`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _show_dungeon_floor(self, ctx, player, dungeon, run_data):
        """Show current dungeon floor"""
        current_floor = run_data['current_floor']
        
        embed = discord.Embed(
            title=f"🏰 {dungeon.name} - Floor {current_floor}",
            description=f"Dungeon Run: Floor {current_floor} of {dungeon.max_floors}",
            color=0x8b4513
        )
        
        # Show enemies on this floor
        if current_floor in dungeon.floor_enemies:
            enemies = dungeon.floor_enemies[current_floor]
            enemy_texts = []
            for enemy in enemies:
                enemy_texts.append(f"**{enemy.name}** - HP: {enemy.health}, ATK: {enemy.attack}, DEF: {enemy.defense}")
            
            embed.add_field(name="👹 Enemies", value="\n".join(enemy_texts), inline=False)
        else:
            embed.add_field(name="👹 Enemies", value="No enemies on this floor", inline=False)
        
        # Show player status
        combat_stats = player.get_combat_stats()
        embed.add_field(name="❤️ Your HP", value=str(combat_stats['health']), inline=True)
        embed.add_field(name="⚔️ Your Attack", value=str(combat_stats['attack']), inline=True)
        embed.add_field(name="🛡️ Your Defense", value=str(combat_stats['defense']), inline=True)
        
        # Show boss info if on final floor
        if current_floor == dungeon.max_floors and dungeon.boss_enemy:
            embed.add_field(
                name="👑 Boss Fight!",
                value=f"**{dungeon.boss_enemy.name}** awaits!",
                inline=False
            )
        
        embed.add_field(
            name="⚔️ Combat Actions",
            value="`!dungeon-attack attack` - Attack enemies\n"
                  "`!dungeon-attack defend` - Focus on defense\n"
                  "`!dungeon-attack cast` - Use magic/spells\n"
                  "`!dungeon-attack flee` - Try to escape",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _show_combat_result(self, ctx, result):
        """Show combat result"""
        embed = discord.Embed(
            title="⚔️ Combat Result",
            color=0xff0000 if result['player_hp'] <= 0 else 0x00ff00
        )
        
        if result['player_hp'] <= 0:
            # Player died
            embed.add_field(name="💀 You Died!", value="You've been defeated and forced to leave the dungeon.", inline=False)
            embed.add_field(name="📉 XP Lost", value=f"{result.get('xp_lost', 0)} XP", inline=True)
            embed.add_field(name="💰 Gold Lost", value=f"{result.get('gold_lost', 0)} gold", inline=True)
            
            embed.add_field(
                name="🔄 Next Steps",
                value="• Use `!stats` to check your progress\n• `!dungeon` to try another dungeon\n• Catch more rats to level up!",
                inline=False
            )
        else:
            # Combat continues
            embed.add_field(name="✅ Combat Success", value=f"You defeated an enemy!", inline=False)
            embed.add_field(name="❤️ Your HP", value=str(result['player_hp']), inline=True)
            embed.add_field(name="🏆 Enemies Defeated", value=str(result.get('enemies_defeated', 0)), inline=True)
            
            # Loot obtained
            if result.get('loot'):
                loot_text = "\n".join(result['loot'])
                embed.add_field(name="🎁 Loot", value=loot_text, inline=False)
            
            # XP gained
            if result.get('xp_gained'):
                embed.add_field(name="⭐ XP Gained", value=str(result['xp_gained']), inline=True)
            
            # Check if dungeon completed
            if result.get('dungeon_completed'):
                embed.add_field(
                    name="🎉 Dungeon Completed!",
                    value="Congratulations! You've completed the dungeon!",
                    inline=False
                )
                
                if result.get('completion_rewards'):
                    embed.add_field(name="🏆 Completion Rewards", value="\n".join(result['completion_rewards']), inline=False)
        
        await ctx.send(embed=embed)