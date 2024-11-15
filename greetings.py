from discord.ext import commands

class Greetings(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.command()
    async def ping(self,ctx):
        await ctx.send("Pong!")

    @commands.command()
    async def hello(self,ctx):
        user = ctx.author.id
        await ctx.send(f"<@{user}>! Moin")
        
def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Greetings(bot)) # add the cog to the bot
