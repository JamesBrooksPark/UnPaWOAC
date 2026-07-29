import numpy as np
import soundfile as sf
from scipy import signal
import os

C_Hz = 1000
Fs = 44100

# Design low pass filter
order = 4
nyquist = Fs / 2
normalized_cutoff = C_Hz / nyquist
b, a = signal.butter(order, normalized_cutoff, btype='low')

# Create filters subdirectory if it doesn't exist
filter_dir = os.path.join(os.path.dirname(__file__), 'filters')
os.makedirs(filter_dir, exist_ok=True)

# Save filter coefficients
filter_path = os.path.join(filter_dir, 'lowpass_filter.npy')
np.save(filter_path, {'b': b, 'a': a, 'cutoff_Hz': C_Hz, 'Fs': Fs})




