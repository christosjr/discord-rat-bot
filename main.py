import asyncio
import os
from discord.ext import commands
from discord import Intents
from flask import Flask
import threading

from src.character import setup_character_commands
from src.database import init_db

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

app = Flask(__name__)

@app.route("/")
def home():
    return "RimBot is alive 🐾"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

intents = Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()

async def main():
    init_db()
    setup_character_commands(bot)
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
