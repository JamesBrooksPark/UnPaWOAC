import numpy as np
from scipy import signal
from scipy.io import wavfile
import os

C_Hz = 1000
Fs = 44100

order = 4
nyquist = Fs / 2
normalized_cutoff = C_Hz / nyquist
b, a = signal.butter(order, normalized_cutoff, btype='low')

filter_dir = os.path.join(os.path.dirname(__file__), 'filters')
os.makedirs(filter_dir, exist_ok=True)

np.save(filter_path, {'b': b, 'a': a, 'cutoff_Hz': C_Hz, 'Fs': Fs})

impulse = np.zeros(2048, dtype=np.float32)
impulse[0] = 1.0
response = signal.lfilter(b, a, impulse)
response /= np.max(np.abs(response))
response_wav = (response * 32767).astype(np.int16)

wav_path = os.path.join(filter_dir, 'lowpass_impulse_response.wav')
wavfile.write(wav_path, Fs, response_wav)




