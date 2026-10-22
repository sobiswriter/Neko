"""Preview lifecycle scenes through NekoWidget's actual trajectory and painter."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw
from PySide6.QtCore import QPoint, QRect, QSettings
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, CLIPS
from behavior import NekoState
from main import NekoWidget


def pixels(pixmap):
    image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes("RGBA", (image.width(), image.height()), bytes(image.constBits()))


def scene(atlas, destination):
    app = QApplication.instance() or QApplication([])
    frames = []
    with tempfile.TemporaryDirectory() as folder, \
            patch("main.SpriteAtlas", return_value=atlas), \
            patch("main.ActivityMonitor.start"), \
            patch("main.desktop_activity", return_value=(0, 0, False)), \
            patch("main.NekoWidget.offline_line"), patch("main.QApplication.quit"):
        cats = []
        for i, (clip, y) in enumerate((("arrive", 166), ("depart", 166), ("depart", 36))):
            settings = QSettings(str(Path(folder) / f"{i}.ini"), QSettings.IniFormat)
            cat = NekoWidget(settings)
            cat.show_neko()
            for timer in (cat.tick_timer, cat.invitation_timer, cat.animation_timer, cat.save_timer):
                timer.stop()
            cat.move(84, y)
            with patch("main.time.monotonic", return_value=1000):
                cat.start_transition(NekoState.ARRIVING if clip == "arrive" else NekoState.LEAVING, clip)
                cat.lifecycle_area = QRect(0, 0, 360, 320)
                if clip == "arrive":
                    cat.arrival_top = -64
                    cat.move(84, -64)
                cat.animate()
            cats.append((cat, clip))
        for i in range(90):
            elapsed = round(i / 30, 6)
            canvas = Image.new("RGB", (1080, 360), "#eee9df")
            draw = ImageDraw.Draw(canvas)
            for column, (cat, clip) in enumerate(cats):
                left = column * 360
                draw.rectangle((left, 30, left + 359, 349), fill=("#fbf9f5", "#343c4c", "#fbf9f5")[column])
                draw.text((left + 12, 8), ("Curious visitor", "See you soon", "Goodbye from a higher perch")[column], fill="#4c4948")
                duration = sum(CLIPS[clip].durations) / 1000
                with patch("main.time.monotonic", return_value=1000 + elapsed):
                    if elapsed >= duration:
                        if clip == "depart":
                            continue
                        if cat.arrival_target is not None:
                            cat.finish_transition()
                    else:
                        cat.animate()
                    frame = pixels(cat.grab())
                panel = Image.new("RGBA", (360, 320))
                panel.paste(frame, (cat.x(), cat.y()))
                canvas.paste(panel, (left, 30), panel)
            frames.append(canvas)
        for cat, _ in cats:
            cat.transition_timer.stop()
            cat.animation_timer.stop()
            cat.activity.close()
            cat.bubble.hide()
            cat.bubble.deleteLater()
            cat.tray_icon.hide()
            cat.hide()
            cat.deleteLater()
        app.processEvents()
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=[30, 30, 40] * 30, loop=0, disposal=2)
    frames[27].save(Path(destination).with_suffix(".png"))


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT / "assets")
    sheet = Image.new("RGB", (1664, 1800), "#f8f5ef")
    draw = ImageDraw.Draw(sheet)
    band = 0
    for background in ("#f8f5ef", "#343c4c"):
        for name in ("arrive", "depart"):
            clip = CLIPS[name]
            for n, i in enumerate(clip.order):
                x, y = n % 8 * 208, (band + n // 8) * 180
                draw.rectangle((x, y, x + 207, y + 179), fill=background)
                frame = pixels(atlas.frames[clip.bank, i // 4, i % 4])
                sheet.paste(frame, (x + 8, y + 16), frame)
                draw.text((x + 8, y + 162), f"{name} {i}", fill="#918b83")
            band += (len(clip.order) + 7) // 8
    sheet.save(ROOT / "docs/visitor-frames.png")
    scene(atlas, ROOT / "docs/visitor-scene.gif")
