import discord
from discord.ext import commands
from discord.commands import slash_command

# BOT COG CLASS
class Dialog(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready():
        pass

    
        
def setup(bot):
    bot.add_cog(Dialog(bot))
    