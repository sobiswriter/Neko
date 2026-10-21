"""Small palm strokes; only the cursor image moves, never the mouse pointer."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPainterPath, QPen, QPixmap


def petting_cursors():
    palm = QPainterPath()
    palm.moveTo(9, 16)
    palm.lineTo(9, 7)
    palm.quadTo(9, 4, 11, 4)
    palm.quadTo(13, 4, 13, 7)
    palm.lineTo(13, 13)
    palm.lineTo(13, 4)
    palm.quadTo(13, 1, 15, 1)
    palm.quadTo(17, 1, 17, 4)
    palm.lineTo(17, 13)
    palm.lineTo(17, 5)
    palm.quadTo(17, 2, 19, 2)
    palm.quadTo(21, 2, 21, 5)
    palm.lineTo(21, 14)
    palm.lineTo(21, 8)
    palm.quadTo(21, 5, 23, 5)
    palm.quadTo(25, 5, 25, 8)
    palm.lineTo(25, 19)
    palm.quadTo(25, 24, 22, 27)
    palm.lineTo(12, 27)
    palm.quadTo(10, 27, 9, 25)
    palm.lineTo(4, 18)
    palm.quadTo(2, 15, 4, 14)
    palm.quadTo(6, 13, 8, 16)
    palm.closeSubpath()
    frames = []
    for dx, dy in ((0, 0), (1, 1), (2, 2), (1, 1), (0, 0), (-1, 1), (-2, 2), (-1, 1), (0, 0)):
        frame = QPixmap(32, 32)
        frame.fill(Qt.transparent)
        painter = QPainter(frame)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(2 + dx, 2 + dy)
        painter.scale(0.85, 0.85)
        painter.setPen(QPen(QColor("#332f29"), 1.3))
        painter.setBrush(QColor("#fffdf7"))
        painter.drawPath(palm)
        painter.end()
        frames.append(QCursor(frame, 16, 16))
    return frames
