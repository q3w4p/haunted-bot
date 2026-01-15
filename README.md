# Haunted Bot

A fully-featured Discord bot with moderation, economy, fun commands, and more.

## Features

- **Moderation**: Ban, kick, mute, warn, jail, and more
- **Economy**: Balance, daily rewards, gambling, stealing
- **Fun**: Games, roleplay, social commands
- **Music**: Music playback with queue management
- **Tickets**: Support ticket system with categories
- **VoiceMaster**: Temporary voice channels
- **Antinuke**: Server protection against malicious actions
- **Starboard**: Highlight popular messages
- **LastFM**: Music scrobbling integration
- **Levels**: XP and leveling system
- **And much more!**

## Setup

### 1. Database Setup

First, run the database setup script to create all required tables in your Supabase PostgreSQL database:

```bash
python3 setup_database.py
```

This will create all the necessary tables for the bot to function.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Bot

```bash
python3 haunted.py
```

## Configuration

The bot is pre-configured with:

- **Bot Token**: Already set in `haunted.py`
- **Database**: Supabase PostgreSQL connection
- **Owner ID**: `1243921076606599224`
- **Default Prefix**: `,`

### Custom Emojis

The bot uses these custom emojis:
- Check: `<:check:1451659525986848878>`
- Deny: `<:deny:1451659356448755763>`
- Warning: `<:warning:1451659617632522260>`

Make sure these emojis exist in a server the bot has access to.

## Commands

Use `,help` to see all available commands with a dropdown menu to browse categories:

- **Config**: Server configuration, prefix, autoroles, logging
- **Economy**: Balance, daily, give, gambling
- **Fun**: Games, random commands
- **Information**: User info, server info, bot info
- **Moderation**: Ban, kick, mute, warn, jail, purge
- **Music**: Play, pause, skip, queue
- **Tickets**: Ticket system management
- **And more categories...**

## File Structure

```
haunted-bot/
├── haunted.py          # Main bot entry point
├── setup_database.py   # Database setup script
├── requirements.txt    # Python dependencies
├── bot/
│   ├── bot.py          # Bot class definition
│   ├── database.py     # Database table creation
│   ├── helpers.py      # Context and help command
│   ├── ext.py          # Utility functions
│   ├── headers.py      # HTTP session
│   └── dynamicrolebutton.py
├── cogs/               # Command modules
├── events/             # Event handlers
├── patches/            # Utility patches
└── utils/              # Additional utilities
```

## Support

For support, join our Discord server or create an issue on GitHub.

## License

This project is for educational purposes.
