"""Rendered pickup invariants; desktop input cases live in test_main."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import shutil
import tempfile
import unittest
from PySide6.QtWidgets import QApplication
from animations import SpriteAtlas, CLIPS, CARRY_ROWS, CANVAS_WIDTH, CANVAS_HEIGHT, sprite_bounds, held_clip

APP = QApplication.instance() or QApplication([])


class PickupArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = SpriteAtlas(Path(__file__).parent / "assets")

    def test_mood_clock_keeps_global_loop_phase_and_yawns_once(self):
        for elapsed, expected in ((0.2, "pickup"), (1, "held_excited"), (3.1, "carry_to_calm"),
                                  (3.5, "held_calm"), (10.1, "carry_to_unimpressed"),
                                  (11, "held_unimpressed"), (20.1, "carry_yawn"),
                                  (21, "held_sleepy"), (10001, "held_sleepy")):
            self.assertEqual(held_clip(elapsed)[0], expected)
        self.assertEqual(held_clip(3.5)[1], 3.5)
        self.assertEqual(held_clip(100, sleeping=True)[0], "held_sleepy")

    def test_all_carry_drawings_fit_and_have_one_connected_silhouette(self):
        for name, rows in CARRY_ROWS.items():
            for index in range(rows * 4):
                image = self.atlas.frames[f"carry-{name}", index // 4, index % 4].toImage()
                self.assertEqual((image.width(), image.height()), (CANVAS_WIDTH, CANVAS_HEIGHT))
                bounds = sprite_bounds(image)
                self.assertGreater(bounds.left(), 0, (name, index))
                self.assertGreater(bounds.top(), 0, (name, index))
                self.assertLess(bounds.right(), CANVAS_WIDTH - 1, (name, index))
                self.assertLess(bounds.bottom(), CANVAS_HEIGHT - 1, (name, index))
                opaque = {(x, y) for y in range(image.height()) for x in range(image.width())
                          if image.pixelColor(x, y).alpha() >= 128}
                components = []
                while opaque:
                    todo = [opaque.pop()]
                    size = 0
                    while todo:
                        x, y = todo.pop()
                        size += 1
                        for dx, dy in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                            point = x + dx, y + dy
                            if point in opaque:
                                opaque.remove(point)
                                todo.append(point)
                    components.append(size)
                self.assertEqual(sum(n > 2 for n in components), 1, (name, index, components))

    def test_held_moods_preserve_head_scale_anchor_and_body_volume(self):
        centers, heights = [], []
        for name in ("held_excited", "held_calm", "held_unimpressed", "held_sleepy"):
            for elapsed in (0, 0.6, 1.2, 1.8, 2.39):
                image = self.atlas.frame(name, elapsed).toImage()
                runs = []
                for y in range(16, 50):
                    start = None
                    for x in range(image.width() + 1):
                        if x < image.width() and image.pixelColor(x, y).alpha() >= 128:
                            if start is None: start = x
                        elif start is not None:
                            runs.append((x-start,(x-1+start)/2))
                            start = None
                width, center = max(runs)
                self.assertAlmostEqual(width, 62, delta=3, msg=(name, elapsed))
                centers.append(center)
                heights.append(sprite_bounds(image).height())
        self.assertLessEqual(max(centers)-min(centers), 2)
        self.assertLessEqual(max(heights)-min(heights), 6)

    def test_entry_and_release_meet_actual_idle_with_a_complete_landing(self):
        idle = self.atlas.frame("idle", 0).toImage()
        self.assertEqual(self.atlas.frame("pickup", 0).toImage(), idle)
        self.assertEqual(self.atlas.frame("set_down", 999).toImage(), idle)
        self.assertFalse(CLIPS["set_down"].loop)
        self.assertGreaterEqual(len(CLIPS["set_down"].order), 8)
        self.assertLessEqual(sum(CLIPS["set_down"].durations), 850)

    def test_a_damaged_carry_bank_preserves_ordinary_drag_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in CARRY_ROWS:
                shutil.copyfile(Path(__file__).parent / "assets" / f"neko-carry-{name}-v1.png",
                                Path(folder) / f"neko-carry-{name}-v1.png")
            (Path(folder) / "neko-carry-bridges-v1.png").write_bytes(b"broken PNG")
            fallback = SpriteAtlas("missing")
            fallback.frames = {key: value for key, value in self.atlas.frames.items()
                               if not key[0].startswith("carry-")}
            original = set(fallback.frames)
            fallback.load_carry(folder)
            self.assertEqual(set(fallback.frames), original)


if __name__ == "__main__":
    unittest.main()
