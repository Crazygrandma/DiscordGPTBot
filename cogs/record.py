import glob
import random
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
import os
from mutagen.wave import WAVE

NUMBER_OF_FILES = 0

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
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AI is ready")
        
    
    @slash_command(description="Start AI")
    async def start(self,ctx):
        self.guild = ctx.guild
        await ctx.respond("Ok!")
        # Check if user is in any voice channel
        for voice_channel in self.guild.voice_channels:  # Iterate through all voice channels
            for member in voice_channel.members:  # Iterate through members in the voice channel
                # If member is not a bot
                if member.bot:
                    return
                
                voice = member.voice
                vc = await voice.channel.connect()    

                # Check for recordings
                print("Check recordings")
                global NUMBER_OF_FILES
                NUMBER_OF_FILES = get_recordings("./recordings")
                while NUMBER_OF_FILES != 5:
                    print(f"Files: {NUMBER_OF_FILES}")
                    # Connect to voice channel
                    await asyncio.sleep(random.randint(10,15))
                    # Start recording
                    print("Recording sound")
                    vc.start_recording(
                        discord.sinks.WaveSink(),  # The sink type to use.
                        self.once_done,  # What to do once done.
                        voice.channel,  # The channel to disconnect from.
                        # sync_start=True # TODO Maybe this can fix issues (will record everthing including empty parts)
                    )
                    await asyncio.sleep(int(5))
                    vc.stop_recording()
                    print("Saving Recording")
                    await asyncio.sleep(int(2))
                    # Save recording
                
                # Process files
                print("Enough files!")
                print("Pick random sound")
                sound = self.pickRandom("./recordings")
                # TODO Delete sound after picked
                await asyncio.sleep(2)
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                print(f"Playing sound {sound}")
                vc.play(source)
                await asyncio.sleep(int(length))
                await vc.disconnect()
    
                        
    async def once_done(self,sink: discord.sinks, channel: discord.TextChannel):  # Our voice client already passes these in.
        print("ONCE DONE CALL")
        # TODO sink audio data sometimes empty 
        # check if data empty
        for user_id,audio in sink.audio_data.items():
            # Lookup username from known users
            username = usernames.get(user_id)
            if username is None:
                username = user_id
            global NUMBER_OF_FILES
            filename = f"recordings/{username}{NUMBER_OF_FILES}.{sink.encoding}"
            print("Saving as ",filename)
            with open(filename, "wb") as outfile:
                outfile.write(audio.file.getbuffer())
                outfile.close()
                
            NUMBER_OF_FILES += 1


    def pickRandom(self,path):
        soundList = glob.glob(f'{path}/*.wav')
        sound = random.choice(soundList)
        return sound   
    
    
          
def setup(bot):
    print("AI extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('AI extension is being UNLOADED')
    