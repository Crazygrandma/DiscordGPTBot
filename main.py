import discord
import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_API_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

bot = discord.Bot(
    intents=intents,
    debug_guilds=[692503362247327889],
)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")

@bot.slash_command(description="Grüße einen Users")
async def greet(ctx, user: discord.Member):
    await ctx.respond(f"Hallo {user.mention}")
    
@bot.slash_command(description="Lass den Bot eine Nachricht senden")
async def say(
    ctx,
    text: str,
    channel: discord.TextChannel
):
    
    await channel.send(text)
    await ctx.respond("Die Nachricht wurde gesendet", ephemeral=True)

@bot.slash_command(description="Bot herunterfahren")
async def shutdown(ctx):
    await ctx.respond("Shutting down...")
    await bot.close()

bot.run(DISCORD_API_TOKEN)