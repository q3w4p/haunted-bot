import discord
import asyncio
import json
from discord.ext import commands
from discord import Embed, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from typing import List, Optional, Union
from patches.permissions import Permissions

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
        """Get the prefix as a string for this context"""
        if not self.guild:
            return ","
        check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", self.guild.id)
        if check:
            return check["prefix"]
        return ","

    async def cmdhelp(self):
        """Send help for the current command"""
        command = self.command
        prefix = await self.get_prefix_str()
        
        embed = Embed(color=self.bot.color)
        embed.set_author(name=f"Command: {command.qualified_name}", icon_url=self.bot.user.display_avatar.url)
        
        # Description with blockquote
        desc = command.description or command.help or "No description available"
        if command.parent:
            desc += f"\nSubcommand of: `{command.parent.qualified_name}`"
        embed.description = f"> {desc}"
        
        # Syntax and Example with ANSI
        usage = command.usage or ""
        syntax = f"{prefix}{command.qualified_name} {usage}".strip()
        example = f"{prefix}{command.qualified_name}"
        if usage:
            example_usage = self._format_example(usage)
            example = f"{prefix}{command.qualified_name} {example_usage}".strip()
        
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        
        # Optional Flags if command has them
        if hasattr(command, 'extras') and 'flags' in command.extras:
            flags_text = ""
            for flag, desc in command.extras['flags'].items():
                flags_text += f"`{flag}`: {desc}\n"
            embed.add_field(name="Optional Flags", value=flags_text, inline=False)
        
        # Footer with module, aliases
        aliases = ", ".join(command.aliases) if command.aliases else "None"
        cog_name = command.cog.qualified_name if command.cog else "No Category"
        embed.set_footer(text=f"Module: {cog_name} • Aliases: {aliases}")
        
        await self.reply(embed=embed, mention_author=False)

    def _format_example(self, usage):
        """Format usage string into example with @qnok highlighted"""
        example = usage
        example = example.replace("<user>", "[@qnok](https://discord.com/invite/hauntedbot)")
        example = example.replace("<member>", "[@qnok](https://discord.com/invite/hauntedbot)")
        example = example.replace("<role>", "@Members")
        example = example.replace("<channel>", "#general")
        example = example.replace("<reason>", "breaking rules")
        example = example.replace("<time>", "1h")
        example = example.replace("<url>", "`https://example.com`")
        example = example.replace("<image>", "`https://example.png`")
        example = example.replace("<message>", "Hello!")
        example = example.replace("<amount>", "10")
        example = example.replace("<status>", "on")
        example = example.replace("<flags>", "--threshold=3")
        example = example.replace("<punishment>", "ban")
        example = example.replace("<threshold>", "3")
        example = example.replace("<duration>", "1h")
        example = example.replace("<query>", "song name")
        example = example.replace("<text>", "Hello world")
        example = example.replace("[", "").replace("]", "").replace("<", "").replace(">", "")
        return example

    async def success(self, message: str):
        return await self.reply(
            embed=Embed(color=self.bot.color, description=f"{self.bot.yes} {self.author.mention}: {message}"),
            mention_author=False
        )

    async def warning(self, message: str):
        return await self.reply(
            embed=Embed(color=self.bot.error_color, description=f"{self.bot.warning} {self.author.mention}: {message}"),
            mention_author=False
        )

    async def deny(self, message: str):
        return await self.reply(
            embed=Embed(color=self.bot.no_color, description=f"{self.bot.no} {self.author.mention}: {message}"),
            mention_author=False
        )

    async def error(self, message: str):
        """Send an error message"""
        return await self.reply(
            embed=Embed(color=self.bot.error_color, description=f"{self.bot.warning} {self.author.mention}: {message}"),
            mention_author=False
        )

    async def neutral(self, message: str):
        """Send a neutral message"""
        return await self.reply(
            embed=Embed(color=self.bot.color, description=f"{self.author.mention}: {message}"),
            mention_author=False
        )

    async def lastfm_message(self, message: str):
        return await self.reply(
            embed=Embed(color=0xd51007, description=f"<:lastfm:1461012699243610327> {self.author.mention}: {message}"),
            mention_author=False
        )

    async def create_pages(self):
        """Send help for the current command (used by group commands)"""
        return await self.send_help(self.command)

    async def paginate(self, pages: list):
        """Paginate a list of embeds"""
        from bot.ext import Paginator
        paginator = Paginator(self.bot, pages, self)
        await paginator.start()


