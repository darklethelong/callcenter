import asyncio
import websockets
import json
import io
import speech_recognition as sr

async def microphone_client():
    async with websockets.connect(
            'ws://localhost:2222') as websocket:
        r = sr.Recognizer()
        mic = sr.Microphone(sample_rate= 16000)
        while True:
            with mic as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source,  phrase_time_limit=4)
                data = io.BytesIO(audio.get_wav_data())
                await websocket.send(data)
                transcription = await websocket.recv()
                if len(transcription) > 1:
                    print(transcription)


asyncio.run(microphone_client())