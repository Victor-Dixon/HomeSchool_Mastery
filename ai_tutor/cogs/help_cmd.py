"""
cogs/help_cmd.py — Custom Help Command
Shows all available commands in a clean embed.
"""

import discord
from discord.ext import commands


class HelpCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["commands"])
    async def help_command(self, ctx):
        """Show all available commands."""
        embed = discord.Embed(
            title="AI Tutor Bot — Commands",
            description="Your personal 7th grade TEKS tutor!",
            color=discord.Color.purple()
        )

        embed.add_field(
            name="Quiz",
            value=(
                "`!quiz` — Start a full quiz session\n"
                "`!question` — Get one random question\n"
                "`!drill <skill>` — Practice a specific skill\n"
                "`!drill` — See all available skills\n"
                "`!quit` — End your current session"
            ),
            inline=False
        )
        embed.add_field(
            name="Homework Help",
            value=(
                "`!ask <question> | <your answer>` — AI help on any problem\n"
                "`!ask <question> | <your answer> | <correct answer>` — With answer\n"
                "`!solve <problem>` — AI solves and explains any problem\n\n"
                "Example: `!ask 3/4 + 1/2 | 4/6`"
            ),
            inline=False
        )
        embed.add_field(
            name="Progress",
            value=(
                "`!progress` — See your skill breakdown\n"
                "`!xp` — See your level, XP & streak\n"
                "`!weakskills` — See what to practice next"
            ),
            inline=False
        )
        embed.set_footer(text="Type any command to get started! | !quiz is the best first step")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCmd(bot))
