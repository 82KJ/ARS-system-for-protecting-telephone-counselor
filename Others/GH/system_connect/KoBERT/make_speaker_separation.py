import librosa
import numpy as np
from sklearn.svm import SVC
import joblib

# Load the reference audio file
ref_file1 = "reference_speaker1.wav"
ref_audio1, sr1 = librosa.load(ref_file1, sr=44100, mono=True)

# Load the reference audio file
ref_file2 = "reference_speaker2.wav"
ref_audio2, sr2 = librosa.load(ref_file2, sr=44100, mono=True)

# Load the reference audio file
ref_file3 = "reference_speaker3.wav"
ref_audio3, sr3 = librosa.load(ref_file3, sr=44100, mono=True)

# Load the reference audio file
ref_file4 = "reference_speaker4.wav"
ref_audio4, sr4 = librosa.load(ref_file4, sr=44100, mono=True)

# # Load the reference audio file
# ref_file5 = "reference_speaker5.wav"
# ref_audio5, sr5 = librosa.load(ref_file5, sr=44100, mono=True)

# # Load the reference audio file
# ref_file6 = "reference_speaker6.wav"
# ref_audio6, sr6 = librosa.load(ref_file6, sr=44100, mono=True)

# # Extract MFCC features from the reference audio file
ref_mfccs1 = librosa.feature.mfcc(ref_audio1, sr=sr1, n_mfcc=13)
ref_mfccs2 = librosa.feature.mfcc(ref_audio2, sr=sr2, n_mfcc=13)
ref_mfccs3 = librosa.feature.mfcc(ref_audio3, sr=sr3, n_mfcc=13)
ref_mfccs4 = librosa.feature.mfcc(ref_audio4, sr=sr4, n_mfcc=13)
# ref_mfccs5 = librosa.feature.mfcc(ref_audio5, sr=sr5, n_mfcc=13)
# ref_mfccs6 = librosa.feature.mfcc(ref_audio6, sr=sr6, n_mfcc=13)

ref_mfccs = np.concatenate((ref_mfccs1, ref_mfccs2, ref_mfccs3 ,ref_mfccs4), axis=1)
#print(ref_mfccs.shape)

# Create a label array for the reference audio file
ref_labels1 = np.full((1293,), "positive")
ref_labels2 = np.full((431,), "negative")
ref_labels3 = np.concatenate((ref_labels1,ref_labels2))
#print(ref_labels3.shape)

# # Train a support vector machine (SVM) classification model using the reference MFCC features
model = SVC(kernel='linear', probability=True)
model.fit(ref_mfccs.T, ref_labels3)

joblib.dump(model, "speaker_separation_model.pkl")

# # Load a new audio file to be classified
# new_file = "reference_speaker4.wav"
# new_audio, sr = librosa.load(new_file, sr=44100, mono=True)

# # Extract MFCC features from the new audio fileq
# new_mfccs = librosa.feature.mfcc(new_audio, sr=sr, n_mfcc=13)
# speaker_separation_model = joblib.load('speaker_separation_model.pkl')

# # Classify the new audio file using the trained SVM model
# predicted_label = speaker_separation_model.predict(new_mfccs.T)
# print(predicted_label)

# # Print the predicted label
# if predicted_label == 'speaker':
#     print("The new audio file is from the same speaker as the reference.")
# else:
#     print("The new audio file is from a different speaker than the reference.")
