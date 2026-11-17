"""裏で受けるやり方のまま、3 つの条件を 5 秒ずつ続けて測る。15 秒ずっとマウスを大きく速く動かす。

A: events と同じ（DefWindowProc で返す、前面にする呼び出しなし）
B: DispatchMessage で返す（前面にする呼び出しなし）
C: 見えない窓に SetForegroundWindow を呼んでから、A と同じ
"""
import ctypes
import sys
import time
from ctypes import wintypes

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
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
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND


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


hwnd = user32.CreateWindowExW(0, "STATIC", "phases", 0, 0, 0, 0, 0, wintypes.HWND(-3), None, None, None)
dev = RAWINPUTDEVICE(0x01, 0x02, 0x100, hwnd)  # RIDEV_INPUTSINK
assert user32.RegisterRawInputDevices(ctypes.byref(dev), 1, ctypes.sizeof(dev))

buf = RAWINPUT()
size = wintypes.UINT()
msg = wintypes.MSG()


def run(label, dispatch, seconds=5.0):
    ts = []
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        user32.MsgWaitForMultipleObjects(0, None, False, 50, 0x04FF)
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            if msg.message == 0x00FF:
                t = time.perf_counter()
                size.value = ctypes.sizeof(buf)
                user32.GetRawInputData(msg.lParam, 0x10000003, ctypes.byref(buf), ctypes.byref(size),
                                       ctypes.sizeof(RAWINPUTHEADER))
                if buf.header.dwType == 0 and (buf.mouse.lLastX or buf.mouse.lLastY):
                    ts.append(t)
                if not dispatch:
                    user32.DefWindowProcW(msg.hWnd, msg.message, msg.wParam, msg.lParam)
                    continue
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    d = np.diff(ts) * 1000
    d = d[d < 20]
    med = np.median(d) if d.size else float("nan")
    print(f"  {label}: 移動 {len(ts):6d} 回、間隔 中央値 {med:.3f} ms（約 {1000 / med:.0f} Hz）", flush=True)


print("15 秒、マウスを大きく速く動かし続けてください（3 秒後に始まります）", flush=True)
time.sleep(3)
print("始め", flush=True)
run("A そのまま          ", dispatch=False)
run("B DispatchMessage   ", dispatch=True)
fg_before = user32.GetForegroundWindow()
ok = user32.SetForegroundWindow(hwnd)
fg_after = user32.GetForegroundWindow()
run("C 前面にする呼び出し", dispatch=False)
print(f"  （SetForegroundWindow の戻り値 {ok}、前面の窓が変わったか {fg_before != fg_after}）")
user32.DestroyWindow(hwnd)
