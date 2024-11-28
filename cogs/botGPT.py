import glob
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

usernames = {
    395847854616215556: "MoviemakerHD",
    327764607257280515: "Jan",
    298494510462140426: "JPH",
    690577696161398885: "DerMensch"
}

# BOT COG CLASS
class GPT(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.mygpt = None
        self.whispermodel = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"GPT is ready")

    @slash_command(description="Stop the dialog")
    async def stopgptvoice(self,ctx):
        global DIALOG_RUNNING
        DIALOG_RUNNING = False
        await ctx.respond(f"<@{ctx.user.id}>! Disable Dialog für die nächste Frage")

   
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
        
        
        await ctx.respond("Ok! Einen Moment!")
        
        
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
        await ctx.respond("GPT Modell geladen! Jetzt kannst du deine Frage stellen!")
        with self.mygpt.getContext():
            global DIALOG_RUNNING
            DIALOG_RUNNING = True
            while DIALOG_RUNNING:
                answer = await self.bot.wait_for("message")
                # print(answer.content)
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
                print(f"Waiting for {length}")
                await asyncio.sleep(int(length))
              
    @slash_command(description="Stelle Fragen an ein lokales LLM über den Voice Chat")
    @is_bot_connected()
    async def askgptvoice(self, ctx):
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
        await ctx.respond("Ok! Einen Moment!")
        print("Loading GPT Model...")
        # Load once
        # Unload the module if already imported
        if 'gptManager' in sys.modules:
            print("Found GPT module deleting it")
            del sys.modules['gptManager']
        
        if 'STT' in sys.modules:
            print("Found WHISPER module deleting it")
            del sys.modules['STT']   
        
        print("(Re)loading module")
        gptmodule = importlib.import_module('gptManager','.')
        self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
        print("GPT Model loaded")
        # game = discord.Game("GPT")
        # await self.bot.change_presence(status=discord.Status.streaming, activity=game)
        
        whisper = importlib.import_module('STT','.')
        self.whispermodel = whisper.STTManager(name='small').model
        print("Whisper Model loaded")
        
        await ctx.respond("GPT und Whisper Modelle geladen! Jetzt wird aufgenommen!")
        
        with self.mygpt.getContext():
            global DIALOG_RUNNING
            DIALOG_RUNNING = True
            while DIALOG_RUNNING:
                modified_answer = ""
                # Get Dialog from voice chat
                # TODO Wait 
                transcribed_text = await self.getDialog(ctx, duration=10)
                for usertext in transcribed_text:
                    modified_answer += usertext
                print(modified_answer)
                
                
                # Get response from LLM
                response = self.mygpt.getResponse(
                    modified_answer,
                    max_tokens=int(maxtokens),
                    repeat_penalty=float(penalty),
                    temp=float(temp)
                )
                print("Got a response")
                
                # Choose text to speech method
                if useElevenLabs == "Jawoll":
                    await self.ttsElevenlabs(response)
                else:
                    await self.ttsgTTS(response)
                    
                await asyncio.sleep(10)
                
                
                # Get length of audiofile
                length = mutagen_length('./response.mp3')
                source = FFmpegPCMAudio(f"./response.mp3")

                print("Play audio")
                voice_client.play(source)
                
                await ctx.respond(response)
                print(f"Waiting for {length}")
                await asyncio.sleep(length)
                print("Done playing audio")
                await ctx.respond("Und die nächste Frage!")
            await ctx.respond("Ende des Dialogs")

    async def getDialog(self,ctx,duration):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        source = FFmpegPCMAudio(f"./sounds/silence.wav")
        voice_client.stop()
        voice_client.play(source)
        voice_client.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            sync_start = True
        )

        # TODO Check Voice client state for voice and cooldown
        await asyncio.sleep(int(duration))
        #print("Done Recording!")
        voice_client.stop_recording()
        voice_client.stop()
        voice_client

        # await ctx.send(f"<@{user}>! Wird übersetzt")
        # Wait for file to be saved
        await asyncio.sleep(3)
        print("Transcribing!")
        result = await self.transcribeDialog()
        await asyncio.sleep(3)
        return result

    async def once_done(self,sink: discord.sinks, *args):  # Our voice client already passes these in.
        
        # Debug: Check if sink.audio_data has any content
        if not sink.audio_data:
            print("No audio data available in sink.")
            return
        
        ####print(f"Recording session finished. Sink audio data length: {len(sink.audio_data)}")
        # Process each user's audio data
        for user_id, audio in sink.audio_data.items():
            #####print(f"User {user_id} audio length: {len(audio.file.getbuffer())}")
            # Lookup or default to user_id if username is unavailable
            username = usernames.get(user_id, str(user_id))  # Replace `usernames` with your actual username mapping
            # Construct the unique filename
            filename = f"dialogrecordings/{username}.wav"  # Using `mp3` as an example; replace with `sink.encoding` if dynamic
            ####print(f"Saving audio as: {filename}")
            # Save the audio file
            try:
                with open(filename, "wb") as outfile:
                    outfile.write(audio.file.getbuffer())

                #####print(f"Audio for user {username} saved successfully.")
            except Exception as e:
                print(f"Error saving audio for user {username}: {e}")
                
        sink.audio_data.clear()
        #####print("Sink audio data cleared.")   

    async def transcribeDialog(self):
        transcribed_text = []
        recordings = glob.glob(f'dialogrecordings/*.wav')
        for filepath in recordings:
            basenamefile = os.path.basename(filepath)[:-4]
            result = self.whispermodel.transcribe(filepath)
            transcribed_text.append(f"[{basenamefile}]: {result['text']}")
        return transcribed_text
        # return "Hallo"
       
    async def ttsgTTS(self,response):
        try:
            tts = gTTS(response,lang='de')
        except AssertionError as e:
            print(e)
            tts = gTTS("Bruh!",lang='de')
        tts.save('./response.mp3')
        # Wait for file to be saved
        
    async def ttsElevenlabs(self,text):
        """
        
        Generate a audio file with the elevenlabs API
        Uses an api token from ELEVENLABS_TOKEN environment variable required
        
        """
        
        
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
    print("GPT Extension IS BEING LOADED")
    bot.add_cog(GPT(bot))
    
def teardown(bot):
    if 'gptManager' in sys.modules:
            print("Found GPT module deleting it")
            del sys.modules['gptManager']
        
    if 'STT' in sys.modules:
        print("Found WHISPER module deleting it")
        del sys.modules['STT']   
    
    
    print('GPT Extension IS BEING UNLOADED')
    