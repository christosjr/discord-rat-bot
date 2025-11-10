# RimBot — Cat RPG Discord Bot 🐈

An interactive Discord RPG inspired by LoreRim, where players become cats catching rats.

## Features
- Interactive `/startcat` character creation (buttons + dropdowns)
- Stat allocation
- Trait selection (20 unique balanced traits)
- `/viewcat` shows expanded character sheet
- SQLite persistence
- Flask keep-alive for Railway

## Setup
1. Create a Discord bot and invite it to your server.
2. Clone this repository.
3. Create a `.env` (or set Railway environment variables):

```
DISCORD_BOT_TOKEN=yourtoken
ADMIN_ID=yourdiscordid
```

4. Deploy to Railway or run locally:

```bash
pip install -r requirements.txt
python main.py
```
