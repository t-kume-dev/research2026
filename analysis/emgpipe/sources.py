"""データ取得元。

実機（Delsys API / AeroPy）と疑似信号の2つを同じインターフェースで扱う。
記録・正規化の側はどちらが相手かを知らなくてよい。

    source.connect()          # 接続とセンサ検出（1回だけ）
    source.channels           # list[ChannelInfo]
    source.start(task)        # 記録開始。task は疑似信号側だけが使う
    source.read()             # dict[チャネル名, np.ndarray]。前回呼び出し以降の新着サンプル
    source.stop()
    source.close()
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ANALYSIS_DIR = Path(__file__).resolve().parents[1]


@dataclass
class ChannelInfo:
    name: str        # 例 "S1_EMG1"。ファイル内のキーにもなる
    type: str        # "EMG", "ACC", ... Delsys API の Type をそのまま入れる
    fs: float        # サンプリング周波数 [Hz]
    sensor: str      # センサの表示名
    guid: str = ""   # Delsys API のチャネル GUID


class Source:
    channels: list[ChannelInfo]

    def connect(self) -> None: ...
    def start(self, task: str = "") -> None: ...
    def read(self) -> dict[str, np.ndarray]: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...

    @property
    def emg_channels(self) -> list[ChannelInfo]:
        return [c for c in self.channels if c.type == "EMG"]


# ---------------------------------------------------------------------------
# 疑似信号
# ---------------------------------------------------------------------------

# task ごとの各チャネルの活動レベル（MVC 比）。ch0 = 伸筋側、ch1 = 屈筋側を想定し、
# クロストークとして相手側にも少し漏れるようにしてある
_SIM_ACTIVATION = {
    "rest": (0.03, 0.02),
    "wrist_extension": (1.0, 0.30),
    "wrist_flexion": (0.25, 1.0),
    "grip": (0.7, 0.8),
}


class SimulatedSource(Source):
    """EMG らしい疑似信号を出す。機材なしでパイプライン全体を動かすため。

    帯域制限した白色雑音を活動レベルで振幅変調したもの。チャネルごとに電極ゲインを
    変えてあるので、正規化しないと比較できないことも再現される。
    task を指定しない（自由記録）ときは、ランダムなバースト（クリック相当）を入れる。
    """

    def __init__(self, n_channels: int = 2, fs: float = 1925.926,
                 realtime: bool = True, seed: int | None = None):
        self.fs = fs
        self.realtime = realtime
        self.rng = np.random.default_rng(seed)
        self.gain_mv = self.rng.uniform(0.2, 1.5, n_channels)  # 100%MVC 時の振幅 [mV]
        self.noise_mv = 0.005
        self.channels = [
            ChannelInfo(f"S{i + 1}_EMG1", "EMG", fs, f"Simulated Avanti {i + 1}")
            for i in range(n_channels)
        ]
        self._task = ""
        self._t0 = 0.0
        self._emitted = 0
        self._bursts: list[tuple[float, float, float]] = []

    def connect(self) -> None:
        pass

    def start(self, task: str = "") -> None:
        self._task = task
        self._t0 = time.perf_counter()
        self._emitted = 0
        self._bursts = []

    def read(self, n: int | None = None) -> dict[str, np.ndarray]:
        """realtime=True なら経過時間分、False なら n サンプル（既定 0.1 秒分）を返す。"""
        if self.realtime:
            due = int((time.perf_counter() - self._t0) * self.fs)
            n = due - self._emitted
            if n <= 0:
                time.sleep(0.005)
                return {}
        elif n is None:
            n = int(self.fs * 0.1)
        t = (self._emitted + np.arange(n)) / self.fs
        self._emitted += n
        act = self._activation(t)
        out = {}
        for i, ch in enumerate(self.channels):
            carrier = self.rng.standard_normal(n)
            sig = self.gain_mv[i] * act[i] * carrier + self.noise_mv * self.rng.standard_normal(n)
            out[ch.name] = sig
        return out

    def _activation(self, t: np.ndarray) -> np.ndarray:
        n_ch = len(self.channels)
        if self._task:
            base = _SIM_ACTIVATION.get(self._task, (0.1,) * n_ch)
            levels = np.array([base[i % len(base)] for i in range(n_ch)])
            if self._task == "rest":
                return np.repeat(levels[:, None], t.size, axis=1)
            # 収縮課題は 0.3 秒かけて立ち上げる
            ramp = np.clip(t / 0.3, 0, 1)
            return levels[:, None] * ramp[None, :]
        # 自由記録: 保持活動 + ランダムなバースト
        act = np.full((n_ch, t.size), 0.05)
        while not self._bursts or self._bursts[-1][0] < t[-1] + 1:
            last = self._bursts[-1][0] if self._bursts else 0.0
            self._bursts.append((last + self.rng.uniform(0.4, 1.2),
                                 self.rng.uniform(0.05, 0.15), self.rng.uniform(0.2, 0.6)))
        for start, dur, amp in self._bursts:
            m = (t >= start) & (t < start + dur)
            if m.any():
                act[:, m] += amp * np.array([1.0, 0.6] * n_ch)[:n_ch, None]
        return act

    def stop(self) -> None:
        pass

    def close(self) -> None:
        pass


# ---------------------------------------------------------------------------
# 実機: Delsys API (AeroPy)
# ---------------------------------------------------------------------------

def _load_credentials() -> tuple[str, str]:
    """キーとライセンスを環境変数か analysis/delsys_license.json から読む。

    どちらも Delsys から発行される文字列。リポジトリには入れない（.gitignore 済み）。
    """
    key = os.environ.get("DELSYS_KEY", "")
    lic = os.environ.get("DELSYS_LICENSE", "")
    path = ANALYSIS_DIR / "delsys_license.json"
    if (not key or not lic) and path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        key, lic = d.get("key", key), d.get("license", lic)
    if not key or not lic:
        raise RuntimeError(
            "Delsys API のキーとライセンスが見つかりません。環境変数 DELSYS_KEY / DELSYS_LICENSE を"
            f"設定するか、{path} に {{\"key\": \"...\", \"license\": \"...\"}} を置いてください。")
    return key, lic


class DelsysSource(Source):
    """Trigno Discover 世代（Trigno Base / Lite / Centro）用。Delsys 公式 Python サンプルの手順に従う。

    必要なもの:
      - pythonnet（pip install pythonnet）
      - DelsysAPI.dll（Delsys の Example-Applications リポジトリの Python/resources/ にある）
        既定の置き場所は analysis/resources/DelsysAPI.dll。環境変数 DELSYS_API_DLL で変更可
      - Delsys 発行のキーとライセンス（_load_credentials 参照）
    Trigno Discover を起動したままだとベースを掴めないので、閉じてから使う。
    """

    def __init__(self, emg_only: bool = True, dll_path: str | None = None):
        self.emg_only = emg_only
        self.dll_path = Path(dll_path or os.environ.get("DELSYS_API_DLL")
                             or ANALYSIS_DIR / "resources" / "DelsysAPI.dll")
        self.channels = []
        self.base = None

    def connect(self) -> None:
        if not self.dll_path.exists():
            raise RuntimeError(f"DelsysAPI.dll が見つかりません: {self.dll_path}")
        from pythonnet import load
        load("coreclr")
        import clr
        clr.AddReference(str(self.dll_path.with_suffix("")))
        clr.AddReference("System.Collections")
        from Aero import AeroPy

        key, lic = _load_credentials()
        self.base = AeroPy()
        self.base.ValidateBase(key, lic)
        print(f"受信機: {self.base.GetTrignoReceiverType()}")

        self._scan()
        self.base.SelectAllSensors()
        self.channels = self._list_channels()
        if not self.channels:
            raise RuntimeError("チャネルが1つも見つかりません。センサが起動・ペアリング済みか確認してください。")

        self.base.Configure()
        if not self.base.IsPipelineConfigured():
            raise RuntimeError(f"Configure に失敗しました（状態: {self.base.GetPipelineState()}）")

    def _scan(self) -> None:
        # ScanSensors の引数は API のバージョンで異なる。
        # 新しいもの: ScanSensors(use_ant, device_types)。device_types は Trigno Link 用で、使わないなら空
        try:
            self.base.ScanSensors().Result
        except TypeError:
            from System import String
            from System.Collections.Generic import List
            self.base.ScanSensors(False, List[String]()).Result

    def _list_channels(self) -> list[ChannelInfo]:
        chans = []
        for idx, s in enumerate(self.base.GetSensors()):
            pair = self.base.GetSensorPairNumber(idx)
            mode = self.base.GetCurrentSensorMode(idx)
            print(f"センサ ({pair}) {s.FriendlyName}  mode: {mode}")
            for c in self.base.GetSensorChannelInfo(idx):
                ctype, cname = str(c["Type"]), str(c["Name"])
                fs = float(c["Sample Rate"])
                print(f"  - {cname} [{ctype}] {fs:.3f} Hz")
                if ctype == "SkinCheck" or (self.emg_only and ctype != "EMG"):
                    continue
                safe = cname.replace(" ", "")
                chans.append(ChannelInfo(f"S{pair}_{safe}", ctype, fs, str(s.FriendlyName), str(c["Guid"])))
        return chans

    def start(self, task: str = "") -> None:
        # 2回目以降は Armed のまま Start し直せる（公式サンプルと同じ扱い）
        self.base.Start(False)

    def read(self) -> dict[str, np.ndarray]:
        if not self.base.CheckDataQueue():
            time.sleep(0.002)
            return {}
        data = self.base.PollDataByString()
        return {ch.name: np.fromiter(data[ch.guid], dtype=float)
                for ch in self.channels if data.ContainsKey(ch.guid)}

    def stop(self) -> None:
        self.base.Stop()

    def close(self) -> None:
        self.base = None


def make_source(kind: str, **kw) -> Source:
    if kind == "sim":
        return SimulatedSource(**kw)
    if kind == "delsys":
        return DelsysSource(**kw)
    raise ValueError(f"未知のソース: {kind}")
