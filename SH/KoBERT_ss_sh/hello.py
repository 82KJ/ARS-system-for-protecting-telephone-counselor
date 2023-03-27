import io
import os
from google.cloud import speech_v1p1beta1 as speech

# 구글 클라우드 스피치 클라이언트 생성
client = speech.SpeechClient()

# 실시간 스트리밍 구성
streaming_config = speech.StreamingRecognitionConfig(
    config=speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        sample_rate_hertz=16000,
        model="default",
        diarization_config=speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2,
    )
    ),
    interim_results=True,
    single_utterance=True,
    #enable_word_time_offsets=True,
    
    # 반드시 `interim_results`가 True일 때 사용해야 합니다.
    #output_intermediates=True,
)

# 실시간 스트리밍 인식 함수 정의
def recognize_streaming(stream):
    responses = client.streaming_recognize(streaming_config, stream)

    for response in responses:
        for result in response.results:
            for word in result.words:
                print(
                    f"Speaker Tag: {word.speaker_tag}, Word: {word.word}, "
                    f"Start Time: {word.start_time.seconds + word.start_time.nanos * 1e-9}, "
                    f"End Time: {word.end_time.seconds + word.end_time.nanos * 1e-9}"
                )

# # 실시간 음성 스트림을 입력으로 받아와 recognize_streaming() 함수 호출
# with io.BytesIO() as audio_stream:
#     # 여기에 음성 스트림을 넣어주면 됩니다.
#     recognize_streaming(audio_stream)


import io
import pyaudio

# PyAudio 라이브러리를 사용하여 오디오 스트림을 읽어옴
audio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# io.BytesIO 객체 생성
stream_buffer = io.BytesIO()

# 오디오 스트림에서 데이터를 읽어와서 io.BytesIO 객체에 쓰기
while True:
    data = audio_stream.read(1024)
    stream_buffer.write(data)

    # 일정 크기 이상 데이터가 쌓이면 처리
    if stream_buffer.tell() > 1024 * 1024:
        # 여기에서 io.BytesIO 객체에 쌓인 데이터를 처리하는 코드를 작성하면 됩니다.
        # 예를 들어, 서버로 데이터를 전송하거나 로컬 파일에 저장할 수 있습니다.
        recognize_streaming(audio_stream)
        
        # 처리가 끝난 후, io.BytesIO 객체 초기화
        stream_buffer.seek(0)
        stream_buffer.truncate()
