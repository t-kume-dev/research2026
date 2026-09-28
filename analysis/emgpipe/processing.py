"""EMG の前処理: バンドパス → 全波整流 → 低域通過で包絡線。

いまはオフライン解析用にゼロ位相（filtfilt）で処理している。リアルタイム提示に進むときは
因果フィルタ（sosfilt に状態を持たせる）に差し替える必要がある。
"""

from __future__ import annotations

import numpy as np
from scipy import signal

BANDPASS_HZ = (20.0, 450.0)   # 表面 EMG の標準的な帯域（SENIAM / ISEK の推奨範囲内）
ENVELOPE_LP_HZ = 6.0          # 包絡線の平滑化。力みの時間変化を見るには 3〜10 Hz 程度
MVC_WINDOW_S = 0.5            # MVC 値は包絡線の 0.5 秒移動平均の最大値とする


def bandpass(x: np.ndarray, fs: float, band=BANDPASS_HZ, order: int = 4) -> np.ndarray:
    hi = min(band[1], 0.45 * fs)
    sos = signal.butter(order, [band[0], hi], btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)


def envelope(x: np.ndarray, fs: float, lp_hz: float = ENVELOPE_LP_HZ) -> np.ndarray:
    """生 EMG から線形包絡線を作る。単位は入力と同じ（Delsys API は V、疑似信号は mV）。"""
    rect = np.abs(bandpass(x, fs))
    sos = signal.butter(4, lp_hz, btype="lowpass", fs=fs, output="sos")
    return np.maximum(signal.sosfiltfilt(sos, rect), 0.0)


def moving_mean(x: np.ndarray, fs: float, window_s: float) -> np.ndarray:
    n = max(1, int(round(window_s * fs)))
    if x.size < n:
        return np.array([x.mean()]) if x.size else x
    c = np.cumsum(np.insert(x, 0, 0.0))
    return (c[n:] - c[:-n]) / n
