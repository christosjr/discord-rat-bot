#!/usr/bin/env python3
"""
Test Runner for Discord Rat Bot
==============================
Simple test runner to verify all systems work correctly.
"""

import sys
import asyncio
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing imports...")
    
    try:
        # Test configuration imports
        from config.bot_config import BOT_CONFIG
        from config.game_balance import XP_REQUIREMENTS
        from config.rat_types import ALL_RATS
        from config.equipment import ALL_EQUIPMENT
        from config.dungeons import ALL_DUNGEONS
        from config.traders import TRADER_INVENTORIES
        print("✅ Configuration imports successful")
        
        # Test core system imports
        from src.database import db_manager
        from src.player import Player
        from src.catch_system import wild_rat_manager
        from src.trader_system import trader_manager
        from src.dungeon_system import dungeon_manager
        print("✅ Core system imports successful")
        
        # Test bot imports
        from discord_bot.client import bot
        print("✅ Bot imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration values"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config.game_balance import WILD_RAT_RATES
        
        # Check rat rates sum to 100%
        total_rate = sum(WILD_RAT_RATES.values())
        if abs(total_rate - 100.0) < 0.1:
            print("✅ Wild rat rates are properly configured")
        else:
            print(f"❌ Wild rat rates don't sum to 100%: {total_rate}%")
            return False
        
        # Check XP requirements
        from config.game_balance import XP_REQUIREMENTS
        if 1 in XP_REQUIREMENTS and XP_REQUIREMENTS[1] == 0:
            print("✅ XP requirements are properly configured")
        else:
            print("❌ XP requirements are misconfigured")
            return False
        
        # Check equipment slots
        from config.equipment import ALL_EQUIPMENT, EquipmentSlot
        if len(ALL_EQUIPMENT) > 0:
            print(f"✅ Equipment system configured with {len(ALL_EQUIPMENT)} items")
        else:
            print("❌ No equipment items found")
            return False
        
        # Check dungeons
        from config.dungeons import ALL_DUNGEONS
        if len(ALL_DUNGEONS) > 0:
            print(f"✅ Dungeon system configured with {len(ALL_DUNGEONS)} dungeons")
        else:
            print("❌ No dungeons found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_database_setup():
    """Test database setup (without actual connection)"""
    print("\n🔍 Testing database configuration...")
    
    try:
        from config.bot_config import DATABASE_CONFIG
        
        # Check database type
        if DATABASE_CONFIG['type'] in ['sqlite', 'postgresql']:
            print(f"✅ Database type configured: {DATABASE_CONFIG['type']}")
        else:
            print(f"❌ Invalid database type: {DATABASE_CONFIG['type']}")
            return False
        
        # Check SQLite is available
        if DATABASE_CONFIG['type'] == 'sqlite':
            print("✅ SQLite configuration looks good")
        elif DATABASE_CONFIG['type'] == 'postgresql':
            print("✅ PostgreSQL configuration looks good")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment setup...")
    
    # Check Python version
    if sys.version_info >= (3, 8):
        print(f"✅ Python version: {sys.version}")
    else:
        print(f"❌ Python version too old: {sys.version}")
        return False
    
    # Check for .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        env_example = Path(__file__).parent.parent / ".env.example"
        if env_example.exists():
            print("⚠️  No .env file found, but .env.example exists")
            print("   Copy .env.example to .env and configure your bot token")
        else:
            print("❌ No environment files found")
            return False
    
    # Check Discord token (only warn if missing)
    if 'DISCORD_BOT_TOKEN' in os.environ:
        print("✅ Discord bot token configured")
    else:
        print("⚠️  Discord bot token not set (required for actual bot operation)")
    
    return True

def main():
    """Run all tests"""
    print("🐭 Discord Rat Bot - System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Database Test", test_database_setup),
        ("Environment Test", test_environment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your bot is ready to deploy.")
        print("\n📋 Next steps:")
        print("1. Configure your Discord bot token in .env file")
        print("2. Push code to GitHub")
        print("3. Deploy to Railway.app")
        print("4. Test in Discord!")
        return True
    else:
        print(f"❌ {len(tests) - passed} tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)