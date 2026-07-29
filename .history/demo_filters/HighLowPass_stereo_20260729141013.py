import numpy as np
from scipy import signal
from scipy.io import wavfile
import os

C_Hz = 1000
Fs = 44100

order = 4
nyquist = Fs / 2
normalized_cutoff = C_Hz / nyquist
b_low, a_low = signal.butter(order, normalized_cutoff, btype='low')
b_high, a_high = signal.butter(order, normalized_cutoff, btype='high')

filter_dir = os.path.join(os.path.dirname(__file__), 'filters')
os.makedirs(filter_dir, exist_ok=True)

impulse = np.zeros(2048, dtype=np.float32)
impulse[0] = 1.0

response_low = signal.lfilter(b_low, a_low, impulse)
response_high = signal.lfilter(b_high, a_high, impulse)

response_low /= np.max([np.max(np.abs(response_low)),np.max(np.abs(response_low))])
response_wav = (response * 32767).astype(np.int16)

wav_path = os.path.join(filter_dir, 'lowpass_impulse_response.wav')
wavfile.write(wav_path, Fs, response_wav)




