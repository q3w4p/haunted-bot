import discord, asyncpg, typing, time, os, asyncio, json, aiohttp

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from typing import List
from humanfriendly import format_timespan

from discord.ext import commands

from bot.helpers import StartUp
from bot.helpers import HauntedContext, HelpCommand
from bot.ext import Client
from bot.database import create_db
from bot.headers import Session
from bot.dynamicrolebutton import DynamicRoleButton

from cogs.voicemaster import vmbuttons
from cogs.ticket import CreateTicket, DeleteTicket
from cogs.giveaway import GiveawayView

# Supabase PostgreSQL connection
DATABASE_URL = "postgresql://postgres.hgmpeiyaivkgiyoxsebg:o5YFYEyk499qXBf8@aws-1-us-east-1.pooler.supabase.com:6543/postgres"


class FakeRedis:
    """Fallback in-memory Redis-like storage when Redis is not available"""
    def __init__(self):
        self._data = {}
        self._lists = {}
    
    async def get(self, key):
        return self._data.get(key)
    
    async def set(self, key, value, ex=None):
        self._data[key] = value
        return True
    
    async def delete(self, *keys):
        for key in keys:
            self._data.pop(key, None)
            self._lists.pop(key, None)
        return len(keys)
    
    async def exists(self, key):
        return key in self._data or key in self._lists
    
    async def lpush(self, key, *values):
        if key not in self._lists:
            self._lists[key] = []
        for v in values:
            self._lists[key].append(v)
        # Keep only last 100 items
        self._lists[key] = self._lists[key][-100:]
        return len(self._lists[key])
    
    async def lrange(self, key, start, end):
        if key not in self._lists:
            return []
        if end == -1:
            return self._lists[key][start:]
        return self._lists[key][start:end+1]
    
    async def lindex(self, key, index):
        if key not in self._lists or index >= len(self._lists[key]):
            return None
        return self._lists[key][index]
    
    async def expire(self, key, seconds):
        """Expire is not supported in FakeRedis (in-memory fallback)"""
        # In-memory storage doesn't support expiry, but we return True to avoid errors
        return True
    
    async def ping(self):
        return True


