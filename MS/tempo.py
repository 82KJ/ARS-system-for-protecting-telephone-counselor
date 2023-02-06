import librosa.display
import matplotlib.pyplot as plt
import librosa
import scipy.signal as signal
import numpy as np


class librosa_tempo:
    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.audio_sample, self.sampling_rate = librosa.load(
            audio_path, sr=None)

    def get_tempo(self):
        window = signal.hann
        hop_length = 512
        win_length = 512
        n_fft = 2048

        S = np.abs(librosa.stft(self.audio_sample))
