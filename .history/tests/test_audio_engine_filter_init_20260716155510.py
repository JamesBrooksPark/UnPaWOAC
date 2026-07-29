import sys
import types

import numpy as np


def install_stub_modules():
    pyqt6 = types.ModuleType("PyQt6")
    qtcore = types.ModuleType("PyQt6.QtCore")

    class QObject:
        pass

    qtcore.QObject = QObject
    pyqt6.QtCore = qtcore

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = qtcore

    soundfile = types.ModuleType("soundfile")
    soundfile.read = lambda path: (np.array([1.0, 2.0, 3.0]), 44100)
    sys.modules["soundfile"] = soundfile

    pyaudio = types.ModuleType("pyaudio")

    class PyAudio:
        def __init__(self):
            pass

        def terminate(self):
            pass

        def get_device_count(self):
            return 0

        def get_device_info_by_index(self, index):
            return {}

        def get_format_from_width(self, width):
            return 0

        def open(self, *args, **kwargs):
            raise NotImplementedError

    pyaudio.PyAudio = PyAudio
    sys.modules["pyaudio"] = pyaudio


install_stub_modules()

sys.path.append("src")
from AudioEngine.audio_engine import AudioEngine
from UnPaWOSC.UnPaWOlAC import UnPaWOlAC


def test_load_filter_initializes_convolver_instance():
    engine = AudioEngine()
    engine.load_filter("mono", "dummy.wav")

    assert isinstance(engine.UPC, UnPaWOlAC)
    assert hasattr(engine.UPC, "update_filter")
