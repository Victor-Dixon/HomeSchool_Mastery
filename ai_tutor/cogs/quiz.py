"""
cogs/quiz.py — Quiz Session Commands
Commands:
  !quiz          — Start a full Day 1 session (all questions)
  !drill <skill> — Drill a specific skill by name
  !question      — Get one random question
"""

import discord
from discord.ext import commands
import random
import asyncio

from ai_tutor.questions import QUESTIONS, get_questions_by_skill
from ai_tutor import progress as prog
from ai_tutor import tutor


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}

    async def ask_question(self, ctx, q: dict) -> bool:
        """
        Send a question, wait for the user's answer, give feedback.
        Returns True if correct, False if wrong.
        """
        user_id = str(ctx.author.id)

        embed = discord.Embed(
            title=f"  {q['skill']}",
            description=f"**{q['question']}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Type your answer below - You have 60 seconds")
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! Moving on...")
            prog.record(user_id, q["skill"], False)
            return False

        user_answer = msg.content.strip().lower()
        correct_answer = q["answer"].strip().lower()

        if user_answer == correct_answer:
            xp = prog.get_xp(user_id) + 10
            await ctx.send(f"**Correct!** +10 XP - Total XP: {xp}")
            prog.record(user_id, q["skill"], True)
            return True
        else:
            await ctx.send(
                f"**Not quite.** The answer was `{q['answer']}`\n"
                f"Hint: {q.get('hint', 'Review this skill!')}\n\n"
                f"Getting AI explanation..."
            )
            prog.record(user_id, q["skill"], False)

            explanation = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tutor.explain(
                    q["skill"], q["question"], msg.content.strip(), q["answer"]
                )
            )

            if len(explanation) > 1800:
                explanation = explanation[:1800] + "..."

            embed = discord.Embed(
                title="Let me explain...",
                description=explanation,
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return False

    @commands.command(name="quiz")
    async def full_quiz(self, ctx):
        """Run a full quiz session with all TEKS questions."""
        user_id = str(ctx.author.id)

        if user_id in self.active_sessions:
            await ctx.send("You already have a session running! Finish it first.")
            return

        self.active_sessions[user_id] = True
        score = 0
        questions = QUESTIONS.copy()
        random.shuffle(questions)

        await ctx.send(
            f"**Starting your quiz, {ctx.author.display_name}!**\n"
            f"{len(questions)} questions - Type your answer after each one\n"
            f"Type `!quit` anytime to stop."
        )
        await asyncio.sleep(1)

        for i, q in enumerate(questions, 1):
            if user_id not in self.active_sessions:
                break

            await ctx.send(f"**Question {i} of {len(questions)}**")
            correct = await self.ask_question(ctx, q)
            if correct:
                score += 1
            await asyncio.sleep(1.5)

        del self.active_sessions[user_id]

        pct = round((score / len(questions)) * 100)
        color = discord.Color.green() if pct >= 70 else discord.Color.red()
        embed = discord.Embed(
            title="Session Complete!",
            description=(
                f"**Score: {score}/{len(questions)} ({pct}%)**\n\n"
                f"XP Earned: {score * 10}\n"
                f"Total XP: {prog.get_xp(user_id)}\n\n"
                f"Type `!progress` to see your weak spots."
            ),
            color=color
        )
        await ctx.send(embed=embed)

    @commands.command(name="drill")
    async def drill_skill(self, ctx, *, skill_name: str = None):
        """Drill a specific skill. Usage: !drill Integer Addition"""
        if not skill_name:
            skills = list(set(q["skill"] for q in QUESTIONS))
            skill_list = "\n".join(f"- {s}" for s in sorted(skills))
            await ctx.send(
                f"**Available skills to drill:**\n{skill_list}\n\n"
                f"Usage: `!drill Integer Addition`"
            )
            return

        questions = get_questions_by_skill(skill_name)
        if not questions:
            await ctx.send(
                f"No questions found for **{skill_name}**.\n"
                f"Use `!drill` with no arguments to see all skills."
            )
            return

        user_id = str(ctx.author.id)
        await ctx.send(f"**Drilling: {skill_name}** ({len(questions)} questions)")
        await asyncio.sleep(0.5)

        score = 0
        for q in questions:
            correct = await self.ask_question(ctx, q)
            if correct:
                score += 1
            await asyncio.sleep(1)

        await ctx.send(
            f"Drill complete! **{score}/{len(questions)}** on {skill_name}."
        )

    @commands.command(name="question", aliases=["q"])
    async def single_question(self, ctx):
        """Get one random question. Usage: !question"""
        q = random.choice(QUESTIONS)
        await self.ask_question(ctx, q)

    @commands.command(name="quit")
    async def quit_session(self, ctx):
        """Quit an active quiz session."""
        user_id = str(ctx.author.id)
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            await ctx.send("Session ended. Come back anytime!")
        else:
            await ctx.send("You don't have an active session.")


async def setup(bot):
    await bot.add_cog(Quiz(bot))
