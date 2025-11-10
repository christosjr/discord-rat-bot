"""
Admin Commands
=============
Administrative commands for bot management.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio
import json

from src.player import Player
import src.database as db_manager
from config.bot_config import BOT_CONFIG, ADMIN_CONFIG

# Custom admin check function
async def is_admin(ctx):
    """Check if user is in admin list"""
    user_id = str(ctx.author.id)
    return user_id in ADMIN_CONFIG['allowed_admin_ids']

class AdminCommands(commands.Cog):
    """Administrative commands with custom permission system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='admin', hidden=True)
    async def admin_panel(self, ctx):
        """Admin panel for bot management"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        embed = discord.Embed(
            title="🔧 Admin Panel",
            description="Bot administration commands",
            color=0xff0000
        )
        
        embed.add_field(
            name="🐭 Rat Spawning",
            value="`!admin_spawn_rate [min] [max] [interval]` - Set spawn frequency\n`!admin_spawn_channels add/remove #channel` - Manage channels\n`!spawn [channel]` - Manual spawn",
            inline=False
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
            value="`!admin_reset_player @user confirm` - Reset player data\n`!admin_reset_self confirm` - Reset your own data",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Bot Control",
            value="`!admin shutdown` - Graceful shutdown\n`!admin restart` - Restart bot",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='admin_spawn_rate', hidden=True)
    async def admin_spawn_rate(self, ctx, min_count: int = None, max_count: int = None, interval_minutes: int = None):
        """Set rat spawn rate for this server"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            guild_id = str(ctx.guild.id)
            
            if min_count is None or max_count is None or interval_minutes is None:
                # Show current settings
                settings = await db_manager.db_manager.fetchone("""
                    SELECT min_spawn_count, max_spawn_count, spawn_interval_minutes, enabled 
                    FROM guild_spawn_settings WHERE guild_id = ?
                """, (guild_id,))
                
                if settings:
                    embed = discord.Embed(
                        title="🐭 Current Spawn Settings",
                        description=f"Server: {ctx.guild.name}",
                        color=0x00ff00
                    )
                    embed.add_field(name="Min Spawn Count", value=str(settings['min_spawn_count']), inline=True)
                    embed.add_field(name="Max Spawn Count", value=str(settings['max_spawn_count']), inline=True)
                    embed.add_field(name="Interval (minutes)", value=str(settings['spawn_interval_minutes']), inline=True)
                    embed.add_field(name="Status", value="Enabled" if settings['enabled'] else "Disabled", inline=True)
                else:
                    embed = discord.Embed(
                        title="🐭 Spawn Settings",
                        description="No spawn settings configured",
                        color=0xff9900
                    )
                    embed.add_field(
                        name="Usage",
                        value="`!admin_spawn_rate [min] [max] [interval]`\nExample: `!admin_spawn_rate 2 4 3`",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
            
            # Validate parameters
            if min_count < 1 or max_count < min_count or interval_minutes < 1:
                await ctx.send("❌ Invalid parameters! Min must be ≥1, max must be ≥ min, interval must be ≥1")
                return
            
            # Update or insert settings (use default empty channel list)
            import json
            await db_manager.db_manager.execute("""
                INSERT OR REPLACE INTO guild_spawn_settings 
                (guild_id, spawn_channel_ids, min_spawn_count, max_spawn_count, spawn_interval_minutes, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
            """, (guild_id, '[]', min_count, max_count, interval_minutes))
            
            embed = discord.Embed(
                title="✅ Spawn Rate Updated",
                description=f"Spawn settings for {ctx.guild.name}",
                color=0x00ff00
            )
            embed.add_field(name="Min Rats", value=str(min_count), inline=True)
            embed.add_field(name="Max Rats", value=str(max_count), inline=True)
            embed.add_field(name="Interval", value=f"{interval_minutes} minutes", inline=True)
            embed.add_field(
                name="Next Steps",
                value="Use `!admin_spawn_channels add #channel` to add channels for rat spawning",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error setting spawn rate: {e}")
    
    @commands.command(name='admin_spawn_channels', hidden=True)
    async def admin_spawn_channels(self, ctx, action: str, channel: discord.TextChannel = None):
        """Manage spawn channels for this server"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            guild_id = str(ctx.guild.id)
            action = action.lower()
            
            # Get current settings
            settings = await db_manager.db_manager.fetchone("""
                SELECT spawn_channel_ids FROM guild_spawn_settings WHERE guild_id = ?
            """, (guild_id,))
            
            if action == 'add':
                if not channel:
                    await ctx.send("❌ Please specify a channel: `!admin_spawn_channels add #channel`")
                    return
                
                # Get current channel list
                if settings:
                    channel_ids = json.loads(settings['spawn_channel_ids'])
                else:
                    channel_ids = []
                
                # Add channel if not already present
                channel_id_str = str(channel.id)
                if channel_id_str in channel_ids:
                    await ctx.send(f"❌ Channel {channel.mention} is already in the spawn list!")
                    return
                
                channel_ids.append(channel_id_str)
                
                # Save back to database
                await db_manager.db_manager.execute("""
                    INSERT OR REPLACE INTO guild_spawn_settings 
                    (guild_id, spawn_channel_ids, min_spawn_count, max_spawn_count, spawn_interval_minutes, enabled)
                    VALUES (?, ?, 2, 4, 3, 1)
                """, (guild_id, json.dumps(channel_ids)))
                
                await ctx.send(f"✅ Added {channel.mention} to spawn channels!")
                
            elif action == 'remove':
                if not channel:
                    await ctx.send("❌ Please specify a channel: `!admin_spawn_channels remove #channel`")
                    return
                
                if not settings:
                    await ctx.send("❌ No spawn channels configured!")
                    return
                
                channel_ids = json.loads(settings['spawn_channel_ids'])
                channel_id_str = str(channel.id)
                
                if channel_id_str not in channel_ids:
                    await ctx.send(f"❌ Channel {channel.mention} is not in the spawn list!")
                    return
                
                channel_ids.remove(channel_id_str)
                
                # Save back to database
                await db_manager.db_manager.execute("""
                    INSERT OR REPLACE INTO guild_spawn_settings 
                    (guild_id, spawn_channel_ids, min_spawn_count, max_spawn_count, spawn_interval_minutes, enabled)
                    VALUES (?, ?, 2, 4, 3, 1)
                """, (guild_id, json.dumps(channel_ids)))
                
                await ctx.send(f"✅ Removed {channel.mention} from spawn channels!")
                
            elif action == 'clear':
                if not settings:
                    await ctx.send("❌ No spawn channels to clear!")
                    return
                
                await db_manager.db_manager.execute("""
                    INSERT OR REPLACE INTO guild_spawn_settings 
                    (guild_id, spawn_channel_ids, min_spawn_count, max_spawn_count, spawn_interval_minutes, enabled)
                    VALUES (?, '[]', 2, 4, 3, 1)
                """, (guild_id,))
                
                await ctx.send("✅ All spawn channels cleared!")
                
            elif action == 'list':
                if not settings:
                    await ctx.send("❌ No spawn channels configured!")
                    return
                
                channel_ids = json.loads(settings['spawn_channel_ids'])
                
                if not channel_ids:
                    await ctx.send("📋 No spawn channels configured yet.")
                    return
                
                # Get channel names
                channel_list = []
                for channel_id in channel_ids:
                    channel_obj = ctx.guild.get_channel(int(channel_id))
                    if channel_obj:
                        channel_list.append(f"• {channel_obj.mention}")
                    else:
                        channel_list.append(f"• Unknown channel ({channel_id})")
                
                embed = discord.Embed(
                    title="📋 Spawn Channels",
                    description=f"Server: {ctx.guild.name}",
                    color=0x0099ff
                )
                embed.add_field(name="Configured Channels", value="\n".join(channel_list), inline=False)
                embed.add_field(
                    name="Management",
                    value="`!admin_spawn_channels add #channel` - Add channel\n`!admin_spawn_channels remove #channel` - Remove channel\n`!admin_spawn_channels clear` - Clear all",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            else:
                await ctx.send("❌ Invalid action! Use: add, remove, clear, or list")
                
        except Exception as e:
            await ctx.send(f"❌ Error managing spawn channels: {e}")
    
    @commands.command(name='spawn', hidden=True)
    async def manual_spawn(self, ctx, channel: discord.TextChannel = None):
        """Manually spawn a rat (for testing)"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
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
    
    @commands.command(name='admin_cleanup', hidden=True)
    async def admin_cleanup(self, ctx):
        """Clean up expired data"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            from src.catch_system import wild_rat_manager
            from src.trader_system import cleanup_all_traders
            
            # Clean expired rats and traders
            await cleanup_all_traders()
            await wild_rat_manager._check_and_cleanup_expired_spawns()
            
            # Clean old dungeon runs
            await db_manager.db_manager.execute("""
                DELETE FROM dungeon_runs 
                WHERE status != 'active' AND completed_at < datetime('now', '-7 days')
            """)
            
            # Clean old wild rats
            await db_manager.db_manager.execute("""
                DELETE FROM wild_rats 
                WHERE expires_at < datetime('now', '-1 day')
            """)
            
            # Clean old traders
            await db_manager.db_manager.execute("""
                DELETE FROM active_traders 
                WHERE expires_at < datetime('now', '-1 day')
            """)
            
            await ctx.send("✅ Database cleanup completed!")
            
        except Exception as e:
            await ctx.send(f"❌ Cleanup failed: {e}")
    
    @commands.command(name='admin_clear_spawns', hidden=True)
    async def admin_clear_spawns(self, ctx):
        """Clear all active rat spawns (debugging)"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            from src.catch_system import wild_rat_manager
            
            # Clear all active spawns
            spawn_count = len(wild_rat_manager.active_spawns)
            wild_rat_manager.clear_all_active_spawns()
            
            await ctx.send(f"🧹 Cleared {spawn_count} active spawns")
            
        except Exception as e:
            await ctx.send(f"❌ Error clearing spawns: {e}")
    
    @commands.command(name='admin_stats', hidden=True)
    async def admin_stats(self, ctx):
        """Show bot statistics"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            # Get database stats
            player_count = await db_manager.db_manager.fetchone("SELECT COUNT(*) as count FROM players")
            dungeon_count = await db_manager.db_manager.fetchone("SELECT COUNT(*) as count FROM dungeon_runs")
            active_runs = await db_manager.db_manager.fetchone("SELECT COUNT(*) as count FROM dungeon_runs WHERE status = 'active'")
            
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
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                embed.add_field(name="💾 Memory Usage", value=f"{memory_mb:.1f} MB", inline=True)
            except:
                embed.add_field(name="💾 Memory Usage", value="N/A", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting stats: {e}")
    
    @commands.command(name='admin_players', hidden=True)
    async def admin_players(self, ctx):
        """Show player information"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            # Get top players by level
            top_players = await db_manager.db_manager.fetchall("""
                SELECT username, level, xp, gold 
                FROM players 
                ORDER BY level DESC, xp DESC 
                LIMIT 10
            """)
            
            # Get total player count
            total_players = await db_manager.db_manager.fetchone("SELECT COUNT(*) as count FROM players")
            
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
            level_dist = await db_manager.db_manager.fetchall("""
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
    
    @commands.command(name='admin_shutdown', hidden=True)
    async def admin_shutdown(self, ctx):
        """Gracefully shutdown the bot"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            await ctx.send("🛑 Bot is shutting down gracefully...")
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"❌ Error during shutdown: {e}")
    
    @commands.command(name='admin_broadcast', hidden=True)
    async def admin_broadcast(self, ctx, *, message: str):
        """Broadcast a message to all servers"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
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
    async def admin_balance(self, ctx, user: discord.User, amount: int):
        """Give/take gold from a player"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
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
    async def admin_level(self, ctx, user: discord.User, levels: int):
        """Give/take levels from a player"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
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
                
                await db_manager.db_manager.execute("""
                    UPDATE players 
                    SET level = ?, xp = ?, stat_points = stat_points + ?, perk_points = perk_points + ?
                    WHERE discord_id = ?
                """, (new_level, new_xp, stat_points, perk_points, str(user.id)))
                
                await ctx.send(f"✅ {levels} levels given to {user.mention}!")
                
            else:
                # Take levels
                new_level = max(1, player.level + levels)
                new_xp = XP_REQUIREMENTS.get(new_level, 0)
                
                await db_manager.db_manager.execute("""
                    UPDATE players 
                    SET level = ?, xp = ?
                    WHERE discord_id = ?
                """, (new_level, new_xp, str(user.id)))
                
                await ctx.send(f"✅ {abs(levels)} levels taken from {user.mention}!")
            
        except Exception as e:
            await ctx.send(f"❌ Error adjusting levels: {e}")
    
    @commands.command(name='admin_reset_player', hidden=True)
    async def admin_reset_player(self, ctx, user: discord.User, confirm: str = None):
        """Reset a player's character data"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            if confirm != 'confirm':
                await ctx.send("⚠️ This will delete all player data! Use `!admin_reset_player @user confirm` to proceed.")
                return
            
            # Get player data before deletion
            player = await Player.get_by_discord_id(str(user.id))
            if not player:
                await ctx.send(f"❌ {user.mention} doesn't have a character!")
                return
            
            # Delete all player data
            await db_manager.db_manager.execute("DELETE FROM player_stats WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM equipment WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM player_perks WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM player_inventory WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM dungeon_runs WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM players WHERE discord_id = ?", (str(user.id)))
            
            await ctx.send(f"✅ {user.mention}'s character data has been reset!")
            
        except Exception as e:
            await ctx.send(f"❌ Error resetting player: {e}")
    
    @commands.command(name='admin_reset_self', hidden=True)
    async def reset_self(self, ctx, confirm: str = None):
        """Reset your own character data"""
        if not await is_admin(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        try:
            if confirm != 'confirm':
                await ctx.send("⚠️ This will delete all your character data! Use `!admin_reset_self confirm` to proceed.")
                return
            
            # Get player data before deletion
            player = await Player.get_by_discord_id(str(ctx.author.id))
            if not player:
                await ctx.send("❌ You don't have a character!")
                return
            
            # Delete all player data
            await db_manager.db_manager.execute("DELETE FROM player_stats WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM equipment WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM player_perks WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM player_inventory WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM dungeon_runs WHERE player_id = ?", (player.id,))
            await db_manager.db_manager.execute("DELETE FROM players WHERE discord_id = ?", (str(ctx.author.id)))
            
            await ctx.send(f"✅ Your character data has been reset! Use `!create` to make a new cat.")
            
        except Exception as e:
            await ctx.send(f"❌ Error resetting: {e}")