import tkinter as tk
import pyaudio
import wave
import requests
import json
import threading

# GUI 생성
root = tk.Tk()
root.geometry('300x100')

# 버튼 클릭 시 실행되는 함수
def start_recording():
    # 녹음 설정
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "recorded.wav"
    
    # 녹음 스레드 생성 및 시작
    def record():
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    # 스트리밍 스레드 생성 및 시작
    def stream():
        url = 'https://api.vito.ai/v1/speech-to-text'
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzgyMDI1MTksImlhdCI6MTY3ODE4MDkxOSwianRpIjoicDRiMWczNFBVak9odTU3d1ZFYkMiLCJwbGFuIjoiYmFzaWMiLCJzY29wZSI6InNwZWVjaCIsInN1YiI6Ik5GSk9NdlVBWWZoUWlaQThaUWl0In0.exOhBgT7FzRKNFaVNwPjaIx2OO0Tk8xS80KfJ0JF54I',
            'Content-Type': 'audio/wav'
        }
        data = open(WAVE_OUTPUT_FILENAME, 'rb').read()
        response = requests.post(url, headers=headers, data=data)
        result = json.loads(response.content)

        # 결과를 출력
        result_label.configure(text=result['result'])

    record_thread = threading.Thread(target=record)
    stream_thread = threading.Thread(target=stream)

    record_thread.start()
    stream_thread.start()

# 버튼 생성
button = tk.Button(root, text='Record', command=start_recording)
button.pack(pady=20)

# 결과를 출력할 라벨 생성
result_label = tk.Label(root, text='')
result_label.pack()

root.mainloop()
