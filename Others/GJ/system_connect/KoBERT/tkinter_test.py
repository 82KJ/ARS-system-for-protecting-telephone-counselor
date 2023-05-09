import tkinter as tk
import pyaudio
import websockets
import asyncio
import numpy as np
import logging
from requests import Session
import time
import json

API_BASE = "https://openapi.vito.ai"


# 웹소켓 서버 URL 설정
WEBSOCKET_SERVER_URL = "ws://localhost:8000"

# Pyaudio 설정
CHUNK_SIZE = 1024
SAMPLE_RATE = 44100
RECORD_SECONDS = 5
CHANNELS = 1
FORMAT = pyaudio.paInt16

class App:
    def __init__(self, master, client_id, client_secret):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = Session()
        self._token = None

        self.master = master
        self.is_recording = False
        
        # 녹음 버튼 생성
        self.record_button = tk.Button(master, text="Record", command=self.start_recording)
        self.record_button.pack()
        
        # 녹음 상태 표시 라벨 생성
        self.status_label = tk.Label(master, text="Not recording")
        self.status_label.pack()
        
        # 결과 표시 라벨 생성
        self.result_label = tk.Label(master, text="결과창")
        self.result_label.pack()
        
        # 웹소켓 연결
        self.ws = None
        
        # Pyaudio 초기화
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=SAMPLE_RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK_SIZE)



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


    async def send_stream(self, websocket):
        while self.is_recording:
            data = self.stream.read(CHUNK_SIZE)
            await websocket.send(data)
        
    async def receive_result(self, websocket):
        while self.is_recording:
            result = await websocket.recv()
            msg = json.loads(result)
            #print(msg)
            if msg["final"] :
                print(msg["alternatives"][0]["text"])   
            # 결과를 실시간으로 표시
                self.result_label.config(text=msg["alternatives"][0]["text"])
        
    async def start_websocket(self, config=None):
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

        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
            self.ws = websocket
            await asyncio.gather(
                self.send_stream(websocket), 
                self.receive_result(websocket)
            )

    def update_result_label(self):
        # 결과 표시 라벨 업데이트
        if self.is_recording:
            result = self.result_label["text"] + "."
            self.result_label.config(text=result)
        # 일정 시간 간격으로 업데이트 호출
        self.master.after(500, self.update_result_label)
    
    def start_recording(self):
        self.is_recording = True
        self.status_label.config(text="Recording...")
        
        asyncio.run(self.start_websocket())
        # 녹음 종료
        self.status_label.config(text="Not recording")
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    

CLIENT_ID = "NFJOMvUAYfhQiZA8ZQit"
CLIENT_SECRET = "XJ2pgsDOaR8RilnUjvHKwaF9_WbXVjwcsfPMHx5L"

root = tk.Tk()
app = App(root, CLIENT_ID, CLIENT_SECRET)
root.mainloop()