class HelpPaginator(View):
    """Paginated help menu with navigation buttons"""
    
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
        """Update button states based on current page"""
        self.children[0].disabled = self.current_page == 0
        self.children[2].disabled = self.current_page >= len(self.pages) - 1
    
    async def update_page(self, interaction: discord.Interaction):
        """Update the embed to show current page"""
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
    
    @discord.ui.button(emoji="↕", style=ButtonStyle.secondary)
    async def jump_button(self, interaction: discord.Interaction, button: Button):
        """Jump to a specific page"""
        await interaction.response.send_message(
            f"Enter a page number (1-{len(self.pages)}):", 
            ephemeral=True
        )
        
        def check(m):
            return m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id
        
        try:
            msg = await self.ctx.bot.wait_for('message', check=check, timeout=30.0)
            page_num = int(msg.content) - 1
            if 0 <= page_num < len(self.pages):
                self.current_page = page_num
                self.update_buttons()
                embed = self.pages[self.current_page]
                embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")
                await self.message.edit(embed=embed, view=self)
            await msg.delete()
        except (ValueError, asyncio.TimeoutError):
            pass


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                'help': 'Shows help for the bot, a category, or a command.',
                'aliases': ['h', 'commands']
            }
        )
    
    async def get_prefix(self) -> str:
        """Get the current prefix"""
        ctx = self.context
        if not ctx.guild:
            return ","
        check = await ctx.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", ctx.guild.id)
        if check:
            return check["prefix"]
        return ","
    
    def get_command_signature(self, command):
        return f"{command.qualified_name} {command.signature}"
    
    async def send_bot_help(self, mapping):
        """Send the main help menu with all categories"""
        ctx = self.context
        prefix = await self.get_prefix()
        
        # Get all cogs with commands
        cogs_with_commands = {}
        total_commands = 0
        
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                cog_name = cog.qualified_name if cog else "No Category"
                cogs_with_commands[cog_name] = filtered
                total_commands += len(filtered)
        
        # Create pages
        pages = []
        
        # Page 1: Main menu with categories in columns
        embed = Embed(color=ctx.bot.color)
        embed.title = f"[ {total_commands} commands ]"
        embed.set_thumbnail(url=HELP_THUMBNAIL)
        
        # Format categories in 3 columns
        category_names = sorted(cogs_with_commands.keys())
        
        # Build category text in columns
        col1, col2, col3 = [], [], []
        for i, name in enumerate(category_names):
            # Make category names clickable
            linked_name = f"[{name}](https://discord.com/invite/hauntedbot)"
            if i % 3 == 0:
                col1.append(name)
            elif i % 3 == 1:
                col2.append(name)
            else:
                col3.append(name)
        
        # Create formatted text
        max_len = max(len(col1), len(col2), len(col3)) if col1 or col2 or col3 else 0
        lines = []
        for i in range(max_len):
            row = ""
            if i < len(col1):
                row += f"{col1[i]:<15}"
            else:
                row += " " * 15
            if i < len(col2):
                row += f"{col2[i]:<15}"
            else:
                row += " " * 15
            if i < len(col3):
                row += col3[i]
            lines.append(row.rstrip())
        
        embed.description = "```\n" + "\n".join(lines) + "\n```"
        embed.set_footer(text=f"Page 1 of {len(category_names) + 1}")
        pages.append(embed)
        
        # Create a page for each category with commands in columns
        for cog_name in sorted(cogs_with_commands.keys()):
            cmds = cogs_with_commands[cog_name]
            cmd_names = [cmd.name for cmd in cmds]
            
            # Split into pages of 21 commands (7 rows x 3 columns)
            chunks = [cmd_names[i:i+21] for i in range(0, len(cmd_names), 21)]
            
            for page_num, chunk in enumerate(chunks, 1):
                embed = Embed(color=ctx.bot.color)
                embed.title = f"[ {cog_name} - Page {page_num}/{len(chunks)} ]"
                embed.set_thumbnail(url=HELP_THUMBNAIL)
                
                # Format commands in 3 columns
                col1, col2, col3 = [], [], []
                for i, name in enumerate(chunk):
                    # Make command names clickable (dark blue)
                    if i % 3 == 0:
                        col1.append(f"[{name}](https://discord.com/invite/hauntedbot)")
                    elif i % 3 == 1:
                        col2.append(f"[{name}](https://discord.com/invite/hauntedbot)")
                    else:
                        col3.append(f"[{name}](https://discord.com/invite/hauntedbot)")
                
                max_len = max(len(col1), len(col2), len(col3)) if col1 or col2 or col3 else 0
                lines = []
                for i in range(max_len):
                    row_parts = []
                    if i < len(col1):
                        row_parts.append(col1[i])
                    if i < len(col2):
                        row_parts.append(col2[i])
                    if i < len(col3):
                        row_parts.append(col3[i])
                    lines.append("  ".join(row_parts))
                
                embed.description = "\n".join(lines)
                pages.append(embed)
        
        # Send with paginator
        view = HelpPaginator(ctx, pages)
        view.update_buttons()
        pages[0].set_footer(text=f"Page 1 of {len(pages)}")
        message = await ctx.reply(embed=pages[0], view=view, mention_author=False)
        view.message = message
    
    async def send_cog_help(self, cog):
        """Send help for a specific cog/category"""
        ctx = self.context
        prefix = await self.get_prefix()
        
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        if not filtered:
            return await ctx.warning(f"No commands found in **{cog.qualified_name}**")
        
        cmd_names = [cmd.name for cmd in filtered]
        chunks = [cmd_names[i:i+21] for i in range(0, len(cmd_names), 21)]
        pages = []
        
        for page_num, chunk in enumerate(chunks, 1):
            embed = Embed(color=ctx.bot.color)
            embed.title = f"[ {cog.qualified_name} - Page {page_num}/{len(chunks)} ]"
            embed.set_thumbnail(url=HELP_THUMBNAIL)
            
            # Format commands in 3 columns with clickable links
            col1, col2, col3 = [], [], []
            for i, name in enumerate(chunk):
                linked = f"[{name}](https://discord.com/invite/hauntedbot)"
                if i % 3 == 0:
                    col1.append(linked)
                elif i % 3 == 1:
                    col2.append(linked)
                else:
                    col3.append(linked)
            
            max_len = max(len(col1), len(col2), len(col3)) if col1 or col2 or col3 else 0
            lines = []
            for i in range(max_len):
                row_parts = []
                if i < len(col1):
                    row_parts.append(col1[i])
                if i < len(col2):
                    row_parts.append(col2[i])
                if i < len(col3):
                    row_parts.append(col3[i])
                lines.append("  ".join(row_parts))
            
            embed.description = "\n".join(lines)
            pages.append(embed)
        
        view = HelpPaginator(ctx, pages)
        view.update_buttons()
        pages[0].set_footer(text=f"Page 1 of {len(pages)}")
        message = await ctx.reply(embed=pages[0], view=view, mention_author=False)
        view.message = message
    
    async def send_group_help(self, group):
        """Send help for a command group"""
        ctx = self.context
        prefix = await self.get_prefix()
        
        embed = Embed(color=ctx.bot.color)
        embed.set_author(name=f"Command: {group.qualified_name}", icon_url=ctx.bot.user.display_avatar.url)
        
        # Description
        desc = group.description or group.help or "No description available"
        embed.description = f"> {desc}"
        
        # Syntax and Example
        usage = group.usage or ""
        syntax = f"{prefix}{group.qualified_name} {usage}".strip()
        example = f"{prefix}{group.qualified_name}"
        if usage:
            example_usage = self._format_example(usage)
            example = f"{prefix}{group.qualified_name} {example_usage}".strip()
        
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        
        # Subcommands
        if group.commands:
            subcommands = await self.filter_commands(group.commands, sort=True)
            if subcommands:
                sub_text = ", ".join([f"[`{cmd.name}`](https://discord.com/invite/hauntedbot)" for cmd in subcommands])
                embed.add_field(name="Subcommands", value=sub_text, inline=False)
        
        # Footer
        aliases = ", ".join(group.aliases) if group.aliases else "None"
        cog_name = group.cog.qualified_name if group.cog else "No Category"
        embed.set_footer(text=f"Module: {cog_name} • Aliases: {aliases}")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    async def send_command_help(self, command):
        """Send help for a specific command"""
        ctx = self.context
        prefix = await self.get_prefix()
        
        embed = Embed(color=ctx.bot.color)
        embed.set_author(name=f"Command: {command.qualified_name}", icon_url=ctx.bot.user.display_avatar.url)
        
        # Description with blockquote
        desc = command.description or command.help or "No description available"
        if command.parent:
            desc += f"\nSubcommand of: `{command.parent.qualified_name}`"
        embed.description = f"> {desc}"
        
        # Syntax and Example with ANSI
        usage = command.usage or command.signature or ""
        syntax = f"{prefix}{command.qualified_name} {usage}".strip()
        example = f"{prefix}{command.qualified_name}"
        
        if usage:
            example_usage = self._format_example(usage)
            example = f"{prefix}{command.qualified_name} {example_usage}".strip()
        
        ansi_block = f"```ansi\n\u001b[0;35mSyntax:\u001b[0m {syntax}\n\u001b[0;35mExample:\u001b[0m {example}\n```"
        embed.add_field(name="\u200b", value=ansi_block, inline=False)
        
        # Optional Flags if command has them
        if hasattr(command, 'extras') and command.extras and 'flags' in command.extras:
            flags_text = ""
            for flag, desc in command.extras['flags'].items():
                flags_text += f"`{flag}`: {desc}\n"
            embed.add_field(name="Optional Flags", value=flags_text, inline=False)
        
        # Footer with module, aliases
        aliases = ", ".join(command.aliases) if command.aliases else "None"
        cog_name = command.cog.qualified_name if command.cog else "No Category"
        embed.set_footer(text=f"Module: {cog_name} • Aliases: {aliases}")
        
        await ctx.reply(embed=embed, mention_author=False)
    
    def _format_example(self, usage):
        """Format usage string into example with @qnok highlighted in dark blue"""
        example = usage
        # Use Discord markdown links for dark blue highlighting
        example = example.replace("<user>", "[@qnok](https://discord.com/invite/hauntedbot)")
        example = example.replace("<member>", "[@qnok](https://discord.com/invite/hauntedbot)")
        example = example.replace("<role>", "@Members")
        example = example.replace("<channel>", "#general")
        example = example.replace("<reason>", "breaking rules")
        example = example.replace("<time>", "1h")
        example = example.replace("<url>", "`https://example.com`")
        example = example.replace("<image>", "`https://example.png`")
        example = example.replace("<message>", "Hello!")
        example = example.replace("<amount>", "10")
        example = example.replace("<status>", "on")
        example = example.replace("<flags>", "--threshold=3")
        example = example.replace("<punishment>", "ban")
        example = example.replace("<threshold>", "3")
        example = example.replace("<duration>", "1h")
        example = example.replace("<query>", "song name")
        example = example.replace("<text>", "Hello world")
        example = example.replace("[", "").replace("]", "").replace("<", "").replace(">", "")
        return example
    
    async def send_error_message(self, error):
        ctx = self.context
        await ctx.warning(error)


class StartUp:
    @staticmethod
    async def loadcogs(bot):
        """Load all cogs and events"""
        import os
        
        # Load events
        events_dir = 'events'
        if os.path.exists(events_dir):
            for filename in os.listdir(events_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    try:
                        await bot.load_extension(f'{events_dir}.{filename[:-3]}')
                        print(f'✓ Loaded event: {filename[:-3]}')
                    except Exception as e:
                        print(f'✗ Failed to load event {filename[:-3]}: {e}')
        
        # Load cogs
        cogs_dir = 'cogs'
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    try:
                        await bot.load_extension(f'{cogs_dir}.{filename[:-3]}')
                        print(f'✓ Loaded cog: {filename[:-3]}')
                    except Exception as e:
                        print(f'✗ Failed to load cog {filename[:-3]}: {e}')
