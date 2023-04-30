import environ
import os
from pathlib import Path
import time
import requests

class VitoStreamingAPI:
    def __init__(self):
        self.config = dict(
            sample_rate="48000",
            encoding="LINEAR16",
            use_itn="true",
            use_disfluency_filter="false",
            use_profanity_filter="false"
        )

        self.API_BASE = "https://openapi.vito.ai"
        self.STREAMING_ENDPOINT = "wss://{}/v1/transcribe:streaming?{}".format(self.API_BASE.split("://")[1], "&".join(map("=".join, self.config.items())))

        self.client_id, self.client_secret = self.get_client_info()

        self.full_token = None
        self.token = self.get_token()


    def get_client_info(self):
        env = environ.Env(DEBUG=(bool,True))
        BASE_DIR = Path(__file__).resolve().parent.parent

        environ.Env.read_env(
            env_file=os.path.join(BASE_DIR, '.env')
        )

        return env('client_id'), env('client_secret')
    
    def get_token(self):
        if self.full_token is None or self.full_token["expire_at"] < time.time():
            resp = requests.post(
                'https://openapi.vito.ai/v1/authenticate',
                 data={'client_id': self.client_id,
                      'client_secret': self.client_secret}
                )
            
            resp.raise_for_status()
            self.full_token = resp.json()
            return self.full_token["access_token"]
        else:
            return self.token


    



