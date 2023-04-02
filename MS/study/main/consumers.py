import os
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
import struct
from main.apps import MainConfig
from kiwipiepy import Kiwi
from . import test_model

API_BASE = "https://openapi.vito.ai"


config = dict(
    sample_rate="44100",
    encoding="LINEAR16",
    use_itn="true",
    use_disfluency_filter="false",
    use_profanity_filter="false",
)

STREAMING_ENDPOINT = "wss://{}/v1/transcribe:streaming?{}".format(
    API_BASE.split("://")[1], "&".join(map("=".join, config.items()))
)

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODA0NTQ5MDgsImlhdCI6MTY4MDQzMzMwOCwianRpIjoiQUQwLTQtaGFDM20zNlYyYXQ4MkIiLCJwbGFuIjoiYmFzaWMiLCJzY29wZSI6InNwZWVjaCIsInN1YiI6Ik5GSk9NdlVBWWZoUWlaQThaUWl0In0.f-L-9eGXGkW2iJNACCZj2LJJbQdri4PsdtMPUjYX7l4"

conn_kwargs = dict(extra_headers={"Authorization": "bearer " + token})

class AudioConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.websocket = await websockets.connect(STREAMING_ENDPOINT, **conn_kwargs)
        print("VITO Websockets Connected")
        self.kiwi = Kiwi()
        print("Kiwi Start")
        self.model = test_model.KoBERT()
        print("model Start")
        # try:
        # # Connect to the WebSocket server
        #     async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
        #         # Connection succeeded
        #         print("WebSocket connection succeeded")

        #         # Do something with the WebSocket connection here

        # except websockets.exceptions.ConnectionClosed as e:
        #     # Connection failed
        #     print("WebSocket connection failed:", e)
        
        await self.accept()
        #print(STREAMING_ENDPOINT)

    async def disconnect(self, close_code):
        await self.websocket.close()

    async def receive(self, bytes_data ):
        #print(len(bytes_data))
        #print(bytes_data[:10])
        # x = list(map(float, text_data.split(',')))
        # print(len(x))
        # audio_bytes = b''.join(struct.pack('f', f) for f in x)
        # print(len(audio_bytes))
        #print(sum(x)/len(x))
        #print(x[:10])
        #print(type(x[0]))
        #byte_array = struct.pack('f'*len(x), *x)
        #print(byte_array[:10])
        #print(type(byte_array))
        #print(byte_array[:5])

        #print("출력 : ", len(text_data))
        #temp = json.dumps({'length':len(text_data)})
        #print(text_data)

        await self.websocket.send(bytes_data)
        #print("Send the msg")
        #data = {'message': 'Hello, world!'}
        #self.send(text_data=json.dumps(data))

        try:
            asd = await asyncio.wait_for(self.websocket.recv(), timeout=1)
            #print(asd)
            msg = json.loads(asd)
            text = msg["alternatives"][0]["text"]

            if msg["final"]:
                print(text)
                morphs = self.kiwi.tokenize(text)
                print("=====BERT 진입======")
                res = self.model.predict(text)                
                print(res)
                data = {'text' : str(text), 'res' : str(res), 'final' : "true"}
                await self.send(text_data = json.dumps(data))
                # for x in morphs:
                #     print(x.form)
            else:
                data = {'text' : text, 'final' : "false"}
                await self.send(text_data=json.dumps(data))

        except:
            pass
            #print("time over")
        


