import discord
from discord.ext import commands
from discord import app_commands
import aiohttp


class Customize(commands.Cog):
    """Customize the bot's appearance per server"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_load(self):
        # Create customize table if not exists
        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS customize (
                guild_id BIGINT PRIMARY KEY,
                avatar_url TEXT,
                banner_url TEXT,
                bio TEXT
            )
        """)
    
    @commands.group(name="customize", aliases=["custom", "customise"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def customize(self, ctx):
        """Group command for customizing the bot's appearance in this server"""
        return await ctx.create_pages()
    
    @customize.command(name="avatar", aliases=["pfp", "icon"])
    @commands.has_permissions(administrator=True)
    async def customize_avatar(self, ctx, url: str = None):
        """Sets the bot's server profile picture"""
        if url is None:
            # Check for attachment
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.cmdhelp()
        
        # Validate URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.warning("Invalid image URL provided")
                    content_type = resp.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        return await ctx.warning("URL must be an image")
        except:
            return await ctx.warning("Failed to fetch the image from URL")
        
        # Save to database
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET avatar_url = $1 WHERE guild_id = $2", url, ctx.guild.id)
        else:
            await self.bot.db.execute("INSERT INTO customize (guild_id, avatar_url) VALUES ($1, $2)", ctx.guild.id, url)
        
        embed = discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: Set the bot's **avatar** for this server")
        embed.set_thumbnail(url=url)
        return await ctx.reply(embed=embed)
    
    @customize.command(name="banner")
    @commands.has_permissions(administrator=True)
    async def customize_banner(self, ctx, url: str = None):
        """Sets the bot's server banner"""
        if url is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                return await ctx.cmdhelp()
        
        # Validate URL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.warning("Invalid image URL provided")
        except:
            return await ctx.warning("Failed to fetch the image from URL")
        
        # Save to database
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET banner_url = $1 WHERE guild_id = $2", url, ctx.guild.id)
        else:
            await self.bot.db.execute("INSERT INTO customize (guild_id, banner_url) VALUES ($1, $2)", ctx.guild.id, url)
        
        embed = discord.Embed(color=self.bot.color, description=f"{self.bot.yes} {ctx.author.mention}: Set the bot's **banner** for this server")
        embed.set_image(url=url)
        return await ctx.reply(embed=embed)
    
    @customize.command(name="bio", aliases=["description", "desc"])
    @commands.has_permissions(administrator=True)
    async def customize_bio(self, ctx, *, text: str):
        """Sets the bot's server bio"""
        if len(text) > 190:
            return await ctx.warning("Bio must be under 190 characters")
        
        # Save to database
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET bio = $1 WHERE guild_id = $2", text, ctx.guild.id)
        else:
            await self.bot.db.execute("INSERT INTO customize (guild_id, bio) VALUES ($1, $2)", ctx.guild.id, text)
        
        return await ctx.success(f"Set the bot's **bio** for this server to: {text}")
    
    @customize.command(name="remove", aliases=["reset"])
    @commands.has_permissions(administrator=True)
    async def customize_remove(self, ctx):
        """Resets the bot's server profile picture to default"""
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET avatar_url = NULL WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Reset the bot's **avatar** to default")
    
    @customize.command(name="clearbanner")
    @commands.has_permissions(administrator=True)
    async def customize_clearbanner(self, ctx):
        """Removes the bot's server banner"""
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET banner_url = NULL WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Removed the bot's **banner**")
    
    @customize.command(name="clearbio")
    @commands.has_permissions(administrator=True)
    async def customize_clearbio(self, ctx):
        """Removes the bot's server bio"""
        existing = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        if existing:
            await self.bot.db.execute("UPDATE customize SET bio = NULL WHERE guild_id = $1", ctx.guild.id)
        return await ctx.success("Removed the bot's **bio**")
    
    @customize.command(name="view", aliases=["show", "settings"])
    @commands.has_permissions(administrator=True)
    async def customize_view(self, ctx):
        """View current customization settings"""
        data = await self.bot.db.fetchrow("SELECT * FROM customize WHERE guild_id = $1", ctx.guild.id)
        
        embed = discord.Embed(color=self.bot.color, title="Bot Customization Settings")
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        if data:
            embed.add_field(name="Avatar", value=f"[View]({data['avatar_url']})" if data['avatar_url'] else "Default", inline=True)
            embed.add_field(name="Banner", value=f"[View]({data['banner_url']})" if data['banner_url'] else "None", inline=True)
            embed.add_field(name="Bio", value=data['bio'] if data['bio'] else "None", inline=False)
            
            if data['avatar_url']:
                embed.set_thumbnail(url=data['avatar_url'])
            if data['banner_url']:
                embed.set_image(url=data['banner_url'])
        else:
            embed.description = "No customization settings configured"
        
        return await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Customize(bot))
