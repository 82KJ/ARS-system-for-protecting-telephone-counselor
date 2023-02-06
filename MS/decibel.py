import librosa.display
import matplotlib.pyplot as plt
import librosa
import scipy.signal as signal
import numpy as np
from io import DEFAULT_BUFFER_SIZE

audio_path = 'test_voice.wav'

audio_sample, sampling_rate = librosa.load(audio_path, sr=None)

window = signal.hann
hop_length = 512     # 전체 frame 수 = 수가 클수록 섬세한 작업
win_length = 512
n_fft = 2048         # frame 하나당 sample 수


S = np.abs(librosa.stft(audio_sample, n_fft=n_fft,
           hop_length=hop_length, win_length=win_length, window=window))
pitches, magnitudes = librosa.piptrack(S=S, sr=sampling_rate)

shape = np.shape(pitches)
nb_samples = shape[0]
nb_windows = shape[1]

pitches_list = []

for i in range(0, nb_windows):
    index = magnitudes[:, i].argmax()
    pitch = pitches[index, i]
    pitches_list.append(pitch)

#print('pitches_list >> ', pitches_list)
#print('len(pitches_list) >> ', len(pitches_list))


log_spectrogram = librosa.amplitude_to_db(S)

shape = np.shape(log_spectrogram)
nb_samples = shape[0]
nb_windows = shape[1]

dB_list = []

for i in range(0, nb_windows):
    index = magnitudes[:, i].argmax()
    pitch = log_spectrogram[index, i]
    dB_list.append(pitch)

print('dB_list >> ', dB_list)
print('len(dB_list) >> ', len(dB_list))

average = sum(dB_list) / len(dB_list)
print(average)


# FFT 결과를 plot

# normalize_function
min_level_db = -100

def _normalize(S):
    return np.clip((S-min_level_db)/(-min_level_db), 0, 1)


mag_db = librosa.amplitude_to_db(S)
mag_n = _normalize(mag_db)

print('np.max(dB_list) >> ', np.max(dB_list),'np.min(dB_list) >> ', np.min(dB_list))

plt_pitch = pitches_list
plt_dB = dB_list

plt.figure()
plt.subplot(2, 1, 1)
plt.plot(plt_dB)
plt.xlabel('time')
plt.ylabel('dB')
plt.show()

