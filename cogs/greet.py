from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.commands import slash_command


class Greet(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        print("User changed voice state")
        if before.channel == None and after.channel is not None:
            if member.name == "moviemakerhd":
                print("Moviemaker joint")
            print(before.channel)
            print(after.channel)
            user = member.id
            voice = member.voice
            vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
            source = FFmpegPCMAudio(f"./sounds/hellothere.wav")
            vc.play(source)
            # self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
            await vc.disconnect()
    
    @slash_command()
    async def greet(self,ctx):
        await ctx.respond(f"Hey {ctx.author.mention}")
        
    
        
def setup(bot):
    bot.add_cog(Greet(bot))
    