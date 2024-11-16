from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.commands import slash_command
import asyncio
from mutagen.wave import WAVE

def mutagen_length(path):
    try:
        audio = WAVE(path)
        length = audio.info.length
        return length
    except:
        return 1


class Greet(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.vc = None
    
    @slash_command()
    async def greet(self,ctx):
        await ctx.respond(f"Hey {ctx.author.mention}") 
    
        
def setup(bot):
    bot.add_cog(Greet(bot))
    