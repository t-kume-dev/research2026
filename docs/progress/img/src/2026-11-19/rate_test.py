"""マウスの報告レートを、ウィンドウが前面のときと裏のときで比べる確認用スクリプト。

python rate_test.py front  … 小さな窓を出す。窓をクリックして前面にしたまま 10 秒マウスを動かす
python rate_test.py back   … 窓を出さず裏で受ける（今の events と同じ）。10 秒マウスを動かす
"""
import ctypes
import sys
import time
from ctypes import wintypes

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
mode = sys.argv[1] if len(sys.argv) > 1 else "front"
DURATION = 10.0
if "--import-emgpipe" in sys.argv:
    sys.path.insert(0, r"C:\Users\akash\Documents\lab\research2026\analysis")
    import emgpipe.__main__  # noqa: F401
    DURATION = 3.0
if "--short" in sys.argv:
    DURATION = 3.0

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.CreateWindowExW.restype = wintypes.HWND
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPVOID,
                                   ctypes.POINTER(wintypes.UINT), wintypes.UINT]
user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT,
                                wintypes.UINT, wintypes.UINT]
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_ssize_t


class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", wintypes.USHORT), ("usUsage", wintypes.USHORT),
                ("dwFlags", wintypes.DWORD), ("hwndTarget", wintypes.HWND)]


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [("dwType", wintypes.DWORD), ("dwSize", wintypes.DWORD),
                ("hDevice", wintypes.HANDLE), ("wParam", wintypes.WPARAM)]


class RAWMOUSE(ctypes.Structure):
    _fields_ = [("usFlags", wintypes.USHORT), ("_pad", wintypes.USHORT),
                ("usButtonFlags", wintypes.USHORT), ("usButtonData", wintypes.USHORT),
                ("ulRawButtons", wintypes.ULONG), ("lLastX", wintypes.LONG), ("lLastY", wintypes.LONG),
                ("ulExtraInformation", wintypes.ULONG)]


class RAWINPUT(ctypes.Structure):
    _fields_ = [("header", RAWINPUTHEADER), ("mouse", RAWMOUSE)]


WS_OVERLAPPEDWINDOW_VISIBLE = 0x00CF0000 | 0x10000000
if mode == "front":
    hwnd = user32.CreateWindowExW(0x8, "STATIC", "ここをクリックして前面にしたまま動かす", WS_OVERLAPPEDWINDOW_VISIBLE,
                                  200, 200, 600, 300, None, None, None, None)  # 0x8 = 最前面
    flags = 0
else:
    hwnd = user32.CreateWindowExW(0, "STATIC", "rate-test", 0, 0, 0, 0, 0, wintypes.HWND(-3), None, None, None)
    flags = 0x100  # RIDEV_INPUTSINK
dev = RAWINPUTDEVICE(0x01, 0x02, flags, hwnd)
assert user32.RegisterRawInputDevices(ctypes.byref(dev), 1, ctypes.sizeof(dev))
user32.SetForegroundWindow(hwnd)

buf = RAWINPUT()
size = wintypes.UINT()
msg = wintypes.MSG()
ts, sx, sy = [], 0, 0
print(f"[{mode}] {DURATION:.0f} 秒、マウスを動かし続けてください")
t0 = time.perf_counter()
while time.perf_counter() - t0 < DURATION:
    user32.MsgWaitForMultipleObjects(0, None, False, 50, 0x04FF)
    while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
        if msg.message == 0x00FF:
            t = time.perf_counter()
            size.value = ctypes.sizeof(buf)
            user32.GetRawInputData(msg.lParam, 0x10000003, ctypes.byref(buf), ctypes.byref(size),
                                   ctypes.sizeof(RAWINPUTHEADER))
            if buf.header.dwType == 0 and (buf.mouse.lLastX or buf.mouse.lLastY):
                ts.append(t)
                sx += buf.mouse.lLastX
                sy += buf.mouse.lLastY
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
user32.DestroyWindow(hwnd)

d = np.diff(ts) * 1000
d = d[d < 50]  # 止めていた間は除く
print(f"[{mode}] 移動 {len(ts)} 回、移動量の合計 |dx|+|dy| 相当 ({sx}, {sy})")
if d.size:
    print(f"[{mode}] 間隔 中央値 {np.median(d):.3f} ms（約 {1000 / np.median(d):.0f} Hz）、"
          f"10% 点 {np.percentile(d, 10):.3f} ms")
