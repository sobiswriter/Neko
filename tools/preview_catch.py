"""Production controller/art previews and a real Windows Qt playback probe."""
import os
import sys
os.environ['QT_QPA_PLATFORM'] = 'windows' if '--native' in sys.argv else 'offscreen'
from pathlib import Path
import json
import statistics
import tempfile
import time
from unittest.mock import patch
from PIL import Image, ImageDraw, ImageOps
from PySide6.QtCore import QPoint, QSettings, QTimer, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QWidget
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animations import CLIPS, GAME_ROWS
from behavior import NekoState
from games import Runway
from main import NekoWidget


def pixels(frame):
    q = frame.toImage().convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes('RGBA', (q.width(), q.height()), bytes(q.constBits()))


def save_gif(frames, path, milliseconds=40):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=milliseconds,
                   loop=0, optimize=False, disposal=2)


def preview(n):
    frames, coverage, logs = [], {}, {}
    banks = [(bank, i) for bank, rows in GAME_ROWS.items() if bank != 'emotion' for i in range(rows * 4)]
    for dark in (False, True):
        sheet = Image.new('RGB', (1600, ((len(banks) + 7) // 8) * 170), '#28343f' if dark else '#faf7f2')
        draw = ImageDraw.Draw(sheet)
        for j, (bank, i) in enumerate(banks):
            frame = pixels(n.atlas.frames[f'game-{bank}', i // 4, i % 4])
            x, y = j % 8 * 200, j // 8 * 170
            sheet.paste(frame, (x, y + 20), frame)
            draw.text((x + 5, y + 4), f'{bank} {i}', fill='#fffaf0' if dark else '#65544f')
        sheet.save(ROOT / ('docs/cursor-play-v2-frames-dark.png' if dark else 'docs/cursor-play-v2-frames.png'))
    for case in ('A tempting arrow', 'A tiny sulk and a cuddle'):
        base = 100.
        with patch('main.time.monotonic', return_value=base):
            n.end_game(immediate=True, clear_mood=True)
            n.move(400, 180)
            n.start_game(base, 'manual')
            n.game.runway = Runway(0, 808, 180, 110)
        comforted = False
        for i in range(18 * 50):
            now = base + i * .02
            cursor = (660, 240) if case == 'A tempting arrow' or i < 210 else (660, 10)
            with patch('main.time.monotonic', return_value=now), patch('main.QCursor.pos', return_value=QPoint(*cursor)):
                n.animate()
                g = n.game
                if g and g.phase == 'curl' and not comforted and i > 590:
                    n.pet_reaction()
                    comforted = True
                sprite = pixels(n.current_frame(now))
                if g:
                    name = n.game_clip()
                    coverage.setdefault(name, set()).add(CLIPS[name].frame_index(now - g.since))
                    logs[case] = list(g.log)
                    if g.direction > 0 and g.phase not in ('win', 'loss', 'loss_finish', 'curl', 'comfort'):
                        sprite = ImageOps.mirror(sprite)
                if i % 2:
                    continue
                scene = Image.new('RGB', (1000, 340), '#faf7f2')
                d = ImageDraw.Draw(scene)
                d.text((24, 18), case + ' — production controller, normal speed', fill='#65544f')
                scene.paste(sprite, (n.x(), n.y()), sprite)
                if n.bubble.isVisible():
                    d.text((max(20, min(730, n.x() - 20)), n.y() - 24), n.bubble.text(), fill='#443c38')
                d.polygon([(cursor[0], cursor[1]), (cursor[0] + 4, cursor[1] + 15),
                           (cursor[0] + 8, cursor[1] + 9), (cursor[0] + 15, cursor[1] + 7)], fill='#4c514f')
                frames.append(scene)
    required = {'game_ready', 'game_three', 'game_two', 'game_one', 'game_go', 'game_run',
                'game_jump', 'game_loss_finish', 'game_curl', 'game_comfort', 'walk', 'game_settle'}
    assert required <= coverage.keys(), required - coverage.keys()
    save_gif(frames, ROOT / 'docs/cursor-play-v2.gif')
    save_gif(frames, ROOT / 'docs/cursor-play-v2-slow.gif', 80)
    # All six distinct outcome stories use their production clip timing.
    frames = []
    for i in range(160):
        scene = Image.new('RGB', (600, 370), '#faf7f2')
        d = ImageDraw.Draw(scene)
        for j, name in enumerate(('game_win_0', 'game_win_1', 'game_win_2', 'game_loss_0', 'game_loss_1', 'game_loss_2')):
            duration = sum(CLIPS[name].durations) / 1000
            t = min(i * .04, duration - .001)
            frame = pixels(n.atlas.frame(name, t))
            x, y = j % 3 * 200, j // 3 * 185
            d.text((x + 12, y + 8), ('three happy hops', 'a proud little hug', 'champion paws',
                                     'empty paws', 'a tiny huff', 'the dramatic turn')[j], fill='#65544f')
            scene.paste(frame, (x + 4, y + 34), frame)
        frames.append(scene)
    save_gif(frames, ROOT / 'docs/cursor-play-v2-outcomes.gif')
    save_gif(frames, ROOT / 'docs/cursor-play-v2-outcomes-slow.gif', 80)
    return {'controller_coverage': {k: sorted(v) for k, v in coverage.items()}, 'controller_logs': logs}


def native(app, n):
    import win32gui
    backdrop = QWidget()
    backdrop.setWindowTitle('Neko v2 verification — test-owned surface')
    backdrop.setStyleSheet('background:#28343f')
    backdrop.resize(1000, 610)
    backdrop.show()
    backdrop.activateWindow()
    app.processEvents()
    area = n.screen().availableGeometry()
    origin = QPoint(area.center().x() - 100, area.bottom() - 230)
    n.move(origin)
    pointer = QPoint(origin.x() + 500, origin.y() + 5)
    n.companion.next_idle = n.companion.next_nap = float('inf')
    n.game_timer.enabled = False
    n.show()
    n.animation_timer.stop()
    n.tick_timer.stop()
    n.invitation_timer.stop()
    n.dismiss_bubble()
    app.processEvents()
    foreground = win32gui.GetForegroundWindow()
    cue_times = {}
    original_say = n.say
    def observe_cue(text, **kwargs):
        shown = original_say(text, **kwargs)
        if shown and text in ('3…', '2…', '1…'):
            cue_times.setdefault(text, time.monotonic())
        elif shown and text.startswith('Here I come!'):
            cue_times.setdefault('go', time.monotonic())
        return shown
    n.say = observe_cue
    with patch('main.QCursor.pos', side_effect=lambda: pointer):
        n.request_game()
        n.poll_game()
    assert n.game is not None
    begin = time.monotonic()
    phase_starts, gaps, coverage, captures = {}, [], {}, []
    last, case = begin, -1
    errors = []
    result = {}
    timer = QTimer()
    timer.setTimerType(Qt.PreciseTimer)
    def sample():
        nonlocal last, case, begin, pointer
        try:
            now = time.monotonic()
            gaps.append(now - last)
            last = now
            n.animate()
            g = n.game
            if g:
                name = n.game_clip()
                coverage.setdefault(name, set()).add(CLIPS[name].frame_index(now - g.since))
                if case == -1:
                    phase_starts.setdefault(g.phase, now)
                if name not in captures:
                    captures.append(name)
                    n.grab().save(str(ROOT / 'build/cursor-v2' / (name + '-native.png')))
            if (case == -1 and not n.game) or (case >= 0 and now - begin > 4.4):
                n.end_game(immediate=True, clear_mood=True)
                case += 1
                if case == 6:
                    result.update(countdown_seconds={a: cue_times[b] - cue_times[a]
                                  for a, b in (('3…', '2…'), ('2…', '1…'), ('1…', 'go'))},
                                  median_interval=statistics.median(gaps), maximum_gap=max(gaps),
                                  foreground_preserved=win32gui.GetForegroundWindow() == foreground,
                                  no_game_overlay=not hasattr(n, 'game_overlay'),
                                  thought_click_through=bool(n.bubble.windowFlags() & Qt.WindowTransparentForInput),
                                  native_thought_click_through=win32gui.WindowFromPoint((n.bubble.geometry().center().x(), n.bubble.geometry().center().y())) != int(n.bubble.winId()),
                                  platform=QApplication.platformName(), dpr=n.devicePixelRatioF(), monitors=len(app.screens()),
                                  pointer='scripted observations; real cursor never moved or captured',
                                  coverage={k: sorted(v) for k, v in coverage.items()},
                                  plays=n.games_played, wins=n.games_won)
                    assert all(v >= .99 for v in result['countdown_seconds'].values()), result
                    assert result['foreground_preserved'] and result['thought_click_through'] and result['native_thought_click_through']
                    assert result['no_game_overlay'] and result['maximum_gap'] < .5
                    for kind in ('win', 'loss'):
                        for i in range(3):
                            name = f'game_{kind}_{i}'
                            assert set(CLIPS[name].order) <= coverage[name], (name, coverage[name])
                    for name in ('game_ready', 'game_three', 'game_two', 'game_one', 'game_run', 'game_jump', 'walk', 'game_settle', 'game_loss_finish'):
                        assert set(CLIPS[name].order) <= coverage[name], (name, coverage[name])
                    timer.stop()
                    app.exit()
                    return
                n.move(origin)
                n.start_game(now, 'manual')
                g = n.game
                g.started = True
                kind = 'win' if case < 3 else 'loss'
                n.outcome_bags[kind] = [case % 3]
                g.result = kind
                g.enter(kind, now, kind)
                begin = now
            if case == -1 and now - begin > 20:
                raise AssertionError('native genuine paw catch did not finish')
        except Exception as e:
            errors.append(repr(e));timer.stop();app.exit()
    with patch('main.QCursor.pos', side_effect=lambda: pointer):
        timer.timeout.connect(sample)
        timer.start(20)
        app.exec()
    assert not errors, (errors, phase_starts, max(gaps), coverage)
    backdrop.close()
    return result


if __name__ == '__main__':
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    with tempfile.TemporaryDirectory() as folder, patch('main.ActivityMonitor.start'), \
            patch('main.desktop_activity', return_value=(0, 0, False)):
        n = NekoWidget(QSettings(str(Path(folder) / 'prefs.ini'), QSettings.IniFormat))
        n.tick_timer.stop();n.invitation_timer.stop();n.animation_timer.stop()
        n.show();app.processEvents()
        result = native(app, n) if '--native' in sys.argv else preview(n)
        target = ROOT / 'docs' / ('cursor-play-v2-native.json' if '--native' in sys.argv else 'cursor-play-v2-preview.json')
        target.write_text(json.dumps(result, indent=2), encoding='utf-8')
        n.tray_icon.hide();n.activity.close();n.bubble.close();n.close()
        print(target)
