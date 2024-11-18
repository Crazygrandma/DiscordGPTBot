from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
from mutagen.wave import WAVE



class AI(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.vc = None
        self.guild = None
    
    @slash_command(description="Start AI")
    async def start(self,ctx):
        self.guild = ctx.guild
        self.join_voice_and_record.start()
        await ctx.respond("Ok!")
        
    @slash_command(description="Stop AI")
    async def stop(self,ctx):
        self.join_voice_and_record.stop()
        await ctx.respond(":(")
    
    @tasks.loop(seconds=5)
    async def join_voice_and_record(self):
        for voice_channel in self.guild.voice_channels:  # Iterate through all voice channels
            for member in voice_channel.members:  # Iterate through members in the voice channel
                if not member.bot:
                    voice = member.voice
                    print("User in voice")
                    if not self.bot.voice_clients:
                        print("Connecting to voice")
                        # Connect to voice channel
                        await voice.channel.connect()
                        # Prepare recording
                        # Save recording
                        # disconnect
                    
            
def setup(bot):
    bot.add_cog(AI(bot))
    