import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QImage

from animations import CLIPS, PET_ROWS, SpriteAtlas, sprite_bounds


APP = QApplication.instance() or QApplication([])


class AnimationTests(unittest.TestCase):
    def test_all_pet_sequences_have_real_transitions_and_shared_idle_endpoints(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        idle = atlas.frame("idle", 0).toImage()
        for name in ("happy", "nuzzle", "knead", "chin_scritch", "blep", "paw_offer", "ear_rub",
                     "pet_stretch", "back_arch", "happy_hop", "side_flop", "shoulder_peek"):
            clip = CLIPS[name]
            self.assertTrue(clip.bank.startswith("pet-"), name)
            self.assertGreaterEqual(len(set(clip.order)), 8, name)
            self.assertFalse(clip.loop, name)
            self.assertEqual(len(clip.order), len(clip.durations), name)
            self.assertLessEqual(sum(clip.durations), 5800, name)
            self.assertEqual(atlas.frame(name, 0).toImage(), idle, name)
            self.assertEqual(atlas.frame(name, 999).toImage(), idle, name)

    def test_reworked_idles_have_drawn_entry_action_and_return_to_idle(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        idle = atlas.frame("idle", 0).toImage()
        for name in ("groom", "stretch", "loaf", "sniff", "ears", "yawn", "peek", "look_left", "look_right"):
            clip = CLIPS[name]
            self.assertTrue(clip.bank.startswith("idleplay-"), name)
            self.assertGreaterEqual(len(set(clip.order)), 5, name)
            self.assertFalse(clip.loop, name)
            self.assertLess(sum(clip.durations), 8000 if name == "loaf" else 6000, name)
            self.assertEqual(atlas.frame(name, 0).toImage(), idle, name)
            self.assertEqual(atlas.frame(name, 999).toImage(), idle, name)

    def test_atlas_has_307_drawings_without_retired_or_malformed_frames(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        self.assertEqual(len(atlas.frames), 307)
        self.assertFalse(any(key[0] in ("pets", "affection", "petting-a", "petting-b")
                             for key in atlas.frames))
        self.assertFalse(any(key[0] == "petting" or key[:2] in (("pets", 2), ("affection", 2), ("idle", 1))
                             for key in atlas.frames))
        for retired in ("wave", "shy_dip", "nose_wiggle", "tail_curl"):
            self.assertNotIn(retired, CLIPS)
        self.assertTrue(all(not frame.isNull() for frame in atlas.frames.values()))
        self.assertNotEqual(atlas.frame("tail", 0.8).toImage(), atlas.frame("tail", 1.2).toImage())
        self.assertNotEqual(atlas.frames["activity", 0, 0].toImage(), atlas.frames["activity", 0, 1].toImage())
        self.assertTrue(all(frame.width() == 112 and frame.height() == 112 for frame in atlas.frames.values()))

    def test_petting_reference_heads_match_idle_width_and_vertical_anchor(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in ("idle", "happy", "nuzzle", "knead", "chin_scritch", "blep", "ear_rub",
                     "pet_stretch", "back_arch", "happy_hop", "side_flop", "shoulder_peek", "paw_offer"):
            image = atlas.frame(name, 0).toImage()
            widest = 0
            for y in range(20, 50):
                run = 0
                for x in range(image.width()):
                    run = run + 1 if image.pixelColor(x, y).alpha() >= 128 else 0
                    widest = max(widest, run)
            self.assertAlmostEqual(widest, 62, delta=2, msg=name)
            self.assertAlmostEqual(sprite_bounds(image).top(), 16, delta=2, msg=name)

    def test_calibrated_pet_poses_are_not_clipped_by_the_canvas(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in ("happy", "nuzzle", "knead", "chin_scritch", "blep", "ear_rub",
                     "pet_stretch", "back_arch", "happy_hop", "side_flop", "shoulder_peek", "paw_offer"):
            clip = CLIPS[name]
            for index in set(clip.order):
                image = atlas.frames[clip.bank, clip.row + index // 4, index % 4].toImage()
                self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                                    for x in range(112) for y in (0, 111)), (name, index))
                self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                                    for x in (0, 111) for y in range(112)), (name, index))

    def test_idle_and_activity_frames_keep_their_seated_scale(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for bank, rows in (("idle", (0,)), ("activity", (0,))):
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

    def test_pet_sequences_use_all_their_drawings_and_return_to_rest(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in PET_ROWS:
            clip = CLIPS[name]
            self.assertEqual(set(clip.order), set(range(PET_ROWS[name] * 4)))
            self.assertFalse(clip.loop)
            self.assertLess(sum(clip.durations), 5800)
            drawings = [atlas.frames[clip.bank, index // 4, index % 4].toImage()
                        for index in sorted(set(clip.order))]
            self.assertGreaterEqual(len({bytes(image.constBits()) for image in drawings}), 8, name)
            elapsed = 0
            for col, duration in zip(clip.order, clip.durations):
                frame = atlas.frame(name, (elapsed + duration / 2) / 1000)
                self.assertFalse(frame.isNull())
                self.assertEqual(frame.toImage(), atlas.frames[clip.bank, col // 4, col % 4].toImage())
                self.assertLessEqual(sprite_bounds(frame.toImage()).bottom(), 110)
                elapsed += duration
            self.assertEqual(clip.frame_index(5.8), clip.order[-1])

    def test_continuous_motions_use_a_gentle_cycle_speed(self):
        for name, minimum in (("typing", 1200), ("walk", 900)):
            self.assertTrue(CLIPS[name].loop)
            self.assertGreaterEqual(sum(CLIPS[name].durations), minimum, name)

    def test_kneading_uses_three_alternating_cycles_then_recovers(self):
        clip = CLIPS["knead"]
        self.assertFalse(clip.loop)
        self.assertEqual(clip.order[2:-3], tuple(range(2, 9)) * 3)
        self.assertEqual(clip.order[-3:], (9, 10, 11))

    def test_near_neutral_pet_poses_keep_idle_head_scale(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in PET_ROWS:
            clip = CLIPS[name]
            for index in (1, PET_ROWS[name] * 4 - 2):
                image = atlas.frames[clip.bank, index // 4, index % 4].toImage()
                widest = 0
                for y in range(20, 55):
                    run = 0
                    for x in range(112):
                        run = run + 1 if image.pixelColor(x, y).alpha() >= 128 else 0
                        widest = max(widest, run)
                self.assertAlmostEqual(widest, 62, delta=4, msg=(name, index))
                if index == PET_ROWS[name] * 4 - 2:
                    self.assertAlmostEqual(sprite_bounds(image).top(), 16, delta=2, msg=(name, index))

    def test_tail_play_and_lifecycle_load_all_their_drawings(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for name in ("tail_chase", "tail_catch", "arrive", "depart"):
            clip = CLIPS[name]
            indices = set(clip.order)
            self.assertTrue(set(range(8)) <= indices)
            self.assertFalse(clip.loop)
            self.assertLess(sum(clip.durations), 6000)
            images = [atlas.frames[clip.bank, clip.row + i // 4, i % 4].toImage() for i in indices]
            expected = len(indices) - (1 if name in ("tail_chase", "tail_catch") else 0)
            self.assertEqual(len({bytes(image.constBits()) for image in images}), expected, name)
        departed = atlas.frame("depart", 999).toImage()
        self.assertEqual(departed.pixelColor(56, 50).alpha(), 0)
        self.assertTrue(all(byte == 0 for byte in bytes(departed.constBits())))
        self.assertNotEqual(atlas.frame("arrive", 0).toImage(), atlas.frame("arrive", 999).toImage())

    def test_tail_actions_share_idle_endpoints_and_finish_before_the_idle_slot(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        idle = atlas.frame("idle", 0).toImage()
        for name in ("tail", "tail_chase", "tail_catch"):
            self.assertFalse(CLIPS[name].loop, name)
            self.assertLess(sum(CLIPS[name].durations), 6000, name)
            self.assertEqual(atlas.frame(name, 0).toImage(), idle, name)
            self.assertEqual(atlas.frame(name, 999).toImage(), idle, name)

    def test_tail_chase_lasts_longer_than_catch_with_shared_drawn_transitions(self):
        for name, turns in (("tail_chase", 5), ("tail_catch", 2)):
            clip = CLIPS[name]
            cycle = tuple(range(11))
            self.assertEqual(clip.order[:4], (16, 17, 18, 19), name)
            self.assertEqual(clip.order[4:4 + turns * 11], cycle * turns, name)
            self.assertEqual(clip.durations[4:4 + turns * 11], (50,) * (turns * 11), name)
            self.assertEqual(clip.order[-3:], (21, 22, 23), name)
            self.assertFalse(clip.loop)
            self.assertLess(sum(clip.durations), 6000)
        self.assertIn(14, CLIPS["tail_catch"].order[26:])
        self.assertGreater(sum(CLIPS["tail_chase"].durations), sum(CLIPS["tail_catch"].durations) + 800)

    def test_new_source_poses_fit_without_clipping_their_silhouettes(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        for key, frame in atlas.frames.items():
            if key[0] not in ("arrival", "tailplay", "farewell") and not key[0].startswith("idleplay-"):
                continue
            image = frame.toImage()
            self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                                for x in range(112) for y in (0, 111)), key)
            self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                                for x in (0, 111) for y in range(112)), key)

    def test_tail_swishing_does_not_pull_the_head_sideways(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        centers = []
        for index in range(8):
            clip = CLIPS["tail"]
            image = atlas.frames[clip.bank, clip.row + index // 4, index % 4].toImage()
            opaque = [x for x in range(112) if image.pixelColor(x, 36).alpha() > 128]
            centers.append((min(opaque) + max(opaque)) / 2)
        self.assertLessEqual(max(centers) - min(centers), 1)
        self.assertIn(8, CLIPS["tail"].order)
        self.assertEqual(atlas.frames["tailswish", 2, 0].toImage(), atlas.frames["idle", 0, 2].toImage())

    def test_lifecycle_motion_continues_between_drawn_poses_and_has_clean_endpoints(self):
        atlas = SpriteAtlas(Path(__file__).parent / "assets")
        idle = atlas.frame("idle", 0).toImage()
        self.assertEqual(atlas.frame("arrive", 999).toImage(), idle)
        self.assertNotEqual(atlas.frame("depart", 0).toImage(), idle)
        self.assertNotEqual(atlas.frame("depart", 1.77).toImage(),
                            atlas.frame("depart", 1.79).toImage())
        self.assertEqual(CLIPS["depart"].frame_index(1.77), CLIPS["depart"].frame_index(1.79))
        self.assertTrue(any(bytes(atlas.frame("arrive", 0).toImage().constBits())))
        for name in ("arrive", "depart"):
            self.assertEqual(atlas.frame(name, 0.2, motion=False).toImage(), idle)
        image = atlas.frame("depart", 999).toImage()
        self.assertFalse(any(bytes(image.constBits())))

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
