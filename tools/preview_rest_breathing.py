"""Compare the previous eye-only rest with the newly authored breathing loop."""
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
        previous, old = frozen(before, folder, "eye_only_rest")
        retained = [key for key in old.frames if key[0] != "idle-v2-rest"]
        assert all(old.frames[key].toImage() == atlas.frames[key].toImage() for key in retained)
        unchanged = [name for name in CLIPS if name != "idle"]
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unchanged)
        frames = []
        for index in range(120):
            canvas = Image.new("RGB", (480, 222), "#f8f5ee")
            draw = ImageDraw.Draw(canvas)
            draw.text((16, 10), "PREVIOUS: EYES ONLY", font=font, fill="#6c6259")
            draw.text((256, 10), "NEW: BREATH + BLINK", font=font, fill="#6c6259")
            for column, source in enumerate((old, atlas)):
                frame = pixels(source.frame("idle", index / 10))
                canvas.paste(frame, (24 + column * 240, 36), frame)
            draw.text((16, 195), "Native size, normal speed | fixed head and paws", font=font, fill="#6c6259")
            frames.append(canvas)
        frames[0].save(ROOT / "docs/rest-breathing-compare.gif", save_all=True,
                       append_images=frames[1:], duration=100, loop=0, disposal=2)
    sheet = Image.new("RGB", (768, 350), "#f8f5ee")
    draw = ImageDraw.Draw(sheet)
    names = ("Settle", "Inhale", "Full chest", "Close", "Happy blink", "Reopen", "Exhale", "Recover")
    for index, title in enumerate(names):
        frame = pixels(atlas.frames["idle-v2-rest", index // 4, index % 4])
        left, top = index % 4 * 192, index // 4 * 175
        sheet.paste(frame, (left, top), frame)
        draw.text((left + 12, top + 147), title, font=font, fill="#6c6259")
    sheet.save(ROOT / "docs/rest-breathing-frames.png")
    result = {"atlas_entries":len(atlas.frames), "unchanged_frames":len(retained),
              "unchanged_clips":unchanged, "blink_ms":300, "loop_ms":sum(CLIPS["idle"].durations),
              "new_authored_source_cells":8, "order":CLIPS["idle"].order,
              "durations_ms":CLIPS["idle"].durations}
    assert len(atlas.frames) == 887 and len(retained) == 878 and len(unchanged) == 64
    (ROOT / "docs/rest-breathing-metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (ROOT / "docs/rest-breathing-compare.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko resting breath</title><style>body{background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:800px;margin:32px auto;padding:0 16px}img{max-width:100%;image-rendering:pixelated}p{line-height:1.6}</style><main><h1>A quiet breath and a happy blink.</h1><p>Previous eye-only rest on the left, newly drawn breathing and expressions on the right. Native desktop size, normal speed. Chest/shoulders breathe locally; head height, paws, tail and physical scale stay anchored.</p><img width="480" height="222" src="rest-breathing-compare.gif" alt="Previous eye-only and new breathing resting idle side by side"><p>Four-second loop with a quick300ms happy blink and quiet holds. The comparison repeats for review.</p><img width="768" height="350" src="rest-breathing-frames.png" alt="Eight newly authored breathing and happy blink phases"><p>Original left/right looks and lazy tail remain restored. Other animations are unchanged.</p><a href="rest-breathing-validation.md">Source, checks and limits</a></main></html>''', encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    preview(Path(sys.argv[1]))
