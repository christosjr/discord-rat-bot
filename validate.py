#!/usr/bin/env python3
"""
Bot Validation Script
====================
Quick validation that the bot can start properly.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print("✅ Python version OK:", sys.version.split()[0])
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = [
        'discord',
        'asyncio',
        'sqlite3',  # Built-in
        'random',
        'datetime',
        'logging',
        'json'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 'discord':
                try:
                    import discord
                except ImportError:
                    missing.append('discord.py')
            else:
                missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:", ', '.join(missing))
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies available")
    return True

def check_project_structure():
    """Check if project structure is complete"""
    required_files = [
        'main.py',
        'requirements.txt',
        '.env.example',
        'config/bot_config.py',
        'config/game_balance.py',
        'config/rat_types.py',
        'config/equipment.py',
        'config/dungeons.py',
        'config/traders.py',
        'src/database.py',
        'src/player.py',
        'src/catch_system.py',
        'src/trader_system.py',
        'src/dungeon_system.py',
        'discord_bot/client.py',
        'discord_bot/commands/__init__.py',
        'discord_bot/commands/player_commands.py',
        'discord_bot/commands/game_commands.py',
        'discord_bot/commands/dungeon_commands.py',
        'discord_bot/commands/admin_commands.py',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing project files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Project structure complete")
    return True

def check_configuration():
    """Check if configuration files load properly"""
    try:
        # Test basic imports
        sys.path.append(str(Path(__file__).parent))
        
        from config.bot_config import BOT_CONFIG
        from config.game_balance import XP_REQUIREMENTS, WILD_RAT_RATES
        from config.rat_types import ALL_RATS
        from config.equipment import ALL_EQUIPMENT
        from config.dungeons import ALL_DUNGEONS
        
        # Basic validation
        assert len(XP_REQUIREMENTS) > 0
        assert abs(sum(WILD_RAT_RATES.values()) - 100.0) < 0.1
        assert len(ALL_RATS) > 0
        assert len(ALL_EQUIPMENT) > 0
        assert len(ALL_DUNGEONS) > 0
        
        print("✅ Configuration files load successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_environment():
    """Check environment setup"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Check if token is set
        with open(env_file, 'r') as f:
            content = f.read()
            if 'DISCORD_BOT_TOKEN=your_discord_bot_token_here' in content:
                print("⚠️  Discord bot token not configured (set in .env)")
            elif 'DISCORD_BOT_TOKEN=' in content:
                print("✅ Discord bot token appears to be configured")
            else:
                print("⚠️  No Discord bot token found in .env")
        
    elif env_example.exists():
        print("⚠️  .env file missing, but .env.example exists")
        print("   Run: cp .env.example .env")
    else:
        print("❌ No environment files found")
        return False
    
    return True

def main():
    """Run all validation checks"""
    print("🐭 Discord Rat Bot - System Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
        ("Environment", check_environment)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your bot is ready to go!")
        print("\n📋 Next steps:")
        print("1. Configure your Discord bot token in .env")
        print("2. Test locally: python main.py")
        print("3. Deploy to Railway.app")
        print("4. Invite bot to your Discord server")
        return True
    else:
        print(f"❌ {total - passed} checks failed. Please fix the issues.")
        print("\n💡 Common solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Copy environment file: cp .env.example .env")
        print("- Check Python version: python --version")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)