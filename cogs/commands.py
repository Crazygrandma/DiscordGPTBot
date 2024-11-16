import discord
from discord.ext import commands
from discord.commands import slash_command, OptionChoice


class Commands(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
    
    @slash_command()
    async def activity(self,ctx,name:str):
        await self.bot.change_presence(activity=discord.Game(name=name), status=discord.Status.dnd)
        await ctx.respond("Status wurde geändert")
        
        
def setup(bot):
    bot.add_cog(Commands(bot))
    