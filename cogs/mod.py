import discord
from discord import app_commands
from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()
    async def sync(self, ctx):
        try:
            synced_commands = await self.bot.tree.sync()
            print(f"Synced {len(synced_commands)} commands.")
        except Exception as e:
            print("An error with syncing application commands occurred", e)
    

    

async def setup(bot):
    await bot.add_cog(Mod(bot))
