import discord
from discord.ext import commands
from contextlib import contextmanager
import asyncio

@contextmanager
def simple_session_manager(session_name):
    print(f"Starting session: {session_name}")
    try:
        yield f"Session {session_name} active"
    finally:
        print(f"Ending session: {session_name}")

class AsyncSessionManager:
    def __init__(self, session_name):
        self.session_name = session_name

    async def __aenter__(self):
        print(f"Starting session: {self.session_name}")
        return f"Session {self.session_name} active"

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"Ending session: {self.session_name}")

class Contextmanager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        # Using a synchronous context manager wrapped in asyncio.to_thread
        session_name = "TestSession"
        session_result = await asyncio.to_thread(self.run_session, session_name)
        await ctx.send(f"Session result: {session_result}")

    def run_session(self, session_name):
        # This is a blocking synchronous context manager
        with simple_session_manager(session_name) as session:
            print("Running inside the session...")
            return session

    @commands.command()
    async def test_async(self, ctx):
        # Using an asynchronous context manager
        async with AsyncSessionManager("AsyncTestSession") as session:
            print("Running inside the async session...")
            await ctx.send(f"Session result: {session}")

async def setup(bot):
    await bot.add_cog(Contextmanager(bot))
