import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix="!", intents=intents) 

    bot.load_extensions('cogs.init','cogs.greetings','cogs.voices')

    bot.run(DISCORD_TOKEN) # Run the bot with your token.

if __name__=='__main__':
    main()