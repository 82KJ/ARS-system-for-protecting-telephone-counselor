# Beat tracking example
import librosa

# vito랑 block 사이즈 맞추기
from io import DEFAULT_BUFFER_SIZE

# 1. Get the file path to an included audio example
filename = "test_voice.wav"


# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
# 여기서 로드 말고 스트리밍으로 바꿔야함.
# y, sr = librosa.load(filename)
stream = librosa.stream(filename,
                        block_length=DEFAULT_BUFFER_SIZE,
                        frame_length=4096,
                        hop_length=1024)
for y_block in stream:
    D_block = librosa.stft(y_block, center=False)

print(D_block)
