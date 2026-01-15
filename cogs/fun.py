import discord, random, asyncio, json, aiohttp
from discord.ext import commands
from patches.fun import Pack
from random import randrange
from io import BytesIO
from patches.permissions import Permissions
from bot.headers import Session
from patches.fun import RockPaperScissors, BlackTea, TicTacToe


class fun(commands.Cog):
    """All the fun related commands such as flags, blacktea, etc."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = Session()

    @commands.command(name="choose", description="choose between options", usage="[choices separated by a comma]")
    async def choose_cmd(self, ctx: commands.Context, *, choice: str): 
        choices = choice.split(", ")
        if len(choices) == 1: 
            return await ctx.reply("please put a `,` between your choices")
        final = random.choice(choices)
        await ctx.reply(embed=discord.Embed(color=self.bot.color, description=final))

    @Permissions.has_permission(manage_messages=True)
    @commands.command(name="poll", description="start a quick poll", help="fun", brief="manage messages")
    async def poll(self, ctx: commands.Context, *, question: str): 
        message = await ctx.send(embed=discord.Embed(color=self.bot.color, description=question).set_author(name=f"{ctx.author} asked"))
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.command(description="flip a coin", help="fun")
    async def coinflip(self, ctx: commands.Context): 
        await ctx.reply(random.choice(["heads", "tails"]))  
    
    @commands.command(aliases=["rps"], description="play rock paper scissors with the bot", help="fun")
    async def rockpaperscisssors(self, ctx: commands.Context): 
        view = RockPaperScissors(ctx)
        embed = discord.Embed(color=self.bot.color, title="Rock Paper Scissors!", description="Click a button to play!")
        view.message = await ctx.reply(embed=embed, view=view)    
    
    @commands.group(invoke_without_command=True)
    async def clock(self, ctx): 
        return await ctx.create_pages()
    
    @clock.command(name="in", help="fun", description="clock in")
    async def clock_in(self, ctx: commands.Context): 
        return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks in...")
    
    @clock.command(name="out", help="fun", description="clock out")
    async def clock_out(self, ctx: commands.Context): 
        return await ctx.reply(f"🕰️ {ctx.author.mention}: clocks out...")
    
    @commands.command(description="retard rate an user", help="fun", usage="@qnok")
    async def howretarded(self, ctx, member: discord.Member=commands.Author):
        if member.id in self.bot.owner_ids: 
            await ctx.reply(embed=discord.Embed(color=self.bot.color, title="how retarded", description=f"{member.mention} is `0%` retarded"))
        else: 
            await ctx.reply(embed=discord.Embed(color=self.bot.color, title="how retarded", description=f"{member.mention} is `{randrange(100)}%` retarded"))

    @commands.command(description="gay rate an user", help="fun", usage="@qnok")
    async def howgay(self, ctx, member: discord.Member=commands.Author):
        if member.id in self.bot.owner_ids: 
            return await ctx.reply(embed=discord.Embed(color=self.bot.color, title="gay r8", description=f"{member.mention} is `0%` gay 🏳️‍🌈"))
        else:
            await ctx.reply(embed=discord.Embed(color=self.bot.color, title="gay r8", description=f"{member.mention} is `{randrange(100)}%` gay 🏳️‍🌈"))
    
    @commands.command(description="cool rate an user", help="fun", usage="@qnok")
    async def howcool(self, ctx, member: discord.Member=commands.Author):
        await ctx.reply(embed=discord.Embed(color=self.bot.color, title="cool r8", description=f"{member.mention} is `{randrange(100)}%` cool 😎"))

    @commands.command(description="check an user's iq", help="fun", usage="@qnok")
    async def iq(self, ctx, member: discord.Member=commands.Author):
        if member.id in self.bot.owner_ids: 
            return await ctx.reply(embed=discord.Embed(color=self.bot.color, title="iq test", description=f"{member.mention} has `3000` iq 🧠"))
        else: 
            await ctx.reply(embed=discord.Embed(color=self.bot.color, title="iq test", description=f"{member.mention} has `{randrange(100)}` iq 🧠"))

    @commands.command(description="hot rate an user", help="fun", usage="@qnok")
    async def hot(self, ctx, member: discord.Member=commands.Author):
        await ctx.reply(embed=discord.Embed(color=self.bot.color, title="hot r8", description=f"{member.mention} is `{randrange(100)}%` hot 🥵"))     
    
    @commands.command()
    async def pp(self, ctx:commands.Context, *, member: discord.Member=commands.Author):
        lol = "===================="
        embed = discord.Embed(color=self.bot.color, description=f"{member.name}'s penis\n\n8{lol[random.randint(1, 20):]}D")
        if member.id in self.bot.owner_ids:
            embed = discord.Embed(color=self.bot.color, description=f"{member.name}'s penis\n\n8==============================D")
        await ctx.reply(embed=embed)  
    
    @commands.command(description="check how many bitches an user has", help="fun", usage="@qnok")
    async def bitches(self, ctx: commands.Context, *, user: discord.Member=commands.Author):
        choices = ["regular", "still regular", "lol", "xd", "id", "zero", "infinite"]
        if random.choice(choices) == "infinite": 
            result = "∞" 
        elif random.choice(choices) == "zero": 
            result = "0"
        else: 
            result = random.randint(0, 100)
        embed = discord.Embed(color=self.bot.color, description=f"{user.mention} has `{result}` bitches")
        if user.id in self.bot.owner_ids:
            embed = discord.Embed(color=self.bot.color, description=f"{user.mention} has `1000000000000` bitches")
        await ctx.reply(embed=embed)

    @commands.command(description="send a random bird image", help="fun")
    async def bird(self, ctx): 
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://some-random-api.com/animal/bird") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=data.get('image'))
                        if data.get('fact'):
                            embed.set_footer(text=data['fact'][:100])
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch bird image")
        except Exception as e:
            await ctx.warning("Could not fetch bird image")

    @commands.command(description="send a random dog image", help="fun")
    async def dog(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://dog.ceo/api/breeds/image/random") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=data.get('message'))
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch dog image")
        except Exception as e:
            await ctx.warning("Could not fetch dog image")

    @commands.command(description="send a random cat image", help="fun")
    async def cat(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=data[0].get('url'))
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch cat image")
        except Exception as e:
            await ctx.warning("Could not fetch cat image")
    
    @commands.command(description="send a random capybara image", help="fun")
    async def capybara(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.capy.lol/v1/capybara?json=true") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=data['data']['url'])
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch capybara image")
        except Exception as e:
            await ctx.warning("Could not fetch capybara image")
    
    @commands.command(description="return an useless fact", help="fun", aliases=["fact", "uf"])
    async def uselessfact(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        await ctx.reply(data['text'])
                    else:
                        await ctx.warning("Could not fetch fact")
        except Exception as e:
            await ctx.warning("Could not fetch fact")

    @commands.command(description='screenshot a website', usage='[url]', help='fun', aliases=['ss', 'screen'])
    async def screenshot(self, ctx: commands.Context, url: str):
        async with ctx.typing():
            if not url.startswith(("https://", "http://")):
                url = f"https://{url}"
            try:
                # Use a free screenshot API
                screenshot_url = f"https://api.screenshotone.com/take?url={url}&format=png&viewport_width=1920&viewport_height=1080"
                embed = discord.Embed(color=self.bot.color)
                embed.set_image(url=screenshot_url)
                await ctx.reply(embed=embed)
            except Exception:
                return await ctx.warning(f"This site **does not** appear to be valid.")

    @commands.command(description='grab info on a roblox profile', usage='[username]', help='fun')
    async def roblox(self, ctx: commands.Context, profile: str):
        try:
            async with aiohttp.ClientSession() as session:
                # Get user ID first
                async with session.post(
                    "https://users.roblox.com/v1/usernames/users",
                    json={"usernames": [profile], "excludeBannedUsers": True}
                ) as resp:
                    if resp.status != 200:
                        return await ctx.warning(f"{profile} **does not** appear to be valid.")
                    data = await resp.json()
                    if not data.get('data'):
                        return await ctx.warning(f"{profile} **does not** appear to be valid.")
                    user_id = data['data'][0]['id']
                    username = data['data'][0]['name']
                
                # Get user info
                async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
                    user_data = await resp.json()
                
                # Get avatar
                async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png") as resp:
                    avatar_data = await resp.json()
                    avatar_url = avatar_data['data'][0]['imageUrl'] if avatar_data.get('data') else None
                
                embed = discord.Embed(
                    color=self.bot.color,
                    title=username,
                    url=f"https://www.roblox.com/users/{user_id}/profile",
                    description=user_data.get('description', 'No description')[:500]
                )
                if avatar_url:
                    embed.set_thumbnail(url=avatar_url)
                embed.add_field(name="Display Name", value=user_data.get('displayName', username), inline=True)
                embed.add_field(name="Created", value=user_data.get('created', 'Unknown')[:10], inline=True)
                embed.set_footer(text='Roblox', icon_url='https://cdn.discordapp.com/attachments/1234567890/roblox.png')
                await ctx.reply(embed=embed)
        except Exception as e:
            return await ctx.warning(f"{profile} **does not** appear to be valid.")

    @commands.command(description="ship rate an user", help="fun", usage="@qnok")
    async def ship(self, ctx, member: discord.Member):
        return await ctx.reply(f"**{ctx.author.name}** 💞 **{member.name}** = **{randrange(101)}%**")

    @commands.command(description="sends a random advice", help="fun")
    async def advice(self, ctx: commands.Context):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.adviceslip.com/advice") as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        data = json.loads(text)
                        await ctx.reply(data['slip']['advice'])
                    else:
                        await ctx.warning("Could not fetch advice")
        except Exception as e:
            await ctx.warning("Could not fetch advice")
    
    @commands.command(description="pack someone", help="fun", usage="[user]")
    async def pack(self, ctx: commands.Context, *, member: discord.Member): 
        if member == ctx.author: 
            return await ctx.warning("You **cannot** pack yourself. I don't know why you would want to either.")
        await ctx.send(f"{member.mention} {random.choice(Pack.scripts)}") 

    @commands.command(aliases=["ttt"], description="play tictactoe with your friends", help="fun", usage="@qnok")
    async def tictactoe(self, ctx: commands.Context, *, member: discord.Member):
        if member is ctx.author: 
            return await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.warning} {ctx.author.mention}: You can't play with yourself. It's ridiculous"))
        if member.bot: 
            return await ctx.reply("bots can't play")      
        vi = TicTacToe(ctx.author, member)
        vi.message = await ctx.send(content=f'{member.mention}\n**{member.name}** vs **{ctx.author.name}**\n\nTic Tac Toe: **{ctx.author.name}** Is First', embed=None, view=vi, allowed_mentions=discord.AllowedMentions(users=True))  

    @commands.command(description="play blacktea with your friends", help="fun")
    async def blacktea(self, ctx: commands.Context): 
        try:
            if BlackTea.MatchStart[ctx.guild.id] is True: 
                return await ctx.reply("somebody in this server is already playing blacktea")
        except KeyError: 
            pass 

        BlackTea.MatchStart[ctx.guild.id] = True 
        embed = discord.Embed(color=self.bot.color, title="BlackTea Matchmaking", description=f"⏰ Waiting for players to join. To join react with 🍵.\nThe game will begin in **20 seconds**")
        embed.add_field(name="goal", value="You have **10 seconds** to say a word containing the given group of **3 letters.**\nIf failed to do so, you will lose a life. Each player has **2 lifes**")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)  
        mes = await ctx.send(embed=embed)
        await mes.add_reaction("🍵")
        await asyncio.sleep(20)
        me = await ctx.channel.fetch_message(mes.id)
        players = [user.id async for user in me.reactions[0].users()]
        leaderboard = []
        players.remove(self.bot.user.id)

        if len(players) < 2:
            BlackTea.MatchStart[ctx.guild.id] = False
            return await ctx.send("😦 {}, not enough players joined to start blacktea".format(ctx.author.mention), allowed_mentions=discord.AllowedMentions(users=True)) 
  
        while len(players) > 1: 
            for player in players: 
                strin = await BlackTea.get_string()
                await ctx.send(f"⏰ <@{player}>, type a word containing **{strin.upper()}** in **10 seconds**", allowed_mentions=discord.AllowedMentions(users=True))
            
                def is_correct(msg): 
                    return msg.author.id == player
            
                try: 
                    message = await self.bot.wait_for('message', timeout=10, check=is_correct)
                except asyncio.TimeoutError: 
                    try: 
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
                        if BlackTea.lifes[player] == 3: 
                            await ctx.send(f"☠️ <@{player}>, you're eliminated", allowed_mentions=discord.AllowedMentions(users=True))
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            leaderboard.append(player)
                            continue 
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(f"💥 <@{player}>, you didn't reply on time! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))
                    continue
                if strin.lower() in message.content.lower() and message.content.lower() in BlackTea.words: 
                    await message.add_reaction("✅")
                else:   
                    try: 
                        BlackTea.lifes[player] = BlackTea.lifes[player] + 1  
                        if BlackTea.lifes[player] == 3: 
                            await ctx.send(f"☠️ <@{player}>, you're eliminated", allowed_mentions=discord.AllowedMentions(users=True))
                            BlackTea.lifes[player] = 0
                            players.remove(player)
                            leaderboard.append(player)
                            continue 
                    except KeyError:
                        BlackTea.lifes[player] = 0
                    await ctx.send(f"💥 <@{player}>, that word is not valid! **{2-BlackTea.lifes[player]}** lifes remaining", allowed_mentions=discord.AllowedMentions(users=True))
                    continue

        leaderboard.append(players[0])
        leaderboard.reverse()
        BlackTea.MatchStart[ctx.guild.id] = False
        
        embed = discord.Embed(
            color=self.bot.color,
            title="🏆 BlackTea Results",
            description="\n".join([f"**{i+1}.** <@{player}>" for i, player in enumerate(leaderboard)])
        )
        await ctx.send(embed=embed)

    @commands.command(description="8ball", help="fun", usage="[question]")
    async def eightball(self, ctx: commands.Context, *, question: str):
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        embed = discord.Embed(
            color=self.bot.color,
            title="🎱 8ball",
            description=f"**Question:** {question}\n**Answer:** {random.choice(responses)}"
        )
        await ctx.reply(embed=embed)

    @commands.command(description="roll a dice", help="fun", usage="[sides]")
    async def dice(self, ctx: commands.Context, sides: int = 6):
        if sides < 2:
            return await ctx.warning("Dice must have at least 2 sides")
        if sides > 100:
            return await ctx.warning("Dice cannot have more than 100 sides")
        result = random.randint(1, sides)
        await ctx.reply(f"🎲 You rolled a **{result}** (1-{sides})")

    @commands.command(description="get a random joke", help="fun")
    async def joke(self, ctx: commands.Context):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(
                            color=self.bot.color,
                            title=data['setup'],
                            description=f"||{data['punchline']}||"
                        )
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch joke")
        except Exception as e:
            await ctx.warning("Could not fetch joke")

    @commands.command(description="get a random meme", help="fun")
    async def meme(self, ctx: commands.Context):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        embed = discord.Embed(
                            color=self.bot.color,
                            title=data['title'],
                            url=data['postLink']
                        )
                        embed.set_image(url=data['url'])
                        embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                        await ctx.reply(embed=embed)
                    else:
                        await ctx.warning("Could not fetch meme")
        except Exception as e:
            await ctx.warning("Could not fetch meme")


async def setup(bot: commands.Bot):
    await bot.add_cog(fun(bot))
