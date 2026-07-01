"""
Discord Bot — Main Entry Point
Run with: python -m ai_tutor.bot
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    await bot.load_extension("ai_tutor.cogs.quiz")
    await bot.load_extension("ai_tutor.cogs.progress")
    await bot.load_extension("ai_tutor.cogs.homework")
    await bot.load_extension("ai_tutor.cogs.help_cmd")


bot.run(TOKEN)
