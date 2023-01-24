# Beat tracking example
import librosa

# 1. Get the file path to an included audio example
filename = "test_voice.wav"


# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
# 여기서 로드 말고 스트리밍으로 바꿔야함.
# y, sr = librosa.load(filename)
sr = librosa.get_samplerate(filename)
stream = librosa.stream(filename, block_length=256,
                        frame_length=2048, hop_length=2048)

for y_block in stream:
    D_block = librosa.stft(y_block, center=False)

# D_block 데시벨 정보가 나옴
print(D_block)
