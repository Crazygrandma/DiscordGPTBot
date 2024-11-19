import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncio
import os
from customVoiceClient import CustomVoiceClient
from helper import get_recordings, mutagen_length, pickRandom

file_counter = 0

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
        
    
    @tasks.loop(seconds=30)
    async def dialogTask(self,ctx):
        
        # Check recordings
        filenumber = get_recordings('./recordings')
        
        if filenumber <= 3:
            # Muting bot
            await ctx.guild.voice_client.guild.me.edit(mute=True)
            await asyncio.sleep(5)
            # record Audio for x seconds
            await self.recordDialog(ctx,5)
        else:
            # Play random audio
            print("Playing audio")
            # Unmute
            await ctx.guild.voice_client.guild.me.edit(mute=False)
            # await asyncio.sleep(5)
            sound = pickRandom('./recordings')
            if ctx.guild.id in self.connections:
                vc = self.connections[ctx.guild.id]
                
                source = FFmpegPCMAudio(sound)
                length = mutagen_length(sound)
                # TODO Fixed getting accurate length
                print(f"Waiting for {int(length)} or 5")
                if int(length) == 0:
                    length = 5
                vc.play(source)
                await asyncio.sleep(int(length))
                # Delete picked sound to record
                if os.path.exists(sound):
                    os.remove(sound)
                    print(f"{sound} has been deleted.")
                else:
                    print(f"{sound} does not exist.")
    
    async def recordDialog(self,ctx,duration):
        vc = self.connections[ctx.guild.id]
        
        vc.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            sync_start = True
        )
        print("Recording!")
        await asyncio.sleep(int(duration))
        vc.stop_recording()
    
    @slash_command(description="Stop AI")
    async def stop(self,ctx):
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            self.dialogTask.cancel()
            await vc.disconnect()
        await ctx.respond(":(")
    
    @slash_command(description="Start AI")
    async def start(self,ctx):
        global file_counter
        file_counter = get_recordings('./recordings')
        user = ctx.user.id
        voice = ctx.author.voice
        vc = await voice.channel.connect(cls=CustomVoiceClient)
        print("Connection with custom voice client")
        await ctx.respond(f"Jo! {ctx.author.mention}") 
            
        if not voice:
            await ctx.repond(f"<@{user}>! Bruh wo soll ich denn rein?")
        
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.
        self.dialogTask.start(ctx)
    
                        
    async def once_done(self,sink: discord.sinks, *args):  # Our voice client already passes these in.
        
        global file_counter
        file_counter = get_recordings('./recordings')
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
    
    
          
def setup(bot):
    print("AI extension is being LOADED")
    bot.add_cog(AI(bot))
    
def teardown(bot):
    print('AI extension is being UNLOADED')
    