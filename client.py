import websockets
import asyncio
from scipy.signal import resample
import websockets.connection
import pyaudio
import numpy as np
audio = pyaudio.PyAudio()

RATE = 44100
RECORDS_TIME = 3
CHUNK = 1024
FORMAT = pyaudio.paFloat32

async def client(url):  
    async with websockets.connect(url) as ws:
        stream = audio.open(rate = RATE, frames_per_buffer= CHUNK, format= FORMAT, input = True, channels= 1, start = True, )
        while True:
            audio_record = []
            for _ in range(int(RATE*RECORDS_TIME/CHUNK)):
                rec = stream.read(CHUNK, exception_on_overflow= False)
                # print(len(rec))
                audio_record.append(rec)

            await ws.send(b"".join(audio_record))
            # print("sending")
            result_response = await ws.recv()
            print(result_response)

asyncio.get_event_loop().run_until_complete(client("ws://localhost:1234"))