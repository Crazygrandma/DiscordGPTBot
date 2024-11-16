import discord
import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_API_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()

status = discord.Status.dnd
activity = discord.Activity(type=discord.ActivityType.watching, name="MoviemakerMOOIN")

bot = discord.Bot(
    intents=intents,
    debug_guilds=[692503362247327889,788437552331882517],
    status=status,
    activity=activity
)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")

@bot.event
async def on_application_command_error(ctx,error):
    await ctx.respond(f"Es ist ein Fehler aufgetreten ```{error}```")
    raise error


@bot.slash_command(description="Bot herunterfahren")
async def shutdown(ctx):
    await ctx.respond("Shutting down...")
    await bot.close()


if __name__ == '__main__':
    for filename in os.listdir('cogs'):
        if filename.endswith(".py"):  
            bot.load_extension(f"cogs.{filename[:-3]}")
    
    bot.run(DISCORD_API_TOKEN)
    