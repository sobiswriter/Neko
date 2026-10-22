"""Small, click-through thoughts with a native Windows frosted backdrop."""

import ctypes
from ctypes import wintypes

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QRegion
from PySide6.QtWidgets import QApplication, QLabel


class AccentPolicy(ctypes.Structure):
    _fields_ = [("state", ctypes.c_int), ("flags", ctypes.c_int),
                ("color", ctypes.c_uint), ("animation", ctypes.c_int)]


class CompositionData(ctypes.Structure):
    _fields_ = [("attribute", ctypes.c_int), ("data", ctypes.c_void_p), ("size", ctypes.c_size_t)]


def enable_backdrop(hwnd):
    if QApplication.platformName() != "windows":
        return False
    try:
        apply = ctypes.WinDLL("user32", use_last_error=True).SetWindowCompositionAttribute
        apply.argtypes = [wintypes.HWND, ctypes.POINTER(CompositionData)]
        apply.restype = wintypes.BOOL
        # shortcut: private accent policy; keep the tinted fallback if Windows removes it.
        policy = AccentPolicy(3, 0, 0, 0)  # ACCENT_ENABLE_BLURBEHIND
        data = CompositionData(19, ctypes.addressof(policy), ctypes.sizeof(policy))
        return bool(apply(hwnd, ctypes.byref(data)))
    except (OSError, AttributeError):
        return False


class ThoughtLabel(QLabel):
    def __init__(self):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                         | Qt.WindowDoesNotAcceptFocus | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setTextFormat(Qt.PlainText)
        self.setWordWrap(True)
        self.setStyleSheet("background: transparent; color: #fffaf0; border: 0;"
                          "border-radius: 10px; padding: 8px 10px; font: 600 16px 'Segoe UI';")
        self.ensurePolished()
        self.native_backdrop = False

    def setText(self, text):
        super().setText(text)
        self.setFixedWidth(min(270, max(96, self.fontMetrics().horizontalAdvance(text) + 24)))
        self.setFixedHeight(self.heightForWidth(self.width()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        shape = QPainterPath()
        shape.addRoundedRect(QRectF(self.rect()), 10, 10)
        self.setMask(QRegion(shape.toFillPolygon().toPolygon()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(40, 35, 47, 110))
        painter.drawRoundedRect(QRectF(self.rect()), 10, 10)
        painter.end()
        super().paintEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.native_backdrop = enable_backdrop(int(self.winId()))
