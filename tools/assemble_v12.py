"""Assemble the user-generated Neko 1.2 sheets into packed, labelled source assets.

Input: the raw sheets in ``assets-incoming/`` (4 x 3 drawings each, transparent background).
Output: ``assets/neko-v12-<bank>.png`` (12 complete crops in 448px cells, bottom-aligned on a
shared baseline) and ``docs/v1.2-assembly.json`` (source file, sha256, crop regions, labels).

Each drawing is cropped to its main connected silhouette. Detached motion marks, sparkles and
"!" glyphs that the generator added are dropped (only alpha connected to the kitten is kept).
No anatomy is painted or moved. Run: python tools/assemble_v12.py
"""
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

CELL, BASELINE = 448, 436

# bank -> (incoming file, prompt id, 12 cell labels)
SHEETS = {
    "win-sproing-a": ("Bouncy White Cat Pixel Sprite Sheet-1.png", "W1a", (
        "neutral", "realises she won (sparkle eyes)", "pops up, tail rising", "arch, happy squeeze",
        "bounce 1 launch", "bounce 1 top", "coming down", "stiff landing",
        "bounce 2 launch", "bounce 2 top (happiest)", "coming down", "landing crouch")),
    "win-sproing-c": ("Bouncing White Kitten Pixel Sprite Sheet-2.png", "W1a (second take)", (
        "neutral", "realises she won", "pops up, tail rising", "arch, happy squeeze",
        "bounce 1 launch", "bounce 1 top", "coming down", "landing",
        "bounce 2 launch", "bounce 2 top", "coming down", "landing crouch")),
    "win-sproing-b": ("Playful White Cat Pixel Sprite Sheet.png", "W1b", (
        "arched bridge", "bounce 3 launch", "bounce 3 top", "light landing",
        "arch relaxes", "half-sit", "proud squeeze", "happy head wiggle",
        "smug half-lids", "contented blink", "eyes reopen", "neutral")),
    "win-roll-a": ("victory 1.png", "W2a", (
        "neutral", "pounce wiggle", "pounce", "pins the prize",
        "rolls onto side", "belly up", "wiggle A", "wiggle B",
        "wiggle A, bigger smile", "bicycle kick", "dreamy pause", "rolling back")),
    "win-roll-b": ("Victory 1 p2.png", "W2b", (
        "lying on side", "head lifts", "sphinx", "four-paw crouch",
        "sits, head shake", "full-body fluff shake", "settles, bright eyes", "proud paw",
        "smug blink", "eyes reopen", "tail curls", "neutral")),
    "dodge-tease": ("Pixel-Art White Kitten Pose Sheet.png", "D1", (
        "neutral", "notices, head tilt", "stalking crouch", "creep step 1",
        "creep step 2", "stops", "rump rises", "butt wiggle",
        "come-on paw swipe", "play-bow wink", "play-bow", "ready stance")),
    "dodge-sidestep": ("Pixel Kitten Animation Sprite Sheet.png", "D2", (
        "ready stance", "tell: leans away", "gathered crouch", "launch",
        "mid-air", "forepaws reach", "fore landing", "safe landing",
        "cheeky wink", "cheeky look", "head forward", "ready stance")),
    "dodge-duck": ("Pixel Cat Duck-and-Recover Sprite Sheet.png", "D3", (
        "ready stance", "tell: eyes up", "ducks", "pancake flat",
        "peeks one eye", "eyes open", "pushes up", "crouch",
        "giggle", "giggle, paw to mouth", "cheeky smile", "ready stance")),
    "dodge-tagged": ("Cute Pixel Cat Sticker Sheet.png", "D4", (
        "neutral", "surprise recoil", "hops back", "lands blinking",
        "mock indignation", "puff and tail lash", "smile wobbles", "giggle, paw to mouth",
        "giggle tipped", "determined cheeky", "stands", "ready")),
    "dodge-caught": ("Pixel Cat Emote Sticker Sheet.png", "D5", (
        "ready", "ah!", "sits laughing", "tips over",
        "belly up laughing", "paws over face", "peeks", "open-paw shrug",
        "rolls to side", "sphinx smile", "good-game blink", "neutral")),
    "restless-sigh": ("Pixel Kitten Emotion Sprite Sheet.png", "R1", (
        "neutral", "glances at you", "hopeful", "ears droop",
        "inhale", "sigh out", "slumps", "chin on paws, looks left",
        "chin on paws, pout", "head lifts", "sits back up", "neutral")),
    "restless-jealous": ("Pixel Cat Animation Sprite Sheet.png", "R2", (
        "neutral", "head snaps left", "glare", "puffed hmph",
        "nose in the air", "one-eye peek", "glare, tail lash", "paw stamp up",
        "paw stamp down", "stalking stance", "jealous pounce-hop", "lands stalking")),
    "restless-demand": ("Pixel Cat Emote Sprite Sheet.png", "R3", (
        "neutral", "pleading eyes", "begging, paws up", "paw reach",
        "paw tap, mew!", "determined pout", "four paws", "head-butt",
        "cheek rub", "pleading again", "impatient tail flick", "neutral")),
    "restless-forgive": ("Pixel Cat Expressions Sticker Sheet.png", "R4", (
        "leftover pout", "pout softens", "happy squeeze", "leans into the hand",
        "melts into loaf", "loaf", "one eye opens warmly", "warm eyes",
        "rises to sit", "head tilt", "bright eyes", "neutral")),
    "move-leap-up": ("Pixel Cat Leap Animation Sheet.png", "M1", (
        "standing, looks up", "measures the jump", "deep crouch", "push-off",
        "rising stretch", "peak", "fore-contact", "hind legs gather",
        "four-paw landing", "standing", "looks back", "standing")),
    "move-leap-down": ("Kawaii Pixel Cat Hop Sprite Sheet.png", "M2", (
        "standing, looks down", "peers down", "small crouch", "steps off",
        "falling", "forepaws about to touch", "fore-contact", "hind legs swing down",
        "landing, compressed", "head shake", "looks around", "standing")),
    "move-pouncehop": ("Pixel Cat Bounce Animation Sprite Sheet.png", "M3", (
        "standing", "quick crouch", "bouncy launch", "mid-hop",
        "fore landing", "landing", "skid stop", "sits, looks around",
        "turn begins", "turn mid", "turn completes (faces right)", "standing (faces right)")),
    "dizzy-a": ("Dizzy Pixel Cat Sprite Sheet.png", "Z1", (
        "neutral", "looks left", "snaps right", "snaps left",
        "eyes crossing", "spiral eyes, circle left", "circle forward", "circle right, tongue",
        "circle up", "sway left", "sway right", "centred wobble")),
    "dizzy-b": ("Kawaii Pixel Cat Sprite Sheet.png", "Z2", (
        "centred wobble", "steadying paw", "eyes squeezed", "head shake left",
        "head shake right", "squeezed, centred", "unfocused blink", "half-lids",
        "focused", "relieved sigh", "settles", "neutral")),
}


