"""Neko's voice: hand-picked kitten sounds with several takes per cue.

Each cue picks a random take, never the same file twice in a row, so she doesn't sound like a
loop. Playback uses the standard library's asynchronous ``winsound``; a looping purr can run
while she is petted and is stopped when the pet ends. Falls back to the original synthesized
``mew/purr/chirp.wav`` when a cue has no prepared takes.
"""
from pathlib import Path
import random

try:
    import winsound
except ImportError:  # Non-Windows test environments.
    winsound = None

CUES = ("mew", "purr", "chirp", "trill", "question", "yawn", "protest", "sad", "demand", "giggle")
# Older one-file names, and cues that may stand in when a cue has no takes of its own.
FALLBACK = {"mew": "mew", "purr": "purr", "chirp": "chirp", "trill": "chirp", "question": "mew",
            "yawn": "mew", "protest": "mew", "sad": "mew", "demand": "mew", "giggle": "chirp"}


class Voice:
    def __init__(self, folder, rng=None):
        self.folder = Path(folder)
        self.rng = rng or random.Random()
        self.takes = {cue: sorted(self.folder.glob(f"{cue}-*.wav")) for cue in CUES}
        self.last = {}
        self.looping = False

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

    def play(self, cue, loop=False):
        """Start a cue asynchronously. Returns the file played, or None."""
        path = self.pick(cue)
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
