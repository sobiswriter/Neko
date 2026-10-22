"""Click-through runway hints; a separate, explicit Stop button owns only its pixels."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget, QPushButton


class GameOverlay(QWidget):
    def __init__(self, neko):
        super().__init__()
        self.neko = neko
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
        self.setWindowFlags(flags | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.stop = QPushButton("End game")
        self.stop.setWindowFlags(flags)
        self.stop.setAttribute(Qt.WA_ShowWithoutActivating)
        self.stop.setFocusPolicy(Qt.NoFocus)
        self.stop.setAccessibleName("End Catch the Cursor")
        self.stop.setStyleSheet("QPushButton { background: #faf7f2; color: #66514d; border: 1px solid #b89b91; border-radius: 8px; padding: 6px 12px; }")
        self.stop.clicked.connect(neko.end_game)

    def hideEvent(self, event):
        self.stop.hide()
        super().hideEvent(event)

    def paintEvent(self, event):
        game = self.neko.game
        if game is None:
            return
        r = game.runway
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setFont(QFont("Segoe UI", 10))
        left, right = r.left + r.paw[0] - self.x(), r.right + 191 - r.paw[0] - self.x()
        bottom = r.y + 124 - self.y()
        top = r.y + r.paw[1] - r.lift - self.y()
        alpha = 220 if game.phase == "ready" else 100
        for color, width in ((QColor(35, 28, 35, alpha), 3), (QColor(239, 186, 163, alpha), 1)):
            p.setPen(QPen(color, width, Qt.DashLine))
            if not game.motion:
                px = r.paw[0] if game.direction < 0 else 191 - r.paw[0]
                p.drawEllipse(QRectF(game.x + px - self.x() - 10, r.y + r.paw[1] - self.y() - 11, 20, 20))
                continue
            p.drawLine(round(left), round(top), round(right), round(top))
            p.drawLine(round(left), round(bottom), round(right), round(bottom))
            p.drawLine(round(left), round(bottom), round(left + 24), round(top))
            p.drawLine(round(right), round(bottom), round(right - 24), round(top))
        remaining = max(0, round(game.deadline - game.last)) if game.deadline != float("inf") else 45
        text = ("Keep the arrow between the lines · one paw touch wins!" if game.phase == "ready"
                else f"Catch the Cursor · {remaining}s · let her catch you… or try to escape!")
        if not game.motion:
            text = "Gentle play · bring the arrow to her reaching paw"
        p.setPen(QColor("#302835"))
        rect = QRectF(left + 4, max(4, top - 25), right - left - 110, 22)
        p.drawText(rect.translated(1, 1), Qt.AlignLeft | Qt.AlignVCenter, text)
        p.setPen(QColor("#fff3e5"))
        p.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, text)
