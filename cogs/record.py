import glob
import importlib
import sys
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
import os
import random
import configparser
# from customVoiceClient import CustomVoiceClient
from helper import get_recordings, mutagen_length, pickRandom, is_bot_connected, ttsgTTS

file_counter = 0
max_files = 4
loop_frequency = 20
recording_length = 5
allow_silence = True

JOIN_ON_VOICE = False
RUN_PLAY_RANDOM = False
DIALOG_RUNNING = True

config = configparser.ConfigParser()

usernames = {
    395847854616215556: "MoviemakerHD",
    327764607257280515: "Jan",
    298494510462140426: "JPH",
    690577696161398885: "DerMensch"
}

class AI(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.guild = None
        self.whisper = None
        self.mygpt = None
        self.connections = {}
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Recording is ready")
        
    
    @tasks.loop(seconds=loop_frequency)
    async def dialogTask(self,ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        # Check recordings
        filenumber = get_recordings('./recordings')
        
        await asyncio.sleep(random.randint(4,12))
        
        if filenumber < max_files:
            # Muting bot
            # await ctx.guild.voice_client.guild.me.edit(mute=True)
            # await asyncio.sleep(5)
            # record Audio for x seconds
            await self.recordDialog(ctx,random.randint(recording_length, recording_length+3))
        else:
            # TRANSSCRIBE AUDIO
            transcribed_texts = self.transcribeDialog()
            
            answerToLLM = ""
            for text in transcribed_texts:
                answerToLLM += text
            
            print(answerToLLM)
            
            
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
            
            
            # GET ANSWER
            if 'gptManager' not in sys.modules:
                print("(Re)loading module")
                gptmodule = importlib.import_module('gptManager','.')
                self.mygpt = gptmodule.GPTManager(GPT_MODEL,SYSTEM_PROMPT)
                print("GPT Model loaded")
            
            # Get response from LLM
            response = self.mygpt.getResponse(
                answerToLLM,
                max_tokens=int(maxtokens),
                repeat_penalty=float(penalty),
                temp=float(temp)
            )
            print("Got a response")
            print(response)



            # Generate sound with gTTS
            await ttsgTTS(response)
                
             
            # PLAY TEXT
            
            length = mutagen_length("./response.mp3")
            source = FFmpegPCMAudio("./response.mp3")
            voice_client.play(source)
            await asyncio.sleep(int(recording_length))
            # Delete picked sound to record
            if os.path.exists("./response.mp3"):
                os.remove("./response.mp3")
                ###print(f"{sound} has been deleted.")
            else:
                print("AAAAAAAAAAAAAAA")
                pass
                ###print(f"{sound} does not exist.")

            await asyncio.sleep(5)    
            await self.recordDialog(ctx,recording_length)
     
    async def recordDialog(self,ctx,duration):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        source = FFmpegPCMAudio(f"./sounds/silence.wav")
        voice_client.play(source)
        voice_client.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            sync_start = True
        )
        # DEBUG 
        #print("Recording!")
        await asyncio.sleep(int(duration))
        #print("Done Recording!")
        voice_client.stop_recording()
        voice_client.stop()
        # await ctx.guild.voice_client.guild.me.edit(mute=False)
    
    @slash_command(description="Stop Fun :(")
    async def stopdialog(self,ctx):
        self.dialogTask.cancel()
        await ctx.respond(":(")
    
    @slash_command(description="Start Fun Lol")
    async def startdialog(self,ctx):
        global file_counter
        file_counter = get_recordings('./recordings')
        voice = ctx.author.voice  
        vc = await voice.channel.connect()
        print("Connecting with normal client")     
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
        # print("Connection with custom voice client")
        await ctx.respond(f"Jo! {ctx.author.mention}") 
        self.dialogTask.start(ctx)
                     
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
            filename = f"recordings/{username}_{round(random.random(),3)}.wav"  # Using `mp3` as an example; replace with `sink.encoding` if dynamic
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
        recordings = glob.glob(f'recordings/*.wav')
        for filepath in recordings:
            basenamefile = os.path.basename(filepath)[:-4]
            result = self.whispermodel.transcribe(filepath)
            transcribed_text.append(f"[{basenamefile}]: {result['text']}")
        return transcribed_text
    
          
def setup(bot):
    print("Record extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('Record extension is being UNLOADED')
    