import asyncio
import json
import logging
import time
from io import DEFAULT_BUFFER_SIZE

import websockets
from requests import Session
import pyaudio

API_BASE = "https://openapi.vito.ai"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class VITOOpenAPIClient:
    def __init__(self, client_id, client_secret):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.client_id = client_id
        self.client_secret = client_secret
        self._sess = Session()
        self._token = None

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

    async def streaming_transcribe(self, config=None):
        if config is None:
            config = dict(
                sample_rate="16000",  # sample rate 설정 -> test 필요
                encoding="LINEAR16",
                use_itn="true",
                use_disfluency_filter="false",
                use_profanity_filter="false",
            )

        STREAMING_ENDPOINT = "wss://{}/v1/transcribe:streaming?{}".format(
            API_BASE.split("://")[1], "&".join(map("=".join, config.items()))
        )
        conn_kwargs = dict(extra_headers={"Authorization": "bearer " + self.token})

        async def streamer(websocket):
            audio = pyaudio.PyAudio()

            def stream_callback(in_data, frame_count, time_info, status):
                asyncio.ensure_future(websocket.send(in_data))
                return (in_data, pyaudio.paContinue)

            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=stream_callback)

        async def transcriber(websocket):
            async for msg in websocket:
                msg = json.loads(msg)
                print(msg)
                if msg["final"]:
                    print(str(msg["seq"]) + " : " + msg["alternatives"][0]["text"])
                    print("시작 시간 :" + str(msg["start_at"]) + ", 걸린 시간 : " + str(msg["duration"]))

        async with websockets.connect(STREAMING_ENDPOINT, **conn_kwargs) as websocket:
            await asyncio.gather(
                streamer(websocket),
                transcriber(websocket),
            )


if __name__ == "__main__":

    # 바꿔주세요~~
    CLIENT_ID = "NFJOMvUAYfhQiZA8ZQit"
    CLIENT_SECRET = "XJ2pgsDOaR8RilnUjvHKwaF9_WbXVjwcsfPMHx5L"

    client = VITOOpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.streaming_transcribe())
