"""Compare the accepted seated rest with its mouth-only smile addition."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtWidgets import QApplication
from animations import CLIPS, SpriteAtlas
from tools.preview_idle_stability import frozen
from tools.preview_idle_refresh import pixels


def preview(before):
    app = QApplication.instance() or QApplication([])
    atlas = SpriteAtlas(ROOT / "assets")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    with tempfile.TemporaryDirectory() as folder:
        previous, old = frozen(before, folder, "before_smile")
        retained = [key for key in old.frames if key[0] != "idle-v2-rest"]
        assert all(old.frames[key].toImage() == atlas.frames[key].toImage() for key in retained)
        unchanged = list(CLIPS)
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unchanged)
        for tick in range(116):
            before_frame = pixels(old.frame("idle",tick/20))
            after_frame = pixels(atlas.frame("idle",tick/20))
            for region in ((0,0,192,93),(0,99,192,144),(0,93,83,99),(95,93,192,99)):
                assert before_frame.crop(region).tobytes() == after_frame.crop(region).tobytes(), (tick,region)
        changed_keys = [key for key in old.frames if old.frames[key].toImage() != atlas.frames[key].toImage()]
        assert changed_keys == [("idle-v2-rest",1,2),("idle-v2-rest",1,3),("idle-v2-rest",2,0)], changed_keys
        frames = []
        for index in range(120):
            canvas = Image.new("RGB", (480, 222), "#f8f5ee")
            draw = ImageDraw.Draw(canvas)
            draw.text((16, 10), "PREVIOUS SMILE", font=font, fill="#6c6259")
            draw.text((256, 10), "YOUR SELECTED SMILE", font=font, fill="#6c6259")
            for column, source in enumerate((old, atlas)):
                frame = pixels(source.frame("idle", index / 10))
                canvas.paste(frame, (24 + column * 240, 36), frame)
            draw.text((16, 195), "Native size, normal speed | fixed head and paws", font=font, fill="#6c6259")
            frames.append(canvas)
        frames[0].save(ROOT / "docs/simple-smile-compare.gif", save_all=True,
                       append_images=frames[1:], duration=100, loop=0, disposal=2)
    sheet = Image.new("RGB", (768, 525), "#f8f5ee")
    draw = ImageDraw.Draw(sheet)
    names = ("Quiet sit", "Ear response", "Foreleg yield", "Settle hold", "Close", "Selected smile", "Smile + reopen", "Recover + smile", "Quiet smile", "Selected smile")
    for index, title in enumerate(names):
        frame = pixels(atlas.frames["idle-v2-rest", index // 4, index % 4])
        left, top = index % 4 * 192, index // 4 * 175
        sheet.paste(frame, (left, top), frame)
        draw.text((left + 12, top + 147), title, font=font, fill="#6c6259")
    sheet.save(ROOT / "docs/simple-smile-frames.png")
    components = []
    for index in range(10):
        image = atlas.frames["idle-v2-rest", index//4, index%4].toImage()
        opaque = {(x,y) for y in range(144) for x in range(192)
                  if image.pixelColor(x,y).alpha() >= 128}
        sizes = []
        while opaque:
            pending = [opaque.pop()]
            size = 0
            while pending:
                x,y = pending.pop()
                size += 1
                neighbors = {(x+dx,y+dy) for dx in (-1,0,1) for dy in (-1,0,1)} & opaque
                opaque -= neighbors
                pending.extend(neighbors)
            sizes.append(size)
        significant = [size for size in sizes if size > 2]
        assert len(significant) == 1, (index,sizes)
        components.append(sorted(sizes,reverse=True))
    result = {"atlas_entries":len(atlas.frames), "unchanged_frames":len(retained),
              "unchanged_clips":unchanged, "changed_frames":changed_keys, "all_other_frames_identical":905, "blink_ms":300, "loop_ms":sum(CLIPS["idle"].durations),
              "components_alpha128":components, "reused_body_cells":8, "smile_ms":2900, "order":CLIPS["idle"].order,
              "durations_ms":CLIPS["idle"].durations}
    assert len(atlas.frames) == 908 and len(retained) == 895 and len(unchanged) == 65
    (ROOT / "docs/simple-smile-metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (ROOT / "docs/simple-smile-compare.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko small resting smile</title><style>body{background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:800px;margin:32px auto;padding:0 16px}img{max-width:100%;image-rendering:pixelated}p{line-height:1.6}</style><main><h1>That exact tiny smile.</h1><p>Previous mouth on the left; the exact tiny smile selected in your screenshot on the right, held for half the loop (2.9s). Same5.8s loop, same body/eyes/ears/head, no breathing.</p><img width="480" height="222" src="simple-smile-compare.gif" alt="Accepted seated idle and mouth-only smile addition side by side at native size and normal speed"><img width="768" height="525" src="simple-smile-frames.png" alt="Seated drawings with smile onset, hold and release"><p>All pixels outside the mouth match the accepted version at synchronized times. Other animations remain unchanged.</p><a href="simple-smile-validation.md">Checks and provenance</a></main></html>',encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    preview(Path(sys.argv[1]))
