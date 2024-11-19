
from discord.ext import commands
from discord.commands import slash_command
from mutagen.wave import WAVE


class Greet(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.connections = {}
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Greet is ready")
    
    @slash_command()
    async def greet(self,ctx):
        await ctx.respond(f"Hey! What's up {ctx.author.mention}!") 
    
        
def setup(bot):
    print("GREET IS BEING LOADED")
    bot.add_cog(Greet(bot))
    
def teardown(bot):
    print('GREET IS BEING UNLOADED')
    