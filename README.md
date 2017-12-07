# SharedFFMpegStream
A custom implementation of FFmpegStreams to allow a single stream to be broadcast to multiple voiceconnections


## Usage Example
```python
import audio

stream = audio.SharedFFmpegStream(source='URL or File Path')

voice_client.play(stream)
```
