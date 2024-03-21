import discord
import configparser
from discord.ext import commands

config = configparser.ConfigParser()

class Initilize(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready now!")

    @commands.command()
    async def reload(self,ctx):
        self.bot.reload_extension('cogs.init')
        self.bot.reload_extension('cogs.greetings')
        self.bot.reload_extension('cogs.voices')
        await ctx.send("Reloading")

    @commands.command()
    async def stop(self,ctx):
        await ctx.send("Fahre runter...")
        await self.bot.close()


    @commands.command()
    async def config(self,ctx):
        config.read('config.ini')
        embed = discord.Embed(
            title="MoviemakerBot",
            description="BotInfo",
            color=discord.Colour.blurple(), # Pycord provides a class with default colors you can choose from
        )
        embed.add_field(name="System Prompt", value=config['GPT']['SYSTEM_PROMPT'])

        embed.add_field(name="GPT4ALL Modell", value=config['GPT']['MODEL'],inline=False)
        embed.add_field(name="Use ElevenLabs", value=config['LABS']['enabled'],inline=False)
        embed.add_field(name="Elevenlabs AI Voice ID", value=config['LABS']['VOICE_ID'],inline=False)
        embed.add_field(name="Stability", value=config['LABS']['STABILITY'],inline=False)
        embed.add_field(name="Labs Model", value=config['LABS']['MODEL_ID'],inline=False)
        await ctx.send("Soos!", embed=embed) # Send the embed with some text

    @commands.command()
    async def prompt(self,ctx,arg):
        config.read('config.ini')
        config.set('GPT','SYSTEM_PROMPT',str(arg))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command()
    async def labs(self,ctx,arg):
        config.read('config.ini')
        config.set('LABS','enabled',str(arg))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command()
    async def model(self,ctx,arg):
        config.read('config.ini')
        config.set('GPT','model',str(arg))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    @commands.command()
    async def stability(self,ctx,arg):
        config.read('config.ini')
        config.set('LABS','STABILITY',str(arg))
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Initilize(bot)) # add the cog to the bot
