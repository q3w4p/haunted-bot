# Haunted Bot Setup Guide

This guide will help you set up Lavalink for music functionality and Redis for caching features.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Redis Setup](#redis-setup)
4. [Lavalink Setup](#lavalink-setup)
5. [Running the Bot](#running-the-bot)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher
- Java 17 or higher (for Lavalink)
- Git installed
- A Discord bot token

---

## Database Setup

### 1. Run the Database Migration Script

If you're getting column errors like `column "avatar_url" does not exist`, run the migration script:

```bash
python3 fix_database.py
```

This script will:
- Add missing columns to existing tables
- Create any missing tables
- Verify all table structures

### 2. Run the Full Setup Script (First Time Only)

```bash
python3 setup_database.py
```

---

## Redis Setup

Redis is used for caching snipe messages, reaction snipes, and other temporary data.

### Option 1: Local Redis (Recommended for Development)

#### On Ubuntu/Debian:
```bash
# Install Redis
sudo apt update
sudo apt install redis-server -y

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

#### On macOS:
```bash
# Install with Homebrew
brew install redis

# Start Redis
brew services start redis

# Verify
redis-cli ping
```

#### On Windows:
1. Download Redis from https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use WSL2 with Ubuntu

### Option 2: GitHub Codespaces

In GitHub Codespaces, you can install Redis directly:

```bash
# Install Redis
sudo apt update && sudo apt install redis-server -y

# Start Redis in background
redis-server --daemonize yes

# Verify
redis-cli ping
```

### Option 3: Cloud Redis (Production)

For production, consider:
- **Redis Cloud** (free tier available): https://redis.com/try-free/
- **Upstash** (serverless Redis): https://upstash.com/
- **Railway** (easy deployment): https://railway.app/

After getting your Redis URL, set it as an environment variable:

```bash
export REDIS_URL="redis://username:password@host:port"
```

### Redis Fallback

If Redis is not available, the bot will automatically use an in-memory fallback. This means:
- Snipe/editsnipe commands will still work but won't persist across restarts
- Some features may have reduced functionality

---

## Lavalink Setup

Lavalink is required for music playback functionality.

### Step 1: Install Java 17+

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install openjdk-17-jre-headless -y

# Verify
java -version
```

#### On macOS:
```bash
brew install openjdk@17
```

#### On Windows:
Download from https://adoptium.net/

### Step 2: Download Lavalink

```bash
# Create a directory for Lavalink
mkdir -p ~/lavalink && cd ~/lavalink

# Download the latest Lavalink jar
wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.8/Lavalink.jar
```

### Step 3: Create Lavalink Configuration

Create a file called `application.yml` in the same directory:

```yaml
server:
  port: 2333
  address: 0.0.0.0

lavalink:
  plugins:
    - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:4.0.1"
    - dependency: "com.github.topi314.lavasearch:lavasearch-plugin:1.0.0"
    - dependency: "dev.lavalink.youtube:youtube-plugin:1.5.2"
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    filters:
      volume: true
      equalizer: true
      karaoke: true
      timescale: true
      tremolo: true
      vibrato: true
      distortion: true
      rotation: true
      channelMix: true
      lowPass: true
    bufferDurationMs: 400
    frameBufferDurationMs: 5000
    opusEncodingQuality: 10
    resamplingQuality: LOW
    trackStuckThresholdMs: 10000
    useSeekGhosting: true
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

plugins:
  youtube:
    enabled: true
    allowSearch: true
    allowDirectVideoIds: true
    allowDirectPlaylistIds: true
    clients:
      - MUSIC
      - ANDROID_TESTSUITE
      - WEB
      - TVHTML5EMBEDDED

metrics:
  prometheus:
    enabled: false

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    path: ./logs/

  level:
    root: INFO
    lavalink: INFO

  request:
    enabled: true
    includeClientInfo: true
    includeHeaders: false
    includeQueryString: true
    includePayload: true
    maxPayloadLength: 10000

  logback:
    rollingpolicy:
      max-file-size: 1GB
      max-history: 30
```

### Step 4: Start Lavalink

```bash
cd ~/lavalink
java -jar Lavalink.jar
```

You should see output like:
```
[main] INFO lavalink.server.Launcher - Starting Lavalink
...
[main] INFO lavalink.server.Launcher - Lavalink is ready to accept connections.
```

### Step 5: Update Bot Configuration

In your bot's `cogs/music.py`, ensure the Lavalink connection settings match:

```python
await self.pomice.create_node(
    bot=self.bot,
    host="127.0.0.1",  # or your Lavalink server IP
    port=2333,
    password="youshallnotpass",  # must match application.yml
    identifier="MAIN",
    spotify_client_id="YOUR_SPOTIFY_CLIENT_ID",  # optional
    spotify_client_secret="YOUR_SPOTIFY_CLIENT_SECRET"  # optional
)
```

### Running Lavalink in Background (Linux)

Using screen:
```bash
screen -S lavalink
java -jar Lavalink.jar
# Press Ctrl+A, then D to detach
# To reattach: screen -r lavalink
```

Using systemd (recommended for production):
```bash
sudo nano /etc/systemd/system/lavalink.service
```

```ini
[Unit]
Description=Lavalink Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lavalink
ExecStart=/usr/bin/java -jar Lavalink.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable lavalink
sudo systemctl start lavalink
```

---

## Running the Bot

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)

```bash
# Redis URL (if using external Redis)
export REDIS_URL="redis://localhost:6379"

# Database URL (if different from default)
export DATABASE_URL="postgresql://user:pass@host:port/database"
```

### 3. Run Database Migrations

```bash
python3 fix_database.py
```

### 4. Start the Bot

```bash
python3 haunted.py
```

---

## Troubleshooting

### Redis Errors

**Error:** `AttributeError: 'Haunted' object has no attribute 'redis'`

**Solution:** The bot now initializes Redis automatically with a fallback. Make sure you're using the latest `haunted.py` that calls `await bot.setup_redis()`.

### Database Column Errors

**Error:** `column "avatar_url" of relation "customize" does not exist`

**Solution:** Run the migration script:
```bash
python3 fix_database.py
```

### Lavalink Connection Failed

**Error:** `NodeConnectionFailure: The connection to node 'MAIN' failed.`

**Solutions:**
1. Ensure Lavalink is running: `java -jar Lavalink.jar`
2. Check if port 2333 is open: `netstat -tlnp | grep 2333`
3. Verify password matches in both `application.yml` and `music.py`
4. If using Docker/remote server, ensure the host IP is correct

### Music Commands Not Working

1. Make sure Lavalink is running before starting the bot
2. Check that you're in a voice channel when using music commands
3. Verify the bot has permissions to join and speak in voice channels

### 403 Forbidden Error (Shard Data)

This error is usually related to external API calls. It's safe to ignore if the bot is functioning normally.

---

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Java 17+ installed (for Lavalink)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations run (`python3 fix_database.py`)
- [ ] Redis running (or using fallback)
- [ ] Lavalink running (for music)
- [ ] Bot token set in `haunted.py`
- [ ] Bot started (`python3 haunted.py`)

---

## Support

Join our Discord server for help: https://discord.com/invite/hauntedbot