def components(image, box):
    """Main 8-connected alpha>=128 silhouette inside box; returns (crop, kept-bounds)."""
    x0, y0, x1, y1 = box
    crop = image.copy(x0, y0, x1 - x0, y1 - y0).convertToFormat(QImage.Format_ARGB32)
    w, h = crop.width(), crop.height()
    # Keep the converted image alive while its buffer is copied (a temporary's memory can be freed).
    alpha_image = crop.convertToFormat(QImage.Format_Alpha8)
    alpha = bytes(alpha_image.constBits())
    stride = alpha_image.bytesPerLine()
    solid = bytearray(w * h)
    for y in range(h):
        row = alpha[y * stride:y * stride + w]
        for x in range(w):
            solid[y * w + x] = row[x] >= 128
    label = bytearray(w * h)
    best, best_size = None, 0
    for start in range(w * h):
        if solid[start] and not label[start]:
            stack, members = [start], []
            label[start] = 1
            while stack:
                p = stack.pop()
                members.append(p)
                px, py = p % w, p // w
                for dy in (-1, 0, 1):
                    yy = py + dy
                    if 0 <= yy < h:
                        for dx in (-1, 0, 1):
                            xx = px + dx
                            q = yy * w + xx
                            if 0 <= xx < w and solid[q] and not label[q]:
                                label[q] = 1
                                stack.append(q)
            if len(members) > best_size:
                best, best_size = members, len(members)
    keep = bytearray(w * h)
    for p in best:
        keep[p] = 1
    # Grow the kept region by 2px so the soft anti-aliased rim around the outline survives.
    for _ in range(2):
        grown = bytearray(keep)
        for p in range(w * h):
            if keep[p]:
                px, py = p % w, p // w
                for q in (p - 1, p + 1, p - w, p + w):
                    if 0 <= q < w * h and abs(q % w - px) <= 1:
                        grown[q] = 1
        keep = grown
    out = QImage(w, h, QImage.Format_ARGB32)
    out.fill(Qt.transparent)
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if keep[y * w + x]:
                c = crop.pixelColor(x, y)
                if c.alpha():
                    out.setPixelColor(x, y, c)
                    xs.append(x)
                    ys.append(y)
    left, top, right, bottom = min(xs), min(ys), max(xs) + 1, max(ys) + 1
    return out.copy(left, top, right - left, bottom - top), (x0 + left, y0 + top, x0 + right, y0 + bottom)


