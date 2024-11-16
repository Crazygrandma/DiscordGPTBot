import discord
from discord.ext import commands, tasks
from discord.commands import slash_command

class Task(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.keks.start()

    @tasks.loop(seconds=2)
    async def keks(self):
        if self.keks.current_loop == 0:
            return
        print("Keks")
        
def setup(bot):
    bot.add_cog(Task(bot))
    