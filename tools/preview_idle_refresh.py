"""Compare quiet idles against an explicitly supplied pre-refresh executable."""
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
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, CLIPS, IDLE_ROWS

ITEMS = [("idle", "Resting idle"), ("loaf", "Cozy loaf"), ("stretch", "Front stretch"),
         ("groom", "Paw grooming"), ("yawn", "Yawn"), ("peek", "Sleepy peek"),
         ("ears", "Ear flick"), ("sniff", "Curious sniff"), ("look_left", "Look left"),
         ("look_right", "Look right"), ("tail", "Lazy tail swish")]


def pixels(frame):
    image = frame.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes("RGBA", (image.width(), image.height()), bytes(image.constBits()))


def displayed(atlas, clips, name, elapsed, previous):
    if name != "idle":
        if elapsed < .8:
            name = "idle"
        else:
            elapsed -= .8
            deadline = (8 if name == "loaf" else 6) if previous else sum(clips[name].durations) / 1000
            if elapsed >= deadline:
                elapsed -= deadline
                name = "idle"
    return pixels(atlas.frame(name, round(elapsed, 3)))


def preview(executable):
    app = QApplication.instance() or QApplication([])
    current = SpriteAtlas(ROOT / "assets")
    archive = CArchiveReader(str(executable))
    previous = ModuleType("previous_idle_animations")
    sys.modules[previous.__name__] = previous
    exec(archive.open_embedded_archive("PYZ.pyz").extract("animations"), previous.__dict__)
    names = {name.replace("\\", "/"): name for name in archive.toc}
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    folder = ROOT / "docs"
    with tempfile.TemporaryDirectory() as temporary:
        for name in ("neko-runtime.png", "neko-runtime.json"):
            Path(temporary, name).write_bytes(archive.extract(names["assets/" + name]))
        old = previous.SpriteAtlas(temporary)
        retained = [key for key in old.frames if key in current.frames]
        assert all(old.frames[key].toImage() == current.frames[key].toImage() for key in retained)
        allowed = {name for name, _ in ITEMS}
        unchanged = [name for name in CLIPS if name not in allowed]
        assert all(asdict(CLIPS[name]) == asdict(previous.CLIPS[name]) for name in unchanged)
        assert len(current.frames) == len(retained) + sum(IDLE_ROWS.values()) * 4 + len(IDLE_ROWS)
        for name, title in ITEMS:
            frames = []
            count = round(sum(CLIPS[name].durations) / 1000 * 20) if name == "idle" else 112
            for index in range(count):
                elapsed = index / 10
                canvas = Image.new("RGB", (480, 222), "#f8f5ee")
                draw = ImageDraw.Draw(canvas)
                draw.text((16, 10), "OLD", font=font, fill="#6c6259")
                draw.text((256, 10), "UPDATED", font=font, fill="#6c6259")
                draw.line((240, 8, 240, 197), fill="#ddd2c5")
                for column, (atlas, clips, is_old) in enumerate(((old, previous.CLIPS, True), (current, CLIPS, False))):
                    frame = displayed(atlas, clips, name, elapsed, is_old)
                    canvas.paste(frame, (24 + column * 240, 36), frame)
                draw.text((16, 195), title + "  |  actual speed, same scale", font=font, fill="#6c6259")
                frames.append(canvas)
            frames[0].save(folder / f"idle-refresh-{name}-compare.gif", save_all=True,
                           append_images=frames[1:], duration=100, loop=0, disposal=2)
            print(name, "compared", flush=True)
    sheet = Image.new("RGB", (192 * 8 + 160, 180 * len(ITEMS)), "#f8f5ee")
    draw = ImageDraw.Draw(sheet)
    for row, (name, title) in enumerate(ITEMS):
        clip = CLIPS[name]
        order = list(dict.fromkeys(clip.order))
        selected = [order[round(i * (len(order)-1) / 7)] for i in range(8)]
        draw.text((8, row * 180 + 8), title, font=font, fill="#6c6259")
        for column, index in enumerate(selected):
            frame = pixels(current.frames[clip.bank, clip.row + index // 4, index % 4])
            left, top = 160 + column * 192, row * 180 + 22
            sheet.paste(frame, (left, top), frame)
            draw.text((left + 8, row * 180 + 162), str(index), font=font, fill="#6c6259")
    sheet.save(folder / "idle-refresh-keys.png")
    links = "".join(f'<button data-name="{name}">{title}</button>' for name, title in ITEMS)
    (folder / "idle-refresh-compare.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neko idle refresh - before and after</title><style>body{margin:0;background:#f8f5ee;color:#403b36;font:16px system-ui}main{max-width:1000px;margin:32px auto;padding:0 20px}h1{font-size:28px}nav{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}button{font:inherit;padding:8px 12px;border:1px solid #d2c7ba;border-radius:10px;background:#fffaf3;color:inherit;cursor:pointer}button[aria-pressed=true]{background:#e8d3cb;border-color:#aa7c72}img{display:block;width:480px;max-width:100%;image-rendering:pixelated;border:1px solid #ded2c4;border-radius:12px}p{line-height:1.6}a{color:#84564b}</style><main><h1>A little more life, a little more rest.</h1><p>Old on the left, updated on the right. Same character scale, synchronized time, original playback speed. Resting idle has priority; tail chase and tail catch are unchanged.</p><nav aria-label="Compare an idle">''' + links + '''</nav><img id="comparison" src="idle-refresh-idle-compare.gif" alt="Old and updated resting idle side by side"><p>Each finite gesture plays once and returns to quiet rest. The comparison repeats for review. Production does not repeat gestures this quickly. Resting idle includes long open-eyed pauses and a brief natural blink.</p><p><a href="idle-refresh-keys.png">Expression and transition key frames</a> · <a href="idle-refresh-validation.md">Verification and remaining limits</a></p></main><script>const image=document.getElementById('comparison');const buttons=[...document.querySelectorAll('button')];buttons.forEach(button=>button.onclick=()=>{buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));image.src='idle-refresh-'+button.dataset.name+'-compare.gif';image.alt='Old and updated '+button.textContent+' side by side';});buttons[0].setAttribute('aria-pressed','true');</script></html>''', encoding="utf-8")
    result = {"retained_pixel_identical_frames": len(retained), "retired_idle_frames": len(old.frames) - len(retained),
              "new_frames": len(current.frames) - len(retained), "atlas_entries": len(current.frames),
              "unchanged_clips": unchanged, "comparison_clips": [name for name, _ in ITEMS],
              "durations_ms": {name: sum(CLIPS[name].durations) for name, _ in ITEMS},
              "protected_tail_clips_identical": all(name in unchanged for name in ("tail_chase", "tail_catch"))}
    (folder / "idle-refresh-metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    preview(Path(sys.argv[1]))
