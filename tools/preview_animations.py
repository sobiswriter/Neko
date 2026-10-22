"""Rebuild documentation previews from the actual atlas (requires optional Pillow)."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animations import CLIPS, PET_ROWS, SpriteAtlas, drop_progress, CANVAS_PADDING, CANVAS_TOP
from cursors import petting_cursors


IDLES = [("idle", "Sitting / blink"), ("tail", "Tail swish"), ("ears", "Ear flick"),
         ("sniff", "Sniffing"), ("stretch", "Seated stretch"), ("groom", "Grooming"),
         ("yawn", "Yawning"), ("loaf", "Loaf"), ("peek", "Sleepy peek"),
         ("look_left", "Looking left"), ("look_right", "Looking right"),
         ("tail_chase", "Tail chase"), ("tail_catch", "Tail catch")]
ACTIVITIES = [("typing", "Typing"), ("walk", "Walking"), ("fall_asleep", "Settling"),
              ("sleep", "Sleeping"), ("wake", "Waking"),
              ("arrive", "Drop in / hello"), ("depart", "Hop down / goodbye")]
REWORK = [ACTIVITIES[-2], ACTIVITIES[-1], IDLES[1], IDLES[-2], IDLES[-1]]
PETS = [("happy", "Head pats"), ("nuzzle", "Cheek nuzzle"), ("knead", "Kneading"),
        ("chin_scritch", "Chin scritches"), ("roll", "Playful roll"), ("paw_offer", "Paw offer"),
        ("ear_rub", "Ear rubs"), ("pet_stretch", "Front stretch"), ("back_arch", "Back arch"),
        ("happy_hop", "Tiny hop"), ("side_flop", "Side flop"), ("shoulder_peek", "Shoulder peek")]
BACKGROUND = (248, 246, 241)


def pixels(pixmap):
    assert not pixmap.isNull(), "Missing runtime sprite"
    image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    # Existing catalogs omit empty top padding to retain their original layout.
    return Image.frombytes("RGBA", (image.width(), image.height()), bytes(image.constBits())).crop(
        (0, CANVAS_TOP, image.width(), CANVAS_TOP + 112))


def displayed(atlas, name, elapsed):
    if name in {item[0] for item in PETS}:
        end = 0.8 + sum(CLIPS[name].durations) / 1000
        if elapsed < 0.8:
            name = "idle"
        elif elapsed >= end:
            name, elapsed = "idle", elapsed - end
        else:
            # Keep the 50ms samples exact after subtracting the idle introduction.
            elapsed = round(elapsed - 0.8, 3)
    slot = 8 if name == "loaf" else 6
    if name in {item[0] for item in IDLES} and elapsed >= slot:
        name, elapsed = "idle", elapsed - slot
    if name not in ("arrive", "depart"):
        fps = 20 if name in ("tail_chase", "tail_catch") or name in {item[0] for item in PETS} else 10
        elapsed = int(elapsed * fps) / fps
    return pixels(atlas.frame(name, elapsed))


def frame_sheet(atlas, entries, destination, source=False):
    bands = [((len(set(CLIPS[name].order)) + 7) // 8) for name, _ in entries]
    sheet = Image.new("RGB", (180 + 8 * 208, sum(bands) * 160), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    band = 0
    for row, (name, label) in enumerate(entries):
        draw.text((8, band * 160 + 12), label, fill="#514a43")
        clip = CLIPS[name]
        indices = sorted(set(clip.order))
        for col, index in enumerate(indices):
            if source:
                frame = pixels(atlas.frames[clip.bank, clip.row + index // 4, index % 4])
            else:
                first = clip.order.index(index)
                elapsed = (sum(clip.durations[:first]) + clip.durations[first] / 2) / 1000
                frame = pixels(atlas.frame(name, elapsed))
            left, top = 180 + col % 8 * 208, (band + col // 8) * 160
            sheet.paste(frame, (left, top + 25), frame)
            draw.text((left + 4, top + 140), str(index + 1), fill="#514a43")
        band += bands[row]
    sheet.save(destination)


def lifecycle_scene(atlas, destination):
    frames = []
    durations = [30, 30, 40] * 60
    elapsed_ms = 0
    for duration in durations:
        canvas = Image.new("RGB", (480, 360), BACKGROUND)
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 10), "Monitor top", fill="#514a43")
        draw.line((0, 30, 240, 30), fill="#bcb4a7")
        draw.text((252, 10), "Sad pause, then hop", fill="#514a43")
        draw.line((0, 299, 480, 299), fill="#bcb4a7")
        elapsed = elapsed_ms / 1000
        y = round(-82 + 270 * drop_progress(elapsed))
        arrival = displayed(atlas, "arrive", elapsed).crop((CANVAS_PADDING, 0, CANVAS_PADDING + 112, 112))
        # Crop horizontal transparent padding; retain the native top-edge clip/trajectory.
        canvas.paste(arrival, (64, y), arrival)
        draw.rectangle((0, 0, 239, 29), fill=BACKGROUND)
        draw.text((12, 10), "Monitor top", fill="#514a43")
        departure = pixels(atlas.frame("depart", max(0, elapsed - 0.5))).crop(
            (CANVAS_PADDING, 0, CANVAS_PADDING + 112, 112))
        canvas.paste(departure, (304, 188), departure)
        frames.append(canvas)
        elapsed_ms += duration
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2)


def flight_sheet(atlas, destination):
    sheet = Image.new("RGB", (160 + 10 * 112, 4 * 144), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for row in range(4):
        name = "arrive" if row < 2 else "depart"
        draw.text((8, row * 144 + 8), name, fill="#514a43")
        for col in range(10):
            elapsed = (row % 2 * 10 + col) / 10
            frame = pixels(atlas.frame(name, elapsed)).crop((CANVAS_PADDING, 0, CANVAS_PADDING + 112, 112))
            left, top = 160 + col * 112, row * 144
            sheet.paste(frame, (left, top), frame)
            draw.text((left + 6, top + 124), f"{elapsed:.1f}s", fill="#514a43")
    sheet.save(destination)


def catalog(atlas, entries, stem, columns=4, scale=1, seconds=8):
    if any(name in PET_ROWS for name, _ in entries):
        seconds = max(seconds, math.ceil(max(sum(CLIPS[name].durations) / 1000
                                            for name, _ in entries) + 1.6))
    width, height = columns * 240, ((len(entries) + columns - 1) // columns) * 152
    frames = []
    fast_only = all(name in ("tail_chase", "tail_catch") or name in {item[0] for item in PETS}
                    for name, _ in entries)
    # Tail-only playback preserves the reference's exact 50ms footfalls.
    durations = [50] * (seconds * 20) if fast_only else [30, 30, 40] * (seconds * 10)
    elapsed_ms = 0
    for duration in durations:
        canvas = Image.new("RGB", (width, height), BACKGROUND)
        draw = ImageDraw.Draw(canvas)
        for index, (name, label) in enumerate(entries):
            left, top = index % columns * 240, index // columns * 152
            draw.text((left + 8, top + 8), label, fill="#514a43")
            frame = displayed(atlas, name, elapsed_ms / 1000)
            canvas.paste(frame, (left + 24, top + 30), frame)
        if scale != 1:
            canvas = canvas.resize((width * scale, height * scale), Image.Resampling.NEAREST)
        frames.append(canvas)
        elapsed_ms += duration
    assert elapsed_ms == seconds * 1000
    frames[0].save(stem.with_suffix(".gif"), save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2)
    frames[18].save(stem.with_suffix(".png"))
    assert len(frames) == seconds * (20 if fast_only else 30)


def cursor_preview(atlas, destination):
    hands = petting_cursors()
    assert all(cursor.hotSpot() == hands[0].hotSpot() for cursor in hands)
    frames = []
    for index in range(48):
        elapsed = index / 20 - 0.6
        canvas = Image.new("RGB", (160, 152), BACKGROUND)
        frame = pixels(atlas.frame("idle" if elapsed < 0 else "happy", max(0, elapsed))).crop(
            (CANVAS_PADDING, 0, CANVAS_PADDING + 112, 112))
        canvas.paste(frame, (24, 30), frame)
        if 0 <= elapsed < len(hands) * 0.07:
            hand = hands[min(len(hands) - 1, int(elapsed / 0.07))]
            frame = pixels(hand.pixmap())
            canvas.paste(frame, (80 - hand.hotSpot().x(), 60 - hand.hotSpot().y()), frame)
        frames.append(canvas.resize((480, 456), Image.Resampling.NEAREST))
    frames[0].save(destination, save_all=True, append_images=frames[1:], duration=50,
                   loop=0, disposal=2)


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT / "assets")
    assert len(atlas.frames) == 147 + sum(PET_ROWS.values()) * 4 + len(PET_ROWS)
    folder = ROOT / "docs"
    for entries, stem in ((IDLES, "neko-idle-catalog"), (ACTIVITIES, "neko-activity-catalog")):
        catalog(atlas, entries, folder / stem)
        frame_sheet(atlas, entries, folder / (stem + "-frames.png"))
    catalog(atlas, PETS, folder / "neko-pet-catalog")
    frame_sheet(atlas, PETS, folder / "neko-pet-frames.png", source=True)
    frame_sheet(atlas, PETS[:6], folder / "neko-pet-frames-a.png", source=True)
    frame_sheet(atlas, PETS[6:], folder / "neko-pet-frames-b.png", source=True)
    cursor_preview(atlas, folder / "neko-palm-preview.gif")
    frame_sheet(atlas, REWORK, folder / "neko-tail-life-frames.png")
    frame_sheet(atlas, REWORK, folder / "neko-tail-life-source-frames.png", source=True)
    flight_sheet(atlas, folder / "neko-lifecycle-flight.png")
    lifecycle_scene(atlas, folder / "neko-lifecycle-scene.gif")
    catalog(atlas, REWORK, folder / "neko-tail-life-native", columns=5, seconds=6)
    catalog(atlas, REWORK, folder / "neko-tail-life-preview", columns=5, scale=2, seconds=6)
    catalog(atlas, IDLES[-2:], folder / "neko-tail-reference-preview", columns=2, scale=2, seconds=6)
    print("Rebuilt idle, activity and animation-rework previews from SpriteAtlas.")
