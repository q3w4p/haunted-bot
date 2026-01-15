# Lavalink Installation Guide for Haunted Bot

Lavalink is required for music playback features in the bot. This guide will help you set up Lavalink for your bot.

## Prerequisites

- Java 17 or higher (Java 21 recommended)
- At least 512MB of RAM available

---

## Option 1: Install Lavalink Locally (GitHub Codespaces / Ubuntu)

### Step 1: Install Java

```bash
sudo apt update
sudo apt install openjdk-21-jre-headless -y
```

Verify Java installation:

```bash
java -version
```

You should see something like `openjdk version "21.0.x"`.

### Step 2: Download Lavalink

Create a directory for Lavalink:

```bash
mkdir -p ~/lavalink
cd ~/lavalink
```

Download the latest Lavalink JAR:

```bash
wget https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar
```

### Step 3: Create application.yml Configuration

Create a configuration file:

```bash
nano application.yml
```

Paste this configuration:

```yaml
server:
  port: 2333
  address: 0.0.0.0

lavalink:
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
    bufferDurationMs: 400
    frameBufferDurationMs: 5000
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    path: ./logs/

  level:
    root: INFO
    lavalink: INFO

  logback:
    rollingpolicy:
      max-file-size: 1GB
      max-history: 30
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 4: Start Lavalink

Run Lavalink:

```bash
java -jar Lavalink.jar
```

You should see:
```
Lavalink is ready to accept connections.
```

To run Lavalink in the background:

```bash
nohup java -jar Lavalink.jar > lavalink.log 2>&1 &
```

### Step 5: Update .env File

Add these lines to your `.env` file:

```env
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
```

---

## Option 2: Use a Public Lavalink Server (Quick Setup)

If you don't want to host your own Lavalink server, you can use a public one:

### Free Public Lavalink Servers

⚠️ **Warning**: Public servers may be unreliable or have rate limits.

Example public server:

```env
LAVALINK_HOST=lavalink.oops.wtf
LAVALINK_PORT=443
LAVALINK_PASSWORD=www.freelavalink.ga
```

Or:

```env
LAVALINK_HOST=lava.link
LAVALINK_PORT=80
LAVALINK_PASSWORD=dismusic
```

### Step: Update .env File

Add the public server details to your `.env` file.

---

## Option 3: Use a Hosted Lavalink Service

### Recommended Providers

1. **FreeLavalink** - https://freelavalink.ga (Free)
2. **Lavalink.cloud** - https://lavalink.cloud (Paid, reliable)
3. **Replit** - Host your own Lavalink on Replit

### Step: Get Connection Details

Sign up for a service and get your connection details:
- Host
- Port  
- Password

### Step: Update .env File

Add the connection details to your `.env` file.

---

## Testing Lavalink Connection

After setting up Lavalink, restart your bot and try a music command:

```
;play never gonna give you up
```

If Lavalink is connected properly, the bot will start playing music.

---

## Troubleshooting

### Java not found

If you get "java: command not found":

```bash
sudo apt install default-jre -y
```

### Port 2333 already in use

Check if Lavalink is already running:

```bash
lsof -i :2333
```

Kill the process:

```bash
kill -9 <PID>
```

### Lavalink crashes immediately

Check the logs:

```bash
cat ~/lavalink/logs/spring.log
```

Common issues:
- Not enough RAM (need at least 512MB)
- Java version too old (need Java 17+)
- Port already in use

### Bot can't connect to Lavalink

1. Make sure Lavalink is running:
   ```bash
   ps aux | grep Lavalink
   ```

2. Check if the port is open:
   ```bash
   netstat -tuln | grep 2333
   ```

3. Verify your `.env` file has the correct credentials

4. Check bot logs for connection errors

---

## Running Lavalink on Startup (Linux)

To make Lavalink start automatically:

### Step 1: Create a systemd service

```bash
sudo nano /etc/systemd/system/lavalink.service
```

Paste this:

```ini
[Unit]
Description=Lavalink Music Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lavalink
ExecStart=/usr/bin/java -jar Lavalink.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 2: Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable lavalink
sudo systemctl start lavalink
```

### Step 3: Check status

```bash
sudo systemctl status lavalink
```

---

## What Features Require Lavalink?

All music commands require Lavalink:
- `;play` - Play a song
- `;pause` - Pause playback
- `;resume` - Resume playback
- `;skip` - Skip to next song
- `;queue` - View queue
- `;nowplaying` - Show current song
- `;volume` - Adjust volume
- `;loop` - Loop current song
- `;shuffle` - Shuffle queue
- `;disconnect` - Disconnect from voice

Without Lavalink, music commands will not work.

---

## Updating Lavalink

To update to the latest version:

```bash
cd ~/lavalink
rm Lavalink.jar
wget https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar
```

Then restart Lavalink.

---

## Performance Tips

1. **Allocate more RAM** (if available):
   ```bash
   java -Xmx512M -jar Lavalink.jar
   ```

2. **Use Java 21** for better performance

3. **Enable GC logging** in application.yml for debugging

4. **Monitor logs** regularly:
   ```bash
   tail -f ~/lavalink/logs/spring.log
   ```

---

## Need Help?

- Lavalink Documentation: https://lavalink.dev/
- Lavalink GitHub: https://github.com/lavalink-devs/Lavalink
- Discord Support: https://discord.gg/lavalink
