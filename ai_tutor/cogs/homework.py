"""
cogs/homework.py — Free-Form Homework Help
Commands:
  !ask <question> | <student answer>
  !ask <question> | <student answer> | <correct answer>

This is the money command — parents paste any problem directly.
No quiz structure needed. AI figures out if it's right and explains.

Examples:
  !ask 3/4 + 1/2 | 4/6
  !ask What is 25% of 80? | 15 | 20
  !ask Solve 2x + 3 = 11 | x = 3
"""

import discord
from discord.ext import commands
import asyncio
from ai_tutor import tutor


class Homework(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ask", aliases=["hw", "homework"])
    async def ask(self, ctx, *, content: str = None):
        """
        Free-form homework help.
        Usage: !ask <question> | <your answer>
        Or:    !ask <question> | <your answer> | <correct answer>
        """
        if not content:
            embed = discord.Embed(
                title="Homework Help",
                description=(
                    "**How to use:**\n"
                    "`!ask <question> | <your answer>`\n"
                    "`!ask <question> | <your answer> | <correct answer>`\n\n"
                    "**Examples:**\n"
                    "`!ask 3/4 + 1/2 | 4/6`\n"
                    "`!ask What is 25% of 80? | 15 | 20`\n"
                    "`!ask Solve 2x + 3 = 11 | x = 3`\n\n"
                    "You can leave out the correct answer — the AI will figure it out!"
                ),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        parts = [p.strip() for p in content.split("|")]

        if len(parts) < 2:
            await ctx.send(
                "Please use the format: `!ask <question> | <your answer>`\n"
                "Example: `!ask 3/4 + 1/2 | 4/6`"
            )
            return

        question = parts[0]
        user_answer = parts[1]
        correct_answer = parts[2] if len(parts) >= 3 else None

        thinking_msg = await ctx.send("Thinking...")

        explanation = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: tutor.ask_freeform(question, user_answer, correct_answer)
        )

        await thinking_msg.delete()

        if len(explanation) > 1900:
            explanation = explanation[:1900] + "..."

        embed = discord.Embed(
            title="Homework Help",
            color=discord.Color.green()
        )
        embed.add_field(name="Question", value=f"`{question}`", inline=False)
        embed.add_field(name="Your Answer", value=f"`{user_answer}`", inline=True)
        if correct_answer:
            embed.add_field(name="Correct Answer", value=f"`{correct_answer}`", inline=True)
        embed.add_field(name="Explanation", value=explanation, inline=False)
        embed.set_footer(text="Practice more with !quiz | See your progress with !progress")

        await ctx.send(embed=embed)

    @commands.command(name="solve", aliases=["check"])
    async def solve(self, ctx, *, question: str = None):
        """
        Ask the AI to solve a problem outright (no student answer needed).
        Usage: !solve 3/4 + 1/2
        """
        if not question:
            await ctx.send("Usage: `!solve <math problem>`\nExample: `!solve 3/4 + 1/2`")
            return

        thinking_msg = await ctx.send("Solving...")

        explanation = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: tutor.ask_freeform(question, "I don't know — please show me how to solve this")
        )

        await thinking_msg.delete()

        if len(explanation) > 1900:
            explanation = explanation[:1900] + "..."

        embed = discord.Embed(
            title="Solution",
            description=explanation,
            color=discord.Color.purple()
        )
        embed.add_field(name="Problem", value=f"`{question}`", inline=False)
        embed.set_footer(text="Try a quiz next! -> !quiz")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Homework(bot))
