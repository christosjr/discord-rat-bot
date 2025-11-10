"""
Admin Commands
=============
Administrative commands for bot management.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio

from src.player import Player
from src.database import db_manager
from config.bot_config import BOT_CONFIG

class AdminCommands(commands.Cog):
    """Administrative commands (for bot owners only)"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='admin', hidden=True)
    @commands.is_owner()
    async def admin_panel(self, ctx):
        """Admin panel for bot management"""
        embed = discord.Embed(
            title="🔧 Admin Panel",
            description="Bot administration commands",
            color=0xff0000
        )
        
        embed.add_field(
            name="🗃️ Database",
            value="`!admin cleanup` - Clean expired data\n`!admin backup` - Create database backup",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistics", 
            value="`!admin stats` - Bot statistics\n`!admin players` - Player count",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Game Management",
            value="`!admin spawn_rat [channel]` - Force rat spawn\n`!admin reset_player [user]` - Reset player data",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Bot Control",
            value="`!admin shutdown` - Graceful shutdown\n`!admin restart` - Restart bot",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='admin_cleanup', hidden=True)
    @commands.is_owner()
    async def admin_cleanup(self, ctx):
        """Clean up expired data"""
        try:
            from src.catch_system import wild_rat_manager
            from src.trader_system import cleanup_all_traders
            
            # Clean expired rats and traders
            await cleanup_all_traders()
            await wild_rat_manager._check_and_cleanup_expired_spawns()
            
            # Clean old dungeon runs
            await db_manager.execute("""
                DELETE FROM dungeon_runs 
                WHERE status != 'active' AND completed_at < datetime('now', '-7 days')
            """)
            
            # Clean old wild rats
            await db_manager.execute("""
                DELETE FROM wild_rats 
                WHERE expires_at < datetime('now', '-1 day')
            """)
            
            # Clean old traders
            await db_manager.execute("""
                DELETE FROM active_traders 
                WHERE expires_at < datetime('now', '-1 day')
            """)
            
            await ctx.send("✅ Database cleanup completed!")
            
        except Exception as e:
            await ctx.send(f"❌ Cleanup failed: {e}")
    
    @commands.command(name='admin_stats', hidden=True)
    @commands.is_owner()
    async def admin_stats(self, ctx):
        """Show bot statistics"""
        try:
            # Get database stats
            player_count = await db_manager.fetchone("SELECT COUNT(*) as count FROM players")
            dungeon_count = await db_manager.fetchone("SELECT COUNT(*) as count FROM dungeon_runs")
            active_runs = await db_manager.fetchone("SELECT COUNT(*) as count FROM dungeon_runs WHERE status = 'active'")
            
            # Get active content
            from src.catch_system import wild_rat_manager
            from src.trader_system import trader_manager
            
            active_rats = len(wild_rat_manager.active_spawns)
            active_traders = len(trader_manager.active_traders)
            
            embed = discord.Embed(
                title="📊 Bot Statistics",
                description="Current bot statistics and status",
                color=0x0099ff
            )
            
            embed.add_field(name="👥 Total Players", value=str(player_count['count']), inline=True)
            embed.add_field(name="🏰 Total Dungeon Runs", value=str(dungeon_count['count']), inline=True)
            embed.add_field(name="⚔️ Active Dungeon Runs", value=str(active_runs['count']), inline=True)
            embed.add_field(name="🐭 Active Wild Rats", value=str(active_rats), inline=True)
            embed.add_field(name="🏪 Active Traders", value=str(active_traders), inline=True)
            
            # Bot info
            embed.add_field(name="🤖 Bot Username", value=self.bot.user.name, inline=True)
            embed.add_field(name="🆔 Bot ID", value=str(self.bot.user.id), inline=True)
            embed.add_field(name="🔗 Connected Servers", value=str(len(self.bot.guilds)), inline=True)
            
            # Memory usage (if available)
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            embed.add_field(name="💾 Memory Usage", value=f"{memory_mb:.1f} MB", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting stats: {e}")
    
    @commands.command(name='admin_players', hidden=True)
    @commands.is_owner()
    async def admin_players(self, ctx):
        """Show player information"""
        try:
            # Get top players by level
            top_players = await db_manager.fetchall("""
                SELECT username, level, xp, gold 
                FROM players 
                ORDER BY level DESC, xp DESC 
                LIMIT 10
            """)
            
            # Get total player count
            total_players = await db_manager.fetchone("SELECT COUNT(*) as count FROM players")
            
            embed = discord.Embed(
                title="👥 Player Statistics",
                description=f"Total Players: {total_players['count']}",
                color=0x00ff00
            )
            
            if top_players:
                player_text = []
                for i, player in enumerate(top_players, 1):
                    player_text.append(f"{i}. **{player['username']}** - Level {player['level']} ({player['xp']} XP, {player['gold']} gold)")
                
                embed.add_field(name="🏆 Top Players", value="\n".join(player_text), inline=False)
            else:
                embed.add_field(name="🏆 Top Players", value="No players found", inline=False)
            
            # Get level distribution
            level_dist = await db_manager.fetchall("""
                SELECT level, COUNT(*) as count 
                FROM players 
                GROUP BY level 
                ORDER BY level 
                LIMIT 10
            """)
            
            if level_dist:
                level_text = []
                for level_data in level_dist:
                    level_text.append(f"Level {level_data['level']}: {level_data['count']} players")
                
                embed.add_field(name="📊 Level Distribution", value="\n".join(level_text), inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting player info: {e}")
    
    @commands.command(name='admin_spawn_rat', hidden=True)
    @commands.is_owner()
    async def admin_spawn_rat(self, ctx, channel: discord.TextChannel = None):
        """Force spawn a wild rat"""
        try:
            if not channel:
                channel = ctx.channel
            
            from src.catch_system import wild_rat_manager
            
            success = await wild_rat_manager.spawn_wild_rat(str(channel.id))
            
            if success:
                await ctx.send(f"✅ Wild rat spawned in {channel.mention}!")
            else:
                await ctx.send(f"❌ Could not spawn rat in {channel.mention} (might already have one)")
            
        except Exception as e:
            await ctx.send(f"❌ Error spawning rat: {e}")
    
    @commands.command(name='admin_reset_player', hidden=True)
    @commands.is_owner()
    async def admin_reset_player(self, ctx, user: discord.User):
        """Reset a player's data"""
        try:
            confirm_msg = await ctx.send(
                f"⚠️ **WARNING** ⚠️\n\n"
                f"This will completely reset {user.mention}'s character data.\n"
                f"This action cannot be undone!\n\n"
                f"Type `CONFIRM` to proceed."
            )
            
            def check(m):
                return m.author.id == ctx.author.id and m.content == "CONFIRM"
            
            try:
                await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="❌ Reset cancelled - timeout")
                return
            
            # Reset player data
            await db_manager.execute("DELETE FROM player_stats WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM player_inventory WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM equipment WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM player_perks WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM achievements WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM daily_quests WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM dungeon_runs WHERE player_id IN (SELECT id FROM players WHERE discord_id = ?)", (str(user.id),))
            await db_manager.execute("DELETE FROM players WHERE discord_id = ?", (str(user.id),))
            
            await ctx.send(f"✅ {user.mention}'s character has been reset!")
            
        except Exception as e:
            await ctx.send(f"❌ Error resetting player: {e}")
    
    @commands.command(name='admin_shutdown', hidden=True)
    @commands.is_owner()
    async def admin_shutdown(self, ctx):
        """Gracefully shutdown the bot"""
        try:
            await ctx.send("🛑 Bot is shutting down gracefully...")
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"❌ Error during shutdown: {e}")
    
    @commands.command(name='admin_broadcast', hidden=True)
    @commands.is_owner()
    async def admin_broadcast(self, ctx, *, message: str):
        """Broadcast a message to all servers"""
        try:
            sent_count = 0
            for guild in self.bot.guilds:
                try:
                    system_channel = guild.system_channel
                    if system_channel:
                        await system_channel.send(f"📢 **ADMIN BROADCAST** 📢\n\n{message}")
                        sent_count += 1
                except:
                    continue  # Skip guilds where we can't send
            
            await ctx.send(f"📢 Broadcast sent to {sent_count} servers!")
            
        except Exception as e:
            await ctx.send(f"❌ Error broadcasting: {e}")
    
    @commands.command(name='admin_balance', hidden=True)
    @commands.is_owner()
    async def admin_balance(self, ctx, user: discord.User, amount: int):
        """Give/take gold from a player"""
        try:
            player = await Player.get_by_discord_id(str(user.id))
            if not player:
                await ctx.send(f"❌ {user.mention} doesn't have a character!")
                return
            
            if amount > 0:
                await player.add_gold(amount)
                action = "given"
            else:
                success = await player.spend_gold(-amount)
                if not success:
                    await ctx.send(f"❌ {user.mention} doesn't have enough gold!")
                    return
                action = "taken"
            
            await ctx.send(f"✅ {amount} gold {action} {'from' if amount < 0 else 'to'} {user.mention}!")
            
        except Exception as e:
            await ctx.send(f"❌ Error adjusting balance: {e}")
    
    @commands.command(name='admin_level', hidden=True)
    @commands.is_owner()
    async def admin_level(self, ctx, user: discord.User, levels: int):
        """Give/take levels from a player"""
        try:
            player = await Player.get_by_discord_id(str(user.id))
            if not player:
                await ctx.send(f"❌ {user.mention} doesn't have a character!")
                return
            
            if levels > 0:
                # Give levels
                from config.game_balance import XP_REQUIREMENTS
                new_level = min(100, player.level + levels)
                new_xp = XP_REQUIREMENTS.get(new_level, player.xp)
                
                # Calculate stat/perk points earned
                level_diff = new_level - player.level
                stat_points = level_diff * 3
                perk_points = level_diff
                
                await db_manager.execute("""
                    UPDATE players 
                    SET level = ?, xp = ?, stat_points = stat_points + ?, perk_points = perk_points + ?
                    WHERE discord_id = ?
                """, (new_level, new_xp, stat_points, perk_points, str(user.id)))
                
                await ctx.send(f"✅ {levels} levels given to {user.mention}!")
                
            else:
                # Take levels
                new_level = max(1, player.level + levels)
                new_xp = XP_REQUIREMENTS.get(new_level, 0)
                
                await db_manager.execute("""
                    UPDATE players 
                    SET level = ?, xp = ?
                    WHERE discord_id = ?
                """, (new_level, new_xp, str(user.id)))
                
                await ctx.send(f"✅ {abs(levels)} levels taken from {user.mention}!")
            
        except Exception as e:
            await ctx.send(f"❌ Error adjusting levels: {e}")