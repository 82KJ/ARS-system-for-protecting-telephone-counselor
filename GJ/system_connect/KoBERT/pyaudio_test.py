import asyncio
import json
import logging
import time
from io import DEFAULT_BUFFER_SIZE

import pyaudio
import websockets
from requests import Session

import test_model
import librosa
import numpy as np
import keyboard

from kiwipiepy import Kiwi
import make_dict


API_BASE = "https://openapi.vito.ai"

# 초당 16000개의 frame을 3200 frame 단위로 나눠서 전달 --> DEFAULT_BUFFER_SIZE로 수정
# CHUNK = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class VITOOpenAPIClient:
    def __init__(self, client_id, client_secret):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = Session()
        self._token = None

        self.sexual_dict = make_dict.Sexual_dict()
        self.kiwi = Kiwi()

        self.amplitude = 0
        self.tempo = 0

        self.model = test_model.KoBERT()
        self.amplitude_list = np.array([])
        self.exit_cnt = 0

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

    async def streaming_transcribe(self, audio_generator, config=None):
        if config is None:
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
        conn_kwargs = dict(extra_headers={"Authorization": "bearer " + self.token})

        async def make_amplitude_list(data):
            new_data = np.frombuffer(data, dtype=np.int16)
            new_buffer = np.zeros(len(new_data))
            for i in range(len(new_data)):
                if np.isnan(new_data[i]) == False:
                    new_buffer[i] = new_data[i]
            y = librosa.to_mono(new_buffer)

            self.amplitude_list = np.append(self.amplitude_list, y)

        async def streamer(websocket):
            for data in audio_generator:
                
                # 1. 진폭 저장하기
                await make_amplitude_list(data)

                # 2. 동시에 vito로 전달
                await websocket.send(data)

                if keyboard.is_pressed("q"):
                    print("q is pressed")
                    break
            print("탈출이오~")
            await websocket.send("EOS")

        texts = []
        async def transcriber(websocket):
            async for msg in websocket:
                msg = json.loads(msg)
                if msg["final"]:
                    text = msg["alternatives"][0]["text"]
                    idx = msg["seq"]
                    cnt = idx + 1

                    print()
                    print(str(msg["seq"]) + " : " + msg["alternatives"][0]["text"])
                    texts.append([idx, text, (msg["start_at"], msg["start_at"]+msg["duration"]), -1])

                    speech_tempo = len(msg["alternatives"][0]["text"]) * 1000 / msg["duration"]
                    self.tempo = (self.tempo + speech_tempo) / cnt

                    speech_amplitude = analyzer(msg)
                    self.amplitude = (self.amplitude * (cnt-1) + speech_amplitude) / cnt

                    print("발화 속도 : ", speech_tempo)
                    print("평균 발화 속도 : ", self.tempo)
                    print("발화 크기: ", speech_amplitude)
                    print("평균 발화 크기: ", self.amplitude)

                    # 문장 형태소 분리
                    morphs = self.kiwi.tokenize(text)
                    match_flag = False
                    for x in morphs:
                        if self.sexual_dict.match(x.form):
                            print(x,"가 성희롱 사전과 매칭되었습니다.")
                            match_flag = True

                    if match_flag == True:     
                        bert(idx)

        def analyzer(msg):
            edited_data = split_wav(44100, msg["start_at"], msg["start_at"]+msg["duration"])
            stft = librosa.stft(edited_data, n_fft = 1600, hop_length = 400)
            spectrogram = np.abs(stft)
            log_spectrogram = librosa.amplitude_to_db(spectrogram)
    
            return log_spectrogram.mean(axis=0).mean(axis=0)

        def split_wav(sample_rate, start, end):
            start *= sample_rate
            end *= sample_rate
            start = int(start /1000)
            end = int(end / 1000)
            return self.amplitude_list[start:end]
            
        def bert(idx):
            print("=====BERT 진입======")
            print("["+texts[idx][1] + "]을 ai 분류기에 투입")
            self.model.predict(texts[idx][1])                

        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
            await asyncio.gather(
                streamer(websocket),
                transcriber(websocket),
            )

if __name__ == "__main__":
    CLIENT_ID = "NFJOMvUAYfhQiZA8ZQit"
    CLIENT_SECRET = "XJ2pgsDOaR8RilnUjvHKwaF9_WbXVjwcsfPMHx5L"

    client = VITOOpenAPIClient(CLIENT_ID, CLIENT_SECRET)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=4096)
    audio_generator = iter(lambda: stream.read(DEFAULT_BUFFER_SIZE), b"")
    asyncio.run(client.streaming_transcribe(audio_generator))
    stream.stop_stream()
    stream.close()
    p.terminate()

    print("종료합니다")



