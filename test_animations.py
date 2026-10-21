import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QImage

from animations import CLIPS, SpriteAtlas, sprite_bounds


APP = QApplication.instance() or QApplication([])


class AnimationTests(unittest.TestCase):
    def test_atlas_has_112_drawings_without_retired_or_malformed_frames(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        self.assertEqual(len(atlas.frames), 112)
        self.assertFalse(any(key[0] == "petting" or key[:2] in (("pets", 2), ("affection", 2))
                             for key in atlas.frames))
        for retired in ("wave", "shy_dip", "nose_wiggle", "tail_curl"):
            self.assertNotIn(retired, CLIPS)
        self.assertTrue(all(not frame.isNull() for frame in atlas.frames.values()))
        self.assertNotEqual(atlas.frames["idle", 1, 0].toImage(), atlas.frames["idle", 1, 1].toImage())
        self.assertNotEqual(atlas.frames["activity", 0, 0].toImage(), atlas.frames["activity", 0, 1].toImage())
        self.assertTrue(all(frame.width() == 112 and frame.height() == 100 for frame in atlas.frames.values()))

    def test_affection_and_look_frames_never_shrink_the_seated_cat(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for bank, rows in (("idle", range(4)), ("pets", (0, 1, 3)), ("affection", (0, 1, 3)),
                           ("activity", range(3)), ("movement", (1, 2))):
            for row in rows:
                for col in range(4):
                    bounds = sprite_bounds(atlas.frames[bank, row, col].toImage())
                    self.assertAlmostEqual(bounds.height(), 84, delta=2)

    def test_idle_gestures_finish_once_and_rest_instead_of_repeating_frantically(self):
        for name in ("ears", "sniff", "happy", "nuzzle", "groom", "stretch",
                     "look_left", "look_right", "peek", "chin_scritch", "blep", "paw_offer", "ear_rub"):
            clip = CLIPS[name]
            self.assertFalse(clip.loop, name)
            self.assertEqual(clip.frame_index(5), clip.order[-1], name)
            self.assertEqual(clip.frame_index(6), clip.order[-1], name)

    def test_new_pet_reactions_use_four_distinct_drawings_and_return_to_rest(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in ("pet_stretch", "back_arch", "happy_hop", "side_flop", "shoulder_peek", "paw_offer"):
            clip = CLIPS[name]
            self.assertEqual(set(clip.order), set(range(4)))
            self.assertFalse(clip.loop)
            self.assertLess(sum(clip.durations), 5800)
            drawings = [atlas.frames[clip.bank, clip.row, col].toImage() for col in range(4)]
            for col in range(4):
                for other in range(col):
                    self.assertNotEqual(drawings[col], drawings[other], (name, col, other))
            elapsed = 0
            for col, duration in zip(clip.order, clip.durations):
                frame = atlas.frame(name, (elapsed + duration / 2) / 1000)
                self.assertFalse(frame.isNull())
                self.assertEqual(frame.toImage(), atlas.frames[clip.bank, clip.row, col].toImage())
                self.assertLessEqual(sprite_bounds(frame.toImage()).bottom(), 99)
                elapsed += duration
            self.assertEqual(clip.frame_index(5.8), 0)

    def test_continuous_motions_use_a_gentle_cycle_speed(self):
        for name, minimum in (("tail", 2400), ("knead", 1600), ("typing", 1200), ("walk", 900)):
            self.assertTrue(CLIPS[name].loop)
            self.assertGreaterEqual(sum(CLIPS[name].durations), minimum, name)

    def test_sleep_and_wake_use_eight_real_frames_and_meet_at_the_same_sleep_pose(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in ("fall_asleep", "wake"):
            self.assertEqual(len(CLIPS[name].order), 8)
            self.assertFalse(CLIPS[name].loop)
            self.assertFalse(atlas.frame(name, 999).isNull())
        self.assertEqual(atlas.frame("fall_asleep", 999).toImage(), atlas.frame("sleep", 1.5).toImage())

    def test_idle_holds_then_blinks_and_loops(self):
        idle = CLIPS["idle"]
        self.assertEqual(idle.frame_index(0), 0)
        self.assertEqual(idle.frame_index(2.6), 1)
        self.assertEqual(idle.frame_index(sum(idle.durations) / 1000), 0)

    def test_one_shot_actions_end_without_looping(self):
        self.assertEqual(CLIPS["fall_asleep"].frame_index(999), 7)
        self.assertEqual(CLIPS["fall_asleep"].frame_index(-1), 0)

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
