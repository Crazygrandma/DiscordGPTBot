# This example requires the 'message_content' privileged intent for prefixed commands.

import asyncio
import random
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.commands import slash_command

from helper import is_bot_connected, mutagen_length, pickRandom

RUN_PLAY_RANDOM = False

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Sounds/Music is ready")

    @slash_command(description="Disable random sounds")
    async def stoprandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = False
        await ctx.respond(f"<@{ctx.user.id}>! Disable Randomsounds")

    @slash_command(description="Play a random sound at a random time")
    @is_bot_connected()
    async def randomplay(self, ctx, mintime: int=10, maxtime: int=30):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        user = ctx.user.id
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = True
        await ctx.respond(f"<@{user}>! Viel Spaß")
        while RUN_PLAY_RANDOM:
            sound = pickRandom('./sounds/soundboard')
            randWait = random.randint(int(mintime),int(maxtime))
            print(f"Waiting {randWait} seconds")
            await asyncio.sleep(randWait)
            source = discord.FFmpegPCMAudio(sound)
            length = mutagen_length(sound)
            voice_client.play(source)
            await asyncio.sleep(int(length))

    @slash_command(description="Play a sound")
    @is_bot_connected()
    async def play(self,ctx,arg:str):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await ctx.respond("Play sound.")
        source = FFmpegPCMAudio(f"./sounds/soundboard/{arg}.wav")
        length = mutagen_length(source)
        voice_client.play(source)
        await asyncio.sleep(int(length))
        
    @slash_command(description="Play a music file")
    async def music(self,ctx,arg:str):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await ctx.respond("Play sound.")
        source = FFmpegPCMAudio(f"./sounds/songs/{arg}.wav")
        length = mutagen_length(source)
        voice_client.play(source)
        game = discord.Game(arg)
        await self.bot.change_presence(status=discord.Status.streaming, activity=game)
        await asyncio.sleep(int(length))
        
    # TODO Add music search command with pytube
def setup(bot):
    print("Music extension is being LOADED")
    bot.add_cog(Music(bot))
    
def teardown(bot):
    print('Music extension is being UNLOADED')