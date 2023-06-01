from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
from kiwipiepy import Kiwi
from . import test_model
import numpy as np
import librosa
import time

# Vito API Load
from .vito_streaming_api import VitoStreamingAPI

# DB table Load
from .model_control import ModelControl

# 형태소 분리기 + KoBERT 모델 로드
kiwi = Kiwi()
model = test_model.KoBERT()
print("Kiwi and KoBERT Model SetUp")

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # Refresh시, ConversationLog Table Clear 진행
        self.model_control = ModelControl()
        await self.model_control.drop_conversationlog_table()
        await self.model_control.drop_recordstarttime_table()
        #await self.drop_table()

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

        # 언어폭력 횟수 체크
        self.abuse_cnt = 0
        self.sexual_cnt = 0
        
        # 녹음 버튼을 누른 시각
        self.record_start_time = False

        await self.accept()

    async def disconnect(self, close_code):
        await self.websocket.close()

    async def receive(self, bytes_data):

        if self.record_start_time == False:
            await self.model_control.insert_record_time()
            self.record_start_time = True

        await self.websocket.send(bytes_data)
        await self.make_amplitude_list(bytes_data)

        try:
            received_data = await asyncio.wait_for(self.websocket.recv(), timeout=1)
            msg = json.loads(received_data)
            text = msg["alternatives"][0]["text"]

            if text == "":
                raise Exception("No Text")

            if msg["final"]:
                start_timer = time.time()

                # 1. Text DB에 저장하고, 저장 결과 확인하는 부분
                await self.model_control.insert_content(text)
                latest_conversation = await self.model_control.select_lastest_conversation()
                print(latest_conversation.content, latest_conversation.time)

                # 2. 언어폭력 의심 문장 확인 (폭언, 성희롱, 상담원 사전)
                start_dict_timer = time.time()

                morphs = kiwi.tokenize(text)
                abuse_dict_flag = False
                sexual_dict_flag = False
                counselor_dict_flag = False

                for morph in morphs:
                    morpheme = morph.form

                    # 폭언 사전
                    if await self.model_control.morph_in_abusedict(morpheme):
                        abuse_dict_flag = True
                    # 성희롱 사전
                    elif await self.model_control.morph_in_sexualdict(morpheme):
                        sexual_dict_flag = True
                    
                    # 상담원 사전
                    if await self.model_control.morph_in_counselordict(morpheme):
                        counselor_dict_flag = True

                end_dict_timer = time.time()


                # 3. 언어폭력 의심 문장 확인 (음성 메타 정보)
                start_voice_timer = time.time()

                cur_text_bert_flag = False
                past_text_bert_flag = False

                if abuse_dict_flag or sexual_dict_flag:
                    cur_text_bert_flag = True
                else:   # 음성 메타 정보 판정 진행 --> 사전에서 매칭이 되었다면, 진입 x
                    print("음성 메타 정보 추출 중")
                    start, end = self.split_wav(msg["start_at"], msg["start_at"]+msg["duration"])
                    start_pitch, end_pitch = await self.analyzer(start,end)
                    print((start_pitch - end_pitch) / (msg["duration"] / 1000))

                    # 평균 피치 변화율 기준은 오차범위 고려 절대값 60 적용
                    if (start_pitch - end_pitch) / (msg["duration"] / 1000) < -60 or (start_pitch - end_pitch) / (msg["duration"] / 1000) > 60:
                        cur_text_bert_flag = True

                if counselor_dict_flag:
                    past_text_bert_flag = True
                
                end_voice_timer = time.time()

                # 사전 매칭 log check
                print(abuse_dict_flag, sexual_dict_flag, cur_text_bert_flag, counselor_dict_flag)

                # 4. KoBert 분류기 투입
                start_bert_timer = time.time()

                res = 0
                if cur_text_bert_flag:
                    print("1=====BERT 진입======")
                    
                    res = model.predict(text)  
                    await self.model_control.update_result(latest_conversation.log_id, res)
                    print(res)
                
                if past_text_bert_flag:
                    past_1_id = latest_conversation.log_id-1
                    past_2_id = latest_conversation.log_id-2
                    
                    past_1_flag = await self.model_control.id_in_conversation(past_1_id)
                    past_2_flag = await self.model_control.id_in_conversation(past_2_id)

                    if past_1_flag and past_2_flag:
                        print("2=====BERT 진입======")

                        past_1_conversation = await self.model_control.select_conversation(past_1_id)
                        past_1_res = past_1_conversation.result
                        res1 = model.predict(past_1_conversation.content)  

                        past_2_conversation = await self.model_control.select_conversation(past_2_id)
                        past_2_res = past_2_conversation.result
                        res2 = model.predict(past_2_conversation.content)  
                        
                        await self.model_control.update_result(past_1_id, res1)
                        await self.model_control.update_result(past_2_id, res2)

                        if past_1_res != res1:
                            if res1 == 1: self.abuse_cnt += 1
                            if res1 == 2: self.sexual_cnt += 1
                        
                        if past_2_res != res2:
                            if res2 == 1: self.abuse_cnt += 1
                            if res2 == 2: self.sexual_cnt += 1
                        print(past_1_res, past_2_res)
                        print(res1, res2)

                        data = {'res1' : str(res1), 'res2' : str(res2)}
                        await self.send(text_data = json.dumps(data))
                    elif past_1_flag == True:
                        print("3=====BERT 진입======")
                        past_1_conversation = await self.model_control.select_conversation(past_1_id)
                        past_1_res = past_1_conversation.result
                        res1 = model.predict(past_1_conversation.content)  

                        await self.model_control.update_result(past_1_id, res1)

                        if past_1_res != res1:
                            if res1 == 1: self.abuse_cnt += 1
                            if res1 == 2: self.sexual_cnt += 1

                        print(res1)

                        data = {'res1' : str(res1), 'res2' : str(0)}
                        await self.send(text_data = json.dumps(data))

                end_bert_timer = time.time()

                # 언어폭력 횟수 추가
                if res == 1:
                    self.abuse_cnt += 1
                elif res == 2:
                    self.sexual_cnt += 1
                
                stop_flag = False
                if self.sexual_cnt == 2:
                    stop_flag = True
                elif self.abuse_cnt + self.sexual_cnt == 3:
                    stop_flag = True
                
                print("폭언 횟수 : ", self.abuse_cnt)
                print("성희롱 횟수 :", self.sexual_cnt)

                text_time = str(latest_conversation.time)[11:-7]
                data = {'text' : str(text), 'res' : str(res), 'final' : "true", 'time' : text_time, 
                        'stop_flag':str(stop_flag), 'abuse_cnt':str(self.abuse_cnt), 'sexual_cnt':str(self.sexual_cnt)}
                await self.send(text_data = json.dumps(data))
                end_timer = time.time()

                print(f"문장 도착부터 결과 출력까지 산출 시간 : {end_timer - start_timer:.5f} sec")
                print(f"사전 매칭 시간 : {end_dict_timer - start_dict_timer:5f} sec")
                print(f"음성 메타 구하는 시간 : {end_voice_timer - start_voice_timer:.5f} sec")
                print(f"BERT 판별 시간 : {end_bert_timer - start_bert_timer:.5f} sec")
                print()

            else:
                data = {'text' : text, 'res' : str(0), 'final' : "false"}
                await self.send(text_data=json.dumps(data))

        except:
            pass
    
    async def make_amplitude_list(self, data):
        new_data = np.frombuffer(data, dtype=np.int16)
        new_buffer = np.zeros(len(new_data))
        for i in range(len(new_data)):
            if np.isnan(new_data[i]) == False:
                new_buffer[i] = new_data[i]
        y = librosa.to_mono(new_buffer)
        self.amplitude_list = np.append(self.amplitude_list, y)
        self.cnt_list.append(len(y)) 

    
    async def analyzer(self, start, end):
        edited_data = self.amplitude_list[start:end]
        start_data = self.amplitude_list[start:start+48000]
        end_data = self.amplitude_list[end-48000:end]
        start_data = np.append(start_data, end_data)

        f0, voiced_flag, voiced_probs = librosa.pyin(start_data, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        mel = 1127.01048 * np.log(1 + f0 / 700) 
        output2 = mel[~np.isnan(mel)] # Line 2

        return output2[0], output2[-1]
    
    
    def split_wav(self, start, end):
        start *= 48000
        end *= 48000
        start = int(start /1000)
        end = int(end / 1000)
        return start,end

