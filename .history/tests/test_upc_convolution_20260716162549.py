import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from UnPaWOSC.UnPaWOlAC import UnPaWOlAC


def test_upc_convolution_accepts_stereo_input():
    h = np.zeros((2, 64), dtype=np.float32)
    upc = UnPaWOlAC(16, h)

    data = np.random.randn(2, 16).astype(np.float32)
    out = upc.UPC_Convolution(data)

    assert out.shape == (2, 16)
