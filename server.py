import websockets
from threading import Thread
from queue import Queue
from websockets.sync.server import serve 
import io
from faster_whisper import WhisperModel

class Listening(Thread):
    
    '''
    Websocket for rec data
    '''
    
    def __init__(self, ws, listen_queue = Queue()):
        super.__init__(Thread)
        
        # queue rec data
        self.listen_queue = listen_queue
        
        # websocket
        self.ws = ws
        
    def run(self):
        
        '''
        Loop forever retrieving data client
        '''
        
        while True:
            
            # put data to rec queue
            self.listen_queue.put(self.ws.recv())

        
class Engine():
    
    def __init__(self, model_path = "base.en"):
        
        # load speech recognition model
        self.sr_model = WhisperModel(model_path)
    
    def service(self, ws):
        
        listening = Listening(ws)
        
        # Start thread
        listening.start()
        
        # Join Thread
        listening.join()
        
        while True:
        
            # get data from rec queue
            bytes_received = listening.listen_queue.get()
            
            # convert to io bytes for input sr model
            byte_data = io.BytesIO(bytes_received)
            
            # inference 
            segments, _ = self.sr_model.transcribe(byte_data, beam_size=5)
            segments = list(segments)
            text = " ".join([segment.text for segment in segments])
            
            # print for debug
            print(text)
            # start receiving queue
            ws.send(text)
            
with serve(Engine().service, "localhost", 2222) as server:
    server.serve_forever() 
        