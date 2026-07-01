"""
cogs/progress.py — Progress & Stats Commands
Commands:
  !progress   — See your skill breakdown + weak spots
  !xp         — See your XP and streak
  !weakskills — Show skills that need more practice
"""

import discord
from discord.ext import commands
from ai_tutor import progress as prog


class Progress(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="progress", aliases=["stats"])
    async def show_progress(self, ctx):
        """Show your full skill breakdown."""
        user_id = str(ctx.author.id)
        summary = prog.get_summary(user_id)

        if not summary:
            await ctx.send(
                "No progress yet! Start with `!quiz` to begin your first session."
            )
            return

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Progress",
            color=discord.Color.blue()
        )

        lines = []
        for skill, stats in sorted(summary.items()):
            total = stats["correct"] + stats["wrong"]
            acc = round((stats["correct"] / total) * 100) if total else 0
            indicator = "HIGH" if acc >= 70 else "MID" if acc >= 40 else "LOW"
            lines.append(
                f"[{indicator}] **{skill}**: {acc}% ({stats['correct']} correct, {stats['wrong']} wrong)"
            )

        embed.description = "\n".join(lines)
        embed.set_footer(
            text=f"XP: {prog.get_xp(user_id)} | Streak: {prog.get_streak(user_id)} days"
        )
        await ctx.send(embed=embed)

    @commands.command(name="xp")
    async def show_xp(self, ctx):
        """Show your XP and streak."""
        user_id = str(ctx.author.id)
        xp = prog.get_xp(user_id)
        streak = prog.get_streak(user_id)

        level = xp // 100
        progress_bar_filled = min(int((xp % 100) / 10), 10)
        bar = "#" * progress_bar_filled + "-" * (10 - progress_bar_filled)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Stats",
            color=discord.Color.gold()
        )
        embed.add_field(name="Level", value=f"Level {level}", inline=True)
        embed.add_field(name="XP", value=f"{xp} XP", inline=True)
        embed.add_field(name="Streak", value=f"{streak} days", inline=True)
        embed.add_field(
            name=f"Progress to Level {level + 1}",
            value=f"`[{bar}]` {xp % 100}/100 XP",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="weakskills", aliases=["weak"])
    async def show_weak_skills(self, ctx):
        """Show skills that need more practice."""
        user_id = str(ctx.author.id)
        weak = prog.get_weak_skills(user_id)

        if not weak:
            await ctx.send(
                "No weak skills found yet! Either you're crushing it "
                "or you need more practice sessions. Try `!quiz`!"
            )
            return

        embed = discord.Embed(
            title="Skills to Work On",
            description="These are your lowest-accuracy skills. Drill them with `!drill <skill name>`",
            color=discord.Color.red()
        )

        for item in weak[:5]:
            embed.add_field(
                name=f"[LOW] {item['skill']}",
                value=f"{item['accuracy']}% accuracy ({item['correct']} correct, {item['wrong']} wrong)",
                inline=False
            )

        if weak:
            top_weak = weak[0]["skill"]
            embed.set_footer(text=f"Start with: !drill {top_weak}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Progress(bot))
