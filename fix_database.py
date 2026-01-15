#!/usr/bin/env python3
"""
Database Migration Script for Haunted Bot
Run this script to fix existing database tables with correct column names.
This will add missing columns to existing tables without losing data.
"""
import asyncio
import asyncpg
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.hgmpeiyaivkgiyoxsebg:o5YFYEyk499qXBf8@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
)

# Migration queries to fix existing tables
MIGRATIONS = [
    # Fix customize table - add missing columns
    """
    DO $$
    BEGIN
        -- Add avatar_url column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customize' AND column_name = 'avatar_url') THEN
            ALTER TABLE customize ADD COLUMN avatar_url TEXT;
        END IF;
        
        -- Add banner_url column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customize' AND column_name = 'banner_url') THEN
            ALTER TABLE customize ADD COLUMN banner_url TEXT;
        END IF;
        
        -- Add bio column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customize' AND column_name = 'bio') THEN
            ALTER TABLE customize ADD COLUMN bio TEXT;
        END IF;
    END $$;
    """,
    
    # Fix lastfm_users table - add discord_user_id column
    """
    DO $$
    BEGIN
        -- Check if table exists and add column
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lastfm_users') THEN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'lastfm_users' AND column_name = 'discord_user_id') THEN
                ALTER TABLE lastfm_users ADD COLUMN discord_user_id BIGINT;
            END IF;
        ELSE
            CREATE TABLE lastfm_users (discord_user_id BIGINT PRIMARY KEY, username TEXT);
        END IF;
    END $$;
    """,
    
    # Create roleplay_stats table if not exists
    """
    CREATE TABLE IF NOT EXISTS roleplay_stats (
        user_id BIGINT,
        target_id BIGINT,
        action_type TEXT,
        count INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, target_id, action_type)
    );
    """,
    
    # Create customize table if not exists
    """
    CREATE TABLE IF NOT EXISTS customize (
        guild_id BIGINT PRIMARY KEY,
        avatar_url TEXT,
        banner_url TEXT,
        bio TEXT
    );
    """,
    
    # Ensure lastfm table exists
    """
    CREATE TABLE IF NOT EXISTS lastfm (
        user_id BIGINT PRIMARY KEY,
        username TEXT
    );
    """,
]

async def run_migrations():
    print("🔧 Running database migrations...")
    print(f"📡 Connecting to database...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
        print("✓ Connected to Supabase PostgreSQL")
        
        for i, migration in enumerate(MIGRATIONS, 1):
            try:
                await conn.execute(migration)
                print(f"✓ Migration {i}/{len(MIGRATIONS)} completed")
            except Exception as e:
                print(f"⚠ Migration {i} warning: {e}")
        
        # Verify tables
        print("\n📋 Verifying table columns...")
        
        # Check customize table
        cols = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'customize'
        """)
        print(f"✓ customize table columns: {[c['column_name'] for c in cols]}")
        
        # Check lastfm_users table
        cols = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'lastfm_users'
        """)
        print(f"✓ lastfm_users table columns: {[c['column_name'] for c in cols]}")
        
        # Check roleplay_stats table
        cols = await conn.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'roleplay_stats'
        """)
        print(f"✓ roleplay_stats table columns: {[c['column_name'] for c in cols]}")
        
        await conn.close()
        print("\n✅ All migrations completed successfully!")
        print("You can now start the bot.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migrations())
