"""Compare the previous breathing rest with the seated resettle."""
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
        previous, old = frozen(before, folder, "previous_breath")
        retained = [key for key in old.frames if key[0] != "idle-v2-rest"]
        assert all(old.frames[key].toImage() == atlas.frames[key].toImage() for key in retained)
        unchanged = [name for name in CLIPS if name != "idle"]
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unchanged)
        frames = []
        for index in range(120):
            canvas = Image.new("RGB", (480, 222), "#f8f5ee")
            draw = ImageDraw.Draw(canvas)
            draw.text((16, 10), "PREVIOUS: BREATHING", font=font, fill="#6c6259")
            draw.text((256, 10), "NEW: SEATED SETTLE", font=font, fill="#6c6259")
            for column, source in enumerate((old, atlas)):
                frame = pixels(source.frame("idle", index / 10))
                canvas.paste(frame, (24 + column * 240, 36), frame)
            draw.text((16, 195), "Native size, normal speed | fixed head and paws", font=font, fill="#6c6259")
            frames.append(canvas)
        frames[0].save(ROOT / "docs/seated-idle-compare.gif", save_all=True,
                       append_images=frames[1:], duration=100, loop=0, disposal=2)
    sheet = Image.new("RGB", (768, 350), "#f8f5ee")
    draw = ImageDraw.Draw(sheet)
    names = ("Quiet sit", "Ear response", "Foreleg yield", "Settle hold", "Close", "Happy blink", "Reopen", "Recover")
    for index, title in enumerate(names):
        frame = pixels(atlas.frames["idle-v2-rest", index // 4, index % 4])
        left, top = index % 4 * 192, index // 4 * 175
        sheet.paste(frame, (left, top), frame)
        draw.text((left + 12, top + 147), title, font=font, fill="#6c6259")
    sheet.save(ROOT / "docs/seated-idle-frames.png")
    components = []
    for index in range(8):
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
              "unchanged_clips":unchanged, "blink_ms":300, "loop_ms":sum(CLIPS["idle"].durations),
              "components_alpha128":components, "new_authored_source_cells":8, "order":CLIPS["idle"].order,
              "durations_ms":CLIPS["idle"].durations}
    assert len(atlas.frames) == 904 and len(retained) == 895 and len(unchanged) == 64
    (ROOT / "docs/seated-idle-metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (ROOT / "docs/seated-idle-compare.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko seated idle</title><style>body{background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:800px;margin:32px auto;padding:0 16px}img{max-width:100%;image-rendering:pixelated}p{line-height:1.6}</style><main><h1>A quiet little sit.</h1><p>Previous breathing idle on the left; new seated idle on the right. Native desktop size, normal speed, synchronized time. No breathing pulse or whole-body bob: one small foreleg/shoulder resettle over planted paws, an ear response and a brisk happy blink.</p><img width="480" height="222" src="seated-idle-compare.gif" alt="Previous breathing and new seated resting idle side by side"><p>5.8-second loop with a 300 ms blink and 4.5 seconds of shared quiet holds. The 12-second comparison shows two complete cycles.</p><img width="768" height="350" src="seated-idle-frames.png" alt="Eight seated gesture drawings"><p>Updated tilted left/right looks, original lazy tail and accepted tail chase/catch remain unchanged.</p><a href="seated-idle-validation.md">Source, checks and limits</a></main></html>', encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    preview(Path(sys.argv[1]))
