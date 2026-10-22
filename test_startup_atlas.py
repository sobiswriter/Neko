"""The packaged atlas must skip preprocessing without changing a single pixel."""
import os
import json
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas
from tools.bake_atlas import bake

APP = QApplication.instance() or QApplication([])
ROOT = Path(__file__).parent


class StartupAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = SpriteAtlas(ROOT / "assets")

    def test_baked_frames_are_pixel_identical_and_skip_source_processing(self):
        with tempfile.TemporaryDirectory() as folder:
            bake(self.original, Path(folder))
            with patch("animations.sprite_bounds", side_effect=AssertionError("Source processing at startup")):
                loaded = SpriteAtlas(folder)
            self.assertEqual(loaded.frames.keys(), self.original.frames.keys())
            for key, frame in self.original.frames.items():
                self.assertEqual(loaded.frames[key].toImage(), frame.toImage(), key)

    def test_damaged_bake_falls_back_to_the_source_loader(self):
        for metadata in ('not json', '[]', '[["idle", 0, 0]]', json.dumps(list(self.original.frames))):
            with self.subTest(metadata=metadata), tempfile.TemporaryDirectory() as folder:
                Path(folder, "neko-runtime.json").write_text(metadata)
                with patch("animations.QImage", wraps=QImage) as read_image:
                    # Missing raw sheets remain a safe empty atlas, as before.
                    loaded = SpriteAtlas(folder)
                self.assertEqual(loaded.frames, {})
                self.assertIn(call(str(Path(folder, "neko-idle-v3.png"))), read_image.call_args_list)


if __name__ == "__main__":
    unittest.main()
