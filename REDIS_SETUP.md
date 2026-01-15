# Redis Installation Guide for Haunted Bot

Redis is used for caching snipe data (deleted messages, edited messages, removed reactions). The bot will work without Redis using an in-memory fallback, but Redis is recommended for production.

## Option 1: Install Redis Locally (GitHub Codespaces / Ubuntu)

### Step 1: Install Redis Server

```bash
sudo apt update
sudo apt install redis-server -y
```

### Step 2: Configure Redis

Edit the Redis configuration file:

```bash
sudo nano /etc/redis/redis.conf
```

Find the line that says `supervised no` and change it to:

```
supervised systemd
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 3: Start Redis

```bash
sudo systemctl restart redis.service
sudo systemctl enable redis
```

### Step 4: Verify Redis is Running

```bash
redis-cli ping
```

You should see `PONG` as the response.

### Step 5: Update .env File

Add these lines to your `.env` file:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

---

## Option 2: Use Redis Cloud (Recommended for Production)

### Step 1: Create a Free Redis Cloud Account

1. Go to [Redis Cloud](https://redis.com/try-free/)
2. Sign up for a free account
3. Create a new database (Free tier: 30MB)

### Step 2: Get Connection Details

After creating your database, you'll see:
- **Endpoint**: `redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345`
- **Password**: `your_password_here`

### Step 3: Update .env File

Add these lines to your `.env` file:

```env
REDIS_HOST=redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your_password_here
```

---

## Option 3: Use Upstash Redis (Serverless)

### Step 1: Create an Upstash Account

1. Go to [Upstash](https://upstash.com/)
2. Sign up for a free account
3. Create a new Redis database

### Step 2: Get Connection Details

Copy the connection details from your Upstash dashboard:
- **Endpoint**: `your-endpoint.upstash.io`
- **Port**: `6379` or `6380` (SSL)
- **Password**: `your_password_here`

### Step 3: Update .env File

Add these lines to your `.env` file:

```env
REDIS_HOST=your-endpoint.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your_password_here
```

---

## Testing Redis Connection

After setting up Redis, restart your bot and check the logs:

```bash
python3 haunted.py
```

You should see:
```
✓ Connected to Redis at localhost:6379
```

If you see:
```
⚠ Redis connection failed: ...
⚠ Using in-memory fallback for Redis features
```

Then check your connection details in the `.env` file.

---

## Troubleshooting

### Redis not starting on Codespaces

If Redis fails to start in Codespaces, you may need to run it manually:

```bash
redis-server --daemonize yes
```

### Connection refused error

Make sure Redis is running:

```bash
sudo systemctl status redis
```

If it's not running:

```bash
sudo systemctl start redis
```

### Permission denied

If you get permission errors, try:

```bash
sudo chown -R redis:redis /var/lib/redis
sudo systemctl restart redis
```

---

## What Features Require Redis?

- `;snipe` - View deleted messages
- `;editsnipe` - View edited messages  
- `;reactionsnipe` - View removed reactions
- `;clearsnipes` - Clear snipe cache

Without Redis, these commands will use an in-memory cache that resets when the bot restarts.
