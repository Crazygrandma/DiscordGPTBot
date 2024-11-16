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

DIALOG_RUNNING = True
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




    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if member.bot:
            return
        
        voice = member.voice 
        
        if self.vc is None and voice is not None:     
            self.vc = await voice.channel.connect()
            
        
        # user joins channel
        if before.channel == None and after.channel is not None:
            print("User joined")
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
            self.vc.play(source)
            await asyncio.sleep(int(length))

    @slash_command()
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
                    if self.mygpt is not None:
                        del(self.mygpt)
                        print("Free memory gpt")
                    DIALOG_RUNNING = False
                    return
                response = self.mygpt.getResponse(answer.content)
                await self.ttsgTTS(response)  
                await answer.reply(response)
                # Play gtts in voice chat
                
                
    
        if self.mygpt is not None:
                del(self.mygpt)
                print("Free memory gpt")
        else:
            print("Gpt not loaded AAAAAAAAAAAA")
            
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
        
def setup(bot):
    bot.add_cog(GPT(bot))
    