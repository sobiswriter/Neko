from array import array
from pathlib import Path
import unittest
import wave


class SoundAssetTests(unittest.TestCase):
    def test_cues_are_short_soft_pcm_with_silent_edges(self):
        for kind in ("mew", "chirp", "purr"):
            with wave.open(str(Path(__file__).parent / "assets" / "sounds" / f"{kind}.wav"), "rb") as audio:
                self.assertEqual((audio.getnchannels(), audio.getsampwidth()), (1, 2))
                duration = audio.getnframes() / audio.getframerate()
                self.assertTrue(0.4 <= duration <= 1)
                data = array("h", audio.readframes(audio.getnframes()))
            self.assertLess(max(map(abs, data)), 32767 * 0.08)
            self.assertGreater(max(map(abs, data)), 100)
            self.assertLess(abs(data[0]) + abs(data[-1]), 5)
