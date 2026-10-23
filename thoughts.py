"""Click-through glass thoughts with a softly blurred, rounded backdrop sample."""

import ctypes

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPalette, QPen, QPixmap, QRegion
from PySide6.QtWidgets import QApplication, QGraphicsBlurEffect, QGraphicsScene, QLabel


def soften(source):
    scene = QGraphicsScene()
    item = scene.addPixmap(source)
    blur = QGraphicsBlurEffect()
    blur.setBlurRadius(3 * source.devicePixelRatio())
    item.setGraphicsEffect(blur)
    result = QPixmap(source.size())
    result.setDevicePixelRatio(source.devicePixelRatio())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    bounds = QRectF(0, 0, source.width() / source.devicePixelRatio(),
                    source.height() / source.devicePixelRatio())
    scene.render(painter, bounds, bounds)
    painter.end()
    return result


class ThoughtLabel(QLabel):
    shown = Signal(str)
    dismissed = Signal(str)

    def __init__(self):
        super().__init__(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                         | Qt.WindowDoesNotAcceptFocus | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowOpacity(0.88)
        self.setTextFormat(Qt.PlainText)
        self.setWordWrap(True)
        self.setStyleSheet("background: transparent; border: 0;"
                          "border-radius: 20px; padding: 8px 10px; font: 600 16px 'Segoe UI';")
        self.ensurePolished()
        self.backdrop = QPixmap()
        self.painted_text = None
        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor("#fffaf0"))
        self.setPalette(palette)

    def setText(self, text):
        super().setText(text)
        self.setFixedWidth(min(270, max(96, self.fontMetrics().horizontalAdvance(text) + 24)))
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setFixedHeight(self.heightForWidth(self.width()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        shape = QPainterPath()
        shape.addRoundedRect(QRectF(self.rect()), 20, 20)
        self.setMask(QRegion(shape.toFillPolygon().toPolygon()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        shape = QPainterPath()
        shape.addRoundedRect(QRectF(self.rect()), 20, 20)
        painter.setClipPath(shape)
        if not self.backdrop.isNull():
            painter.drawPixmap(0, 0, self.backdrop)
        glass = QLinearGradient(0, 0, 0, self.height())
        glass.setColorAt(0, QColor(255, 250, 243, 32))
        glass.setColorAt(0.45, QColor(255, 255, 255, 10))
        glass.setColorAt(1, QColor(30, 28, 36, 28))
        painter.setPen(QPen(QColor(255, 255, 255, 64), 0.8))
        painter.setBrush(glass)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 20, 20)
        painter.end()
        super().paintEvent(event)
        if self.isVisible() and self.painted_text != self.text():
            self.painted_text = self.text()
            self.shown.emit(self.painted_text)

    def prepare_backdrop(self):
        self.backdrop = QPixmap()
        palette = self.palette()
        palette.setColor(QPalette.WindowText, QColor("#fffaf0"))
        self.setPalette(palette)
        if QApplication.platformName() == "windows" and self.screen() is not None:
            # A per-thought sample avoids native blur spilling beyond rounded regions.
            try:
                ctypes.windll.dwmapi.DwmFlush()
            except (OSError, AttributeError):
                pass
            source = self.screen().grabWindow(0, self.x() - 6, self.y() - 6,
                                              self.width() + 12, self.height() + 12)
            if not source.isNull():
                ratio = source.devicePixelRatio()
                self.backdrop = soften(source).copy(round(6 * ratio), round(6 * ratio),
                                                    round(self.width() * ratio), round(self.height() * ratio))
                palette = self.palette()
                brightness = self.backdrop.scaled(1, 1, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).toImage().pixelColor(0, 0).lightness()
                palette.setColor(QPalette.WindowText, QColor("#29272e" if brightness > 145 else "#fffaf0"))
                self.setPalette(palette)

    def showEvent(self, event):
        if self.backdrop.isNull():
            self.prepare_backdrop()
        super().showEvent(event)

    def hideEvent(self, event):
        self.backdrop = QPixmap()
        super().hideEvent(event)
        if self.painted_text is not None:
            text, self.painted_text = self.painted_text, None
            self.dismissed.emit(text)
