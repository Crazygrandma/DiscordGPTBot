import discord
from discord.ext import commands
from discord.commands import slash_command

import requests
import importlib
import asyncio
import random
from discord import FFmpegPCMAudio
import os
import glob
import configparser
from dotenv import load_dotenv
from mutagen.wave import WAVE
from gtts import gTTS

RUN_PLAY_RANDOM = False
DIALOG_RUNNING = True
ELEVENLABS_TOKEN = os.getenv('ELEVENLABS_TOKEN')

CHUNK_SIZE = 1024
config = configparser.ConfigParser()

#### HELPER FUNCTIONS

# Get length of audio
def mutagen_length(path):
    try:
        audio = WAVE(path)
        length = audio.info.length
        return length
    except:
        return 1

# BOT COG CLASS
class GPT(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.mygpt = None
        self.vc = None



    @slash_command(description="Play a random sound at a random time")
    async def randomplay(self, ctx, mintime: int=10, maxtime: int=30):
        user = ctx.user.id
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = not RUN_PLAY_RANDOM
        if self.vc:
            await ctx.respond(f"<@{user}>! Viel Spaß")
            while RUN_PLAY_RANDOM:
                sound = self.pickRandom()
                randWait = random.randint(int(mintime),int(maxtime))
                print(f"Waiting {randWait} seconds")
                await asyncio.sleep(randWait)
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                self.vc.play(source)
                await asyncio.sleep(int(length))

    def pickRandom(self):
        soundList = glob.glob('./sounds/*.wav')
        sound = random.choice(soundList)
        return sound


    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if member.bot:
            return
        
        voice = member.voice 
        
        if self.vc is None and voice is not None:     
            self.vc = await voice.channel.connect()
            
        
        # user joins channel
        if before.channel == None and after.channel is not None:
            print(f"User joined {after.channel}")
            soundpath = ""
            if member.name == "moviemakerhd":
                soundpath = "./sounds/moviemakermoin.wav"
            elif member.name == "paulhfr":
                soundpath = "./sounds/JJJPH.wav"
            elif member.name == "pauldermensch":
                soundpath = "./sounds/dermensch.wav"
            else:
                soundpath = "./sounds/JorisYT.wav" 
            length = mutagen_length(soundpath)
            source = FFmpegPCMAudio(source=soundpath)
            # Wait for user to connect to voice
            await asyncio.sleep(0.5)
            self.vc.play(source)
            await asyncio.sleep(int(length))
        elif before.channel is not None and after.channel is None:
            print(f"User left from channel {before.channel}")
            if self.vc:
                if member.name == "moviemakerhd":
                    await asyncio.sleep(1)
                    await self.vc.disconnect()
                    self.vc = None

    @slash_command(description="Stelle Fragen an ein lokales LLM")
    async def askgpt(self, ctx):
        
        # if not in voice conntect to it
        if self.vc is None:
            voice = ctx.user.voice     
            self.vc = await voice.channel.connect()
        
        print("Loading config")
        config.read('config.ini',encoding='utf-8')
        gpt = config['GPT']
        elevenlabs = config['LABS']
        GPT_MODEL = gpt['MODEL']
        SYSTEM_PROMPT = gpt['SYSTEM_PROMPT']
        maxtokens = gpt['maxtoken']
        penalty = gpt['penalty']
        temp = gpt['temp']
        useElevenLabs = elevenlabs['enabled']
        
        print("Loading GPT Model...")
        # Load once
        if self.mygpt is None:
            gptmodule = importlib.import_module('gptManager','.')
            self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
        
        print("GPT Model loaded")
        def check(message):
            return message.author == ctx.author
        
        await ctx.respond("Was möchtest du fragen?")
        with self.mygpt.getContext():
            global DIALOG_RUNNING
            while DIALOG_RUNNING:
                answer = await self.bot.wait_for("message", check=check)
                if answer.content == "exit":
                    await answer.reply("Fahre GPT runter...")
                    if self.mygpt is not None:
                        del(self.mygpt)
                        self.mygpt = None
                        print("Free memory gpt")
                    DIALOG_RUNNING = False
                    return
                response = self.mygpt.getResponse(answer.content,max_tokens=maxtokens,repeat_penalty=penalty,temp=temp)
                if useElevenLabs == "Jawoll":
                    await self.ttsElevenlabs(response)
                else:
                    await self.ttsgTTS(response)  
                await answer.reply(response)
            
    async def ttsgTTS(self,response):
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
        self.vc.play(source)
        # Wait till finished
        await asyncio.sleep(int(length))
        
    async def ttsElevenlabs(self,text):
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
            self.vc.play(source)
        
def setup(bot):
    bot.add_cog(GPT(bot))
    