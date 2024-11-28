import importlib
import os
import sys
import glob
import random
import discord
from discord.ext import commands
from gtts import gTTS
from mutagen.wave import WAVE
from mutagen.mp3 import MP3

def get_recordings(folder_path):
    file_count = 0

    # Iterate through all items in the folder
    for item in os.listdir(folder_path):
        # Construct the full path of the item
        full_path = os.path.join(folder_path, item)
        # Check if it's a file
        if os.path.isfile(full_path):
            file_count += 1

    return file_count

# Get length of audio
def mutagen_length(path):
    calc_length = 0
    try:
        audio = WAVE(path)
        calc_length = audio.info.length
        
        # if int(length) == 0:
        #     print(f"Length 0  - Falling back to wave module.")
        #     try:
        #         # Fallback to Python's built-in wave module
        #         with wave.open(path, 'rb') as wave_file:
        #             frames = wave_file.getnframes()
        #             rate = wave_file.getframerate()
        #             length = frames / float(rate)
        #     except Exception as e:
        #         print(f"Wave module also failed with error: {e}")
        #         return 1  # Return None to indicate failure  
        
        return calc_length
    except:
        audio = MP3(path)
        calc_length = audio.info.length
        return calc_length


def transcribeDialog():
    
    if 'STT' in sys.modules:
        print("Found WHISPER module deleting it")
        del sys.modules['STT']
    else:
        whisper = importlib.import_module('STT','.')
        whisper = whisper.STTManager(name='small').model
        print("Whisper Model loaded")
    
    transcribed_text = []
    recordings = glob.glob(f'dialogrecordings/*.wav')
    for filepath in recordings:
        basenamefile = os.path.basename(filepath)[:-4]
        result = whisper.transcribe(filepath)
        transcribed_text.append(f"[{basenamefile}]: {result['text']}")
    return transcribed_text
  
async def ttsgTTS(text,filename):
    """
        
        Generate an audio file with the gTTS API
        
        @param text - Text to convert
        @param filename - file to save the audio data to. Default mp3 in . directory
        
    """
    try:
        tts = gTTS(text,lang='de')
    except AssertionError as e:
        print(e)
        tts = gTTS("Bruh!",lang='de')
    tts.save(f'./{filename}.mp3')
    # Wait for file to be saved


def pickRandom(path):
        soundList = glob.glob(f'{path}/*.wav')
        sound = random.choice(soundList)
        return sound   
    
def is_bot_connected():
    """
    A custom check to verify that the bot is connected to a voice channel.
    """
    async def predicate(ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            return True
        await ctx.respond("I need to be connected to a voice channel to execute this command.")
        return False
    return commands.check(predicate)