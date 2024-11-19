import asyncio
import select
import threading
import time
import discord
from discord.abc import Connectable
from discord.voice_client import VoiceClient
from discord.sinks import Sink ,RecordingException

class CustomVoiceClient(VoiceClient):
    
    def __init__(self, client: discord.Client, channel: Connectable):
        super().__init__(client, channel)
    
    def start_recording(self, sink, callback, *args, sync_start: bool = False):
        """The bot will begin recording audio from the current voice channel it is in.
        This function uses a thread so the current code line will not be stopped.
        Must be in a voice channel to use.
        Must not be already recording.

        .. versionadded:: 2.0

        Parameters
        ----------
        sink: :class:`.Sink`
            A Sink which will "store" all the audio data.
        callback: :ref:`coroutine <coroutine>`
            A function which is called after the bot has stopped recording.
        *args:
            Args which will be passed to the callback function.
        sync_start: :class:`bool`
            If True, the recordings of subsequent users will start with silence.
            This is useful for recording audio just as it was heard.

        Raises
        ------
        RecordingException
            Not connected to a voice channel.
        RecordingException
            Already recording.
        RecordingException
            Must provide a Sink object.
        """
        if not self.is_connected():
            raise RecordingException("Not connected to voice channel.")
        if self.recording:
            raise RecordingException("Already recording.")
        if not isinstance(sink, Sink):
            raise RecordingException("Must provide a Sink object.")

        self.empty_socket()

        self.decoder = discord.opus.DecodeManager(self)
        self.decoder.start()
        self.recording = True
        self.sync_start = sync_start
        self.sink = sink
        sink.init(self)

        t = threading.Thread(
            target=self.recv_audio_fixed,
            args=(
                sink,
                callback,
                *args,
            ),
        )
        t.start()

    def recv_audio_fixed(self, sink, callback, *args):
        # Gets data from _recv_audio and sorts
        # it by user, handles pcm files and
        # silence that should be added.

        self.user_timestamps: dict[int, tuple[int, float]] = {}
        self.starting_time = time.perf_counter()
        self.first_packet_timestamp: float
        while self.recording:
            ready, _, err = select.select([self.socket], [], [self.socket], 0.01)
            if not ready:
                if err:
                    print(f"Socket error: {err}")
                continue

            try:
                data = self.socket.recv(4096)
            except OSError:
                self.stop_recording()
                continue

            self.unpack_audio(data)

            ##### MAKE SURE THE CONNECTIONS DOESNT QUIT
            
            self.empty_socket()
            self.send_audio_packet(b"\x00\x00\x00\x00")

            ########

        self.stopping_time = time.perf_counter()
        self.sink.cleanup()
        callback = asyncio.run_coroutine_threadsafe(callback(sink, *args), self.loop)
        result = callback.result()

        if result is not None:
            print(result)