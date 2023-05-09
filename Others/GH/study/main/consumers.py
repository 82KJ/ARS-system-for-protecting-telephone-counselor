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
import numpy as np
import math
import librosa
import time


API_BASE = "https://openapi.vito.ai"


config = dict(
    sample_rate="48000",
    encoding="LINEAR16",
    use_itn="true",
    use_disfluency_filter="false",
    use_profanity_filter="false",
)

STREAMING_ENDPOINT = "wss://{}/v1/transcribe:streaming?{}".format(
    API_BASE.split("://")[1], "&".join(map("=".join, config.items()))
)

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODI5MjA5MTAsImlhdCI6MTY4Mjg5OTMxMCwianRpIjoiSGw3UkNlWXhwaE90RXBIeEk3RGwiLCJwbGFuIjoiYmFzaWMiLCJzY29wZSI6InNwZWVjaCIsInN1YiI6Ik5GSk9NdlVBWWZoUWlaQThaUWl0In0.se76GiKI02sXtt-CZYON2ypOycCq7rMmSoBcmann4Q0"

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
        self.amplitude_list = list()
        self.cnt_list = list()
        self.cnt_list.append(0)
        
        await self.accept()
        #print(STREAMING_ENDPOINT)

    async def disconnect(self, close_code):
        await self.websocket.close()

    async def receive(self, bytes_data ):
        await self.websocket.send(bytes_data)
        await self.make_amplitude_list(bytes_data)
        #print(len(bytes_data))

        try:
            asd = await asyncio.wait_for(self.websocket.recv(), timeout=1)
            #print(asd)
            msg = json.loads(asd)
            text = msg["alternatives"][0]["text"]

            if text == "":
                raise Exception("no text case")
            
            if msg["final"]:
                #print(msg)
                start_voice_meta = time.time()
                
                start = self.cnt_list[0]
                end = self.cnt_list[-1]

                self.cnt_list.clear()
                self.cnt_list.append(0)

                #print("time :  [ " + (msg["start_at"])/1000 + " : " + (msg["start_at"]+msg["duration"])/1000 + " ]")
                #start, end = await self.split_wav(msg["start_at"], msg["start_at"]+msg["duration"])
                print(len(self.amplitude_list))
                print(self.amplitude_list)
                
                start_pitch, end_pitch = await self.analyzer(start,end)
                self.amplitude_list = []

                #print("pitch : [ ", start_pitch, " : ", end_pitch, " ]")

                if(np.isnan(start_pitch) or np.isnan(end_pitch)):
                    print("isNaN")
                    pitch_slope = 0
                else:
                    pitch_slope = (end_pitch - start_pitch) / (msg["duration"] / 1000)

                end_voice_meta = time.time()

                #print(f"음성 메타 구하는 시간 : {end_voice_meta - start_voice_meta:.5f} sec")

                print('text: [', text, ']')
                morphs = self.kiwi.tokenize(text)

                print(f'pitch_slope:  {pitch_slope:.5f}')

                # bert 진입 조건 필요
                if(pitch_slope < -30 or pitch_slope >20):
                    start_bert = time.time()
                    print("=====BERT 진입======")
                    res = self.model.predict(text)  
                    end_bert = time.time()
                    print(res)
                    #print(f"bert 산출 시간 : {end_bert - start_bert:.5f} sec")

                else:
                    print("일반")

                data = {'text' : str(text), 'res' : str(res), 'final' : "true"}
                await self.send(text_data = json.dumps(data))
                final_end = time.time()

                print(f"문장 도착부터 결과 출력까지 산출 시간 : {final_end - start_voice_meta:.5f} sec")
                print()

                # for x in morphs:
                #     print(x.form)
            else:
                data = {'text' : text, 'final' : "false"}
                await self.send(text_data=json.dumps(data))

        except:
            pass
            #print("time over")
    
    async def make_amplitude_list(self, data):
        new_data = np.frombuffer(data, dtype=np.int16)
        new_buffer = np.zeros(len(new_data))
        for i in range(len(new_data)):
            if np.isnan(new_data[i]) == False:
                new_buffer[i] = new_data[i]
        y = librosa.to_mono(new_buffer)

        self.amplitude_list = np.append(self.amplitude_list, y)

        cnt = self.cnt_list[-1] + len(y)
        self.cnt_list.append(cnt)

    async def analyzer(self, start, end):
        x = min(int((end - start)/2), 48000)

        data_start = self.amplitude_list[0 : x]
        data_end = self.amplitude_list[end - x : end]

        # 음성에서 기본주파수 f0 추출
        # [C2=65.41 : C7=2093]
        f0_s, voiced_flag, voiced_probs = librosa.pyin(data_start, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=48000)
        f0_e, voiced_flag, voiced_probs = librosa.pyin(data_end, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=48000)

        # 직접 mel 변환
        # [C2=166 : C7=3377]
        mel1 = 1127.01048 * np.log(1 + f0_s / 700)
        mel2 = 1127.01048 * np.log(1 + f0_e / 700)

        # NaN 데이터 제거
        output1 = mel1[~np.isnan(mel1)]
        output2 = mel2[~np.isnan(mel2)]

        # 두 구간의 mel 데이터 확인
        #print("start: ", output1)
        #print("end: ", output2)

        # 구간의 평균을 반환
        return np.mean(output1), np.mean(output2)

    async def split_wav(self, start, end):
        start_sec = int(start / 1000)
        end_sec = int(end / 1000)

        # sec + cnt[] * ms
        start = int(self.cnt_list[start_sec] + ((self.cnt_list[start_sec + 1] - self.cnt_list[start_sec]) * (start/1000 - start_sec)))
        end = int(self.cnt_list[end_sec] + ((self.cnt_list[end_sec + 1] - self.cnt_list[end_sec]) * (end/1000 - end_sec)))
        
        return start, end

# mel = 1127.01048 x ln(1 + hz/ 700)