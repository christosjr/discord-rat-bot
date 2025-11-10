import discord
from discord import app_commands
from discord.ext import commands
from src.database import SessionLocal
from src.models import Player
from src.traits_data import TRAITS
from src.utils import random_cat_emoji, color_options
import os

ADMIN_ID = os.getenv("ADMIN_ID")

def setup_character_commands(bot: commands.Bot):
    tree = bot.tree

    @tree.command(name="startcat", description="Create your cat character.")
    async def startcat(interaction: discord.Interaction):
        session = SessionLocal()
        if session.query(Player).filter_by(discord_id=interaction.user.id).first():
            await interaction.response.send_message(
                "You already have a cat! Use /viewcat to see it.", ephemeral=True
            )
            session.close()
            return

        await interaction.response.send_message(
            "Let's begin! What will your cat's name be?", ephemeral=True
        )

        def check_name(msg):
            return msg.author.id == interaction.user.id

        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check_name)
            name = msg.content.strip()
        except:
            await interaction.followup.send("Timed out. Try again.", ephemeral=True)
            session.close()
            return

        # Fur color selection
        options = [discord.SelectOption(label=c) for c in color_options()]
        select_color = discord.ui.Select(placeholder="Choose fur color", options=options)
        view = discord.ui.View()
        view.add_item(select_color)

        async def color_callback(interact):
            await interact.response.defer(thinking=False)
            color = select_color.values[0]
            emoji = random_cat_emoji()
            base = {"hp": 100, "stamina": 100, "magicka": 100}
            points = 5

            async def make_embed():
                e = discord.Embed(title=f"{emoji} {name}", description=f"Points left: {points}")
                e.add_field(name="HP", value=str(base["hp"]), inline=True)
                e.add_field(name="Stamina", value=str(base["stamina"]), inline=True)
                e.add_field(name="Magicka", value=str(base["magicka"]), inline=True)
                return e

            hp_b = discord.ui.Button(label="+HP", style=discord.ButtonStyle.red)
            st_b = discord.ui.Button(label="+STA", style=discord.ButtonStyle.green)
            mg_b = discord.ui.Button(label="+MAG", style=discord.ButtonStyle.blurple)
            confirm_b = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.gray, disabled=True)

            async def update_view():
                confirm_b.disabled = points > 0
                await interact.edit_original_response(embed=await make_embed(), view=view2)

            async def add_stat(field):
                nonlocal points
                if points <= 0: return
                base[field] += 10
                points -= 1
                await update_view()

            hp_b.callback = lambda _: add_stat("hp")
            st_b.callback = lambda _: add_stat("stamina")
            mg_b.callback = lambda _: add_stat("magicka")

            async def confirm_stats(i_confirm):
                await i_confirm.response.defer(thinking=False)
                # Trait selection phase
                trait_opts = [discord.SelectOption(label=t["name"], description=t["desc"][:80], emoji=t["emoji"]) for t in TRAITS]
                trait_select = discord.ui.Select(placeholder="Select up to 3 traits", options=trait_opts, max_values=3)
                confirm_traits = discord.ui.Button(label="Confirm Traits", style=discord.ButtonStyle.green)
                view3 = discord.ui.View()
                view3.add_item(trait_select)
                view3.add_item(confirm_traits)

                selected = []

                async def trait_select_cb(i2):
                    nonlocal selected
                    selected = trait_select.values
                    await i2.response.defer()

                async def confirm_traits_cb(i3):
                    await i3.response.defer(thinking=False)
                    if not selected:
                        await i3.followup.send("You must select at least one trait.", ephemeral=True)
                        return
                    player = Player(
                        discord_id=interaction.user.id,
                        name=name,
                        emoji=emoji,
                        color=color,
                        hp=base["hp"],
                        stamina=base["stamina"],
                        magicka=base["magicka"],
                        traits=",".join(selected),
                    )
                    session.add(player)
                    session.commit()
                    trait_text = "\n".join(
                        [f"{t['emoji']} **{t['name']}** — {t['desc']}" for t in TRAITS if t["name"] in selected]
                    )
                    e = discord.Embed(title=f"{emoji} {name}", description=f"🎨 Color: {color}")
                    e.add_field(name="❤️ HP", value=str(base['hp']))
                    e.add_field(name="⚡ Stamina", value=str(base['stamina']))
                    e.add_field(name="🔮 Magicka", value=str(base['magicka']))
                    e.add_field(name="Traits", value=trait_text, inline=False)
                    await i3.followup.send("✅ Character created!", embed=e, ephemeral=True)
                    session.close()

                trait_select.callback = trait_select_cb
                confirm_traits.callback = confirm_traits_cb
                await i_confirm.followup.send("Select your traits:", view=view3, ephemeral=True)

            confirm_b.callback = confirm_stats

            view2 = discord.ui.View()
            for b in (hp_b, st_b, mg_b, confirm_b):
                view2.add_item(b)
            await interact.followup.send(content="Distribute 5 points:", embed=await make_embed(), view=view2, ephemeral=True)

        select_color.callback = color_callback
        await interaction.followup.send("Choose your fur color:", view=view, ephemeral=True)

    @tree.command(name="viewcat", description="View your cat character.")
    async def viewcat(interaction: discord.Interaction):
        session = SessionLocal()
        player = session.query(Player).filter_by(discord_id=interaction.user.id).first()
        if not player:
            await interaction.response.send_message(
                "You haven't created a cat yet. Use /startcat first.", ephemeral=True
            )
            session.close()
            return

        chosen_traits = player.traits.split(",") if player.traits else []
        trait_text = "\n".join(
            [f"{t['emoji']} **{t['name']}** — {t['desc']}" for t in TRAITS if t["name"] in chosen_traits]
        )
        e = discord.Embed(title=f"{player.emoji} {player.name}", description=f"🎨 Color: {player.color}")
        e.add_field(name="❤️ HP", value=str(player.hp))
        e.add_field(name="⚡ Stamina", value=str(player.stamina))
        e.add_field(name="🔮 Magicka", value=str(player.magicka))
        if trait_text:
            e.add_field(name="Traits", value=trait_text, inline=False)
        await interaction.response.send_message(embed=e)
        session.close()

    @tree.command(name="resetcat", description="Admin: Delete a user's cat.")
    @app_commands.describe(user="The user whose cat should be deleted.")
    async def resetcat(interaction: discord.Interaction, user: discord.User):
        if str(interaction.user.id) != str(ADMIN_ID):
            await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
            return
        session = SessionLocal()
        player = session.query(Player).filter_by(discord_id=user.id).first()
        if not player:
            await interaction.response.send_message(f"{user.display_name} has no cat.", ephemeral=True)
            session.close()
            return
        session.delete(player)
        session.commit()
        session.close()
        await interaction.response.send_message(f"🗑️ {user.display_name}'s cat has been deleted.", ephemeral=True)
