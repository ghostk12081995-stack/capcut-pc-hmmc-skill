"""Automated CapCut PC Export + TikTok 1080p60 Anti-Compression Mastering.

Must be invoked on the interactive desktop (e.g. via Win32_Process.Create with
pythonw.exe).
"""

import ctypes
from ctypes import wintypes
import os
import subprocess
import sys
import time
import winreg
import numpy as np
from PIL import ImageGrab

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    user32.SetProcessDPIAware()

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def get_capcut_windows():
    wins = []

    def cb(hwnd, lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        if "CapCut" in buf.value and "Qt622QWindowIcon" in cls.value:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            vis = user32.IsWindowVisible(hwnd)
            ic = user32.IsIconic(hwnd)
            if vis or ic:
                wins.append(
                    (
                        hwnd,
                        buf.value,
                        cls.value,
                        vis,
                        ic,
                        (rect.left, rect.top, rect.right, rect.bottom),
                    )
                )
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return wins


def force_focus(hwnd, maximize=True):
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)
        time.sleep(0.3)
    if maximize:
        user32.ShowWindow(hwnd, 3)
        time.sleep(0.2)
    user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)
    fg = user32.GetForegroundWindow()
    fg_tid = user32.GetWindowThreadProcessId(fg, None)
    cur_tid = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(cur_tid, fg_tid, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(cur_tid, fg_tid, False)
    time.sleep(0.3)
    user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)


def hw_move(x, y):
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    nx = int(x * 65535 / screen_w)
    ny = int(y * 65535 / screen_h)
    user32.SetCursorPos(int(x), int(y))
    user32.mouse_event(0x8001, nx, ny, 0, 0)


def hw_move_and_click(x, y):
    hw_move(x, y)
    time.sleep(0.25)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.08)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def set_registry_export_path(export_dir):
    os.makedirs(export_dir, exist_ok=True)
    reg_val = export_dir.replace("\\", "/")
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Bytedance\CapCut\Modules\Export",
        0,
        winreg.KEY_SET_VALUE,
    )
    winreg.SetValueEx(key, "ExportPath", 0, winreg.REG_SZ, reg_val)
    winreg.CloseKey(key)


def build_tiktok_1080p60_sharp(master_mp4, output_mp4):
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        master_mp4,
        "-vf",
        "scale=1080:1920:flags=lanczos,unsharp=3:3:0.35:3:3:0.0",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-level:v",
        "4.2",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "fast",
        "-crf",
        "15",
        "-maxrate",
        "20M",
        "-bufsize",
        "40M",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-colorspace",
        "bt709",
        "-c:a",
        "aac",
        "-b:a",
        "320k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        output_mp4,
    ]
    subprocess.run(cmd, check=True)
