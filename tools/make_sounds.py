"""Generate Neko's original, deliberately soft pixel-pet cues using only Python."""

import math
from pathlib import Path
import struct
import wave


RATE = 22050


def samples(kind):
    duration = {"mew": 0.72, "chirp": 0.44, "purr": 1.0}[kind]
    phase = 0.0
    for i in range(round(RATE * duration)):
        t = i / RATE
        u = t / duration
        envelope = math.sin(math.pi * u) ** 1.5
        if kind == "purr":
            frequency = 135 + 8 * math.sin(2 * math.pi * 3 * t)
            envelope *= 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * 26 * t))
        else:
            frequency = (590 + 370 * math.sin(math.pi * u) - 200 * u if kind == "mew"
                         else 720 + 360 * math.sin(math.pi * u) - 250 * u)
            frequency += 12 * math.sin(2 * math.pi * 18 * t)
        phase += 2 * math.pi * frequency / RATE
        voice = math.sin(phase) + 0.38 * math.sin(2 * phase) + 0.15 * math.sin(3 * phase)
        yield round(32767 * 0.045 * envelope * voice)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets" / "sounds"
    root.mkdir(parents=True, exist_ok=True)
    for kind in ("mew", "chirp", "purr"):
        data = list(samples(kind))
        with wave.open(str(root / f"{kind}.wav"), "wb") as audio:
            audio.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
            audio.writeframes(struct.pack(f"<{len(data)}h", *data))
