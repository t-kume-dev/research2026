"""マウスのイベント（動き・クリック）を時刻付きで記録する（M2-2）。

Windows の Raw Input で、マウスから届いた生の移動量（dx, dy）とボタンの押し・離しを受け取る。
FPS のゲームはカーソルを画面中央に固定するので、カーソル位置（GetCursorPos）では動きが取れない。
Raw Input は、ゲームが前面にあっても裏で受け取れる（RIDEV_INPUTSINK）。

時刻は time.perf_counter()。EMG の記録（recording.py）も同じ時計なので、あとで合わせられる（M2-3）。
1 行 = 1 回の通知。列は events.csv の COLUMNS を見る。
"""

from __future__ import annotations

import csv
import ctypes
import json
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

COLUMNS = ["t_s", "dx", "dy", "button", "cursor_x", "cursor_y", "abs"]

# usButtonFlags → 名前（押し: down / 離し: up）
BUTTONS = {
    0x0001: "L_down", 0x0002: "L_up",
    0x0004: "R_down", 0x0008: "R_up",
    0x0010: "M_down", 0x0020: "M_up",
    0x0040: "X1_down", 0x0080: "X1_up",
    0x0100: "X2_down", 0x0200: "X2_up",
}
MOUSE_MOVE_ABSOLUTE = 0x0001  # リモートデスクトップなどでは絶対座標で届く


