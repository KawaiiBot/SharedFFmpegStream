import asyncio
import shutil
import subprocess

import discord
from discord.errors import ClientException
from discord.opus import Encoder as OpusEncoder

executable = str(shutil.which('avconv') or shutil.which('ffmpeg')).split('/')[-1]


class SharedFFmpegStream(discord.AudioSource):
    """ Experimental AudioSource """

    def __init__(self, source, title='Unknown Shared Stream'):
        if executable is None:
            raise FileNotFoundError('ffmpeg and avconv was not found on the system')

        self.title = title
        self._packet = ''

        args = [executable]

        args.append('-i')
        args.append(source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))

        args.append('pipe:1')

        try:
            self._process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self._stdout = self._process.stdout
            asyncio.ensure_future(self.read_packet())
        except FileNotFoundError:
            raise ClientException(f'{executable} was not found.') from None
        except subprocess.SubprocessError as e:
            raise ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(e)) from e

    async def read_packet(self):
        DELAY = OpusEncoder.FRAME_LENGTH / 1000.0
        FSIZE = OpusEncoder.FRAME_SIZE
        while self._process is not None and not self._process.stdout.closed:
            self._packet = self._process.stdout.read(FSIZE)
            await asyncio.sleep(DELAY)
        print(f'[Shared Stream] {self.title} ended')

    def read(self):
        ret = self._packet
        return b'' if len(ret) != OpusEncoder.FRAME_SIZE else ret

    def cleanup(self):
        return

    # def terminate(self):
    #     self.terminated = True
    #     proc = self._process

    #     if proc is None:
    #         return

    #     proc.kill()
    #     if proc.poll() is None:
    #         proc.communicate()
    #         self._process = None
