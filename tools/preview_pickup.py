"""Preview the actual carry controller and atlas; optional Pillow, Windows only."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image, ImageDraw
from PySide6.QtCore import QSettings, QPoint
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animations import CARRY_ROWS, CLIPS, held_clip
from behavior import NekoState
from main import NekoWidget


def pixels(frame):
    image = frame.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes("RGBA", (image.width(), image.height()), bytes(image.constBits()))


def card(frame, label):
    image = Image.new("RGB", (400, 184), "#faf7f2")
    draw = ImageDraw.Draw(image)
    draw.text((8, 7), label, fill="#514a43")
    draw.rectangle((200, 25, 399, 183), fill="#262334")
    sprite = pixels(frame)
    for x in (4, 204):
        image.paste(sprite, (x, 29), sprite)
    return image


def save_gif(frames, destination, duration=50):
    frames[0].save(destination, save_all=True, append_images=frames[1:], duration=duration,
                   loop=0, disposal=2, optimize=False)
    with Image.open(destination) as decoded:
        decoded_duration = 0
        for index in range(decoded.n_frames):
            decoded.seek(index)
            decoded_duration += decoded.info.get("duration", 0)
        assert decoded_duration == len(frames) * duration, (destination, decoded_duration)


def render(neko, folder):
    atlas = neko.atlas
    sheet = Image.new("RGB", (8 * 208, 14 * 172), "#faf7f2")
    draw = ImageDraw.Draw(sheet)
    slot = 0
    for name, rows in CARRY_ROWS.items():
        for index in range(rows * 4):
            x, y = slot % 8 * 208, slot // 8 * 172
            draw.text((x + 4, y + 4), f"{name} {index}", fill="#514a43")
            sprite = pixels(atlas.frames[f"carry-{name}", index // 4, index % 4])
            sheet.paste(sprite, (x + 4, y + 23), sprite)
            slot += 1
    assert slot == 100
    sheet.crop((0, 0, sheet.width, ((slot + 7) // 8) * 172)).save(folder / "neko-pickup-frames.png")

    base = 100.0
    frames, coverage = [], {}
    for index in range(540):
        elapsed = index / 20
        if index == 16:
            with patch("main.time.monotonic", return_value=base + 0.8):
                neko.pose_started = base + 0.8
                neko.begin_pickup()
        if index == 484:
            with patch("main.time.monotonic", return_value=base + 24.2):
                neko.release_pickup()
        now = base + elapsed + 0.025
        with patch("main.time.monotonic", return_value=now):
            neko.animate()
            sprite = neko.current_frame(now)
            if neko.companion.state == NekoState.HELD:
                name, phase = held_clip(neko.carry_elapsed(now))
                coverage.setdefault(name, set()).add(CLIPS[name].frame_index(phase))
            label = neko.current_clip.replace("held_", "").replace("carry_", "").replace("_", " ")
            frames.append(card(sprite, label).resize((800, 368), Image.Resampling.NEAREST).quantize(colors=96))
    for name in ("held_excited", "held_calm", "held_unimpressed", "held_sleepy",
                 "carry_to_calm", "carry_to_unimpressed", "carry_yawn"):
        assert coverage[name] == set(CLIPS[name].order), (name, coverage[name])
    save_gif(frames, folder / "neko-pickup-preview.gif")
    save_gif(frames, folder / "neko-pickup-preview-slow.gif", 100)

    cases = []
    for label, hold, asleep in (("Early release", 0.18, False), ("Excited", 1.2, False),
                                ("Calm", 6, False), ("Unimpressed", 13, False),
                                ("Mid-yawn", 20.35, False), ("Sleepy", 25, False),
                                ("Real nap", 6, True)):
        with patch("main.time.monotonic", return_value=base):
            neko.cancel_pickup()
            neko.companion.state = NekoState.SLEEPING if asleep else NekoState.IDLE
            neko.companion.nap_started = base - 5 if asleep else None
            neko.pose_started = base
            neko.refresh_asset()
            neko.begin_pickup()
        with patch("main.time.monotonic", return_value=base + hold):
            neko.release_pickup()
        cases.append((label, list(neko.carry_path), neko.carry_path_clip))
    release_sheet = Image.new("RGB", (10 * 208, len(cases) * 2 * 172), "#faf7f2")
    draw = ImageDraw.Draw(release_sheet)
    for row, (label, poses, clip) in enumerate(cases):
        assert len(poses) <= 20
        for index, frame in enumerate(poses):
            x, y = index % 10 * 208, (row * 2 + index // 10) * 172
            draw.text((x + 3, y + 3), f"{label} {index}", fill="#514a43")
            sprite = pixels(frame)
            release_sheet.paste(sprite, (x + 4, y + 24), sprite)
    release_sheet.save(folder / "neko-pickup-release-frames.png")
    entries = (("Stretch", NekoState.PET_STRETCH, "pet_stretch", 2.5),
               ("Flop", NekoState.SIDE_FLOP, "side_flop", 2.4),
               ("Roll", NekoState.ROLLING, "roll", 2.8),
               ("Hop", NekoState.HAPPY_HOP, "happy_hop", 2.1),
               ("Nap", NekoState.SLEEPING, "sleep", 0),
               ("Loaf", NekoState.LOAFING, "loaf", 3.0))
    entry_sheet = Image.new("RGB", (12 * 208, len(entries) * 172), "#faf7f2")
    draw = ImageDraw.Draw(entry_sheet)
    for row, (label, state, name, elapsed) in enumerate(entries):
        with patch("main.time.monotonic", return_value=base):
            neko.cancel_pickup()
            neko.companion.state = state
            neko.companion.nap_started = base - 5 if state == NekoState.SLEEPING else None
            neko.pose_started = base - elapsed
            neko.refresh_asset()
            assert neko.current_clip == name
            neko.begin_pickup()
        for index, frame in enumerate(neko.carry_path):
            x, y = index * 208, row * 172
            draw.text((x + 3, y + 3), f"{label} {index}", fill="#514a43")
            sprite = pixels(frame)
            entry_sheet.paste(sprite, (x + 4, y + 24), sprite)
    entry_sheet.save(folder / "neko-pickup-entry-frames.png")
    print("Rendered all 100 source slots, 27s/54s mood previews, seven release stories and six posture entries.")


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    with TemporaryDirectory() as temporary, patch("main.ActivityMonitor.start"), \
            patch("main.desktop_activity", return_value=(0, 0, False)):
        settings = QSettings(str(Path(temporary) / "prefs.ini"), QSettings.IniFormat)
        settings.setValue("quiet", True)
        neko = NekoWidget(settings)
        neko.tick_timer.stop()
        neko.save_timer.stop()
        try:
            render(neko, ROOT / "docs")
        finally:
            neko.cancel_pickup()
            neko.hide()
            neko.tray_icon.hide()
            neko.bubble.deleteLater()
            neko.deleteLater()
            app.processEvents()
