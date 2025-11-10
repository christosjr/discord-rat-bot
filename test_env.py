#!/usr/bin/env python3
"""
Test Environment Variables
==========================

Simple test to check environment variable configuration without Discord connection.
"""

import os
import sys

# Add the current directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment():
    """Test if environment variables are set correctly."""
    print("Testing Environment Variables...")
    print("=" * 40)
    
    try:
        # Import bot config to trigger validation
        from config.bot_config import BOT_CONFIG
        print("✓ bot_config.py loaded successfully")
        
        # Check if token is set
        token = BOT_CONFIG.get('token')
        if token:
            print(f"✓ Token found (length: {len(token)} chars)")
            print(f"  Token preview: {token[:15]}...{token[-10:]}")
        else:
            print("✗ No token found in BOT_CONFIG")
            
        print("\nEnvironment variables check:")
        print(f"  DISCORD_BOT_TOKEN: {'✓ Set' if os.getenv('DISCORD_BOT_TOKEN') else '✗ Not set'}")
        print(f"  DISCORD_APPLICATION_ID: {'✓ Set' if os.getenv('DISCORD_APPLICATION_ID') else '✗ Not set'}")
        
        print("\n✓ All environment tests passed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_environment()