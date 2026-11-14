"""Prepare the user's hand-picked kitten sounds for Neko 1.2.

Input: ``assets-incoming/sounds/`` (the generator kept the start of each brief description as
the filename). Output: ``assets/sounds/<cue>-<n>.wav``: 44.1 kHz, 16-bit mono, leading silence
trimmed, short fade-out, all cues levelled to one soft loudness with a peak limit, and purrs made
seamlessly loopable. Writes ``docs/sound-credits.md``. Needs ffmpeg on PATH (development only;
the app plays the prepared WAV files with the standard-library ``winsound``).
"""
import hashlib
import math
from array import array
from pathlib import Path
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets-incoming" / "sounds"
OUTPUT = ROOT / "assets" / "sounds"
RATE = 44100

# Filename start (from the sound brief's descriptions) -> cue. Matched case-insensitively.
CUES = (
    ("a_tiny,_soft,_rising", "mew"),            # "a tiny, soft, rising mew?"
    ("2–4_s,_loopable", "purr"),                 # "2–4 s, loopable … steady soft purr"
    ("a_steady,_soft,_clos", "purr"),            # "a steady, soft, close purr"
    ("the_bright_brrp", "chirp"),                # "the bright brrp! / trill"
    ("an_excited_rolling", "trill"),             # "an excited rolling mrrrp!"
    ("a_short,_breathy_kit", "question"),        # "a short curious mrr? with an upward ending"
    ("a_kitten's_soft,_bre", "yawn"),            # "a kitten yawn, a little squeak at the end"
    ("soft,_tiny_kitten_br", "protest"),         # the remaining set: the short complaining mrrow
    ("sad-mew", "sad"),
    ("demand-meow", "demand"),
    ("giggle-chatter", "giggle"),
)
# Target loudness of the voiced part (dBFS RMS) and the peak ceiling. Purr sits under the voice.
LOUDNESS = {"purr": -31.0}
DEFAULT_LOUDNESS, PEAK_CEILING = -25.0, -5.0


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1",
                          "-ar", str(RATE), "-"], check=True, capture_output=True).stdout
    return array("h", raw)


def rms(samples):
    return math.sqrt(sum(s * s for s in samples) / max(1, len(samples)))


def envelope(samples, window=441):
    return [rms(samples[i:i + window]) for i in range(0, max(1, len(samples) - window), window)]


def trim(samples, window=441):
    env = envelope(samples, window)
    top = max(env) or 1
    voiced = [i for i, e in enumerate(env) if e > top * 0.06]
    if not voiced:
        return samples
    start = max(0, voiced[0] * window - 441)        # keep 10 ms of breath before the onset
    end = min(len(samples), (voiced[-1] + 1) * window + 2205)  # 50 ms of tail
    return samples[start:end]


def level(samples, cue, voiced):
    target = 10 ** (LOUDNESS.get(cue, DEFAULT_LOUDNESS) / 20) * 32767
    gain = target / max(1.0, rms(voiced))
    peak = max(abs(s) for s in samples) or 1
    gain = min(gain, 10 ** (PEAK_CEILING / 20) * 32767 / peak)
    return array("h", (max(-32767, min(32767, round(s * gain))) for s in samples))


def fade(samples, out_ms=40, in_ms=4):
    n_out, n_in = RATE * out_ms // 1000, RATE * in_ms // 1000
    out = array("h", samples)
    for i in range(min(n_in, len(out))):
        out[i] = round(out[i] * i / n_in)
    for i in range(min(n_out, len(out))):
        out[-1 - i] = round(out[-1 - i] * i / n_out)
    return out


def loopable(samples, cross_ms=250):
    """Crossfade the tail into the head so the purr can repeat without a click or a gap."""
    n = RATE * cross_ms // 1000
    body, tail = samples[n:len(samples) - n], samples[len(samples) - n:]
    head = samples[:n]
    mixed = array("h", (round(t * (1 - i / n) + h * (i / n)) for i, (t, h) in enumerate(zip(tail, head))))
    return body + mixed


def write(path, samples):
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(samples.tobytes())


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    counters, rows = {}, []
    for path in sorted(SOURCE.iterdir(), key=lambda p: p.name.casefold()):
        cue = next((c for prefix, c in CUES if path.name.casefold().startswith(prefix)), None)
        if cue is None:
            print("skipped (unknown cue):", path.name)
            continue
        samples = decode(path)
        if cue == "purr":
            voiced = samples
            samples = loopable(level(samples, cue, voiced))
        else:
            samples = trim(samples)
            samples = fade(level(samples, cue, samples))
        counters[cue] = counters.get(cue, 0) + 1
        name = f"{cue}-{counters[cue]}.wav"
        write(OUTPUT / name, samples)
        rows.append((name, path.name, hashlib.sha256(path.read_bytes()).hexdigest()[:16],
                     round(len(samples) / RATE, 2)))
        print(f"{name:14} {len(samples) / RATE:5.2f}s  <- {path.name}")
    lines = ["# Sound credits", "",
             "Neko 1.2's kitten sounds were hand-picked by the project owner (Sobi) and supplied in",
             "`assets-incoming/sounds/`. `tools/prepare_sounds.py` trims, levels and (for purrs) loops",
             "them; it does not otherwise alter the recordings. The earlier synthesized `mew.wav`,",
             "`purr.wav` and `chirp.wav` (from `tools/make_sounds.py`) remain only as a fallback.", "",
             "| Runtime file | Source file | Source sha256 (first 16) | Seconds |", "|---|---|---|---|"]
    lines += [f"| `{a}` | `{b}` | `{c}` | {d} |" for a, b, c, d in rows]
    (ROOT / "docs" / "sound-credits.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