def cell_boxes(image, count=12, step=3, margin=10):
    """The drawings in reading order, located by their own silhouettes (a pose may cross the
    nominal grid line, so fixed grid cells would cut it)."""
    w, h = image.width(), image.height()
    alpha = image.convertToFormat(QImage.Format_Alpha8)
    data, stride = bytes(alpha.constBits()), alpha.bytesPerLine()
    gw, gh = w // step, h // step
    solid = bytearray(gw * gh)
    for y in range(gh):
        row = y * step * stride
        for x in range(gw):
            solid[y * gw + x] = data[row + x * step] >= 128
    seen, found = bytearray(gw * gh), []
    for start in range(gw * gh):
        if solid[start] and not seen[start]:
            stack, n = [start], 0
            seen[start] = 1
            x0 = y0 = 1 << 30
            x1 = y1 = -1
            while stack:
                p = stack.pop()
                n += 1
                px, py = p % gw, p // gw
                x0, x1, y0, y1 = min(x0, px), max(x1, px), min(y0, py), max(y1, py)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        qx, qy = px + dx, py + dy
                        q = qy * gw + qx
                        if 0 <= qx < gw and 0 <= qy < gh and solid[q] and not seen[q]:
                            seen[q] = 1
                            stack.append(q)
            found.append((n, (x0 * step, y0 * step, (x1 + 1) * step, (y1 + 1) * step)))
    found.sort(reverse=True)
    if len(found) < count or found[count - 1][0] < 20 * found[count][0] if len(found) > count else False:
        raise ValueError("expected exactly %d kittens, found sizes %s" % (count, [n for n, _ in found[:count + 2]]))
    boxes = [b for _, b in found[:count]]
    # Reading order: rows by vertical centre (three bands), then left to right.
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = [sorted(boxes[i:i + 4]) for i in range(0, count, 4)]
    return [(max(0, x0 - margin), max(0, y0 - margin), min(w, x1 + margin), min(h, y1 + margin))
            for row in rows for x0, y0, x1, y1 in row]


def main():
    app = QApplication.instance() or QApplication([])
    record = {"tool": "tools/assemble_v12.py", "cell": CELL, "baseline": BASELINE,
              "method": "main alpha>=128 silhouette per grid cell, +2px soft rim; detached marks dropped; "
                        "complete original RGBA; bottom-aligned; no anatomy painted", "sheets": {}}
    for bank, (filename, prompt, labels) in SHEETS.items():
        source = ROOT / "assets-incoming" / filename
        image = QImage(str(source)).convertToFormat(QImage.Format_ARGB32)
        sheet = QImage(4 * CELL, 3 * CELL, QImage.Format_ARGB32)
        sheet.fill(Qt.transparent)
        painter = QPainter(sheet)
        regions = []
        for index, box in enumerate(cell_boxes(image)):
            crop, region = components(image, box)
            if crop.width() > CELL - 8 or crop.height() > BASELINE - 4:
                raise ValueError(f"{bank} cell {index} is too large: {crop.size()}")
            x = index % 4 * CELL + (CELL - crop.width()) // 2
            y = index // 4 * CELL + BASELINE - crop.height()
            painter.drawImage(x, y, crop)
            regions.append({"index": index, "label": labels[index], "source": list(region),
                            "size": [crop.width(), crop.height()]})
        painter.end()
        asset = ROOT / "assets" / f"neko-v12-{bank}.png"
        sheet.save(str(asset))
        # Runtime reads the exact crop sizes instead of re-scanning 12 large cells on every launch.
        (ROOT / "assets" / f"neko-v12-{bank}.json").write_text(
            json.dumps([r["size"] for r in regions]), encoding="utf-8")
        record["sheets"][bank] = {
            "prompt": prompt, "source": f"assets-incoming/{filename}",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "asset": f"assets/{asset.name}", "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
            "regions": regions}
        print(bank, "ok")
    (ROOT / "docs" / "v1.2-assembly.json").write_text(json.dumps(record, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
