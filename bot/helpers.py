import discord
import asyncio
import json
import re
from discord.ext import commands
from discord import Embed, ButtonStyle
from discord.ui import View, Button
from typing import List, Optional, Union

# Help menu thumbnail - ghost/haunted image
HELP_THUMBNAIL = "https://cdn.discordapp.com/attachments/1199044941946200164/1199045012431511582/image.png"


class HauntedContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    async def getprefix(bot, message):
        if not message.guild:
            return ","
        check = await bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", message.guild.id)
        if check:
            return check["prefix"]
        return ","

    async def get_prefix_str(self):
        if not self.guild:
            return ","
        check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", self.guild.id)
        if check:
            return check["prefix"]
        return ","

    async def cmdhelp(self):
        command = self.command
        prefix = await self.get_prefix_str()
        embed = Embed(color=self.bot.color)
        embed.set_author(name=f"Command: {command.qualified_name}", icon_url=self.bot.user.display_avatar.url)
        desc = command.description or command.help or "No description available"
        if command.parent:
            desc += f"\nSubcommand of: `{command.parent.qualified_name}`"
        embed.description = f"> {desc}"
        usage = command.usage or ""
        syntax = f"{prefix}{command.qualified_name} {usage}".strip()
        example = f"{prefix}{command.qualified_name}"
        if usage:
            example_usage = self._format_example(usage)
            example = f"{prefix}{command.qualified_name} {example_usage}".strip()
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        aliases = ", ".join(command.aliases) if command.aliases else "None"
        cog_name = command.cog.qualified_name if command.cog else "No Category"
        embed.set_footer(text=f"Module: {cog_name} • Aliases: {aliases}")
        await self.reply(embed=embed, mention_author=False)

    def _format_example(self, usage):
        example = usage
        # User/Member mentions with ANSI blue color
        example = example.replace("<user>", "\u001b[0;34m@qnok\u001b[0m")
        example = example.replace("<member>", "\u001b[0;34m@qnok\u001b[0m")
        example = example.replace("<role>", "@Members")
        example = example.replace("<channel>", "#general")
        example = example.replace("<reason>", "breaking rules")
        example = example.replace("<time>", "1h")
        example = example.replace("<duration>", "1h")
        example = example.replace("<url>", "https://example.com")
        example = example.replace("<image>", "https://example.png")
        example = example.replace("<message>", "Hello!")
        example = example.replace("<amount>", "10")
        example = example.replace("<number>", "10")
        example = example.replace("<status>", "on")
        example = example.replace("<flags>", "--threshold=3")
        example = example.replace("<punishment>", "ban")
        example = example.replace("<threshold>", "3")
        example = example.replace("<query>", "song name")
        example = example.replace("<text>", "Hello world")
        example = example.replace("<name>", "MyName")
        # Code examples for embed/code parameters
        example = example.replace("<code>", "{embed}$v{color: #D4BCD2}$v{title: haunted}$v{description: you can edit this description}")
        example = example.replace("<embed>", "{embed}$v{color: #D4BCD2}$v{title: haunted}$v{description: you can edit this description}")
        # Remove remaining brackets
        example = re.sub(r'[\[\]<>]', '', example)
        return example

    async def success(self, message: str):
        return await self.reply(embed=Embed(color=self.bot.color, description=f"{self.bot.yes} {self.author.mention}: {message}"), mention_author=False)

    async def warning(self, message: str):
        return await self.reply(embed=Embed(color=self.bot.error_color, description=f"{self.bot.warning} {self.author.mention}: {message}"), mention_author=False)

    async def deny(self, message: str):
        return await self.reply(embed=Embed(color=self.bot.no_color, description=f"{self.bot.no} {self.author.mention}: {message}"), mention_author=False)

    async def error(self, message: str):
        return await self.reply(embed=Embed(color=self.bot.error_color, description=f"{self.bot.warning} {self.author.mention}: {message}"), mention_author=False)

    async def neutral(self, message: str):
        return await self.reply(embed=Embed(color=self.bot.color, description=f"{self.author.mention}: {message}"), mention_author=False)

    async def lastfm_message(self, message: str):
        return await self.reply(embed=Embed(color=0xd51007, description=f"<:lastfm:1461012699243610327> {self.author.mention}: {message}"), mention_author=False)

    async def create_pages(self):
        """Send help for the current command (used by group commands)"""
        return await self.send_help(self.command)

    async def paginate(self, pages: list):
        from bot.ext import Paginator
        paginator = Paginator(self.bot, pages, self)
        await paginator.start()


