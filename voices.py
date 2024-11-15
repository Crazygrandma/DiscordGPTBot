import discord
import requests
import importlib
import asyncio
import random
from discord.ext import commands
from discord import FFmpegPCMAudio
from gtts import gTTS
import os
import glob
import configparser
from dotenv import load_dotenv
from psutil import Process
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

def mutagen_length(path):
    try:
        audio = WAVE(path)
        length = audio.info.length
        return length
    except:
        return None

def get_memory_usage():
    process: Process= Process(os.getpid())
    megabytes: float= process.memory_info().rss / (1024*1024)
    return megabytes

config = configparser.ConfigParser()

RUN_DIALOG = True
RUN_PLAY_RANDOM = True

load_dotenv()
ELEVENLABS_TOKEN = os.getenv('ELEVENLABS_TOKEN')

CHUNK_SIZE = 1024

class Voices(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.connections = {}
        self.users = {}
        self.mygpt = None
        self.username = ''

    @commands.command()
    async def join(self,ctx):  # If you're using commands.Bot, this will also work.
        user = ctx.author.id
        voice = ctx.author.voice
        if not voice:
            await ctx.send(f"<@{user}>! Bruh wo soll ich denn rein?")
        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        source = FFmpegPCMAudio(f"./sounds/hellothere.wav")
        vc.play(source)
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
    
    @commands.command()
    async def leave(self,ctx):  
        if ctx.guild.id in self.connections:  # Check if the guild is in the cache.
            vc = self.connections[ctx.guild.id]
            await vc.disconnect()

    @commands.command()
    async def play(self,ctx,arg):
        user = ctx.author.id
        voice = ctx.author.voice
        if not voice:
            await ctx.send(f"<@{user}>! Bruh wo soll ich denn rein?")
        else:
            try:
                vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
                self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
            except:
                vc = self.connections[ctx.guild.id]
            source = FFmpegPCMAudio(f"./sounds/{arg}.wav")
            print("playing ",arg)
            vc.play(source)

    @commands.command()
    async def stoprandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = False

    @commands.command()
    async def enablerandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = True



    # @commands.command()
    # async def dialog(self,ctx,arg):
    #     config.read('config.ini',encoding='utf-8')
    #     gpt = config['GPT']
    #     elevenlabs = config['LABS']
    #     GPT_MODEL = gpt['MODEL']
    #     SYSTEM_PROMPT = gpt['SYSTEM_PROMPT']
    #     useElevenLabs = elevenlabs['enabled']
    #     user = ctx.author.id
    #     # await ctx.send(f"<@{user}> Starte Dialogsession")
    #     result = await self.getDialog(ctx,arg)
    #     memory_before_gpt:float = get_memory_usage()

    #     gptmodule = importlib.import_module('GPTManager','.')
    #     self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
    #     context = self.mygpt.getContext()

    #     memory_after_gpt:float = get_memory_usage()
    #     mem_diff = memory_after_gpt - memory_before_gpt

    #     print(f"After gpt import: {mem_diff:.2f} MB")
    #     with context:
    #         response = self.mygpt.getResponse(prompt=result)
    #         memory_after_response:float = get_memory_usage()
    #         mem_diff = memory_after_response - memory_before_gpt
    #         print(f"After response: {mem_diff:.2f} MB")
    #         if useElevenLabs == 'Nein':
    #             # await ctx.send(f"<@{user}> Generiere Audio mit gTTS!")
    #             await self.ttsgTTS(ctx,response)    
    #         elif useElevenLabs == 'Jawoll':
    #             await ctx.send(f"<@{user}> Generiere Audio mit ElevenLabs!")
    #             # Text to speech with ElevenLabs
    #             await self.ttsElevenlabs(ctx,response)
    #         global RUN_DIALOG
    #         while RUN_DIALOG:
    #             result = await self.getDialog(ctx,arg)
    #             response = self.mygpt.getResponse(prompt=result)
    #             memory_after_response:float = get_memory_usage()
    #             mem_diff = memory_after_response - memory_before_gpt
    #             print(f"After response: {mem_diff:.2f} MB")
    #             if useElevenLabs == 'Nein':
    #                 # await ctx.send(f"<@{user}> Generiere Audio mit gTTS!")
    #                 await self.ttsgTTS(ctx,response)    
    #             elif useElevenLabs == 'Jawoll':
    #                 # await ctx.send(f"<@{user}> Generiere Audio mit ElevenLabs!")
    #                 # Text to speech with ElevenLabs
    #                 await self.ttsElevenlabs(ctx,response)
    #     if self.mygpt is not None:
    #         del(self.mygpt)
    #         await ctx.send("Free memory gpt")
    #     else:
    #         await ctx.send("Gpt not loaded")

    @commands.command()
    async def randomplay(self,ctx,arg1,arg2):
        user = ctx.author.id
        voice = ctx.author.voice
        if not voice:
            await ctx.send(f"<@{user}>! Bruh wo soll ich denn rein?")
        else:
            try:
                vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
                self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
            except:
                vc = self.connections[ctx.guild.id]
            RUN_PLAY_RANDOM
            while RUN_PLAY_RANDOM:
                sound = self.pickRandom()
                randWait = random.randint(int(arg1),int(arg2))
                await asyncio.sleep(randWait)
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                print("waiting ",length)
                vc.play(source)
                await asyncio.sleep(int(length))

    def pickRandom(self):
        soundList = glob.glob('./sounds/*.wav')
        sound = random.choice(soundList)
        return sound

    async def getDialog(self,ctx,arg):
        user = ctx.author.id
        voice = ctx.author.voice
        if not voice:
            await ctx.send(f"<@{user}>! Bruh wo soll ich denn rein?")
        else:
            whisper = importlib.import_module('STT','.')
            self.model = whisper.STTManager(name='small').model

            if ctx.guild.id in self.connections:  # Check if the guild is in the cache.
                vc = self.connections[ctx.guild.id]
                await ctx.send(f"<@{user}>! Frag los!")
                vc.start_recording(
                    discord.sinks.WaveSink(),  # The sink type to use.
                    self.once_done,  # What to do once done.
                    ctx.channel  # The channel to disconnect from.
                )
                await asyncio.sleep(int(arg))
                await ctx.send(f"<@{user}>! Ok!")
                vc.stop_recording()

                # await ctx.send(f"<@{user}>! Wird übersetzt")
                # Wait for file to be saved
                await asyncio.sleep(2)
                result = await self.transcribeDialog(user)
                await ctx.send(f"<@{user}>:"+result)
                await asyncio.sleep(3)

        del(self.model)
        return result

    async def once_done(self,sink: discord.sinks, channel: discord.TextChannel):  # Our voice client already passes these in.
        for user_id,audio in sink.audio_data.items():
            with open(f"{user_id}.{sink.encoding}", "wb") as outfile:
                    outfile.write(audio.file.getbuffer())
    
    async def ttsElevenlabs(self,ctx,text):
        vc = self.connections[ctx.guild.id]
        elevenlabs = config['LABS']
        stability = elevenlabs['STABILITY']
        similarity = elevenlabs['SIMILARITY']
        voice_id = elevenlabs['VOICE_ID']
        model_id = elevenlabs['MODEL_ID']
        payload = {
            "model_id": model_id,
            "text": text,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity
            }
        }
        headers = {"Content-Type": "application/json","xi-api-key": ELEVENLABS_TOKEN}

        elevenLabsTTSAPIURL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        response = requests.request("POST", elevenLabsTTSAPIURL, json=payload, headers=headers)

        with open('response.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
            await ctx.send(f"<@{ctx.author.id}>: {text}")
            source = FFmpegPCMAudio(f"./response.mp3")
            vc.play(source)

    async def ttsgTTS(self,ctx,response):
        vc = self.connections[ctx.guild.id]
        try:
            tts = gTTS(response,lang='de')
        except AssertionError as e:
            print(e)
            tts = gTTS("Bruh!",lang='de')
        tts.save('./response.mp3')
        # await ctx.send(f"<@{ctx.author.id}>:"+response)
        # Wait for file to be saved
        await asyncio.sleep(1)
        length = mutagen_length('./response.mp3')
        source = FFmpegPCMAudio(f"./response.mp3")
        vc.play(source)
        # Wait till finished
        await asyncio.sleep(int(length))
        
    async def transcribeDialog(self,userid):
        result = self.model.transcribe(f'./{userid}.wav')
        return result["text"]

    async def fetchUser(self,id):
        DISCORD_USERAPI = "https://discordlookup.mesavirep.xyz/v1/user/"
        response = requests.request("GET", f"{DISCORD_USERAPI}{id}")
        return response.json()["username"]

async def setup(bot): # this is called by Pycord to setup the coga
    await bot.add_cog(Voices(bot)) # add the cog to the bot
