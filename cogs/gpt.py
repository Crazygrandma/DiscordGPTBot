import discord
import requests
import importlib
import asyncio
from GPTManager import GPTManager
import random
from discord.ext import commands
from discord import app_commands
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

config = configparser.ConfigParser()

RUN_DIALOG = True
RUN_PLAY_RANDOM = True

load_dotenv()
ELEVENLABS_TOKEN = os.getenv('ELEVENLABS_TOKEN')

CHUNK_SIZE = 1024

class GPT(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.connections = {}
        self.users = {}
        config.read('config.ini',encoding='utf-8')
        self.username = ''
        self.mygpt = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("GPT cog is ready")
        # await self.bot.change_presence(activity=discord.Game("GPT ready!"))

    @app_commands.command(name="moin", description="Join the current voice channel")
    async def join(self,interaction:discord.Interaction):  # If you're using commands.Bot, this will also work.
        user = interaction.user.id
        voice = interaction.user.voice
        if not voice:
            await interaction.response.send_message(f"<@{user}>! Bruh wo soll ich denn rein?")
        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        await interaction.response.send_message(f"<@{user}>! Moin")
        source = FFmpegPCMAudio(f"./sounds/hellothere.wav")
        vc.play(source)
        self.connections.update({interaction.guild.id: vc})  # Updating the cache with the guild and channel.
    
    @app_commands.command(name="nööö", description="Leave the current voice channel")
    async def leave(self,interaction:discord.Interaction):
        if interaction.guild.id in self.connections:  # Check if the guild is in the cache.
            vc = self.connections[interaction.guild.id]
            await interaction.response.send_message(f"<@{interaction.user.id}>! Ok")
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
            await vc.disconnect()

    @app_commands.command(name="gpt", description="Ask a local gpt model a question and keep the context")
    async def gpt(self, interaction:discord.Interaction, prompt: str, temp:float=0.7, max_tokens:int=256,repeat_last_n:int=1):
        config.read('config.ini',encoding='utf-8')
        gpt = config['GPT']
        elevenlabs = config['LABS']
        GPT_MODEL = gpt['MODEL']
        SYSTEM_PROMPT = gpt['SYSTEM_PROMPT']
        useElevenLabs = elevenlabs['enabled']
        user = interaction.user.id

        await interaction.response.send_message(f"<@{user}> Frage MoviemakerBot: {prompt}")
        
        # Load once
        if self.mygpt is None:
            gptmodule = importlib.import_module('GPTManager','.')
            self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
            self.mygpt.set_system_prompt(SYSTEM_PROMPT)
        
        # Exit message to unload
        if prompt == "exit":
            if self.mygpt is not None:
                del(self.mygpt)
                print("Free memory gpt")
            else:
                print("Gpt not loaded AAAAAAAAAAAA")
        else:
            # Gen response with context
            response = self.mygpt.getResponseWithContext(prompt, temp, max_tokens, repeat_last_n)
            print(response)
            # if useElevenLabs == 'Jawoll':
            #     await self.ttsElevenlabs(interaction.guild.id,response)
            # else:
            await self.ttsgTTS(interaction.guild.id,response)    

    @app_commands.command(name="gptold", description="Ask a local gpt model a question")
    async def gptold(self, interaction:discord.Interaction, prompt: str):
        config.read('config.ini',encoding='utf-8')
        gpt = config['GPT']
        elevenlabs = config['LABS']
        GPT_MODEL = gpt['MODEL']
        SYSTEM_PROMPT = gpt['SYSTEM_PROMPT']
        useElevenLabs = elevenlabs['enabled']
        user = interaction.user.id

        await interaction.response.send_message(f"<@{user}> Frage GPT: {prompt}")
        
        gptmodule = importlib.import_module('GPTManager','.')
        self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
        context = self.mygpt.getContext()

        with context:
            response = self.mygpt.getResponse(prompt=prompt)
            if useElevenLabs == 'Nein':
                # await ctx.send(f"<@{user}> Generiere Audio mit gTTS!")
                await self.ttsgTTS(interaction.guild.id,response)    
            elif useElevenLabs == 'Jawoll':
                # await ctx.send(f"<@{user}> Generiere Audio mit ElevenLabs!")
                # Text to speech with ElevenLabs
                await self.ttsElevenlabs(interaction.guild.id,response)
        if self.mygpt is not None:
            del(self.mygpt)
            print("Free memory gpt")
        else:
            print("Gpt not loaded")

    @commands.command()
    async def stoprandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = False

    @commands.command()
    async def enablerandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = True

    @app_commands.command(name="randomplay", description="Play a random sound at a random time")
    async def randomplay(self, interaction:discord.Interaction, mintime: int=10, maxtime: int=30):
        user = interaction.user.id
        voice = interaction.user.voice
        if not voice:
            await interaction.response.send_message(f"<@{user}>! Bruh wo soll ich denn rein?")
        else:
            try:
                await interaction.response.send_message(f"<@{user}>! Viel Spaß")
                vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
                self.connections.update({interaction.guild.id: vc})  # Updating the cache with the guild and channel.
            except:
                vc = self.connections[interaction.guild.id]
            RUN_PLAY_RANDOM
            while RUN_PLAY_RANDOM:
                sound = self.pickRandom()
                randWait = random.randint(int(mintime),int(maxtime))
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

    async def ttsgTTS(self,id,response):
        vc = self.connections[id]
        try:
            tts = gTTS(response,lang='de')
        except AssertionError as e:
            print(e)
            tts = gTTS("Bruh!",lang='de')
        tts.save('./response.mp3')
        # Wait for file to be saved
        await asyncio.sleep(1)
        length = mutagen_length('./response.mp3')
        source = FFmpegPCMAudio(f"./response.mp3")
        vc.play(source)
        # Wait till finished
        await asyncio.sleep(int(length))

    async def ttsElevenlabs(self,id,text):
        vc = self.connections[id]
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
            source = FFmpegPCMAudio(f"./response.mp3")
            vc.play(source)

async def setup(bot):
    await bot.add_cog(GPT(bot))
