import asyncio
import json
import logging
import time
from io import DEFAULT_BUFFER_SIZE

from requests import Session
import websockets

from sentence_transformers import SentenceTransformer

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

                    if "안녕" in text:
                        texts[idx-1][3] = 1
                        await bert(model, idx-1)
                    else:
                        # 음성 메타로 판단하기 위해서, 동기화 단계 진행
                        pass
                    
                    #arr.append(msg["alternatives"][0]["text"])
                    #print(model.encode(msg["alternatives"][0]["text"]))
                    #print(arr)
                    #print("final ended with " + msg["alternatives"][0]["text"] + "\n")

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
            )


if __name__ == "__main__":
    CLIENT_ID = "NFJOMvUAYfhQiZA8ZQit"
    CLIENT_SECRET = "XJ2pgsDOaR8RilnUjvHKwaF9_WbXVjwcsfPMHx5L"

    client = VITOOpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    fname = "test_voice.wav"
    asyncio.run(client.streaming_transcribe(fname))