class Haunted(commands.AutoShardedBot):
    def __init__(self, db: asyncpg.Pool = None):
        super().__init__(
            command_prefix=HauntedContext.getprefix,
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=False),
            intents=discord.Intents.all(),
            owner_ids=[1243921076606599224],  # Owner IDs
            shard_count=1,
            help_command=HelpCommand(),
            strip_after_prefix=True,
            activity=discord.CustomActivity(name="👻 haunted.gg")
        )
        
        self.db = db
        
        # Haunted theme colors - Updated to #2702f7
        self.color = 0x2702f7
        self.error_color = 0xFF6B6B
        self.yes_color = 0x2702f7
        self.no_color = 0xFF6B6B
        
        # Custom emojis
        self.yes = "<:check:1451659525986848878>"
        self.no = "<:deny:1451659356448755763>"
        self.warning = "<:warning:1451659617632522260>"
        self.left = "<:left:1451659678164582694>"
        self.right = "<:right:1451659703124885697>"
        self.loading = "<a:loading:1460999563581325418>"
        self.goto = "🔍"
        
        self.ext = Client(self)
        self.redis = None  # Will be set in setup
        
        # Cooldowns
        self.m_cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.member)
        self.c_cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.channel)
        self.m_cd2 = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.member)
        self.global_cd = commands.CooldownMapping.from_cooldown(2, 3, commands.BucketType.member)
        
        self.uptime = time.time()
        self.session = Session()
        
    async def create_db_pool(self):
        """Create connection pool to Supabase PostgreSQL"""
        self.db = await asyncpg.create_pool(
            DATABASE_URL,
            ssl="require",
            min_size=1,
            max_size=10,
            statement_cache_size=0
        )
        print("✓ Connected to Supabase PostgreSQL")
        
    async def setup_redis(self):
        """Setup Redis connection"""
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        try:
            if aioredis is None:
                raise ImportError("redis.asyncio not available")
            self.redis = await aioredis.from_url(redis_url, decode_responses=True)
            await self.redis.ping()
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"⚠ Redis connection failed: {e}")
            print("⚠ Using in-memory fallback for Redis features")
            self.redis = FakeRedis()

    async def on_ready(self) -> None:
        print(f"✓ Logged in as {self.user} (ID: {self.user.id})")
        print(f"✓ Connected to {len(self.guilds)} guilds")
        print(f"✓ Haunted Bot is ready!")
        
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound): return 
        if isinstance(error, commands.NotOwner): pass
        if isinstance(error, commands.CheckFailure): 
            if isinstance(error, commands.MissingPermissions): 
                return await ctx.warning(f"This command requires **{error.missing_permissions[0]}** permission")
        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.command.name != "hit": 
                return await ctx.reply(
                    embed=discord.Embed(
                        color=self.color, 
                        description=f"{self.warning} {ctx.author.mention}: You are on cooldown. Try again in {format_timespan(error.retry_after)}"
                    ), 
                    mention_author=False
                )    
        if isinstance(error, commands.MissingRequiredArgument): return await ctx.cmdhelp()
        if isinstance(error, commands.EmojiNotFound): return await ctx.warning(f"Unable to convert {error.argument} into an **emoji**")
        if isinstance(error, commands.MemberNotFound): return await ctx.warning(f"Unable to find member **{error.argument}**")
        if isinstance(error, commands.UserNotFound): return await ctx.warning(f"Unable to find user **{error.argument}**")
        if isinstance(error, commands.RoleNotFound): return await ctx.warning(f"Couldn't find role **{error.argument}**")
        if isinstance(error, commands.ChannelNotFound): return await ctx.warning(f"Couldn't find channel **{error.argument}**")
        if isinstance(error, commands.ThreadNotFound): return await ctx.warning(f"I was unable to find the thread **{error.argument}**")
        if isinstance(error, commands.UserConverter): return await ctx.warning(f"Couldn't convert that into an **user** ")
        if isinstance(error, commands.MemberConverter): return await ctx.warning("Couldn't convert that into a **member**")
        if isinstance(error, commands.BadArgument): return await ctx.warning(error.args[0])
        if isinstance(error, commands.BotMissingPermissions): return await ctx.warning(f"I do not have enough **permissions** to execute this command")
        if isinstance(error, commands.CommandInvokeError): return await ctx.warning(error.original)
        if isinstance(error, discord.HTTPException): return await ctx.warning("Unable to execute this command")
        if isinstance(error, commands.NoPrivateMessage): return await ctx.warning(f"This command cannot be used in private messages.")
        if isinstance(error, commands.UserInputError): return await ctx.send_help(ctx.command.qualified_name)
        if isinstance(error, discord.NotFound): return await ctx.warning(f"**Not found** - the **ID** is invalid")
        if isinstance(error, commands.GuildNotFound): return await ctx.warning(f"I was unable to find that **server** or the **ID** is invalid")
        if isinstance(error, commands.BadInviteArgument): return await ctx.warning(f"Invalid **invite code** given")
        
    async def channel_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        cd = self.c_cd
        bucket = cd.get_bucket(message)
        return bucket.update_rate_limit()

    async def on_message_edit(self, before, after):
        if before.content != after.content: await self.process_commands(after)

    async def prefixes(self, message: discord.Message) -> List[str]: 
        prefixes = []
        for l in set(p for p in await self.command_prefix(self, message)): 
            prefixes.append(l)
        return prefixes

    async def member_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        cd = self.m_cd
        bucket = cd.get_bucket(message)
        return bucket.update_rate_limit()
      
    async def on_message(self, message: discord.Message): 
        channel_rl = await self.channel_ratelimit(message)
        member_rl = await self.member_ratelimit(message)
      
        if channel_rl == True:
            return
      
        if member_rl == True:
            return
      
        if message.content == "<@{}>".format(self.user.id): 
            return await message.reply(content="prefixes: " + " ".join(f"`{g}`" for g in await self.prefixes(message)))
        await self.process_commands(message) 
    
    async def setup_hook(self):
        self.add_view(vmbuttons())
        self.add_dynamic_items(DynamicRoleButton)
        self.add_view(CreateTicket())
        self.add_view(DeleteTicket())
        self.add_view(GiveawayView())
        
        await self.load_extension('jishaku')
        await self.create_db_pool()
        
        await StartUp.loadcogs(self)
        await create_db(self)

    async def get_context(self, message: discord.Message, cls=None) -> 'HauntedContext':
        if cls is None:
            cls = HauntedContext
        return await super().get_context(message, cls=cls)
