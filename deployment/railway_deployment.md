# Discord Rat Bot - Complete Setup Guide

This guide will walk you through setting up and deploying the Discord Rat Bot from start to finish.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Discord Developer Setup](#discord-developer-setup)
3. [Local Development Setup](#local-development-setup)
4. [GitHub Repository Setup](#github-repository-setup)
5. [Railway.app Deployment](#railwayapp-deployment)
6. [Testing and Verification](#testing-and-verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, make sure you have:

- **Git** installed on your computer
- **Python 3.8+** installed
- A **Discord account**
- A **GitHub account** (for code repository)
- A **Railway.app account** (for hosting)

## Discord Developer Setup

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name (e.g., "Rat Catching Bot")
4. Click "Create"

### 2. Create a Bot

1. In your application, go to "Bot" section in the left sidebar
2. Click "Add Bot"
3. Choose "Yes, do it!"
4. Under "Token", click "Reset Token" and copy the token
5. **IMPORTANT**: Save this token - you'll need it later!

### 3. Configure Bot Permissions

Go to "OAuth2" > "URL Generator" in the left sidebar:

**Scopes to select:**
- ✅ bot
- ✅ applications.commands

**Bot Permissions:**
- ✅ Send Messages
- ✅ Read Message History
- ✅ Use External Emojis
- ✅ Add Reactions
- ✅ Connect (for voice features, not required but safe)
- ✅ Speak (for voice features, not required but safe)

### 4. Invite Bot to Your Server

1. Copy the generated URL from the URL Generator
2. Open it in your browser
3. Select your Discord server
4. Click "Authorize"
5. Complete the CAPTCHA

## Local Development Setup

### 1. Clone/Download the Project

If you have the code locally, navigate to the project directory:
```bash
cd discord_rat_bot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv rat_bot_env

# Activate it
# On Windows:
rat_bot_env\Scripts\activate
# On macOS/Linux:
source rat_bot_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and add your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   DISCORD_APPLICATION_ID=your_application_id_here
   ```

### 5. Test Locally

```bash
python main.py
```

If everything works, you should see:
- Bot connects to Discord
- Database setup messages
- "Bot is now online and running!" message

## GitHub Repository Setup

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name it (e.g., "discord-rat-bot")
4. Make it **Public** (Railway.app free tier works with public repos)
5. Don't initialize with README (we already have files)
6. Click "Create repository"

### 2. Upload Your Code

Choose one of these methods:

**Option A: Using Git Command Line**
```bash
git init
git add .
git commit -m "Initial commit: Discord Rat Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

**Option B: Using GitHub Desktop**
1. Download [GitHub Desktop](https://desktop.github.com/)
2. Clone your repository
3. Copy all the bot files into the cloned folder
4. Commit and push

### 3. Verify Repository

Your repository should now contain all the bot files including:
- `main.py`
- `requirements.txt`
- `config/` folder
- `src/` folder
- `discord_bot/` folder
- `.env.example`
- `railway.toml`

## Railway.app Deployment

### 1. Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Authorize Railway to access your repositories

### 2. Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select your Discord bot repository
4. Click "Deploy Now"

### 3. Configure Environment Variables

After deployment starts:

1. Click on your project in Railway dashboard
2. Go to "Variables" tab
3. Add these environment variables:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   DISCORD_APPLICATION_ID=your_application_id_here
   DATABASE_TYPE=sqlite
   LOG_LEVEL=INFO
   ```

### 4. Wait for Deployment

Railway will automatically:
- Install Python dependencies
- Start the bot
- Provide you with a live URL

### 5. Verify Deployment

1. Check the "Deploy" tab in Railway
2. You should see "Build completed" and "Deploy completed"
3. Check the logs to ensure the bot started successfully

## Testing and Verification

### 1. Test Bot Commands

In your Discord server, test these commands:

- `!create` - Should create your character
- `!stats` - Should show character stats
- `!help` - Should show all available commands
- `!catch` - Should catch a wild rat when one spawns

### 2. Check Database

The bot uses SQLite database which will be automatically created and managed by Railway.

### 3. Monitor Logs

In Railway dashboard:
1. Go to your project
2. Click on the service
3. Check the "Logs" section for any errors

## Troubleshooting

### Common Issues

**1. "Token is invalid" error**
- Double-check your Discord bot token in Railway variables
- Make sure no extra spaces or characters

**2. "Database connection failed"**
- Check if the database configuration is correct
- For SQLite, no additional setup is needed

**3. Bot not responding to commands**
- Check if the bot has proper permissions in your Discord server
- Verify the bot is online in Railway

**4. Import errors**
- Make sure all required files are in your repository
- Check that `requirements.txt` includes all dependencies

**5. Commands not showing up**
- This is normal for slash commands - they may take up to 1 hour to appear
- Use traditional `!` commands for immediate functionality

### Log Analysis

**Successful startup log should show:**
```
INFO - Database setup completed
INFO - Bot is ready! Logged in as BotName (ID: 123456789)
INFO - Bot is now online and running!
```

**Common error patterns:**
- `ModuleNotFoundError` → Missing dependencies, check requirements.txt
- `ConnectionError` → Network/DNS issues
- `PermissionError` → File system permissions

### Getting Help

If you encounter issues:

1. **Check Railway logs** first
2. **Verify environment variables** are set correctly
3. **Test locally** to ensure code works
4. **Check Discord bot permissions** in your server
5. **Review this guide** for any missed steps

### Performance Optimization

For better performance:
- Use PostgreSQL instead of SQLite for larger deployments
- Implement Redis for caching (optional)
- Monitor memory usage in Railway dashboard
- Consider upgrading Railway plan for better performance

## Next Steps

Once your bot is successfully deployed:

1. **Add more features** by editing the configuration files
2. **Customize the game balance** in `config/game_balance.py`
3. **Add new equipment** in `config/equipment.py`
4. **Create new dungeons** in `config/dungeons.py`
5. **Scale up** by inviting more users to your server

## Support and Updates

- **Regular backups**: Download your database periodically from Railway
- **Code updates**: Push changes to GitHub and Railway will auto-deploy
- **Monitoring**: Keep an eye on Railway dashboard for performance metrics

Your Discord Rat Bot should now be live and running! 🎉