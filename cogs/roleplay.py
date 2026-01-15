import discord, datetime, asyncio, random, aiohttp
from discord.ext import commands 
from discord.ui import Button, View
from patches.permissions import Permissions
from patches.fun import MarryView, DiaryModal, Joint


class roleplay(commands.Cog):
    """Interact with other users"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot 
        self.joint_emoji = "🍃"
        self.smoke = "🌬️" 
        self.joint_color = 0x57D657
        self.book = "📖"
        
        self.nekos_base = "https://nekos.life/api/v2/img/"
        self.waifu_base = "https://api.waifu.pics/sfw/"
        self.purrbot_base = "https://purrbot.site/api/img/sfw/"
    
    async def cog_load(self):
        await self.bot.db.execute("""
            CREATE TABLE IF NOT EXISTS roleplay_stats (
                user_id BIGINT,
                target_id BIGINT,
                action_type TEXT,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, target_id, action_type)
            )
        """)
    
    async def increment_action(self, user_id: int, target_id: int, action_type: str) -> int:
        existing = await self.bot.db.fetchrow(
            "SELECT count FROM roleplay_stats WHERE user_id = $1 AND target_id = $2 AND action_type = $3",
            user_id, target_id, action_type
        )
        
        if existing:
            new_count = existing['count'] + 1
            await self.bot.db.execute(
                "UPDATE roleplay_stats SET count = $1 WHERE user_id = $2 AND target_id = $3 AND action_type = $4",
                new_count, user_id, target_id, action_type
            )
        else:
            new_count = 1
            await self.bot.db.execute(
                "INSERT INTO roleplay_stats (user_id, target_id, action_type, count) VALUES ($1, $2, $3, $4)",
                user_id, target_id, action_type, new_count
            )
        
        return new_count
    
    def ordinal(self, n: int) -> str:
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return f"{n}{suffix}"
    
    async def get_roleplay_gif(self, action: str) -> str:
        nekos_actions = {"cuddle": "cuddle", "hug": "hug", "kiss": "kiss", "pat": "pat", "poke": "poke", "slap": "slap", "tickle": "tickle", "feed": "feed", "smug": "smug"}
        waifu_actions = {"cuddle": "cuddle", "hug": "hug", "kiss": "kiss", "pat": "pat", "poke": "poke", "slap": "slap", "lick": "lick", "bite": "bite", "highfive": "highfive", "handhold": "handhold", "wave": "wave", "wink": "wink", "bonk": "bonk", "kill": "kill", "kick": "kick", "cry": "cry", "blush": "blush", "smile": "smile", "happy": "happy", "dance": "dance", "nom": "nom", "glomp": "glomp", "cringe": "cringe"}
        purrbot_actions = {"bite": "bite/gif", "cuddle": "cuddle/gif", "hug": "hug/gif", "kiss": "kiss/gif", "lick": "lick/gif", "pat": "pat/gif", "poke": "poke/gif", "slap": "slap/gif", "tickle": "tickle/gif"}
        
        if action in waifu_actions:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.waifu_base}{waifu_actions[action]}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("url")
            except: pass
        
        if action in nekos_actions:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.nekos_base}{nekos_actions[action]}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("url")
            except: pass
        
        if action in purrbot_actions:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.purrbot_base}{purrbot_actions[action]}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("link")
            except: pass
        
        return None
    
    async def joint_send(self, ctx: commands.Context, message: str) -> discord.Message:
        embed = discord.Embed(color=self.joint_color, description=f"{self.joint_emoji} {ctx.author.mention}: {message}") 
        return await ctx.reply(embed=embed)
    
    async def smoke_send(self, ctx: commands.Context, message: str) -> discord.Message: 
        embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: {message}")
        return await ctx.reply(embed=embed)

    @commands.group(name="joint", invoke_without_command=True, description="have fun with a joint")
    async def jointcmd(self, ctx): 
        return await ctx.create_pages()

    @jointcmd.command(name="toggle", description="toggle the server joint", brief="manage guild")
    @Permissions.has_permission(manage_guild=True)
    async def joint_toggle(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = {}".format(ctx.guild.id)) 
        if not check: 
            await self.bot.db.execute("INSERT INTO joint VALUES ($1,$2,$3)", ctx.guild.id, 0, ctx.author.id)
            return await self.joint_send(ctx, "The joint is yours")
        await self.bot.db.execute("DELETE FROM joint WHERE guild_id = $1", ctx.guild.id)
        return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: Got rid of the server's joint")) 
    
    @jointcmd.command(name="stats", description="check joint stats", aliases=["status", "settings"])
    @Joint.check_joint()
    async def joint_stats(self, ctx: commands.Context):      
        check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
        embed = discord.Embed(color=self.joint_color, description=f"{self.smoke} hits: **{check['hits']}**\n{self.joint_emoji} Holder: <@{check['holder']}>")      
        embed.set_author(icon_url=ctx.guild.icon, name=f"{ctx.guild.name}'s joint")
        return await ctx.reply(embed=embed)

    @jointcmd.command(name="hit", description="hit the server joint")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_hit(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
        newhits = int(check["hits"]+1) 
        mes = await self.joint_send(ctx, "Hitting the **joint**.....")
        await asyncio.sleep(2)
        embed = discord.Embed(color=self.bot.color, description=f"{self.smoke} {ctx.author.mention}: You just hit the **joint**. This server has a total of **{newhits}** hits!")
        await mes.edit(embed=embed)
        await self.bot.db.execute("UPDATE joint SET hits = $1 WHERE guild_id = $2", newhits, ctx.guild.id)
    
    @joint_hit.error 
    async def on_error(self, ctx: commands.Context, error: Exception): 
        if isinstance(error, commands.CommandOnCooldown): 
            return await self.joint_send(ctx, "You are getting too high! Please wait until you can hit again") 

    @jointcmd.command(name="pass", description="pass the joint to someone else", usage="@qnok")
    @Joint.check_joint()
    @Joint.joint_owner()
    async def joint_pass(self, ctx: commands.Context, *, member: discord.Member):
        if member.id == self.bot.user.id: 
            return await ctx.reply("Thank you, but i do not smoke")
        elif member.bot: 
            return await ctx.warning("Bots do not smoke")
        elif member.id == ctx.author.id: 
            return await ctx.warning("You already have the **joint**")
        await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", member.id, ctx.guild.id)
        await self.joint_send(ctx, f"Passing the **joint** to **{member.name}**")
    
    @jointcmd.command(name="steal", description="steal the server's joint")
    @Joint.check_joint()
    async def joint_steal(self, ctx: commands.Context): 
        check = await self.bot.db.fetchrow("SELECT * FROM joint WHERE guild_id = $1", ctx.guild.id)
        if check["holder"] == ctx.author.id: 
            return await self.joint_send(ctx, "You already have the **joint**")
        chances = ["yes", "yes", "yes", "no", "no"]
        if random.choice(chances) == "no": 
            return await self.smoke_send(ctx, f"You tried to steal the **joint** and **{(await self.bot.fetch_user(int(check['holder']))).name}** hit you")
        await self.bot.db.execute("UPDATE joint SET holder = $1 WHERE guild_id = $2", ctx.author.id, ctx.guild.id)
        return await self.joint_send(ctx, "You got the server **joint**")

    @commands.command(description='cuddle a user', usage='<user>')
    async def cuddle(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("cuddle")
        count = await self.increment_action(ctx.author.id, user.id, "cuddle")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just cuddled **{user.name}** for the **{self.ordinal(count)}** time!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='poke a user', usage='<user>')
    async def poke(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("poke")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just poked **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='kiss a user', usage='<user>')
    async def kiss(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("kiss")
        count = await self.increment_action(ctx.author.id, user.id, "kiss")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just kissed **{user.name}** for the **{self.ordinal(count)}** time!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='hug a user', usage='<user>')
    async def hug(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("hug")
        count = await self.increment_action(ctx.author.id, user.id, "hug")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just hugged **{user.name}** for the **{self.ordinal(count)}** time!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='pat a user', usage='<user>')
    async def pat(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("pat")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just patted **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='tickle a user', usage='<user>')
    async def tickle(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("tickle")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just tickled **{user.name}**!")
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='lick a user', usage='<user>')
    async def lick(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("lick")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just licked **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='slap a user', usage='<user>')
    async def slap(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("slap")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just slapped **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='bite a user', usage='<user>')
    async def bite(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("bite")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just bit **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='feed a user', usage='<user>')
    async def feed(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("nom")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just fed **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='punch a user', usage='<user>')
    async def punch(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("bonk")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just punched **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='highfive a user', usage='<user>')
    async def highfive(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("highfive")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just highfived **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='wave at a user', usage='<user>')
    async def wave(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("wave")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just waved at **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='wink at a user', usage='<user>')
    async def wink(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("wink")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just winked at **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='bonk a user', usage='<user>')
    async def bonk(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("bonk")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just bonked **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='kill a user', usage='<user>')
    async def kill(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("kill")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just killed **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='kick a user (roleplay)', usage='<user>')
    async def rkick(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("kick")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just kicked **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='cry')
    async def cry(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("cry")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is crying!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='blush')
    async def blush(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("blush")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is blushing!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='smile')
    async def smile(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("smile")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is smiling!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='dance')
    async def dance(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("dance")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is dancing!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='glomp a user', usage='<user>')
    async def glomp(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("glomp")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** just glomped **{user.name}**!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='cringe at something')
    async def cringe(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("cringe")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is cringing!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='hold hands with a user', usage='<user>')
    async def handhold(self, ctx: commands.Context, user: discord.Member):
        gif_url = await self.get_roleplay_gif("handhold")
        count = await self.increment_action(ctx.author.id, user.id, "handhold")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is holding hands with **{user.name}** for the **{self.ordinal(count)}** time!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description='be smug')
    async def smug(self, ctx: commands.Context):
        gif_url = await self.get_roleplay_gif("smug")
        embed = discord.Embed(colour=self.bot.color, description=f"**{ctx.author.name}** is being smug!")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if gif_url: embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)

    @commands.command(description="marry a user", usage="<user>")
    async def marry(self, ctx: commands.Context, *, member: discord.Member):
        if member == ctx.author: return await ctx.warning("You can't marry yourself")
        if member.bot: return await ctx.warning("You can't marry a bot")
        
        author_check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id)
        if author_check: return await ctx.warning("You are already married")
        
        member_check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)
        if member_check: return await ctx.warning(f"**{member.name}** is already married")
        
        embed = discord.Embed(color=self.bot.color, description=f"💍 {member.mention}, **{ctx.author.name}** wants to marry you! Do you accept?")
        view = MarryView(ctx, member)
        view.message = await ctx.reply(embed=embed, view=view)

    @commands.command(description="divorce your partner")
    async def divorce(self, ctx: commands.Context):
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", ctx.author.id)
        if not check: check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", ctx.author.id)
        if not check: return await ctx.warning("You are not married")
        await self.bot.db.execute("DELETE FROM marry WHERE author = $1 OR soulmate = $1", ctx.author.id)
        return await ctx.success("You are now divorced 💔")

    @commands.command(description="check your marriage status", aliases=["marriage"])
    async def partner(self, ctx: commands.Context, *, member: discord.Member = None):
        if member is None: member = ctx.author
        check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE author = $1", member.id)
        if not check: check = await self.bot.db.fetchrow("SELECT * FROM marry WHERE soulmate = $1", member.id)
        if not check: return await ctx.warning(f"**{member.name}** is not married")
        partner_id = check["soulmate"] if check["author"] == member.id else check["author"]
        partner = await self.bot.fetch_user(partner_id)
        embed = discord.Embed(color=self.bot.color, description=f"💍 **{member.name}** is married to **{partner.name}**")
        embed.set_footer(text=f"Married since {datetime.datetime.fromtimestamp(check['time']).strftime('%B %d, %Y')}")
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(roleplay(bot))
