import librosa.display
import matplotlib.pyplot as plt
import librosa
import scipy.signal as signal
import numpy as np
import scipy.stats


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

        y, sr = librosa.load(self.audio_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr,
                                    aggregate=None)
        prior_lognorm = scipy.stats.lognorm(loc=np.log(120), scale=120, s=1)
        dtempo_lognorm = librosa.beat.tempo(onset_envelope=onset_env, sr=sr,
                                            aggregate=None,
                                            prior=prior_lognorm)
        # print(dtempo_lognorm)

        # 템포가 빠른 기준 어쩌지
        aver = 60
        for i in range(0, len(dtempo_lognorm)):
            if (dtempo_lognorm[i] > aver):
                print(dtempo_lognorm[i])


if __name__ == "__main__":
    audio_path = "test_voice.wav"
    aa = librosa_tempo(audio_path)
    aa.get_tempo()
