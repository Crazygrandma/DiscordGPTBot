import discord
from discord.ext import commands

class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  # Restrict the command to the bot owner
    async def load(self, ctx, extension: str):
        """Loads a cog."""
        try:
            self.bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"✅ Loaded `{extension}` cog.")
        except Exception as e:
            await ctx.send(f"❌ Failed to load cog `{extension}`: {e}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        """Unloads a cog."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
            await ctx.send(f"✅ Unloaded `{extension}` cog.")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload cog `{extension}`: {e}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        """Reloads a cog."""
        try:
            self.bot.unload_extension(f"cogs.{extension}")
            self.bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"🔄 Reloaded `{extension}` cog.")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload cog `{extension}`: {e}")

def setup(bot):
    bot.add_cog(CogManager(bot))
