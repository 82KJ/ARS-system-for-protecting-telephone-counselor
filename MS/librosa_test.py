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

# 3. Run the default beat tracker
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

print('Estimated tempo: {:.2f} beats per minute'.format(tempo))

# 4. Convert the frame indices of beat events into timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
