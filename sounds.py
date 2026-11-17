"""Neko's voice: hand-picked kitten sounds with several takes per cue.

Each cue picks a random take, never the same file twice in a row, so she doesn't sound like a
loop. Playback uses the standard library's asynchronous ``winsound``; a looping purr can run
while she is petted and is stopped when the pet ends. Falls back to the original synthesized
``mew/purr/chirp.wav`` when a cue has no prepared takes.
"""
from array import array
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import threading
import wave

try:
    import winsound
except ImportError:  # Non-Windows test environments.
    winsound = None

# Volume slider range (percent of the prepared level). The takes peak at -18 dBFS, so even
# 300 % (+9.5 dB) stays clear of clipping.
VOLUME_MIN, VOLUME_MAX = 0, 300
CUES = ("mew", "purr", "chirp", "trill", "question", "yawn", "protest", "sad", "demand", "giggle", "laugh")
# Older one-file names, and cues that may stand in when a cue has no takes of its own.
FALLBACK = {"mew": "mew", "purr": "purr", "chirp": "chirp", "trill": "chirp", "question": "mew",
            "yawn": "mew", "protest": "mew", "sad": "mew", "demand": "mew", "giggle": "chirp",
            "laugh": "chirp"}


class Voice:
    def __init__(self, folder, rng=None, cache=None):
        self.folder = Path(folder)
        self.rng = rng or random.Random()
        self.takes = {cue: sorted(self.folder.glob(f"{cue}-*.wav")) for cue in CUES}
        self.last = {}
        self.looping = False
        self.volume = 100   # Percent of the prepared (already soft) level, 0-VOLUME_MAX.
        self.cache = Path(cache) if cache else Path(tempfile.gettempdir()) / "DesktopNeko-sounds"

    def available(self, cue):
        return bool(self.takes.get(cue)) or (self.folder / f"{FALLBACK.get(cue, cue)}.wav").exists()

    def pick(self, cue):
        takes = self.takes.get(cue) or []
        if not takes:
            fallback = self.folder / f"{FALLBACK.get(cue, cue)}.wav"
            return fallback if fallback.exists() else None
        choices = [t for t in takes if t != self.last.get(cue)] or takes
        choice = self.rng.choice(choices)
        self.last[cue] = choice
        return choice

    def set_level(self, volume):
        """Change the volume and prepare that level's scaled copies in the background, so the
        first sound at a new level never stalls the animation while its copy is written."""
        self.volume = volume
        if volume in (0, 100) or not any(self.takes.values()):
            return
        def warm():
            for takes in list(self.takes.values()):
                for take in takes:
                    if self.volume != volume:
                        return            # The slider moved on; that level's worker takes over.
                    self.at_volume(take, volume)
            self.prune()
        threading.Thread(target=warm, name="neko-volume", daemon=True).start()

    def prune(self):
        """Keep only the current level's copies."""
        try:
            keep = self.cache / f"v{self.volume}"
            if self.cache.exists():
                for old in self.cache.iterdir():
                    if old.is_dir() and old != keep:
                        shutil.rmtree(old, ignore_errors=True)
        except OSError:
            pass

    def at_volume(self, path, volume=None):
        """The file to play for ``path`` at the volume (percent of the prepared level; default the
        current one). 100 % plays the bundled file; other levels play a scaled copy kept in a cache
        folder, so playback stays asynchronous. Returns None when muted."""
        volume = self.volume if volume is None else volume
        if path is None or volume <= 0:
            return None
        if volume == 100:
            return path
        folder = self.cache / f"v{volume}"
        target = folder / path.name
        if target.exists():
            return target
        try:
            folder.mkdir(parents=True, exist_ok=True)
            with wave.open(str(path), "rb") as source:
                params = source.getparams()
                frames = source.readframes(params.nframes)
            if params.sampwidth != 2:
                return path
            samples = array("h", frames)
            if sys.byteorder != "little":
                samples.byteswap()
            gain = volume / 100
            samples = array("h", (max(-32768, min(32767, round(s * gain))) for s in samples))
            if sys.byteorder != "little":
                samples.byteswap()
            temporary = target.with_suffix(f".{threading.get_ident()}.tmp")
            with wave.open(str(temporary), "wb") as out:
                out.setparams(params)
                out.writeframes(samples.tobytes())
            os.replace(temporary, target)
            return target
        except OSError:
            return path

    def play(self, cue, loop=False):
        """Start a cue asynchronously. Returns the file played, or None."""
        path = self.at_volume(self.pick(cue))
        if path is None or winsound is None:
            return None
        flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
        if loop:
            flags |= winsound.SND_LOOP
        # A new cue replaces the previous one (a giggle cuts a purr short, as a real kitten would).
        winsound.PlaySound(str(path), flags)
        self.looping = loop
        return path

    def stop(self):
        self.looping = False
        if winsound is not None:
            winsound.PlaySound(None, 0)
