"""Local activity signals. Read raw-input headers only, never key values or text."""

from collections import deque
import ctypes
from ctypes import wintypes
import time

import win32gui
from PySide6.QtCore import QAbstractNativeEventFilter
from PySide6.QtWidgets import QApplication


class RawInputHeader(ctypes.Structure):
    _fields_ = [("kind", wintypes.DWORD), ("size", wintypes.DWORD),
                ("device", wintypes.HANDLE), ("parameter", wintypes.WPARAM)]


class RawInputDevice(ctypes.Structure):
    _fields_ = [("page", wintypes.USHORT), ("usage", wintypes.USHORT),
                ("flags", wintypes.DWORD), ("target", wintypes.HWND)]


WinEventProc = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
                                 wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
USER32 = ctypes.WinDLL("user32", use_last_error=True)
USER32.RegisterRawInputDevices.argtypes = [ctypes.POINTER(RawInputDevice), wintypes.UINT, wintypes.UINT]
USER32.RegisterRawInputDevices.restype = wintypes.BOOL
USER32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p,
                                   ctypes.POINTER(wintypes.UINT), wintypes.UINT]
USER32.GetRawInputData.restype = wintypes.UINT
USER32.SetWinEventHook.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE,
                                   WinEventProc, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
USER32.SetWinEventHook.restype = wintypes.HANDLE
USER32.UnhookWinEvent.argtypes = [wintypes.HANDLE]
USER32.UnhookWinEvent.restype = wintypes.BOOL


class ActivityMonitor(QAbstractNativeEventFilter):
    def __init__(self):
        super().__init__()
        self.keyboard = deque(maxlen=120)
        self.window_event = None
        self.hooks = []
        self.registered = False
        self.installed = False
        self.enabled = True
        self.windows = {win32gui.GetForegroundWindow()}
        self.callback = WinEventProc(self.on_window_event)

    def start(self, hwnd):
        if QApplication.platformName() != "windows":
            return
        device = RawInputDevice(1, 6, 0x100, hwnd)  # Keyboard INPUTSINK; no input suppression.
        self.registered = bool(USER32.RegisterRawInputDevices(ctypes.byref(device), 1, ctypes.sizeof(device)))
        QApplication.instance().installNativeEventFilter(self)
        self.installed = True
        for first, last in ((0x0003, 0x000B), (0x8000, 0x800C)):
            hook = USER32.SetWinEventHook(first, last, None, self.callback, 0, 0, 2)
            if hook:
                self.hooks.append(hook)

    def nativeEventFilter(self, event_type, message):
        if self.enabled and event_type in (b"windows_generic_MSG", b"windows_dispatcher_MSG"):
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x00FF:
                header = RawInputHeader()
                size = wintypes.UINT(ctypes.sizeof(header))
                copied = USER32.GetRawInputData(msg.lParam, 0x10000005, ctypes.byref(header),
                                                ctypes.byref(size), ctypes.sizeof(header))
                if copied == ctypes.sizeof(header) and header.kind == 1:
                    self.keyboard.append(time.monotonic())
        return False, 0

    def on_window_event(self, hook, event, hwnd, object_id, child_id, thread, timestamp):
        if not self.enabled or not hwnd or object_id != 0 or child_id != 0:
            return
        if event == 0x8001:
            if hwnd in self.windows:
                self.windows.discard(hwnd)
                self.window_event = "close"
            return
        if event not in (0x0003, 0x000B, 0x8002, 0x800C):
            return
        try:
            if (not win32gui.IsWindowVisible(hwnd) or win32gui.GetAncestor(hwnd, 2) != hwnd
                    or win32gui.GetWindowLong(hwnd, -20) & 0x80
                    or win32gui.GetClassName(hwnd) in ("Progman", "WorkerW", "Shell_TrayWnd")):
                return
            if len(self.windows) >= 128:
                self.windows.clear()
            self.windows.add(hwnd)
            if event == 0x8002:
                self.window_event = "open"
            elif hwnd == win32gui.GetForegroundWindow():
                # shortcut: title changes hint at tabs; use an extension for exact tab lifecycle events.
                self.window_event = "move" if event == 0x000B else "change"
        except win32gui.error:
            pass  # A window can disappear between the event and these queries.

    def consume(self, now):
        while self.keyboard and self.keyboard[0] < now - 2:
            self.keyboard.popleft()
        count = len(self.keyboard)
        event, self.window_event = self.window_event, None
        if not self.enabled:
            self.keyboard.clear()
            return 0, None
        return count, event

    def close(self):
        for hook in self.hooks:
            USER32.UnhookWinEvent(hook)
        self.hooks.clear()
        if self.registered:
            device = RawInputDevice(1, 6, 1, None)
            USER32.RegisterRawInputDevices(ctypes.byref(device), 1, ctypes.sizeof(device))
            self.registered = False
        if self.installed:
            QApplication.instance().removeNativeEventFilter(self)
            self.installed = False
        self.keyboard.clear()
