import asyncio
import json
import logging
import time
from io import DEFAULT_BUFFER_SIZE

from requests import Session
import websockets

from sentence_transformers import SentenceTransformer

import sys

import librosa
import numpy as np

API_BASE = "https://openapi.vito.ai"

class VITOOpenAPIClient:
    def __init__(self, client_id, client_secret):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = Session()
        self._token = None
        self.model = SentenceTransformer('all-mpnet-base-v2')

        self.amplitude = 0
        self.tempo = 0
        
    @property
    def token(self):
        if self._token is None or self._token["expire_at"] < time.time():
            resp = self._sess.post(
                API_BASE + "/v1/authenticate",
                data={"client_id": self.client_id, "client_secret": self.client_secret},
            )
            resp.raise_for_status()
            self._token = resp.json()
        return self._token["access_token"]

    async def streaming_transcribe(self, filename, config=None):
        if config is None:
            config = dict(sample_rate="32000", encoding="LINEAR16", use_itn="true",  use_disfluency_filter="false", use_profanity_filter="false")

        STREAMING_ENDPOINT = "wss://{}/v1/transcribe:streaming?{}".format(
            API_BASE.split("://")[1], "&".join(map("=".join, config.items()))
        )
        conn_kwargs = dict(extra_headers={"Authorization": "bearer " + self.token})

        async def streamer(websocket):
            with open(filename, "rb") as f:
                while True:
                    buff = f.read(DEFAULT_BUFFER_SIZE)
                    if buff is None or len(buff) == 0:
                        break
                    await websocket.send(buff)
                await websocket.send("EOS")

        texts = []
        async def transcriber(websocket, model):
            async for msg in websocket:
                msg = json.loads(msg)
                #print(msg)
                if msg["final"]:
                    text = msg["alternatives"][0]["text"]
                    idx = msg["seq"]

                    print()
                    print(str(msg["seq"]) + " : " + msg["alternatives"][0]["text"])
                    print("시작 시간 :" + str(msg["start_at"]) + ", 걸린 시간 : " + str(msg["duration"]))
                    texts.append([idx, text, (msg["start_at"], msg["start_at"]+msg["duration"]), -1])
                    print(texts)

                    speech_tempo = len(msg["alternatives"][0]["text"]) * 1000 / msg["duration"]
                    self.tempo = (self.tempo + speech_tempo) / msg["seq"]

                    speech_amplitude = await analyzer(msg)
                    self.amplitude = (self.amplitude * (msg["seq"]-1) + speech_amplitude) / msg["seq"]

                    print("발화 속도 : ", speech_tempo)
                    print("평균 발화 속도 : ", self.tempo)
                    print("발화 크기: ", speech_amplitude)
                    print("평균 발화 크기: ", self.amplitude)

                    if speech_tempo > (self.tempo * 1.5):
                        # 해당 텍스트의 발화 속도가 평균 발화속도 * 1.5 보다 빠르면 bert 모델 투입
                        await bert(model, idx-1)
                    elif speech_amplitude > (self.amplitude + np.abs(self.amplitude* 0.2)):
                        # 발화 크기체크
                        await bert(model, idx-1)
                    elif "안녕" in text:
                        # 텍스트 매칭
                        texts[idx-1][3] = 1
                        await bert(model, idx-1)
                    else:
                        # 음성 메타로 판단하기 위해서, 동기화 단계 진행
                        pass
                    
                    #arr.append(msg["alternatives"][0]["text"])
                    #print(model.encode(msg["alternatives"][0]["text"]))
                    #print(arr)
                    #print("final ended with " + msg["alternatives"][0]["text"] + "\n")

        async def analyzer(msg):
                        
            y, sr = librosa.load(filename, sr = 32000)

            edited_data = await split_wav(y, 32000, msg["start_at"], msg["start_at"]+msg["duration"])
            
            stft = librosa.stft(edited_data, n_fft = 1600, hop_length = 400)
        
            spectrogram = np.abs(stft)

            log_spectrogram = librosa.amplitude_to_db(spectrogram)

            # speech_amplitude = log_spectrogram.mean(axis=0).mean(axis=0)
            # self.amplitude = (self.amplitude * (msg["seq"]-1) + speech_amplitude) / msg["seq"]

            # print("log_spectrogram: \n", log_spectrogram)
            # print()
            # print("발화 크기: ", speech_amplitude)
            # print("평균 발화 크기: ", self.amplitude)

            return log_spectrogram.mean(axis=0).mean(axis=0)

        async def split_wav(data, sample_rate, start, end):
            start *= sample_rate
            end *= sample_rate
            start = int(start /1000)
            end = int(end / 1000)
            return data[start:end]
            # 3초부터 21초 까지의 데이터만 추출

        async def bert(model, idx):
            print("=====BERT 진입======")
            print("["+texts[idx][1] + "]을 ai 분류기에 투입")
            embedd = model.encode(texts[idx][1])
            print("문장 임베딩 결과 : " + str(embedd[0]))

        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
            model = SentenceTransformer('all-mpnet-base-v2')
            await asyncio.gather(
                streamer(websocket),
                transcriber(websocket, model)
                #analyzer(websocket)
            )


       
            
            
if __name__ == "__main__":
    CLIENT_ID = "NpLwRFyBfxWGUPd3OsZ7"
    CLIENT_SECRET = "SSmusUj2y_CaxXU0F3QaWszLaHH9fCUB5triQRbY"
    
    client = VITOOpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    fname = "test_voice.wav"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.streaming_transcribe(fname))
    loop.close
