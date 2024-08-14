import websockets
from faster_whisper import WhisperModel
import os
import io
import multiprocessing as mp
import asyncio 
import threading

import websockets.sync
import websockets.sync.server
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import socket

class __Receiver(threading.Thread):

    def __init__(self, receiving_queue : mp.Queue, ws: socket.socket):
        threading.Thread.__init__(self)
        self.__ws = ws
        self.__receiving_queue = receiving_queue

    def run(self):
        print("Receving data from client")
        while True:
            try:
                __client_data = self.__ws.recv()
                self.__receiving_queue.put(__client_data)
            except KeyboardInterrupt:
                break

class __Transcribe(threading.Thread):

    def __init__(self, sending_queue: mp.Queue, receiving_queue: mp.Queue, type_model = "base.en"): 
        threading.Thread.__init__(self, daemon = True)
        self.__model = WhisperModel(type_model)
        self.__receiving_queue = receiving_queue
        self.__sending_queue = sending_queue

    def run(self):
        print("Start STT service")
        while True:
            try:
                __raw_data = self.__receiving_queue.get()
                __data = io.BytesIO(__raw_data)
                __result, _ = self.__model.transcribe(__data, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
                __segments = list(__result)
                __text = " ".join([segment.text for segment in __segments])
                # if len(__text) > 0:
                self.__sending_queue.put(__text.strip())
            except NameError as e:
                print(e)
                break
        
class __Sender(threading.Thread):

    def __init__(self, sending_queue : mp.Queue, ws : socket.socket):
        threading.Thread.__init__(self)
        self.__ws = ws 
        self.__sending_queue = sending_queue
    
    def run(self):
        while True:
            try:
                __transcription = self.__sending_queue.get()
                self.__ws.send(__transcription)
            except KeyboardInterrupt:
                break


def main(ws : socket.socket):
    while True:
        try:
            __sending_queue = mp.Queue()
            __receiving_queue = mp.Queue()
            
            __receiving_service = __Receiver(__receiving_queue, ws)
            __transcription_service = __Transcribe(__sending_queue, __receiving_queue)
            __sending_service = __Sender(__sending_queue, ws)

            __receiving_service.start()
            __transcription_service.start()
            __sending_service.start()

            __receiving_service.join()
            __transcription_service.join()
            __sending_service.join()
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    try:
        with websockets.sync.server.serve(main, "localhost", 2222) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        import sys
        sys.exit()




