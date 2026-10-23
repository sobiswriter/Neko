"""Append drawn head/neck tilts to the preserved updated directional-look frames."""
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


def assemble():
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT / "assets")
    canonical_q = atlas.frames["idle", 0, 0].toImage()
    canonical = pixels(atlas.frames["idle", 0, 0])
    cb = sprite_bounds(canonical_q)
    _, canonical_head, _, _ = pet_landmarks(canonical_q.copy(cb))
    canonical_head += cb.left()
    raw = QImage(str(ROOT / "references/look-tilt/2026-10-23/tilt-raw.png"))
    assert not raw.isNull()
    poses, boxes = [], []
    for index in range(8):
        l, r = (round((index % 4 + n) * raw.width() / 4) for n in (0, 1))
        t, b = (round((index // 4 + n) * raw.height() / 2) for n in (0, 1))
        cell = raw.copy(l, t, r - l, b - t)
        box = sprite_bounds(cell)
        assert not box.isEmpty()
        boxes.append([l + box.x(), t + box.y(), box.width(), box.height()])
        poses.append(cell.copy(box))
    sx, sy = 62 / pet_landmarks(poses[0])[0], 82 / poses[0].height()
    _, reference_head, left, right = pet_landmarks(poses[0])
    foot = canonical_head + ((left + right) / 2 - reference_head) * sx
    generated, registrations = [], []
    for index, pose in enumerate(poses):
        _, _, a, b = pet_landmarks(pose)
        q = pose.convertToFormat(QImage.Format_RGBA8888)
        image = Image.frombytes("RGBA", (q.width(), q.height()), bytes(q.constBits()))
        image = image.resize((round(image.width * sx), round(image.height * sy)), Image.Resampling.NEAREST)
        offset = (round(foot - (a + b) / 2 * sx), 130 - image.height)
        registered = Image.new("RGBA", canonical.size)
        registered.paste(image, offset)
        frame = canonical.copy()
        head = (48, 34, 136, 108)
        frame.paste(registered.crop(head), head[:2])
        assert frame.crop((0,108,192,144)).tobytes() == canonical.crop((0,108,192,144)).tobytes()
        assert frame.getbbox()[0] >= 2 and frame.getbbox()[2] < 190
        generated.append(frame)
        registrations.append({"source":index,"xy":offset,"size":image.size})
    base = Image.open(ROOT / "references/look-tilt/2026-10-23/updated-look-base.png").convert("RGBA")
    assert base.size == (768,576)
    sheet = Image.new("RGBA", (768,864))
    sheet.paste(base, (0,0))
    selection = (1,2,3,0,5,6,7,4)
    for slot, source in enumerate(selection,16):
        sheet.paste(generated[source], (slot % 4 * 192, slot // 4 * 144))
    sheet.save(ROOT / "assets/neko-idle-look-v2.png")
    record_path = ROOT / "docs/look-tilt-prompts.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["assembly"] = {"source_boxes":boxes,"batch_scale":[sx,sy],"registrations":registrations,
                          "source_support_target_on_canonical_head_axis":foot,"head_neck_region":[48,34,136,108],
                          "appended_source_order":selection,"base_cells_preserved":16,
                          "output":"assets/neko-idle-look-v2.png","canvas":[192,144],
                          "method":"Preserve updated glance cells; use one neutral calibration/support registration for drawn head/neck tilts. Lower body/tail remains exact canonical. Opposite head tilts authored separately, no full-body mirroring or rotation."}
    record_path.write_text(json.dumps(record,indent=2),encoding="utf-8")


if __name__ == "__main__":
    assemble()