class HelpPaginator(View):
    def __init__(self, ctx: HauntedContext, pages: List[Embed], timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0
        self.message: Optional[discord.Message] = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your help menu!", ephemeral=True)
            return False
        return True
    
    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[2].disabled = self.current_page >= len(self.pages) - 1
    
    async def update_page(self, interaction: discord.Interaction):
        self.update_buttons()
        embed = self.pages[self.current_page]
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="<:left:1451659678164582694>", style=ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page(interaction)
    
    @discord.ui.button(emoji="✖", style=ButtonStyle.secondary)
    async def close_button(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()
        self.stop()
    
    @discord.ui.button(emoji="<:right:1451659703124885697>", style=ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_page(interaction)


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                'help': 'Shows help for the bot, a category, or a command.',
                'aliases': ['h', 'commands']
            }
        )
    
    async def get_prefix(self) -> str:
        ctx = self.context
        if not ctx.guild: return ","
        check = await ctx.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id)
        return check["prefix"] if check else ","
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        cogs_with_commands = {}
        total_commands = 0
        excluded_cogs = ["jishaku", "api", "owner", "auth", "listeners", "bot", "tasks", "messages", "reacts", "no category"]
        
        for cog, cmds in mapping.items():
            if not cmds: continue
            cog_name = cog.qualified_name if cog else "No Category"
            if cog_name.lower() in excluded_cogs: continue
            cogs_with_commands[cog_name] = cmds
            total_commands += len(cmds)
        
        pages = []
        # Main Page
        embed = Embed(color=ctx.bot.color)
        embed.description = f"```ansi\n\u001b[0;34m[ {total_commands} commands ]\u001b[0m\n```\n"
        embed.set_thumbnail(url=HELP_THUMBNAIL)
        category_names = sorted(cogs_with_commands.keys())
        col1, col2, col3 = [], [], []
        for i, name in enumerate(category_names):
            linked_name = f"[`{name.capitalize()}`](https://discord.com/invite/hauntedbot)"
            if i % 3 == 0: col1.append(linked_name)
            elif i % 3 == 1: col2.append(linked_name)
            else: col3.append(linked_name)
        
        max_len = max(len(col1), len(col2), len(col3)) if col1 or col2 or col3 else 0
        lines = []
        for i in range(max_len):
            row = f"{col1[i] if i < len(col1) else '':<25} {col2[i] if i < len(col2) else '':<25} {col3[i] if i < len(col3) else ''}"
            lines.append(row.rstrip())
        embed.description += "\n".join(lines)
        pages.append(embed)
        
        # Category Pages
        for cog_name in sorted(cogs_with_commands.keys()):
            cmds = cogs_with_commands[cog_name]
            cmd_names = sorted([f"[`{cmd.name}`](https://discord.com/invite/hauntedbot)" for cmd in cmds])
            # Limit to 12 commands per page for better spacing (4 rows x 3 columns)
            chunks = [cmd_names[i:i+12] for i in range(0, len(cmd_names), 12)]
            for page_num, chunk in enumerate(chunks, 1):
                embed = Embed(color=ctx.bot.color)
                embed.description = f"```ansi\n\u001b[0;34m[ {cog_name.capitalize()} - Page {page_num}/{len(chunks)} ]\u001b[0m\n```\n"
                embed.set_thumbnail(url=HELP_THUMBNAIL)
                col1, col2, col3 = [], [], []
                for i, name in enumerate(chunk):
                    if i % 3 == 0: col1.append(name)
                    elif i % 3 == 1: col2.append(name)
                    else: col3.append(name)
                
                max_len = max(len(col1), len(col2), len(col3))
                lines = []
                for i in range(max_len):
                    row = f"{col1[i] if i < len(col1) else '':<30} {col2[i] if i < len(col2) else '':<30} {col3[i] if i < len(col3) else ''}"
                    lines.append(row.rstrip())
                embed.description += "\u200b\n" + "\n\n".join(lines) # Double newline for better spacing
                pages.append(embed)
        
        view = HelpPaginator(ctx, pages)
        view.update_buttons()
        pages[0].set_footer(text=f"Page 1 of {len(pages)}")
        message = await ctx.reply(embed=pages[0], view=view, mention_author=False)
        view.message = message

    async def send_cog_help(self, cog):
        ctx = self.context
        cmds = cog.get_commands()
        if not cmds: return await ctx.warning(f"No commands found in **{cog.qualified_name}**")
        cmd_names = sorted([f"[`{cmd.name}`](https://discord.com/invite/hauntedbot)" for cmd in cmds])
        chunks = [cmd_names[i:i+12] for i in range(0, len(cmd_names), 12)]
        pages = []
        for page_num, chunk in enumerate(chunks, 1):
            embed = Embed(color=ctx.bot.color)
            embed.description = f"```ansi\n\u001b[0;34m[ {cog.qualified_name.capitalize()} - Page {page_num}/{len(chunks)} ]\u001b[0m\n```\n"
            embed.set_thumbnail(url=HELP_THUMBNAIL)
            col1, col2, col3 = [], [], []
            for i, name in enumerate(chunk):
                if i % 3 == 0: col1.append(name)
                elif i % 3 == 1: col2.append(name)
                else: col3.append(name)
            max_len = max(len(col1), len(col2), len(col3))
            lines = []
            for i in range(max_len):
                row = f"{col1[i] if i < len(col1) else '':<30} {col2[i] if i < len(col2) else '':<30} {col3[i] if i < len(col3) else ''}"
                lines.append(row.rstrip())
            embed.description += "\u200b\n" + "\n\n".join(lines)
            pages.append(embed)
        view = HelpPaginator(ctx, pages)
        view.update_buttons()
        pages[0].set_footer(text=f"Page 1 of {len(pages)}")
        message = await ctx.reply(embed=pages[0], view=view, mention_author=False)
        view.message = message

    async def send_group_help(self, group):
        ctx = self.context
        prefix = await self.get_prefix()
        embed = Embed(color=ctx.bot.color)
        embed.set_author(name=f"Command: {group.qualified_name}", icon_url=ctx.bot.user.display_avatar.url)
        embed.description = f"> {group.description or group.help or 'No description available'}"
        usage = group.usage or ""
        syntax = f"{prefix}{group.qualified_name} {usage}".strip()
        example = f"{prefix}{group.qualified_name} {self._format_example(usage)}".strip()
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        if group.commands:
            sub_text = ", ".join([f"[`{cmd.name}`](https://discord.com/invite/hauntedbot)" for cmd in group.commands])
            embed.add_field(name="Subcommands", value=sub_text, inline=False)
        embed.set_footer(text=f"Module: {group.cog.qualified_name if group.cog else 'No Category'} • Aliases: {', '.join(group.aliases) if group.aliases else 'None'}")
        await ctx.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command):
        ctx = self.context
        prefix = await self.get_prefix()
        embed = Embed(color=ctx.bot.color)
        embed.set_author(name=f"Command: {command.qualified_name}", icon_url=ctx.bot.user.display_avatar.url)
        embed.description = f"> {command.description or command.help or 'No description available'}"
        usage = command.usage or command.signature or ""
        syntax = f"{prefix}{command.qualified_name} {usage}".strip()
        example = f"{prefix}{command.qualified_name} {self._format_example(usage)}".strip()
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        embed.set_footer(text=f"Module: {command.cog.qualified_name if command.cog else 'No Category'} • Aliases: {', '.join(command.aliases) if command.aliases else 'None'}")
        await ctx.reply(embed=embed, mention_author=False)

    def _format_example(self, usage):
        """Format usage examples with proper replacements"""
        example = usage
        # User/Member mentions with ANSI blue color
        example = example.replace("<user>", "\u001b[0;34m@qnok\u001b[0m")
        example = example.replace("<member>", "\u001b[0;34m@qnok\u001b[0m")
        example = example.replace("<role>", "@Members")
        example = example.replace("<channel>", "#general")
        example = example.replace("<reason>", "breaking rules")
        example = example.replace("<time>", "1h")
        example = example.replace("<duration>", "1h")
        example = example.replace("<url>", "https://example.com")
        example = example.replace("<image>", "https://example.png")
        example = example.replace("<message>", "Hello!")
        example = example.replace("<amount>", "10")
        example = example.replace("<number>", "10")
        example = example.replace("<status>", "on")
        example = example.replace("<flags>", "--threshold=3")
        example = example.replace("<punishment>", "ban")
        example = example.replace("<threshold>", "3")
        example = example.replace("<query>", "song name")
        example = example.replace("<text>", "Hello world")
        example = example.replace("<name>", "MyName")
        # Code examples for embed/code parameters
        example = example.replace("<code>", "{embed}$v{color: #D4BCD2}$v{title: haunted}$v{description: you can edit this description}")
        example = example.replace("<embed>", "{embed}$v{color: #D4BCD2}$v{title: haunted}$v{description: you can edit this description}")
        # Remove remaining brackets
        import re
        example = re.sub(r'[\[\]<>]', '', example)
        return example
    
    async def send_error_message(self, error):
        await self.context.warning(error)


class StartUp:
    @staticmethod
    async def loadcogs(bot):
        import os
        for folder in ['events', 'cogs']:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    if filename.endswith('.py') and not filename.startswith('_'):
                        try:
                            await bot.load_extension(f'{folder}.{filename[:-3]}')
                            print(f'✓ Loaded {folder[:-1]}: {filename[:-3]}')
                        except Exception as e:
                            print(f'✗ Failed to load {folder[:-1]} {filename[:-3]}: {e}')
