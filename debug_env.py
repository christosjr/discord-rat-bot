#!/usr/bin/env python3
"""
Environment Debugger for Discord Bot
====================================

This script checks what's happening with environment variables,
especially the DISCORD_BOT_TOKEN setting.
"""

import os
import sys

def debug_environment():
    """Debug environment variable settings."""
    print("=== Environment Variable Debug ===")
    print()
    
    # Check DISCORD_BOT_TOKEN
    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    print(f"DISCORD_BOT_TOKEN environment variable:")
    if discord_token:
        print(f"  ✓ Set (length: {len(discord_token)} characters)")
        # Show first 10 and last 10 characters for verification
        preview = f"{discord_token[:10]}...{discord_token[-10:]}"
        print(f"  Preview: {preview}")
        
        # Check token format
        parts = discord_token.split('.')
        print(f"  Parts: {len(parts)} (expected: 3)")
        if len(parts) == 3:
            print("  ✓ JWT format looks correct")
        else:
            print("  ✗ JWT format is incorrect")
    else:
        print("  ✗ NOT SET or EMPTY")
        print("  ✗ This is the likely cause of the 'Improper token has been passed' error!")
    
    print()
    
    # Check other environment variables
    other_vars = [
        'DISCORD_APPLICATION_ID',
        'DATABASE_HOST',
        'DATABASE_PORT', 
        'DATABASE_USER',
        'DATABASE_PASSWORD',
        'DATABASE_NAME'
    ]
    
    print("Other environment variables:")
    for var in other_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: Set")
        else:
            print(f"  {var}: Not set")
    
    print()
    print("=== All Environment Variables (keys only) ===")
    all_vars = sorted(os.environ.keys())
    for var in all_vars:
        print(f"  {var}")
    
    print()
    print("=== Recommended Actions ===")
    if not discord_token:
        print("1. The DISCORD_BOT_TOKEN environment variable is NOT SET")
        print("2. In Railway dashboard, go to your service and set:")
        print("   Variable name: DISCORD_BOT_TOKEN")
        print("   Variable value: Your actual Discord bot token")
        print("3. Redeploy the service")
    elif len(discord_token) < 50:
        print("1. The DISCORD_BOT_TOKEN appears to be too short")
        print("2. Make sure you copied the COMPLETE token (should be around 70+ characters)")
        print("3. Check for any trailing spaces or missing characters")
    else:
        print("1. The environment variable appears to be set correctly")
        print("2. The token might be invalid or expired")
        print("3. Check your Discord Developer Portal to regenerate the token")

if __name__ == "__main__":
    debug_environment()