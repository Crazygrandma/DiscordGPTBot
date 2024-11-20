import requests
import importlib
import asyncio
import os
import configparser
from dotenv import load_dotenv
from gtts import gTTS
import sys

# Discord API Imports
import discord
from discord.ext import commands
from discord.commands import slash_command
from discord import FFmpegPCMAudio


# Helper functions
from helper import mutagen_length, pickRandom, is_bot_connected

load_dotenv()

JOIN_ON_VOICE = False
RUN_PLAY_RANDOM = False
DIALOG_RUNNING = True
ELEVENLABS_TOKEN = os.getenv('ELEVENLABS_TOKEN')

CHUNK_SIZE = 1024
config = configparser.ConfigParser()

# BOT COG CLASS
class GPT(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.mygpt = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AI is ready")
    
    @slash_command(description="Stelle Fragen an ein lokales LLM")
    @is_bot_connected()
    async def askgpt(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
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
        # Unload the module if already imported
        if 'gptManager' in sys.modules:
            print("Found module deleting it")
            del sys.modules['gptManager']
        
        print("(Re)loading module")
        gptmodule = importlib.import_module('gptManager','.')
        self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
        print("GPT Model loaded")
        
        await ctx.respond("Was möchtest du fragen?")
        with self.mygpt.getContext():
            global DIALOG_RUNNING
            DIALOG_RUNNING = True
            while DIALOG_RUNNING:
                answer = await self.bot.wait_for("message")
                modified_answer = f"[{answer.author.name}]: {answer.content}"
                
                print(modified_answer)
                
                if answer.content == "exit":
                    await answer.reply("Fahre GPT runter...")
                    if self.mygpt is not None:
                        del(self.mygpt)
                        self.mygpt = None
                        print("Free gpt memory")
                    DIALOG_RUNNING = False
                    return
                response = self.mygpt.getResponse(modified_answer,max_tokens=int(maxtokens),repeat_penalty=float(penalty),temp=float(temp))
                print("Got a response")
                if useElevenLabs == "Jawoll":
                    await self.ttsElevenlabs(response)
                else:
                    await self.ttsgTTS(response)
                await asyncio.sleep(1)
                length = mutagen_length('./response.mp3')
                source = FFmpegPCMAudio(f"./response.mp3")

                voice_client.play(source)

                await answer.reply(response)
                await asyncio.sleep(int(length))
                    
    async def ttsgTTS(self,response):
        try:
            tts = gTTS(response,lang='de')
        except AssertionError as e:
            print(e)
            tts = gTTS("Bruh!",lang='de')
        tts.save('./response.mp3')
        # Wait for file to be saved
        
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
            # source = FFmpegPCMAudio(f"./response.mp3")
            # self.vc.play(source)
        
def setup(bot):
    bot.add_cog(GPT(bot))
    