import asyncio
import subprocess
import threading

import discord
from discord.opus import Encoder as OpusEncoder


class SharedFFmpegStream(discord.AudioSource):
    """ Experimental AudioSource """

    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None, title='Unknown Shared Stream'):
        self.title = title
        self._packet = ""
        stdin = None if not pipe else source

        args = [executable]

        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))

        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))

        if isinstance(options, str):
            args.extend(shlex.split(options))

        args.append('pipe:1')

        try:
            self._process = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self._stdout = self._process.stdout
            asyncio.ensure_future(self.read_packet())
            #thread = threading.Thread(target=self.read_packet)
            #thread.start()
        except FileNotFoundError:
            raise ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as e:
            raise ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(e)) from e           

    async def read_packet(self):
        DELAY = OpusEncoder.FRAME_LENGTH / 1000.0
        FSIZE = OpusEncoder.FRAME_SIZE
        while self._process is not None and not self._process.stdout.closed:
            self._packet = self._process.stdout.read(FSIZE)
            await asyncio.sleep(DELAY)
        print(f'[Shared Stream] {self.title} terminated')

    def read(self):
        ret = self._packet
        return b'' if len(ret) != OpusEncoder.FRAME_SIZE else ret

    def cleanup(self):
        return # Don't cleanup shared streams - they should remain open
        
        # proc = self._process
        # if proc is None:
            # return

        # proc.kill()
        # if proc.poll() is None:
            # proc.communicate()

        # self._process = None

        ### LEAVING THE ABOVE CODE FOR REFERENCE ###