@dataclass
class Events:
    t: np.ndarray          # [s] 記録開始からの時刻
    dx: np.ndarray
    dy: np.ndarray
    button: list[str]      # "" ならボタンなし
    cursor: np.ndarray     # (n, 2) 画面上のカーソル位置
    meta: dict

    @property
    def clicks(self) -> np.ndarray:
        """左クリック（押した瞬間）の時刻。"""
        return np.array([t for t, b in zip(self.t, self.button) if b == "L_down"])

    @property
    def path(self) -> np.ndarray:
        """生の移動量を足し合わせた軌跡（カウント）。(n, 2)"""
        return np.column_stack([np.cumsum(self.dx), np.cumsum(self.dy)])

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            for i in range(len(self.t)):
                w.writerow([f"{self.t[i]:.6f}", int(self.dx[i]), int(self.dy[i]), self.button[i],
                            int(self.cursor[i, 0]), int(self.cursor[i, 1]), int(self.meta.get("absolute", False))])
        path.with_suffix(".json").write_text(json.dumps(self.meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Events":
        path = Path(path)
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        meta_p = path.with_suffix(".json")
        meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        return cls(np.array([float(r["t_s"]) for r in rows]),
                   np.array([int(r["dx"]) for r in rows]),
                   np.array([int(r["dy"]) for r in rows]),
                   [r["button"] for r in rows],
                   np.array([[int(r["cursor_x"]), int(r["cursor_y"])] for r in rows]).reshape(-1, 2),
                   meta)


def summarize(ev: Events) -> dict:
    """記録の概要。移動の通知の間隔から、マウスの報告レート（ポーリングレート）を見積もる。"""
    move = (ev.dx != 0) | (ev.dy != 0)
    tm = ev.t[move]
    gaps = np.diff(tm) if tm.size > 1 else np.zeros(0)
    # 動かしている最中（間隔 20 ms 未満）だけで見る。止まっている間を混ぜないため
    busy = gaps[gaps < 0.02]
    return {
        "duration_s": float(ev.t[-1]) if ev.t.size else 0.0,
        "n_events": int(ev.t.size),
        "n_moves": int(move.sum()),
        "n_left_clicks": int(ev.clicks.size),
        "median_interval_ms": float(np.median(busy) * 1e3) if busy.size else float("nan"),
        "rate_hz": float(1 / np.median(busy)) if busy.size else float("nan"),
        "p99_interval_ms": float(np.percentile(busy, 99) * 1e3) if busy.size else float("nan"),
    }


def print_summary(s: dict) -> None:
    print(f"  長さ          {s['duration_s']:.1f} s")
    print(f"  通知の数      {s['n_events']}（うち移動 {s['n_moves']}）")
    print(f"  左クリック    {s['n_left_clicks']} 回")
    print(f"  移動の間隔    中央値 {s['median_interval_ms']:.2f} ms（約 {s['rate_hz']:.0f} Hz）、"
          f"99% 点 {s['p99_interval_ms']:.2f} ms")


# ---------------------------------------------------------------- Windows Raw Input

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", wintypes.USHORT), ("usUsage", wintypes.USHORT),
                ("dwFlags", wintypes.DWORD), ("hwndTarget", wintypes.HWND)]


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [("dwType", wintypes.DWORD), ("dwSize", wintypes.DWORD),
                ("hDevice", wintypes.HANDLE), ("wParam", wintypes.WPARAM)]


# RAWMOUSE は usFlags のあと 4 バイト境界で union が始まる。上の並びだと位置がずれるので明示する
class _RAWMOUSE(ctypes.Structure):
    class _U(ctypes.Structure):
        _fields_ = [("usButtonFlags", wintypes.USHORT), ("usButtonData", wintypes.USHORT)]
    _fields_ = [("usFlags", wintypes.USHORT), ("_pad", wintypes.USHORT), ("u", _U),
                ("ulRawButtons", wintypes.ULONG), ("lLastX", wintypes.LONG), ("lLastY", wintypes.LONG),
                ("ulExtraInformation", wintypes.ULONG)]


class RAWINPUT(ctypes.Structure):
    _fields_ = [("header", RAWINPUTHEADER), ("mouse", _RAWMOUSE)]


WM_INPUT = 0x00FF
RID_INPUT = 0x10000003
RIM_TYPEMOUSE = 0
RIDEV_INPUTSINK = 0x00000100
HWND_MESSAGE = wintypes.HWND(-3)
PM_REMOVE = 0x0001
QS_ALLINPUT = 0x04FF


def record_events(duration: float, progress: bool = True, stop: "threading.Event | None" = None,
                  ready: "threading.Event | None" = None) -> Events:
    """duration 秒ぶん、マウスのイベントを記録する。Ctrl+C で早めに止められる。

    筋電と同時に取るとき（play）は別スレッドで動かす。stop が立ったら止まり、
    ready は受け取りの準備（Raw Input の登録）ができたら立てる。ウィンドウは呼んだスレッドで作る。
    """
    if sys.platform != "win32":
        raise RuntimeError("マウスの記録は Windows だけで動きます")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                       wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
    user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPVOID,
                                       ctypes.POINTER(wintypes.UINT), wintypes.UINT]
    user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT,
                                    wintypes.UINT, wintypes.UINT]
    user32.MsgWaitForMultipleObjects.argtypes = [wintypes.DWORD, wintypes.LPVOID, wintypes.BOOL,
                                                 wintypes.DWORD, wintypes.DWORD]

    # 見えないウィンドウ（メッセージ専用）を作って、そこに WM_INPUT を届けてもらう
    hwnd = user32.CreateWindowExW(0, "STATIC", "emgpipe-events", 0, 0, 0, 0, 0,
                                  HWND_MESSAGE, None, None, None)
    if not hwnd:
        raise OSError(ctypes.get_last_error(), "ウィンドウを作れませんでした")
    dev = RAWINPUTDEVICE(0x01, 0x02, RIDEV_INPUTSINK, hwnd)  # Generic Desktop / Mouse
    if not user32.RegisterRawInputDevices(ctypes.byref(dev), 1, ctypes.sizeof(dev)):
        raise OSError(ctypes.get_last_error(), "Raw Input を登録できませんでした")
    if ready is not None:
        ready.set()

    t_list: list[float] = []
    dx_l: list[int] = []
    dy_l: list[int] = []
    btn_l: list[str] = []
    cur_l: list[tuple[int, int]] = []
    absolute = False
    last_abs: tuple[int, int] | None = None

    buf = RAWINPUT()
    size = wintypes.UINT(ctypes.sizeof(buf))
    pt = wintypes.POINT()
    msg = wintypes.MSG()

    started = datetime.now().isoformat(timespec="seconds")
    t0 = time.perf_counter()
    t0_wall = time.time()  # KovaaK's などの壁時計の時刻と合わせるため、同じ瞬間の値を残す
    last_print = -1
    try:
        while (now := time.perf_counter() - t0) < duration and not (stop is not None and stop.is_set()):
            user32.MsgWaitForMultipleObjects(0, None, False, 50, QS_ALLINPUT)
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                if msg.message != WM_INPUT:
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                    continue
                t = time.perf_counter() - t0
                size.value = ctypes.sizeof(buf)
                n = user32.GetRawInputData(msg.lParam, RID_INPUT, ctypes.byref(buf), ctypes.byref(size),
                                           ctypes.sizeof(RAWINPUTHEADER))
                user32.DefWindowProcW(msg.hWnd, msg.message, msg.wParam, msg.lParam)
                if n == 0xFFFFFFFF or buf.header.dwType != RIM_TYPEMOUSE:
                    continue
                m = buf.mouse
                x, y = m.lLastX, m.lLastY
                if m.usFlags & MOUSE_MOVE_ABSOLUTE:
                    # 絶対座標（0〜65535）で届いたときは、前回との差を移動量にする
                    absolute = True
                    dx, dy = (0, 0) if last_abs is None else (x - last_abs[0], y - last_abs[1])
                    last_abs = (x, y)
                else:
                    dx, dy = x, y
                flags = m.u.usButtonFlags
                names = [name for bit, name in BUTTONS.items() if flags & bit]
                user32.GetCursorPos(ctypes.byref(pt))
                # 1 回の通知に移動とボタンが両方入ることがある。ボタンごとに行を分け、移動は最初の行に付ける
                for i, b in enumerate(names or [""]):
                    t_list.append(t)
                    dx_l.append(dx if i == 0 else 0)
                    dy_l.append(dy if i == 0 else 0)
                    btn_l.append(b)
                    cur_l.append((pt.x, pt.y))
            if progress and int(now) != last_print:
                last_print = int(now)
                clicks = btn_l.count("L_down")
                print(f"\r  記録中 {last_print:>3d} / {duration:.0f} s   左クリック {clicks} 回", end="", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        dev.dwFlags = 0x00000001  # RIDEV_REMOVE
        dev.hwndTarget = None
        user32.RegisterRawInputDevices(ctypes.byref(dev), 1, ctypes.sizeof(dev))
        user32.DestroyWindow(hwnd)
        if progress:
            print()

    meta = {"started": started, "duration_s": round(time.perf_counter() - t0, 3), "clock": "time.perf_counter",
            "t0_perf_counter": t0, "t0_unix": t0_wall,
            "t0_local": datetime.fromtimestamp(t0_wall).isoformat(timespec="milliseconds"),
            "absolute": absolute,
            "note": "dx, dy はマウスの生のカウント（画面のピクセルではない）。下向きが +y"}
    return Events(np.array(t_list), np.array(dx_l, dtype=int), np.array(dy_l, dtype=int), btn_l,
                  np.array(cur_l, dtype=int).reshape(-1, 2), meta)


# ---------------------------------------------------------------- 図

def plot_events(ev: Events, out: Path | None = None) -> None:
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Meiryo", "sans-serif"]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [1, 1.6]})
    p = ev.path
    a1.plot(p[:, 0], -p[:, 1], color="#6B6B6B", lw=0.8)
    if ev.clicks.size:
        idx = np.searchsorted(ev.t, ev.clicks)
        idx = np.clip(idx, 0, len(p) - 1)
        a1.scatter(p[idx, 0], -p[idx, 1], color="#D9822B", s=18, zorder=3, label="左クリック")
        a1.legend(loc="best", frameon=False)
    a1.set_title("マウスの軌跡（生の移動量を足し合わせたもの）")
    a1.set_xlabel("横 [カウント]")
    a1.set_ylabel("縦 [カウント]")
    a1.set_aspect("equal", adjustable="datalim")

    # 速さ：10 ms ごとの移動量
    bin_s = 0.01
    edges = np.arange(0, (ev.t[-1] if ev.t.size else 0) + bin_s, bin_s)
    if edges.size > 1:
        dist = np.hypot(ev.dx, ev.dy).astype(float)
        speed, _ = np.histogram(ev.t, bins=edges, weights=dist)
        a2.plot(edges[:-1], speed / bin_s / 1000, color="#1A1A1A", lw=0.7)
    for c in ev.clicks:
        a2.axvline(c, color="#D9822B", lw=0.8, alpha=0.8)
    a2.set_title("マウスの速さと、左クリックの時刻（縦線）")
    a2.set_xlabel("時刻 [s]")
    a2.set_ylabel("速さ [千カウント/s]")
    for a in (a1, a2):
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.tight_layout()
    if out:
        fig.savefig(out, dpi=200)
        print(f"  図: {out}")
    else:
        plt.show()
