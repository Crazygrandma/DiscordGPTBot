import discord
# import logging
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')



load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents) 


@bot.event
async def on_ready():
    print("Bot ready")
    await bot.change_presence(activity=discord.Game("GOMMEMODE"))
    # try:
    #     synced_commands = await bot.tree.sync()
    #     print(f"Synced {len(synced_commands)} commands.")
    # except Exception as e:
    #     print("An error with syncing application commands occurred", e)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    await load()
    await bot.start(DISCORD_TOKEN) 


if __name__=='__main__':
    asyncio.run(main())