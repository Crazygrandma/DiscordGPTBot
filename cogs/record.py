import glob
import random
import discord
from discord.voice_client import VoiceProtocol
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
import os
from mutagen.wave import WAVE


file_counter = 0

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
    try:
        audio = WAVE(path)
        length = audio.info.length
        return length
    except:
        return 1

usernames = {
    395847854616215556: "MoviemakerHD"
}

class AI(commands.Cog):
    
    def __init__(self,bot) -> None:
        self.bot = bot
        self.guild = None
        self.connections = {}
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AI is ready")
        
    
    @tasks.loop(seconds=20)
    async def record_dialog(self,ctx):
        
        await asyncio.sleep(random.randint(3,7))
        await self.recordDialog(ctx,10)
    
    
    async def recordDialog(self,ctx,duration):
        vc = self.connections[ctx.guild.id]
        
        vc.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            ctx.channel
        )
        # TODO Mute bot when receiving data
        # await ctx.guild.change_voice_state(channel=ctx.channel, self_mute=True)
        print("Recording!")
        await asyncio.sleep(int(duration))
        vc.stop_recording()
    
    @slash_command(description="Stop AI")
    async def stop(self,ctx):
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            await vc.disconnect()
        await ctx.repond(":(")
    
    @slash_command(description="Start AI")
    async def start(self,ctx):
        user = ctx.user.id
        voice = ctx.author.voice
        vc = await voice.channel.connect()
        await ctx.respond(f"Jo! {ctx.author.mention}") 
            
        if not voice:
            await ctx.repond(f"<@{user}>! Bruh wo soll ich denn rein?")
        
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
        self.record_dialog.start(ctx)  

        # # Check for recordings

        # await asyncio.sleep(5)
        # # Start recording
        # print("Recording sound")
        # vc.start_recording(
        #     discord.sinks.WaveSink(),  # The sink type to use.
        #     self.once_done,  # What to do once done.
        #     voice.channel,  # The channel to disconnect from.
        #     sync_start=True 
        # )
        # await asyncio.sleep(int(10))
        # vc.stop_recording()
        # # sink.audio_data.clear()
        # print("Saving Recording")
        # await asyncio.sleep(int(3))

        # # Process files
        # print("Enough files!")
        # print("Pick random sound")
        # sound = self.pickRandom("./recordings")
        # # TODO Delete sound after picked
        # await asyncio.sleep(2)
        # source = FFmpegPCMAudio(sound)
        # length = mutagen_length(sound)
        # print(f"Playing sound {sound}")
        # vc.play(source)
        # await asyncio.sleep(int(length))
        # await vc.disconnect()
    
                        
    async def once_done(self,sink: discord.sinks, *args):  # Our voice client already passes these in.
        
        global file_counter
        
        # Debug: Check if sink.audio_data has any content
        if not sink.audio_data:
            print("No audio data available in sink.")
            return
        
        print(f"Recording session finished. Sink audio data length: {len(sink.audio_data)}")
        # Process each user's audio data
        for user_id, audio in sink.audio_data.items():
            print(f"User {user_id} audio length: {len(audio.file.getbuffer())}")
            # Lookup or default to user_id if username is unavailable
            username = usernames.get(user_id, str(user_id))  # Replace `usernames` with your actual username mapping
            # Construct the unique filename
            filename = f"recordings/{username}_{file_counter + 1}.wav"  # Using `mp3` as an example; replace with `sink.encoding` if dynamic
            print(f"Saving audio as: {filename}")
            # Save the audio file
            try:
                with open(filename, "wb") as outfile:
                    outfile.write(audio.file.getbuffer())

                # Increment the counter after successful save
                file_counter += 1

                print(f"Audio for user {username} saved successfully.")
            except Exception as e:
                print(f"Error saving audio for user {username}: {e}")
                
        sink.audio_data.clear()
        print("Sink audio data cleared.")       


    def pickRandom(self,path):
        soundList = glob.glob(f'{path}/*.wav')
        sound = random.choice(soundList)
        return sound   
    
    
          
def setup(bot):
    print("AI extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('AI extension is being UNLOADED')
    