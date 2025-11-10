# 🐭 Discord Rat Bot

A feature-rich Discord bot for an engaging rat-catching RPG experience! Inspired by games like Skyrim and modded versions such as Lorerim 4.0, this bot provides hundreds of hours of gameplay through catch mechanics, character progression, dungeon exploration, and an extensive equipment system.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Discord](https://img.shields.io/badge/Discord.py-2.3+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎮 Features

### Core Gameplay
- **Wild Rat Catching**: Bot spawns catchable wild rats with varying rarities
- **Wild Traders**: Special trader rats with unique inventories and rare items
- **Character Progression**: Level up your cat with stats, perks, and equipment
- **Turn-Based Combat**: Engage in strategic dungeon battles
- **Equipment System**: Extensive equipment with multiple slots and rarities

### Progression Systems
- **Multiple Catch Methods**: Wild catching, trapping, location-based hunting, quests
- **Dungeon Exploration**: Various dungeon types with unique mechanics:
  - 🔥 Fire Dungeons (fire resistance required)
  - ❄️ Ice Dungeons (cold environment)
  - 🧟 Undead Dungeons (vulnerable to light, resistant to dark)
  - 🐉 Dragon Lairs (extreme difficulty)
  - 🌌 Void Realms (reality-bending mechanics)
- **Skill Trees**: Three main archetypes (Melee, Ranged, Magic) with hybrid options
- **Achievement System**: Milestone rewards and collection achievements

### Economy & Trading
- **Dynamic Economy**: Multiple currencies and trading systems
- **Dungeon Keys**: Locked dungeons requiring special keys from Key Master traders
- **Equipment Enhancement**: Upgrade and customize your gear
- **Player Trading**: Trade rats and items with other players

### Endgame Content
- **Prestige System**: Long-term progression for dedicated players
- **Legendary Equipment**: Ultra-rare items with game-changing abilities
- **Competitive Elements**: Leaderboards and guild competitions
- **Seasonal Events**: Holiday-themed content and special events

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Developer Account
- Git

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/discord-rat-bot.git
   cd discord-rat-bot
   ```

2. **Set up environment**:
   ```bash
   python -m venv rat_bot_env
   source rat_bot_env/bin/activate  # On Windows: rat_bot_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token
   ```

4. **Test the setup**:
   ```bash
   python tests/test_run.py
   ```

5. **Run locally**:
   ```bash
   python main.py
   ```

### Discord Bot Setup

1. **Create Discord Application**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Go to "Bot" section and create a bot
   - Copy the bot token

2. **Configure Permissions**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Add Reactions`

3. **Invite to Server**:
   - Use the generated URL from OAuth2 URL Generator

## 🌐 Deployment

### Railway.app (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Create Railway account
   - Connect GitHub repository
   - Add environment variables:
     ```
     DISCORD_BOT_TOKEN=your_token_here
     DISCORD_APPLICATION_ID=your_app_id_here
     ```

3. **Verify Deployment**:
   - Check Railway logs
   - Test bot commands in Discord

For detailed deployment instructions, see [Deployment Guide](deployment/railway_deployment.md).

## 📖 Gameplay Guide

### Getting Started

1. **Create Character**: Use `!create` to start your adventure
2. **Catch Rats**: Use `!catch` when wild rats appear
3. **View Progress**: Use `!stats` to see your character information
4. **Explore Dungeons**: Use `!dungeon` to enter challenging dungeons
5. **Get Help**: Use `!help` for all available commands

### Character Progression

- **Stats**: Strength, Agility, Intelligence, Vitality
- **Equipment Slots**: Weapon, Head, Body, Ring, Tail Ring, Neck, Boots
- **Leveling**: Gain XP from catching rats and completing dungeons
- **Perk Points**: Spend on skill trees for build customization

### Catching Mechanics

- **Wild Rats**: Spawn randomly in channels (10-20 minute intervals)
- **Traders**: Special rats with unique inventories (15% spawn chance)
- **Rarity System**: Common → Uncommon → Rare → Epic → Legendary
- **Loot Rewards**: Equipment, consumables, and rare materials

### Dungeons

- **Difficulty Scaling**: Easy → Medium → Hard → Extreme
- **Elemental Types**: Fire, Ice, Lightning, Earth, Undead, Dragon
- **Death Penalties**: Lose XP and exit dungeon
- **Boss Encounters**: Special rewards for completing dungeons
- **Key System**: Some dungeons require keys from Key Master traders

## ⚙️ Configuration

### Game Balance
Edit `config/game_balance.py` to adjust:
- XP requirements and rewards
- Spawn rates and intervals
- Combat mechanics
- Economic parameters

### Content Management
- **Rats**: `config/rat_types.py` - Add new rat types and rarities
- **Equipment**: `config/equipment.py` - Create new weapons, armor, and spells
- **Dungeons**: `config/dungeons.py` - Design new dungeons and encounters
- **Traders**: `config/traders.py` - Configure trader inventories

### Extensibility
The bot is designed for easy expansion:
- **Modular Architecture**: Add new systems without breaking existing code
- **Configuration-Driven**: Most content can be added through config files
- **Plugin System**: Extensible command and event systems
- **Database Migrations**: Schema updates without data loss

## 🛠️ Development

### Project Structure
```
discord_rat_bot/
├── config/              # All game configuration
│   ├── bot_config.py   # Discord bot settings
│   ├── game_balance.py # Game balance values
│   ├── rat_types.py    # Rat definitions
│   ├── equipment.py    # Equipment items
│   ├── dungeons.py     # Dungeon content
│   └── traders.py      # Trader definitions
├── src/                # Core game systems
│   ├── database.py     # Database operations
│   ├── player.py       # Player management
│   ├── catch_system.py # Rat catching logic
│   ├── dungeon_system.py # Dungeon mechanics
│   └── trader_system.py # Trading system
├── discord_bot/        # Discord interface
│   ├── client.py       # Main bot client
│   └── commands/       # Command handlers
├── tests/              # Comprehensive tests
├── deployment/         # Deployment guides
└── main.py             # Bot entry point
```

### Running Tests
```bash
# Run all tests
python tests/test_run.py

# Run specific test categories
python -m pytest tests/test_config.py -v
python -m pytest tests/test_systems.py -v
```

### Adding Content
1. **New Rat Type**: Add to `config/rat_types.py`
2. **New Equipment**: Add to `config/equipment.py`
3. **New Dungeon**: Add to `config/dungeons.py`
4. **New Trader**: Add to `config/traders.py`
5. **Balance Changes**: Modify `config/game_balance.py`

## 📊 System Requirements

### Minimum Requirements
- Python 3.8+
- 512MB RAM
- 1GB storage
- Discord bot token

### Recommended for Production
- Python 3.10+
- 1GB+ RAM
- PostgreSQL database
- Redis for caching (optional)

### Supported Platforms
- 🐧 Linux (Railway.app, VPS)
- 🪟 Windows (local development)
- 🍎 macOS (local development)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [deployment guide](deployment/railway_deployment.md)
- **Issues**: Open GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our Discord server

## 🎯 Roadmap

### Version 1.0 (Current)
- ✅ Core catching system
- ✅ Basic dungeon mechanics
- ✅ Equipment and progression
- ✅ Trading system

### Version 1.1 (Planned)
- 🔄 Trapping system
- 🔄 Location-based hunting
- 🔄 Enhanced perk trees
- 🔄 Guild features

### Version 1.2 (Future)
- 📅 Seasonal events
- 📅 Prestige system
- 📅 Advanced crafting
- 📅 PvP elements

## 🎉 Acknowledgments

- **Skyrim** and **Lorerim 4.0** for gameplay inspiration
- **Discord.py** for the excellent bot framework
- **Railway.app** for seamless deployment
- **Python Community** for amazing libraries

---

**Built with ❤️ by MiniMax Agent**

For questions, support, or just to show off your epic rat-catching achievements, join our community!