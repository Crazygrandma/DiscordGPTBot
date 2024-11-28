import asyncio
import discord
from discord.ext import commands
from discord.commands import slash_command
from discord import FFmpegPCMAudio
# from customVoiceClient import CustomVoiceClient
from helper import is_bot_connected, mutagen_length



class Greet(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.connections = {}
        
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Greet is ready")
    
    @commands.Cog.listener()
    @is_bot_connected()
    async def on_voice_state_update(self,member,before,after):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)
        if member.bot:
            return
        if voice_client == None:
            return
        # user joins channel
        if before.channel == None and after.channel is not None:
            print(f"User joined {after.channel}")
            soundpath = ""
            if member.name == "moviemakerhd":
                soundpath = "./sounds/other/moviemakermoin.wav"
            elif member.name == "paulhfr":
                soundpath = "./sounds/other/JJJPH.wav"
            elif member.name == "pauldermensch":
                soundpath = "./sounds/other/dermensch.wav"
            elif member.name == "weicherpottwal":
                soundpath = "./sounds/other/nefton.wav"
            else:
                soundpath = "./sounds/JorisYT.wav" 
            length = mutagen_length(soundpath)
            source = FFmpegPCMAudio(source=soundpath)
            # Wait for user to connect to voice
            await asyncio.sleep(0.5)
            voice_client.play(source)
            await asyncio.sleep(int(length))
    
    
    @slash_command()
    async def join(self, ctx, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.respond("Jo!")

    @slash_command(description="Leave the voice channel")
    @is_bot_connected()
    async def leave(self,ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await voice_client.disconnect()
        await ctx.respond("Ok :(")
    
    
    @slash_command()
    async def greet(self,ctx):
        await ctx.respond(f"Hey! What's up {ctx.author.mention}!") 
    
        
def setup(bot):
    print("GREET IS BEING LOADED")
    bot.add_cog(Greet(bot))
    
def teardown(bot):
    print('GREET IS BEING UNLOADED')
    