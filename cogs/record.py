import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
import os
import random
from customVoiceClient import CustomVoiceClient
from helper import get_recordings, mutagen_length, pickRandom

file_counter = 0
max_files = 3
loop_frequency = 70
recording_length = 7
allow_silence = True

JOIN_ON_VOICE = False
RUN_PLAY_RANDOM = False
DIALOG_RUNNING = True


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
        self.connections = {}
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AI is ready")
        
    
    @tasks.loop(seconds=loop_frequency)
    async def dialogTask(self,ctx):
        
        # Check recordings
        filenumber = get_recordings('./recordings')
        
        if filenumber < max_files:
            # Muting bot
            # await ctx.guild.voice_client.guild.me.edit(mute=True)
            # record Audio for x seconds
            await self.recordDialog(ctx,recording_length)
        else:
            # Play random audio
            #####print("Playing audio")
            # Unmute
            # await ctx.guild.voice_client.guild.me.edit(mute=False)
            # await asyncio.sleep(5)
            sound = pickRandom('./recordings')
            if ctx.guild.id in self.connections:
                vc = self.connections[ctx.guild.id]
                
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                # TODO Fixed getting accurate length
                print(f"Waiting for {int(length)} or {recording_length}")
                if int(length) == 0:
                    length = recording_length
                vc.play(source)
                await asyncio.sleep(int(length))
                # Delete picked sound to record
                if os.path.exists(sound):
                    os.remove(sound)
                    ###print(f"{sound} has been deleted.")
                else:
                    pass
                    ###print(f"{sound} does not exist.")
    
    @slash_command(description="Disable random sounds")
    async def stoprandom(self,ctx):
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = False
        await ctx.respond(f"<@{ctx.user.id}>! Disable Randomsounds")

    @slash_command(description="Play a random sound at a random time")
    async def randomplay(self, ctx, mintime: int=10, maxtime: int=30):
        user = ctx.user.id
        global RUN_PLAY_RANDOM
        RUN_PLAY_RANDOM = True
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            await ctx.respond(f"<@{user}>! Viel Spaß")
            while RUN_PLAY_RANDOM:
                sound = pickRandom('./sounds/soundboard')
                randWait = random.randint(int(mintime),int(maxtime))
                # print(f"Waiting {randWait} seconds")
                await asyncio.sleep(randWait)
                
                # await ctx.guild.voice_client.guild.me.edit(mute=False)
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                vc.play(source)
                await asyncio.sleep(int(length))
                # await ctx.guild.voice_client.guild.me.edit(mute=True)

    @slash_command(description="Join the voice channel")
    async def join(self,ctx):
        user = ctx.user.id
        voice = ctx.author.voice
        vc = await voice.channel.connect(cls=CustomVoiceClient)
        await ctx.respond(f"Jo! {ctx.author.mention}") 
            
        if not voice:
            await ctx.repond(f"<@{user}>! Bruh wo soll ich denn rein?")
        
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

    @slash_command(description="Leave the voice channel")
    async def leave(self,ctx):
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            await vc.disconnect()
        await ctx.respond(":(")

    @slash_command(description="Play a sound")
    async def play(self,ctx,arg:str):
        await ctx.respond("Play sound.")
        source = FFmpegPCMAudio(f"./sounds/soundboard/{arg}.wav")
        length = mutagen_length(source)
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            vc.play(source)
        await asyncio.sleep(int(length))
        
    async def recordDialog(self,ctx,duration):
        # await ctx.guild.voice_client.guild.me.edit(mute=True)
        await asyncio.sleep(random.randint(6,14))
        vc = self.connections[ctx.guild.id]
        vc.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            sync_start = allow_silence
        )
        # DEBUG 
        print("Recording!")
        await asyncio.sleep(int(duration))
        vc.stop_recording()
        # await ctx.guild.voice_client.guild.me.edit(mute=False)
    
    @slash_command(description="Stop Fun :(")
    async def stopdialog(self,ctx):
        self.dialogTask.cancel()
        await ctx.respond(":(")
    
    @slash_command(description="Start Fun Lol")
    async def startdialog(self,ctx):
        global file_counter
        file_counter = get_recordings('./recordings')
        user = ctx.user.id
        voice = ctx.author.voice
        vc = None
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
        else:
            vc = await voice.channel.connect(cls=CustomVoiceClient)     
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
        print("Connection with custom voice client")
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
    
    
          
def setup(bot):
    print("AI extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('AI extension is being UNLOADED')
    