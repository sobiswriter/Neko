"""Assemble newly drawn local breathing/expression regions on fixed support anchors."""
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
from tools.assemble_rest_blink import nose, EYES

MOUTH = (83, 93, 95, 99)
CHEST = (78, 104, 108, 117)


def assemble():
    app = QApplication.instance() or QApplication([])
    canonical = pixels(SpriteAtlas(ROOT / "assets").frames["idle", 0, 0])
    raw = QImage(str(ROOT / "references/rest-breathing/2026-10-23/rest-raw.png"))
    assert not raw.isNull() and raw.width() >= 4 and raw.height() >= 2
    source, boxes = [], []
    for index in range(8):
        left, right = (round((index % 4 + n) * raw.width() / 4) for n in (0, 1))
        top, bottom = (round((index // 4 + n) * raw.height() / 2) for n in (0, 1))
        cell = raw.copy(left, top, right - left, bottom - top)
        box = sprite_bounds(cell)
        assert not box.isEmpty()
        boxes.append((left + box.x(), top + box.y(), box.width(), box.height()))
        source.append(cell.copy(box))
    scale = 62 / pet_landmarks(source[0])[0]
    frames, registrations = [canonical], []
    for index in range(1, 8):
        qimage = source[index].convertToFormat(QImage.Format_RGBA8888)
        drawing = Image.frombytes("RGBA", (qimage.width(), qimage.height()), bytes(qimage.constBits()))
        drawing = drawing.resize((round(drawing.width * scale), round(drawing.height * scale)), Image.Resampling.NEAREST)
        center = nose(drawing)
        offset = tuple(round(a - b) for a, b in zip((86.5, 90), center))
        registered = Image.new("RGBA", canonical.size)
        registered.paste(drawing, offset)
        frame = canonical.copy()
        for region in (*EYES, MOUTH, CHEST):
            patch = registered.crop(region)
            if index == 2 and region in EYES:
                patch = frames[1].crop(region)
            assert patch.getchannel("A").getextrema()[0] >= 250, (index, region)
            patch.putalpha(canonical.crop(region).getchannel("A"))
            frame.paste(patch, region[:2])
        assert frame.crop((0, 122, 192, 144)).tobytes() == canonical.crop((0, 122, 192, 144)).tobytes()
        frames.append(frame)
        registrations.append({"source":index, "nose":center, "offset":offset})
    assert frames[1].crop(CHEST).tobytes() != frames[2].crop(CHEST).tobytes(), "Missing drawn breath"
    sheet = Image.new("RGBA", (768, 288))
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index % 4 * 192, index // 4 * 144))
    sheet.save(ROOT / "assets/neko-idle-rest-v2.png")
    path = ROOT / "docs/rest-breathing-prompts.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["assembly"] = {"source_boxes":boxes, "constant_scale":scale, "registrations":registrations,
                          "eyes":EYES, "mouth":MOUTH, "chest":CHEST, "canvas":[192,144],
                          "output":"assets/neko-idle-rest-v2.png",
                          "method":"Eight new authored phases; composite expression and internal chest/shoulder drawings only, preserving exact silhouette, head/ear/nose anchors, paws, haunch support and tail. Reject the source's outer-torso variation (up to4px at the proposed larger chest window). Reuse phase1 open eyes at crest2 so breathing does not prolong the300ms blink. No global movement, scaling or anatomy painting."}
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    assemble()
