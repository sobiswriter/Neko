"""Her voice volume: a scaled copy per level, muted at 0, the bundled file at 100 %."""
import tempfile
import unittest
import wave
from array import array
from pathlib import Path

import sounds

ASSETS = Path(__file__).resolve().parent / "assets" / "sounds"


def peak(path):
    with wave.open(str(path), "rb") as w:
        return max(abs(s) for s in array("h", w.readframes(w.getnframes())))


class VolumeTests(unittest.TestCase):
    def setUp(self):
        self.cache = tempfile.TemporaryDirectory()
        self.voice = sounds.Voice(ASSETS, cache=self.cache.name)
        self.take = sorted(ASSETS.glob("mew-*.wav"))[0]

    def tearDown(self):
        self.cache.cleanup()

    def test_default_level_plays_the_bundled_file(self):
        self.assertEqual(self.voice.at_volume(self.take), self.take)

    def test_zero_mutes(self):
        self.voice.volume = 0
        self.assertIsNone(self.voice.at_volume(self.take))

    def test_levels_scale_the_samples_without_clipping(self):
        original = peak(self.take)
        for level in (50, 200, sounds.VOLUME_MAX):
            self.voice.volume = level
            scaled = self.voice.at_volume(self.take)
            self.assertNotEqual(scaled, self.take)
            self.assertAlmostEqual(peak(scaled), original * level / 100, delta=2)
            self.assertLess(peak(scaled), 32767)
        self.voice.prune()   # Only the current level's copies are kept.
        self.assertEqual([p.name for p in Path(self.cache.name).iterdir()], [f"v{sounds.VOLUME_MAX}"])

    def test_a_new_level_is_prepared_in_the_background(self):
        import threading, time
        self.voice.set_level(150)
        deadline = time.monotonic() + 20
        while any(t.name == "neko-volume" for t in threading.enumerate()) and time.monotonic() < deadline:
            time.sleep(0.05)
        folder = Path(self.cache.name) / "v150"
        expected = {p.name for takes in self.voice.takes.values() for p in takes}
        self.assertEqual({p.name for p in folder.iterdir()}, expected)
        self.assertFalse(list(folder.glob("*.tmp")))
        self.assertEqual(self.voice.at_volume(self.take), folder / self.take.name)

    def test_every_take_has_headroom_for_the_loudest_setting(self):
        for take in ASSETS.glob("*-*.wav"):
            self.assertLess(peak(take) * sounds.VOLUME_MAX / 100, 32767, take.name)


if __name__ == "__main__":
    unittest.main()
