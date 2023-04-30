from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
from kiwipiepy import Kiwi
from . import test_model
import numpy as np
import librosa
import time
from asgiref.sync import async_to_sync 
from channels.db import database_sync_to_async

from .vito_streaming_api import VitoStreamingAPI

# DB table Load
from .models import ConversationLog, AbuseDictionary

kiwi = Kiwi()
model = test_model.KoBERT()
print("Kiwi and KoBERT Model SetUp")

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # Refresh시, ConversationLog Table Clear 진행
        await self.drop_table()

        # VITO API 설정 및 Websocket 연결
        vito_streaming_api = VitoStreamingAPI()
        STREAMING_ENDPOINT = vito_streaming_api.STREAMING_ENDPOINT

        token = vito_streaming_api.token
        conn_kwargs = dict(extra_headers={"Authorization": "bearer " + token})

        self.websocket = await websockets.connect(STREAMING_ENDPOINT, **conn_kwargs)
        print("VITO Websockets Connected")

        # 음성 메타 정보 저장을 위한 기본 리스트 선언
        self.amplitude_list = list()
        self.cnt_list = list()
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.websocket.close()

    async def receive(self, bytes_data ):

        await self.websocket.send(bytes_data)
        await self.make_amplitude_list(bytes_data)


        try:
            asd = await asyncio.wait_for(self.websocket.recv(), timeout=1)
            msg = json.loads(asd)
            text = msg["alternatives"][0]["text"]

            if msg["final"]:

                # 1. Text DB에 저장하고, 저장 결과 확인하는 부분
                await self.insert_record(text)
                x = await self.select_text()
                print(x.log_id, x.content, x.time)
                print()
                ##############################################

                start_voice_meta = time.time()
                start, end = self.split_wav(msg["start_at"], msg["start_at"]+msg["duration"])
                start_pitch, end_pitch = await self.analyzer(start,end)
                print((start_pitch - end_pitch) / (msg["duration"] / 1000))
                end_voice_meta = time.time()

                print(f"음성 메타 구하는 시간 : {end_voice_meta - start_voice_meta:.5f} sec")

                # pitch_slope = (start_pitch - end_pitch / msg["duration"] / 1000)
                # print("피치 기울기 : " + pitch_slope)

                print(text)
                morphs = kiwi.tokenize(text)

                start_bert = time.time()
                print("=====BERT 진입======")
                res = model.predict(text)  
                end_bert = time.time()
                print(res)
                print(f"bert 산출 시간 : {end_bert - start_bert:.5f} sec")


                # 2. 산출된 탐지 결과 DB에 Update
                await self.update_result(x.log_id, res)
                ###########################################

                data = {'text' : str(text), 'res' : str(res), 'final' : "true"}
                await self.send(text_data = json.dumps(data))
                final_end = time.time()

                print(f"문장 도착부터 결과 출력까지 산출 시간 : {final_end - start_voice_meta:.5f} sec")
                print()


            else:
                data = {'text' : text, 'res' : "일반",'final' : "false"}
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
        #print(len(y))
        self.amplitude_list = np.append(self.amplitude_list, y)
        self.cnt_list.append(len(y)) 
        #f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

        #print(f0)
    
    async def analyzer(self, start, end):
        edited_data = self.amplitude_list[start:end]
        start_data = self.amplitude_list[start:start+48000]
        end_data = self.amplitude_list[end-48000:end]
        start_data = np.append(start_data, end_data)

        f0, voiced_flag, voiced_probs = librosa.pyin(start_data, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        mel = 1127.01048 * np.log(1 + f0 / 700) 
        output2 = mel[~np.isnan(mel)] # Line 2

        return output2[0], output2[-1]
    
    @database_sync_to_async
    def insert_record(self,text):
        ConversationLog.objects.create(content=text)

    @database_sync_to_async
    def select_text(self):
        return ConversationLog.objects.last()
    
    @database_sync_to_async
    def drop_table(self):
        ConversationLog.objects.all().delete()

    @database_sync_to_async
    def update_result(self, id, res):

        if res == '일반' : res = 0
        elif res == '폭언' : res = 1
        else: res = 2

        ConversationLog.objects.filter(log_id=id).update(result=res)
    
    def split_wav(self, start, end):
        start *= 48000
        end *= 48000
        start = int(start /1000)
        end = int(end / 1000)
        return start,end
        #return self.amplitude_list[start:end]
        
    

# mel = 1127.01048 x ln(1 + hz/ 700)
# 19000, 48400, 49400 ... 매번 48000 안떨어진다
# dp = [19000, 19000+48400 , 합산 식을]
# 슬라이스를 해서 인덱스에 알맞은 값만 짤라오게 만들면 된다
# 끝점과 끝점의 피치기울기.. 끝점 제대로 못 잡는다 --> Hz, mel 뭉뜽그려지면서, 얼추 파악
