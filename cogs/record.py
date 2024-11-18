import discord
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
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AI is ready")
        
    
    @slash_command(description="Start AI")
    async def start(self,ctx):
        self.guild = ctx.guild
        self.join_voice_and_record.start()
        await ctx.respond("Ok!")
        
    @slash_command(description="Stop AI")
    async def stop(self,ctx):
        self.join_voice_and_record.stop()
        await ctx.respond(":(")
    
    @tasks.loop(seconds=20)
    async def join_voice_and_record(self):
        for voice_channel in self.guild.voice_channels:  # Iterate through all voice channels
            for member in voice_channel.members:  # Iterate through members in the voice channel
                if not member.bot:
                    voice = member.voice
                    print("User in voice")
                    if not self.bot.voice_clients:
                        print("Connecting to voice")
                        # Connect to voice channel
                        vc = await voice.channel.connect()
                        await asyncio.sleep(2)
                        # Start recording
                        vc.start_recording(
                            discord.sinks.WaveSink(),  # The sink type to use.
                            self.once_done,  # What to do once done.
                            voice.channel  # The channel to disconnect from.
                        )
                        await asyncio.sleep(int(4))
                        vc.stop_recording()
                        # Save recording
                        # disconnect
                        await vc.disconnect()
                        # Only once
                        self.join_voice_and_record.stop()
                        
    async def once_done(self,sink: discord.sinks, channel: discord.TextChannel):  # Our voice client already passes these in.
        for user_id,audio in sink.audio_data.items():
            with open(f"{user_id}.{sink.encoding}", "wb") as outfile:
                    outfile.write(audio.file.getbuffer())

              
def setup(bot):
    print("AI extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('AI extension is being UNLOADED')
    