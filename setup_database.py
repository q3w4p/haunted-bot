#!/usr/bin/env python3
"""
Haunted Bot - Database Setup Script (UPDATED)
Run this script to create all required tables in your Supabase PostgreSQL database.

Usage:
    python3 setup_database.py

Make sure to set your DATABASE_URL environment variable or update the connection string below.
"""

import asyncio
import asyncpg
import os

# Supabase PostgreSQL connection string
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.hgmpeiyaivkgiyoxsebg:o5YFYEyk499qXBf8@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
)

# Drop tables that need to be recreated with correct columns
DROP_TABLES = [
    "DROP TABLE IF EXISTS customize",
    "DROP TABLE IF EXISTS lastfm_users",
    "DROP TABLE IF EXISTS roleplay_stats",
]

# All table creation statements
TABLES = [
    # Core bot tables
    "CREATE TABLE IF NOT EXISTS prefixes (guild_id BIGINT, prefix TEXT)",
    "CREATE TABLE IF NOT EXISTS selfprefix (user_id BIGINT, prefix TEXT)",
    "CREATE TABLE IF NOT EXISTS nodata (user_id BIGINT, state TEXT)",
    
    # Snipe tables
    "CREATE TABLE IF NOT EXISTS snipe (guild_id BIGINT, channel_id BIGINT, author TEXT, content TEXT, attachment TEXT, avatar TEXT, time TIMESTAMPTZ)",
    "CREATE TABLE IF NOT EXISTS editsnipe (guild_id BIGINT, channel_id BIGINT, author_name TEXT, author_avatar TEXT, before_content TEXT, after_content TEXT)",
    "CREATE TABLE IF NOT EXISTS reactionsnipe (guild_id BIGINT, channel_id BIGINT, author_name TEXT, author_avatar TEXT, emoji_name TEXT, emoji_url TEXT, message_id BIGINT)",
    
    # AFK
    "CREATE TABLE IF NOT EXISTS afk (guild_id BIGINT, user_id BIGINT, reason TEXT, time INTEGER)",
    
    # VoiceMaster
    "CREATE TABLE IF NOT EXISTS voicemaster (guild_id BIGINT, channel_id BIGINT, interface BIGINT)",
    "CREATE TABLE IF NOT EXISTS vcs (user_id BIGINT, voice BIGINT)",
    
    # Permissions
    "CREATE TABLE IF NOT EXISTS fake_permissions (guild_id BIGINT, role_id BIGINT, permissions TEXT)",
    
    # Confessions
    "CREATE TABLE IF NOT EXISTS confess (guild_id BIGINT, channel_id BIGINT, confession INTEGER)",
    "CREATE TABLE IF NOT EXISTS confess_members (guild_id BIGINT, user_id BIGINT, confession INTEGER)",
    "CREATE TABLE IF NOT EXISTS confess_mute (guild_id BIGINT, user_id BIGINT)",
    
    # Marriage/Social
    "CREATE TABLE IF NOT EXISTS marry (author BIGINT, soulmate BIGINT, time INTEGER)",
    
    # Media only channels
    "CREATE TABLE IF NOT EXISTS mediaonly (guild_id BIGINT, channel_id BIGINT)",
    
    # Tickets
    "CREATE TABLE IF NOT EXISTS tickets (guild_id BIGINT, message TEXT, channel_id BIGINT, category BIGINT, color INTEGER, logs BIGINT)",
    "CREATE TABLE IF NOT EXISTS opened_tickets (guild_id BIGINT, channel_id BIGINT, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS ticket_topics (guild_id BIGINT, name TEXT, description TEXT)",
    "CREATE TABLE IF NOT EXISTS ticket_support (guild_id BIGINT, role_id BIGINT)",
    
    # Join settings
    "CREATE TABLE IF NOT EXISTS pingonjoin (channel_id BIGINT, guild_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS autorole (role_id BIGINT, guild_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS joindm (guild_id BIGINT, message TEXT)",
    
    # Levels
    "CREATE TABLE IF NOT EXISTS levels (guild_id BIGINT, author_id BIGINT, exp INTEGER, level INTEGER, total_xp INTEGER)",
    "CREATE TABLE IF NOT EXISTS levelsetup (guild_id BIGINT, channel_id BIGINT, destination TEXT)",
    "CREATE TABLE IF NOT EXISTS levelroles (guild_id BIGINT, level INTEGER, role_id BIGINT)",
    
    # User data
    "CREATE TABLE IF NOT EXISTS oldusernames (username TEXT, discriminator TEXT, time INTEGER, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS birthday (user_id BIGINT, bday TIMESTAMPTZ, said TEXT)",
    "CREATE TABLE IF NOT EXISTS timezone (user_id BIGINT, zone TEXT)",
    "CREATE TABLE IF NOT EXISTS diary (user_id BIGINT, text TEXT, title TEXT, date TEXT)",
    
    # Donor
    "CREATE TABLE IF NOT EXISTS donor (user_id BIGINT, time INTEGER)",
    
    # Restore roles
    "CREATE TABLE IF NOT EXISTS restore (guild_id BIGINT, user_id BIGINT, roles TEXT)",
    
    # LastFM - FIXED: Added lastfm_users table
    "CREATE TABLE IF NOT EXISTS lastfm (user_id BIGINT, username TEXT)",
    "CREATE TABLE IF NOT EXISTS lastfm_users (discord_user_id BIGINT PRIMARY KEY, username TEXT)",
    "CREATE TABLE IF NOT EXISTS lastfmcc (user_id BIGINT, command TEXT)",
    "CREATE TABLE IF NOT EXISTS lfmode (user_id BIGINT, mode TEXT)",
    "CREATE TABLE IF NOT EXISTS lfcrowns (user_id BIGINT, artist TEXT)",
    "CREATE TABLE IF NOT EXISTS lfreactions (user_id BIGINT, reactions TEXT)",
    
    # Starboard
    "CREATE TABLE IF NOT EXISTS starboardmes (guild_id BIGINT, channel_starboard_id BIGINT, channel_message_id BIGINT, message_starboard_id BIGINT, message_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS starboard (guild_id BIGINT, channel_id BIGINT, count INTEGER, emoji_id BIGINT, emoji_text TEXT)",
    "CREATE TABLE IF NOT EXISTS skullboardmes (guild_id BIGINT, channel_starboard_id BIGINT, channel_message_id BIGINT, message_starboard_id BIGINT, message_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS skullboard (guild_id BIGINT, channel_id BIGINT, count INTEGER, emoji_id BIGINT, emoji_text TEXT)",
    
    # Seen
    "CREATE TABLE IF NOT EXISTS seen (guild_id BIGINT, user_id BIGINT, time INTEGER)",
    
    # Booster roles
    "CREATE TABLE IF NOT EXISTS booster_module (guild_id BIGINT, base BIGINT)",
    "CREATE TABLE IF NOT EXISTS booster_roles (guild_id BIGINT, user_id BIGINT, role_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS boosterslost (guild_id BIGINT, user_id BIGINT, time INTEGER)",
    
    # Moderation
    "CREATE TABLE IF NOT EXISTS hardban (guild_id BIGINT, banned BIGINT, author BIGINT)",
    "CREATE TABLE IF NOT EXISTS forcenick (guild_id BIGINT, user_id BIGINT, nickname TEXT)",
    "CREATE TABLE IF NOT EXISTS uwulock (guild_id BIGINT, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS shutup (guild_id BIGINT, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS mod (guild_id BIGINT, channel_id BIGINT, jail_id BIGINT, role_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS cases (guild_id BIGINT, count INTEGER)",
    "CREATE TABLE IF NOT EXISTS warns (guild_id BIGINT, user_id BIGINT, author_id BIGINT, time TEXT, reason TEXT)",
    "CREATE TABLE IF NOT EXISTS jail (guild_id BIGINT, user_id BIGINT, roles TEXT)",
    
    # Automod
    "CREATE TABLE IF NOT EXISTS antiinvite (guild_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS whitelist (guild_id BIGINT, module TEXT, object_id BIGINT, mode TEXT)",
    "CREATE TABLE IF NOT EXISTS chatfilter (guild_id BIGINT, word TEXT)",
    "CREATE TABLE IF NOT EXISTS antispam (guild_id BIGINT, seconds INTEGER, count INTEGER, punishment TEXT)",
    
    # Auto features
    "CREATE TABLE IF NOT EXISTS autoreact (guild_id BIGINT, trigger TEXT, emojis TEXT)",
    "CREATE TABLE IF NOT EXISTS autoresponses (guild_id BIGINT, key TEXT, response TEXT)",
    
    # Greetings
    "CREATE TABLE IF NOT EXISTS welcome (guild_id BIGINT, channel_id BIGINT, mes TEXT)",
    "CREATE TABLE IF NOT EXISTS leave (guild_id BIGINT, channel_id BIGINT, mes TEXT)",
    "CREATE TABLE IF NOT EXISTS boost (guild_id BIGINT, channel_id BIGINT, mes TEXT)",
    
    # Antiraid
    "CREATE TABLE IF NOT EXISTS antiraid (guild_id BIGINT, command TEXT, punishment TEXT, seconds INTEGER)",
    
    # Command settings
    "CREATE TABLE IF NOT EXISTS disablecommand (guild_id BIGINT, command TEXT)",
    "CREATE TABLE IF NOT EXISTS restrictcommand (guild_id BIGINT, command TEXT, role_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS invoke (guild_id BIGINT, command TEXT, embed TEXT)",
    "CREATE TABLE IF NOT EXISTS dm (guild_id BIGINT, command TEXT, embed TEXT)",
    
    # Reaction roles
    "CREATE TABLE IF NOT EXISTS reactionrole (guild_id BIGINT, message_id BIGINT, channel_id BIGINT, role_id BIGINT, emoji_id BIGINT, emoji_text TEXT)",
    
    # Error logging
    "CREATE TABLE IF NOT EXISTS error (code TEXT, error TEXT, guild_id BIGINT, user_id BIGINT, command TEXT, channel BIGINT, time INTEGER)",
    
    # Fun
    "CREATE TABLE IF NOT EXISTS joint (guild_id BIGINT, hits INTEGER, holder BIGINT)",
    "CREATE TABLE IF NOT EXISTS vape (guild_id BIGINT, user_id BIGINT, hits INTEGER)",
    
    # Counters
    "CREATE TABLE IF NOT EXISTS counters (guild_id BIGINT, channel_type TEXT, channel_id BIGINT, channel_name TEXT, module TEXT)",
    
    # Bumps
    "CREATE TABLE IF NOT EXISTS bumps (guild_id BIGINT, bool TEXT)",
    
    # Discrim roles
    "CREATE TABLE IF NOT EXISTS discrim (guild_id BIGINT, role_id BIGINT)",
    
    # Webhooks
    "CREATE TABLE IF NOT EXISTS webhook (guild_id BIGINT, channel_id BIGINT, code TEXT, url TEXT)",
    "CREATE TABLE IF NOT EXISTS hellohook (guild_id BIGINT, webhook_link TEXT, mes TEXT)",
    
    # Naughty corner
    "CREATE TABLE IF NOT EXISTS naughtycorner (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS naughtycorner_members (guild_id BIGINT, user_id BIGINT)",
    
    # Antinuke
    "CREATE TABLE IF NOT EXISTS antinuke_toggle (guild_id BIGINT, logs BIGINT)",
    "CREATE TABLE IF NOT EXISTS antinuke_whitelist (guild_id BIGINT, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS antinuke_admins (guild_id BIGINT, user_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS antinuke (guild_id BIGINT, module TEXT, punishment TEXT, threshold INTEGER)",
    "CREATE TABLE IF NOT EXISTS antinuke_modules (guild_id BIGINT NOT NULL, module VARCHAR(50) NOT NULL, enabled BOOLEAN DEFAULT TRUE, threshold INTEGER, punishment VARCHAR(20), PRIMARY KEY (guild_id, module))",
    
    # Giveaway
    "CREATE TABLE IF NOT EXISTS giveaway (guild_id BIGINT, channel_id BIGINT, message_id BIGINT, winners INTEGER, members TEXT, finish TIMESTAMPTZ, host BIGINT, title TEXT)",
    "CREATE TABLE IF NOT EXISTS gw_ended (channel_id BIGINT, message_id BIGINT, members TEXT)",
    
    # Reskin
    "CREATE TABLE IF NOT EXISTS reskin (user_id BIGINT, toggled BOOL, name TEXT, avatar TEXT)",
    
    # Vanity
    "CREATE TABLE IF NOT EXISTS vanity (guild_id BIGINT, vanity_message TEXT, vanity_string TEXT, role_id BIGINT)",
    
    # Global bans
    "CREATE TABLE IF NOT EXISTS globalban (banned BIGINT)",
    
    # Settings
    "CREATE TABLE IF NOT EXISTS settings_prefix (guild_id BIGINT, toggled BOOLEAN)",
    "CREATE TABLE IF NOT EXISTS settings_social (guild_id BIGINT, toggled BOOLEAN, prefix TEXT)",
    
    # Autokick/Private
    "CREATE TABLE IF NOT EXISTS autokick (guild_id BIGINT, autokick_users BIGINT, author BIGINT)",
    "CREATE TABLE IF NOT EXISTS private (guild_id BIGINT, private_users BIGINT)",
    
    # Auto media
    "CREATE TABLE IF NOT EXISTS autopfp (guild_id BIGINT, channel_id BIGINT, genre TEXT, type TEXT)",
    "CREATE TABLE IF NOT EXISTS autobanner (guild_id BIGINT, channel_id BIGINT, genre TEXT)",
    
    # Guild lists
    "CREATE TABLE IF NOT EXISTS gblacklist (guild_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS gwhitelist (guild_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS mwhitelist (guild_id BIGINT)",
    
    # Sticky messages
    "CREATE TABLE IF NOT EXISTS sticky (guild_id BIGINT, channel_id BIGINT, key TEXT)",
    "CREATE TABLE IF NOT EXISTS stickymessage (guild_id BIGINT, channel_id BIGINT, message_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS stickym (guild_id BIGINT, channel_id BIGINT, key TEXT)",
    
    # Global uwulock
    "CREATE TABLE IF NOT EXISTS guwulock (user_id BIGINT)",
    
    # Thread bumper
    "CREATE TABLE IF NOT EXISTS threadbumper (guild_id BIGINT, thread_id BIGINT)",
    
    # User avatars
    "CREATE TABLE IF NOT EXISTS user_avatars (guild_id BIGINT, channel_id BIGINT)",
    
    # Authorization
    "CREATE TABLE IF NOT EXISTS authorize (guild_id BIGINT, buyer BIGINT)",
    
    # Reminders
    "CREATE TABLE IF NOT EXISTS reminder (author_id BIGINT, channel_id BIGINT, guild_id BIGINT, time TEXT, task TEXT)",
    
    # Logging
    "CREATE TABLE IF NOT EXISTS member_logs (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS voice_logs (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS server_logs (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS message_logs (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS channel_logs (guild_id BIGINT, channel_id BIGINT)",
    "CREATE TABLE IF NOT EXISTS role_logs (guild_id BIGINT, channel_id BIGINT)",
    
    # Economy
    "CREATE TABLE IF NOT EXISTS economy (user_id BIGINT PRIMARY KEY, bucks INTEGER DEFAULT 0)",
    
    # Customize - NEW: Server-sided bot customization
    "CREATE TABLE IF NOT EXISTS customize (guild_id BIGINT PRIMARY KEY, avatar_url TEXT, banner_url TEXT, bio TEXT)",
    
    # Game stats
    "CREATE TABLE IF NOT EXISTS gamestats (user_id BIGINT, game TEXT, wins INTEGER, loses INTEGER, total INTEGER)",
]


async def setup_database():
    """Create all tables in the database."""
    print("=" * 60)
    print("Haunted Bot - Database Setup")
    print("=" * 60)
    print(f"\nConnecting to database...")
    
    try:
        # Create connection pool with statement_cache_size=0 for Supabase
        pool = await asyncpg.create_pool(DATABASE_URL, ssl="require", statement_cache_size=0)
        print("✓ Connected to Supabase PostgreSQL")
        
        # Create tables
        print("\nCreating tables...")
        success_count = 0
        error_count = 0
        
        async with pool.acquire() as conn:
            for table_sql in TABLES:
                try:
                    await conn.execute(table_sql)
                    # Extract table name for display
                    table_name = table_sql.split("IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"  ✓ {table_name}")
                    success_count += 1
                except Exception as e:
                    table_name = table_sql.split("IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"  ✗ {table_name}: {e}")
                    error_count += 1
        
        await pool.close()
        
        print("\n" + "=" * 60)
        print(f"Setup complete!")
        print(f"  Tables created: {success_count}")
        print(f"  Errors: {error_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        print("\nMake sure your DATABASE_URL is correct and the database is accessible.")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(setup_database())
