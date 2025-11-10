"""
Game Commands
=============
Commands for core gameplay mechanics like catching and trading.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio

from src.player import Player
from src.catch_system import check_and_spawn_rat, get_channel_spawn_info
from src.trader_system import trader_manager
from config.equipment import ALL_EQUIPMENT
from config.traders import TRADER_NAMES, TRADER_TYPES

class GameCommands(commands.Cog):
    """Core game mechanics commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='catch', aliases=['grab'])
    async def catch_rat(self, ctx):
        """Catch a wild rat"""
        try:
            # Check for character
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            # Check if we should spawn a rat
            spawn_result = await check_and_spawn_rat(str(ctx.channel.id))
            
            # Try to catch
            success, message, data = await trader_manager.attempt_catch(str(ctx.channel.id), str(ctx.author.id))
            
            if not success:
                # Check if there's an active spawn that player missed
                spawn_info = await get_channel_spawn_info(str(ctx.channel.id))
                if spawn_info:
                    if 'expires_at' in spawn_info and spawn_info['expires_at'].timestamp() < asyncio.get_event_loop().time():
                        await ctx.send("⏰ Too late! The rat has already escaped.")
                    else:
                        await ctx.send(message)
                else:
                    # No active spawn, encourage the player
                    await ctx.send("😿 No wild rat in this channel right now. Keep an eye out - they spawn randomly!")
            else:
                # Successful catch
                embed = discord.Embed(
                    title="🎯 Catch Successful!",
                    description=message,
                    color=0x00ff00
                )
                
                # Add additional info if it's a trader
                if data.get('trader_type'):
                    embed.add_field(
                        name="🏪 Trading Available",
                        value="Use `!trade` to start trading with this merchant!",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error catching rat: {e}")
    
    @commands.command(name='trade', aliases=['shop', 'merchant'])
    async def trade_with_rat(self, ctx):
        """Trade with a caught trader rat"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            # Check if player has caught a trader in this channel
            from src.trader_system import get_active_trader_for_player
            trader_data = await get_active_trader_for_player(str(ctx.author.id), str(ctx.channel.id))
            
            if not trader_data:
                await ctx.send("❌ You need to catch a trader rat first! Use `!catch` when a trader appears.")
                return
            
            # Start trading interface
            await self._show_trading_interface(ctx, player, trader_data)
            
        except Exception as e:
            await ctx.send(f"❌ Error starting trade: {e}")
    
    async def _show_trading_interface(self, ctx, player, trader_data):
        """Show the trading interface"""
        # This is a simplified version - in a full implementation you'd want
        # a proper modal/pagination system
        
        trader_type = trader_data['trader_type']
        trader_name = TRADER_NAMES.get(trader_type, "Unknown Trader")
        
        embed = discord.Embed(
            title=f"🏪 Trading with {trader_name}",
            description=f"Welcome to the shop! What would you like to do?",
            color=0xffd700
        )
        
        # Show player gold
        embed.add_field(name="💰 Your Gold", value=str(player.gold), inline=True)
        
        # Show basic inventory highlights
        valuable_items = [item for item in player.inventory if self._is_valuable_item(item['item_id'])]
        if valuable_items:
            embed.add_field(
                name="🎒 Items to Sell",
                value=f"You have {len(valuable_items)} valuable items",
                inline=True
            )
        
        # Trading options
        embed.add_field(
            name="🛍️ Trading Options",
            value="**1.** Browse Items for Sale\n**2.** Sell Your Items\n**3.** Leave Shop",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Add simple trading buttons (would use proper UI in full implementation)
        class TradeButton(discord.ui.Button):
            def __init__(self, label, style, custom_id):
                super().__init__(label=label, style=style, custom_id=custom_id)
            
            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("❌ This isn't your trade session!", ephemeral=True)
                    return
                
                await self._handle_trade_action(interaction, self.custom_id)
        
        async def _handle_trade_action(interaction, action):
            if action == "browse":
                await self._show_items_for_sale(interaction, player, trader_type)
            elif action == "sell":
                await self._show_sell_options(interaction, player, trader_type)
            elif action == "leave":
                await interaction.response.send_message("👋 Thanks for trading!", ephemeral=True)
        
        # For now, just show text instructions
        await ctx.send("💡 Use `!buy [item_name]` to buy items, `!sell [item_name]` to sell items")
    
    def _is_valuable_item(self, item_id: str) -> bool:
        """Check if an item is valuable enough to sell"""
        valuable_prefixes = ['epic', 'legendary', 'rare']
        return any(prefix in item_id.lower() for prefix in valuable_prefixes)
    
    @commands.command(name='buy', aliases=['purchase'])
    async def buy_item(self, ctx, *, item_name: str = None):
        """Buy an item from a trader"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            if not item_name:
                await ctx.send("❌ Please specify an item to buy!")
                return
            
            # Check if player is trading
            from src.trader_system import get_active_trader_for_player
            trader_data = await get_active_trader_for_player(str(ctx.author.id), str(ctx.channel.id))
            
            if not trader_data:
                await ctx.send("❌ You need to catch a trader first! Use `!catch` when a trader appears.")
                return
            
            # Find item in trader inventory
            trader_type = trader_data['trader_type']
            inventory = trader_manager.get_trader_inventory(trader_type)
            
            # Search for item (simplified matching)
            found_item = None
            for item_id, item_data in inventory.items():
                if item_name.lower() in item_id.lower() or item_name.lower() in item_data.description.lower():
                    found_item = (item_id, item_data)
                    break
            
            if not found_item:
                await ctx.send(f"❌ Item '{item_name}' not found in trader's inventory!")
                return
            
            item_id, item_data = found_item
            
            # Check if in stock
            if item_data.stock <= 0:
                await ctx.send(f"❌ {item_data.name} is out of stock!")
                return
            
            # Check if player can afford
            if not player.can_afford(item_data.price):
                await ctx.send(f"❌ You need {item_data.price} gold, but you only have {player.gold}!")
                return
            
            # Complete purchase
            success = await player.spend_gold(item_data.price)
            if success:
                # Add item to player inventory
                await player.add_to_inventory(item_id, 'equipment', 1)
                
                # Reduce stock
                # (In a full implementation, you'd update the trader inventory)
                
                await ctx.send(f"✅ Purchased {item_data.name} for {item_data.price} gold!")
            else:
                await ctx.send("❌ Purchase failed!")
            
        except Exception as e:
            await ctx.send(f"❌ Error buying item: {e}")
    
    @commands.command(name='sell', aliases=['sellitem'])
    async def sell_item(self, ctx, *, item_name: str = None):
        """Sell an item to a trader"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            if not item_name:
                await ctx.send("❌ Please specify an item to sell!")
                return
            
            # Find item in player inventory
            found_item = None
            for item in player.inventory:
                item_data = ALL_EQUIPMENT.get(item['item_id'])
                if item_data and (item_name.lower() in item_data.name.lower() or item_name.lower() in item['item_id'].lower()):
                    found_item = item
                    item_data = item_data
                    break
            
            if not found_item:
                await ctx.send(f"❌ You don't have '{item_name}' in your inventory!")
                return
            
            # Calculate sell price (50% of base price or estimated value)
            sell_price = self._calculate_sell_price(item_data)
            
            # Check if trader buys this type of item
            from src.trader_system import get_active_trader_for_player
            trader_data = await get_active_trader_for_player(str(ctx.author.id), str(ctx.channel.id))
            
            if not trader_data:
                await ctx.send("❌ You need to catch a trader first!")
                return
            
            trader_type = trader_data['trader_type']
            buy_list = trader_manager.get_trader_buy_list(trader_type)
            
            if item_data.id not in buy_list:
                await ctx.send(f"❌ This trader doesn't buy {item_data.name}!")
                return
            
            # Complete sale
            await player.remove_from_inventory(item_data.id, 1)
            await player.add_gold(sell_price)
            
            await ctx.send(f"✅ Sold {item_data.name} for {sell_price} gold!")
            
        except Exception as e:
            await ctx.send(f"❌ Error selling item: {e}")
    
    def _calculate_sell_price(self, item_data) -> int:
        """Calculate sell price for an item"""
        # Simple calculation - 50% of estimated value
        base_price = 0
        
        # Estimate based on stats
        if hasattr(item_data, 'stats') and item_data.stats:
            for stat_value in item_data.stats.values():
                base_price += stat_value * 10
        
        # Rarity multiplier
        rarity_multipliers = {
            'common': 1.0,
            'uncommon': 1.5,
            'rare': 2.5,
            'epic': 5.0,
            'legendary': 10.0
        }
        
        multiplier = rarity_multipliers.get(item_data.rarity.value, 1.0)
        return int(base_price * multiplier * 0.5)
    
    @commands.command(name='profile', aliases=['me', 'player'])
    async def view_profile(self, ctx):
        """View detailed player profile"""
        try:
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character yet! Use `!create` to create one.")
                return
            
            # Create detailed profile
            embed = discord.Embed(
                title=f"👤 {ctx.author.display_name}'s Profile",
                description=f"Level {player.level} Rat Catcher",
                color=0x9932cc
            )
            
            # Basic info
            embed.add_field(name="🏆 Level", value=str(player.level), inline=True)
            embed.add_field(name="💰 Gold", value=str(player.gold), inline=True)
            embed.add_field(name="⭐ Total XP", value=str(player.xp), inline=True)
            
            # Perks
            if player.perks:
                perks_text = [f"{perk['tree_name']}: {perk['perk_name']}" for perk in player.perks]
                embed.add_field(name="🌟 Perks", value="\n".join(perks_text), inline=False)
            else:
                embed.add_field(name="🌟 Perks", value="No perks yet", inline=False)
            
            # Equipment summary
            equipment_count = sum(1 for slot in player.equipment.__dict__.values() if slot)
            embed.add_field(name="👕 Equipment", value=f"{equipment_count}/7 slots filled", inline=True)
            
            # Recent achievements (simplified)
            recent_achievements = "Coming soon!"  # Would implement actual achievement system
            embed.add_field(name="🏆 Recent Achievements", value=recent_achievements, inline=True)
            
            # Member since
            from datetime import datetime
            created_date = datetime.fromisoformat(player.created_at.replace('Z', '+00:00'))
            embed.add_field(name="📅 Member Since", value=created_date.strftime("%Y-%m-%d"), inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error viewing profile: {e}")