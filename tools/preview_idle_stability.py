"""Compare the rejected refresh with fixed rest and the restored original gestures."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFont
from PyInstaller.archive.readers import CArchiveReader
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, CLIPS
from tools.preview_idle_refresh import pixels, displayed

ITEMS = (("idle", "Resting idle"), ("look_left", "Look left"),
         ("look_right", "Look right"), ("tail", "Lazy tail swish"))


def frozen(path, folder, label):
    archive = CArchiveReader(str(path))
    module = ModuleType(label)
    sys.modules[label] = module
    exec(archive.open_embedded_archive("PYZ.pyz").extract("animations"), module.__dict__)
    names = {name.replace("\\", "/"):name for name in archive.toc}
    target = Path(folder) / label
    target.mkdir()
    for name in ("neko-runtime.png", "neko-runtime.json"):
        (target / name).write_bytes(archive.extract(names["assets/" + name]))
    return module, module.SpriteAtlas(target)


def preview(before, original):
    app = QApplication.instance() or QApplication([])
    current = SpriteAtlas(ROOT / "assets")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    with tempfile.TemporaryDirectory() as folder:
        previous, old = frozen(before, folder, "rejected_idle")
        initial, legacy = frozen(original, folder, "original_idle")
        changed = {name for name, _ in ITEMS}
        unrelated = [name for name in CLIPS if name not in changed]
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unrelated)
        retained = [key for key in old.frames if key[0] not in ("idle-v2-rest", "idle-v2-look", "idle-v2-tail")]
        assert all(old.frames[key].toImage() == current.frames[key].toImage() for key in retained)
        restored = [key for key in legacy.frames if key[0] == "tailswish" or (key[0] == "idleplay-c" and key[1] >= 4)]
        assert all(legacy.frames[key].toImage() == current.frames[key].toImage() for key in restored)
        assert all(asdict(CLIPS[name]) == asdict(initial.CLIPS[name]) for name in changed - {"idle"})
        assert len(current.frames) == 883
        for name, title in ITEMS:
            frames = []
            for index in range(122 if name == "idle" else 112):
                canvas = Image.new("RGB", (480, 222), "#f8f5ee")
                draw = ImageDraw.Draw(canvas)
                draw.text((16, 10), "PREVIOUS", font=font, fill="#6c6259")
                draw.text((256, 10), "FIXED" if name == "idle" else "ORIGINAL RESTORED", font=font, fill="#6c6259")
                for column, (atlas, clips, is_legacy) in enumerate(((old, previous.CLIPS, False), (current, CLIPS, name != "idle"))):
                    frame = displayed(atlas, clips, name, index / 10, is_legacy)
                    canvas.paste(frame, (24 + column * 240, 36), frame)
                draw.text((16, 195), title + " | native size, normal speed", font=font, fill="#6c6259")
                frames.append(canvas)
            frames[0].save(ROOT / f"docs/idle-stability-{name}.gif", save_all=True,
                           append_images=frames[1:], duration=100, loop=0, disposal=2)
        result = {"atlas_entries":len(current.frames), "unchanged_frames_from_previous":len(retained),
                  "restored_pixel_identical_original_frames":len(restored), "unchanged_clips":unrelated,
                  "restored_clips":[name for name in changed if name != "idle"],
                  "protected_tail_chase_catch_identical":True, "blink_ms":300,
                  "rest_loop_ms":sum(CLIPS["idle"].durations), "eye_rectangles":[[67,73,84,93],[94,73,112,93]]}
        (ROOT / "docs/idle-stability-metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    buttons = "".join(f'<button data-name="{name}">{title}</button>' for name, title in ITEMS)
    (ROOT / "docs/idle-stability-compare.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko idle corrections</title><style>body{background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:800px;margin:32px auto;padding:0 16px}nav{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}button{font:inherit;padding:8px 12px;border:1px solid #d2c7ba;border-radius:10px;background:#fffaf3;cursor:pointer}button[aria-pressed=true]{background:#e8d3cb}img{width:480px;max-width:100%;image-rendering:pixelated}p{line-height:1.6}</style><main><h1>A steadier little companion.</h1><p>Previous refresh on the left; corrected rest or restored original gesture on the right. Native size and normal speed. Rest keeps a fixed body with a quick300ms blink. Left/right looks and lazy tail swish return to their original drawings and cadence.</p><nav aria-label="Choose comparison">''' + buttons + '''</nav><img id="comparison" src="idle-stability-idle.gif" alt="Previous and corrected resting idle side by side"><p>Comparisons repeat for review. The other refreshed gestures remain unchanged; tail chase and catch remain protected.</p><a href="idle-stability-validation.md">Checks and remaining limits</a></main><script>const image=document.getElementById('comparison'),buttons=[...document.querySelectorAll('button')];buttons.forEach(button=>button.onclick=()=>{buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));image.src='idle-stability-'+button.dataset.name+'.gif';image.alt='Previous and corrected '+button.textContent+' side by side';});buttons[0].setAttribute('aria-pressed','true');</script></html>''', encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    preview(Path(sys.argv[1]), Path(sys.argv[2]))
