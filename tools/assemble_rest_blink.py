"""Register generated eyelids onto the unchanged shared seated drawing."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, sprite_bounds, pet_landmarks
from tools.preview_idle_refresh import pixels

EYES = ((67, 73, 84, 93), (94, 73, 112, 93))


def nose(image):
    points = []
    for y in range(image.height * 35 // 100, image.height * 60 // 100):
        for x in range(image.width * 3 // 10, image.width * 7 // 10):
            red, green, blue, alpha = image.getpixel((x, y))
            if alpha >= 128 and red > 190 and 90 < green < 220 and 90 < blue < 225 and red - green > 25:
                points.append((x, y))
    assert points, "Missing nose registration landmark"
    return tuple(sum(p[axis] for p in points) / len(points) for axis in (0, 1))


def assemble():
    app = QApplication.instance() or QApplication([])
    canonical = pixels(SpriteAtlas(ROOT / "assets").frames["idle", 0, 0])
    raw = QImage(str(ROOT / "references/idle-stability/2026-10-23/blink-raw.png"))
    boxes, source = [], []
    for index in range(4):
        cell = raw.copy(index * raw.width() // 4, 0, raw.width() // 4, raw.height())
        box = sprite_bounds(cell)
        boxes.append((box.x(), box.y(), box.width(), box.height()))
        source.append(cell.copy(box))
    scale = 62 / pet_landmarks(source[0])[0]
    target_nose = (86.5, 90)
    frames, registrations = [canonical], []
    for index in (1, 2):
        qimage = source[index].convertToFormat(QImage.Format_RGBA8888)
        drawing = Image.frombytes("RGBA", (qimage.width(), qimage.height()), bytes(qimage.constBits()))
        drawing = drawing.resize((round(drawing.width * scale), round(drawing.height * scale)), Image.Resampling.NEAREST)
        center = nose(drawing)
        offset = tuple(round(a - b) for a, b in zip(target_nose, center))
        registered = Image.new("RGBA", canonical.size)
        registered.paste(drawing, offset)
        frame = canonical.copy()
        for eye in EYES:
            patch = registered.crop(eye)
            assert patch.getchannel("A").getextrema()[0] >= 250, (index, eye)
            patch.putalpha(canonical.crop(eye).getchannel("A"))
            frame.paste(patch, eye[:2])
        assert frame.getchannel("A").tobytes() == canonical.getchannel("A").tobytes()
        frames.append(frame)
        registrations.append({"source":index, "offset":offset, "nose":center})
    frames.append(canonical)
    sheet = Image.new("RGBA", (192 * 4, 144))
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * 192, 0))
    sheet.save(ROOT / "assets/neko-idle-rest-v2.png")
    path = ROOT / "docs/idle-stability-prompts.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["assembly"] = {"source_boxes":boxes, "constant_scale":scale, "registrations":registrations,
                          "eye_rectangles":EYES, "canvas":[192,144], "output":"assets/neko-idle-rest-v2.png",
                          "method":"Crop and register generated eye bands onto the exact canonical body. No facial pixels painted, whole-body refitting or interpolation. All alpha and pixels outside both eyes are identical."}
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    assemble()
