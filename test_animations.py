import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QImage

from animations import CLIPS, SpriteAtlas, sprite_bounds


APP = QApplication.instance() or QApplication([])


class AnimationTests(unittest.TestCase):
    def test_atlas_has_64_distinct_drawings(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        self.assertEqual(len(atlas.frames), 64)
        self.assertTrue(all(not frame.isNull() for frame in atlas.frames.values()))
        self.assertNotEqual(atlas.frames["idle", 1, 0].toImage(), atlas.frames["idle", 1, 1].toImage())
        self.assertNotEqual(atlas.frames["activity", 0, 0].toImage(), atlas.frames["activity", 0, 1].toImage())
        self.assertTrue(all(frame.width() == 112 and frame.height() == 100 for frame in atlas.frames.values()))

    def test_affection_and_look_frames_never_shrink_the_seated_cat(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for bank, rows in (("idle", range(4)), ("pets", range(4)),
                           ("activity", range(3)), ("movement", (1, 2))):
            for row in rows:
                for col in range(4):
                    bounds = sprite_bounds(atlas.frames[bank, row, col].toImage())
                    self.assertAlmostEqual(bounds.height(), 84, delta=2)

    def test_gestures_use_a_complete_noticeable_sequence(self):
        for name, clip in CLIPS.items():
            if name not in ("idle", "sleep", "walk", "typing", "tail", "knead", "loaf"):
                self.assertGreaterEqual(sum(clip.durations), 4000, name)

    def test_idle_holds_then_blinks_and_loops(self):
        idle = CLIPS["idle"]
        self.assertEqual(idle.frame_index(0), 0)
        self.assertEqual(idle.frame_index(2.6), 1)
        self.assertEqual(idle.frame_index(sum(idle.durations) / 1000), 0)

    def test_one_shot_actions_end_without_looping(self):
        self.assertEqual(CLIPS["stretch"].frame_index(999), 3)
        self.assertEqual(CLIPS["stretch"].frame_index(-1), 0)

    def test_reduced_motion_holds_a_real_frame(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        self.assertEqual(atlas.frame("typing", 0).toImage(),
                         atlas.frame("typing", 10, motion=False).toImage())

    def test_missing_sheet_has_a_safe_fallback(self):
        self.assertTrue(SpriteAtlas("missing-sheet.png").frame("idle", 0).isNull())

    def test_neighboring_frame_bleed_does_not_shift_the_character(self):
        cell = QImage(20, 20, QImage.Format_RGBA8888)
        cell.fill(QColor(0, 0, 0, 0))
        for x in range(7, 16):
            for y in range(5, 17):
                cell.setPixelColor(x, y, QColor("white"))
        cell.setPixelColor(0, 10, QColor("black"))
        bounds = sprite_bounds(cell)
        self.assertEqual(bounds.left(), 6)
        self.assertEqual(bounds.right(), 16)
