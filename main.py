"""Desktop Neko — a small, quiet companion for Windows."""

import ctypes
from ctypes import wintypes
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import winreg
import winsound

import win32gui
import win32con
from PySide6.QtCore import QEvent, QLockFile, QPoint, QRect, QRectF, QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QMovie, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMenu, QMessageBox,
    QPushButton, QSpinBox, QFormLayout, QTabWidget, QSystemTrayIcon, QVBoxLayout, QWidget, QPlainTextEdit, QComboBox,
)

from behavior import Companion, NekoState, PET_STATES, CARRY_STATES, GAME_STATES, IDLE_STATES
from games import CursorGame, GameTimer, Runway
from activity import ActivityMonitor, foreground_executable
from app_context import app_kind
from animations import GAME_ROWS, SpriteAtlas, Clip, CLIPS, drop_progress, departure_progress, departure_drop, held_clip, sprite_bounds, CANVAS_WIDTH, CANVAS_PADDING, CANVAS_TOP, CANVAS_HEIGHT
from dialogue import OfflineDialogue
from cursors import petting_cursors
from thoughts import ThoughtLabel
from event_log import EventLog


RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSET_ROOT = RESOURCE_ROOT / "assets"
ICON_PATH = RESOURCE_ROOT / "neko_sleep.ico"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
COMPATIBILITY_KEY = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
TIMING_LIMITS = {"sleep_seconds": (180, 1, 3600),
                 "sleep_duration": (0, 0, 3600),
                 "chatter_seconds": (75, 15, 600), "idle_seconds": (14, 5, 120),
                 "reaction_seconds": (60, 15, 600)}
GESTURE_THOUGHTS = {"tail", "ears", "sniff", "stretch", "groom", "yawn", "loaf", "peek",
                    "look_left", "look_right", "tail_chase", "tail_catch"}


def adjacent_position(anchor, size, area):
    def clamp(x, y):
        return QPoint(max(area.left(), min(x, area.right() - size.width() + 1)),
                      max(area.top(), min(y, area.bottom() - size.height() + 1)))
    for x, y in ((anchor.right() + 13, anchor.top()),
                 (anchor.left() - size.width() - 12, anchor.top()),
                 (anchor.left(), anchor.top() - size.height() - 12),
                 (anchor.left(), anchor.bottom() + 13)):
        point = clamp(x, y)
        if not QRect(point, size).intersects(anchor):
            return point
    return clamp(anchor.left(), anchor.top() - size.height() - 12)


def legacy_shortcut():
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup/DesktopNeko.lnk"


def offset_frame(source, offset):
    frame = QPixmap(source.size())
    frame.fill(Qt.transparent)
    painter = QPainter(frame)
    painter.drawPixmap(offset, source)
    painter.end()
    return frame


def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, "DesktopNeko")
        return True
    except OSError:
        return legacy_shortcut().exists()


def clear_startup_elevation(executable):
    """Logon startup cannot answer an elevation prompt; preserve other app flags."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, COMPATIBILITY_KEY, 0,
                            winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE) as key:
            name = str(Path(executable).resolve())
            value, kind = winreg.QueryValueEx(key, name)
            if not isinstance(value, str):
                raise OSError("Neko's compatibility setting is not text; it was left unchanged.")
            flags = value.split()
            if not any(flag.upper() == "RUNASADMIN" for flag in flags):
                return
            flags = [flag for flag in flags if flag.upper() != "RUNASADMIN"]
            if flags and flags != ["~"]:
                winreg.SetValueEx(key, name, 0, kind, " ".join(flags))
            else:
                winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def set_autostart(enabled):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            executable = Path(sys.executable)
            if not getattr(sys, "frozen", False):
                pythonw = executable.with_name("pythonw.exe")
                executable = pythonw if pythonw.exists() else executable
            args = [str(executable)]
            if not getattr(sys, "frozen", False):
                args.append(str(Path(__file__).resolve()))
            clear_startup_elevation(executable)
            winreg.SetValueEx(key, "DesktopNeko", 0, winreg.REG_SZ, subprocess.list2cmdline(args))
        else:
            try:
                winreg.DeleteValue(key, "DesktopNeko")
            except FileNotFoundError:
                pass
    # Retire the old automatic shortcut so startup never launches two copies.
    legacy_shortcut().unlink(missing_ok=True)


class LastInputInfo(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def desktop_activity():
    info = LastInputInfo()
    info.cbSize = ctypes.sizeof(info)
    idle = 0
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        idle = ((ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000
    window = win32gui.GetForegroundWindow()
    fullscreen = False
    if window and win32gui.IsWindowVisible(window):
        try:
            bounds = win32gui.GetWindowRect(window)
            screen = QApplication.screenAt(QPoint(bounds[0], bounds[1]))
            if (screen and not ctypes.windll.user32.IsZoomed(wintypes.HWND(window))
                    and win32gui.GetClassName(window) not in ("Progman", "WorkerW")):
                area = screen.geometry()
                fullscreen = (bounds[0] <= area.left() and bounds[1] <= area.top()
                              and bounds[2] >= area.right() + 1
                              and bounds[3] >= area.bottom() + 1)
        except win32gui.error:
            pass
    return idle, window, fullscreen


class StatsWindow(QDialog):
    """One small home for preferences and lifetime keepsakes."""

    def __init__(self, neko):
        super().__init__()
        self.neko = neko
        self.startup_error = ""
        self.setWindowTitle("Neko's nook")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QWidget { background: #faf7f2; color: #504b48; }
            QDialog { background: #faf7f2; color: #504b48; }
            QTabWidget::pane { border: 1px solid #e7dcd3; border-radius: 6px; }
            QTabBar::tab { background: #eee5df; color: #66564f; padding: 7px 14px; }
            QTabBar::tab:selected { background: #e7d8d1; }
            QSpinBox { background: #fffdf9; color: #504b48; min-height: 25px; }
            QLineEdit { background: #fffdf9; color: #504b48; }
            QLabel { color: #504b48; font-size: 13px; }
            QCheckBox { color: #504b48; padding: 7px 0; font-size: 13px; }
            QCheckBox::indicator:unchecked { border: 1px solid #baa79d;
                                             border-radius: 3px; background: #fffdf9; }
            QPushButton { background: #eee5df; color: #504b48; border: 0;
                          border-radius: 8px; padding: 9px 16px; }
            QPushButton:hover { background: #e7d8d1; }
            QPushButton:disabled { color: #9c9088; background: #f2ece6; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(12)
        title = QLabel("a little company.")
        title.setStyleSheet("font-size: 23px; font-weight: 600;")
        layout.addWidget(title)
        subtitle = QLabel("happy to be here. nothing to keep up with.")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.keepsakes = QLabel()
        self.keepsakes.setStyleSheet("color: #80675e; padding: 12px 0;")
        layout.addWidget(self.keepsakes)
        self.mood = QLabel()
        self.mood.setStyleSheet("color: #746b65; font-size: 12px;")
        layout.addWidget(self.mood)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        company, settings, play_tab, journal_tab = QWidget(), QWidget(), QWidget(), QWidget()
        tabs.addTab(company, "Company")
        tabs.addTab(play_tab, "Play")
        tabs.addTab(settings, "Settings")
        tabs.addTab(journal_tab, "Journal")
        self.tabs, self.journal_tab = tabs, journal_tab
        journal_layout = QVBoxLayout(journal_tab)
        self.log_filter = QComboBox()
        self.log_filter.addItems(("All", "Thought", "Idle", "Sleep", "Care", "Activity", "Game", "Lifecycle", "System"))
        self.log_filter.setAccessibleName("Filter activity log")
        self.log_filter.currentTextChanged.connect(self.update_journal)
        journal_layout.addWidget(self.log_filter)
        self.activity_log = QPlainTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setAccessibleName("Neko activity log")
        self.activity_log.setMinimumHeight(180)
        journal_layout.addWidget(self.activity_log)
        copy_log = QPushButton("Copy log")
        copy_log.clicked.connect(lambda: QApplication.clipboard().setText(self.activity_log.toPlainText()))
        journal_layout.addWidget(copy_log)
        self.log_status = QLabel()
        self.log_status.setWordWrap(True)
        journal_layout.addWidget(self.log_status)
        company_layout, settings_layout = QVBoxLayout(company), QVBoxLayout(settings)
        play_layout = QVBoxLayout(play_tab)
        self.focus = QCheckBox("Quiet company · no unprompted words")
        self.focus.setChecked(neko.quiet)
        self.focus.toggled.connect(neko.set_quiet)
        company_layout.addWidget(self.focus)
        self.motion = QCheckBox("Gentle motion")
        self.motion.setChecked(neko.motion)
        self.motion.toggled.connect(neko.set_motion)
        settings_layout.addWidget(self.motion)
        sound_row = QHBoxLayout()
        self.sounds = QCheckBox("Soft mews and purrs")
        self.sounds.setChecked(neko.sounds_enabled)
        self.sounds.toggled.connect(neko.set_sounds)
        sound_row.addWidget(self.sounds)
        self.sound_test = QPushButton("Listen")
        self.sound_test.setEnabled(neko.sounds_enabled)
        self.sound_test.setAccessibleName("Preview a soft mew")
        self.sound_test.clicked.connect(lambda: neko.play_sound("mew", prompted=True))
        self.sounds.toggled.connect(self.sound_test.setEnabled)
        sound_row.addWidget(self.sound_test)
        settings_layout.addLayout(sound_row)
        self.reactivity = QCheckBox("Notice typing and window activity")
        self.reactivity.setChecked(neko.reactive)
        self.reactivity.toggled.connect(neko.set_reactivity)
        company_layout.addWidget(self.reactivity)
        self.play = QPushButton("Play · Catch the Cursor")
        self.play.clicked.connect(neko.request_game)
        play_layout.addWidget(self.play)
        self.auto_games = QCheckBox("Automatic cursor games")
        self.auto_games.setChecked(neko.game_timer.enabled)
        self.auto_games.setToolTip("After the cooldown, a fresh approach beside her invites play. Naps and cuddles come first.")
        self.auto_games.toggled.connect(neko.set_auto_games)
        play_layout.addWidget(self.auto_games)
        game_timing = QFormLayout()
        self.game_interval = QSpinBox()
        self.game_interval.setRange(30, 600)
        self.game_interval.setSuffix(" sec")
        self.game_interval.setKeyboardTracking(False)
        self.game_interval.setValue(neko.game_timer.interval)
        self.game_interval.setAccessibleName("Time between cursor games")
        self.game_interval.valueChanged.connect(neko.set_game_interval)
        game_timing.addRow("Time between games", self.game_interval)
        play_layout.addLayout(game_timing)
        self.game_status = QLabel()
        self.game_status.setWordWrap(True)
        play_layout.addWidget(self.game_status)
        instructions = QLabel("Bring the arrow beside her, a little away from her paws, to invite a chase. "
                              "She notices, counts down, then comes for it! A paw touch earns a celebration.\n\n"
                              "The cooldown arms automatic play; she waits for your next approach. "
                              "Naps, cuddles and typing come first. A pet comforts her after a miss.\n\n"
                              "Turn off Gentle motion for a stationary paw game.")
        instructions.setWordWrap(True)
        play_layout.addWidget(instructions)
        play_layout.addStretch()
        timing = QFormLayout()
        self.timing = {}
        for key, label in (("sleep_seconds", "Inactivity before nap"),
                           ("sleep_duration", "Nap duration"),
                           ("chatter_seconds", "Thoughts every"),
                           ("reaction_seconds", "Activity reactions every"),
                           ("idle_seconds", "Idle gestures every")):
            _, minimum, maximum = TIMING_LIMITS[key]
            spin = QSpinBox()
            spin.setRange(minimum, maximum)
            spin.setKeyboardTracking(False)
            spin.setToolTip(f"{minimum}–{maximum} seconds. Type a number, then press Enter or click elsewhere.")
            if key == "reaction_seconds":
                spin.setToolTip("Minimum gap shared by typing, window/tab activity, cursor curiosity. Idle gestures have their own setting.")
            elif key == "chatter_seconds":
                spin.setToolTip("General idle thoughts use this timer. Gesture thoughts belong to their gestures and do not reset it. A visible thought finishes first.")
            spin.setMinimumWidth(100)
            spin.setSuffix(" sec")
            if key == "sleep_duration":
                spin.setMinimumWidth(130)
                spin.setSpecialValueText("Until petted")
                spin.setToolTip("0 = until petted; 1–3600 seconds asleep. Pet her to wake sooner.")
            spin.setValue(getattr(neko.companion, key))
            spin.setAccessibleName(label)
            spin.valueChanged.connect(lambda value, key=key: neko.set_timing(key, value))
            self.timing[key] = spin
            timing.addRow(label, spin)
        company_layout.addLayout(timing)
        note = QLabel("Choose a timed nap or ‘Until petted’.\nTyping and window activity let her sleep.")
        note.setWordWrap(True)
        company_layout.addWidget(note)
        company_layout.addStretch()
        self.fullscreen = QCheckBox("Tuck away during fullscreen apps")
        self.fullscreen.setChecked(neko.hide_fullscreen)
        self.fullscreen.toggled.connect(neko.set_hide_fullscreen)
        settings_layout.addWidget(self.fullscreen)
        self.startup = QCheckBox("Join me when Windows starts")
        self.startup.setChecked(autostart_enabled())
        self.startup.toggled.connect(self.change_startup)
        settings_layout.addWidget(self.startup)
        self.ai = QCheckBox("AI observations · optional")
        self.ai.setChecked(neko.ai_enabled)
        self.ai.toggled.connect(neko.set_ai)
        settings_layout.addWidget(self.ai)
        privacy = QLabel("Offline uses app names and title hints locally.\n"
                         "Never reads what you type.\n"
                         "AI sends the current window title to Google Gemini.\n"
                         "No screenshots. No conversation history.\n"
                         "Uses GEMINI_API_KEY from your environment or config.json.")
        privacy.setWordWrap(True)
        privacy.setStyleSheet("font-size: 11px; color: #746b65;")
        settings_layout.addWidget(privacy)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size: 11px; color: #746b65;")
        settings_layout.addWidget(self.status)
        settings_layout.addStretch()
        row = QHBoxLayout()
        recenter = QPushButton("Back to my corner")
        recenter.clicked.connect(neko.position_to_bottom_right)
        row.addWidget(recenter)
        done = QPushButton("Comfy.")
        done.clicked.connect(self.close)
        row.addWidget(done)
        layout.addLayout(row)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.update_stats()

    def showEvent(self, event):
        self.focus.setChecked(self.neko.quiet)
        self.auto_games.blockSignals(True)
        self.auto_games.setChecked(self.neko.game_timer.enabled)
        self.auto_games.blockSignals(False)
        self.game_interval.blockSignals(True)
        self.game_interval.setValue(self.neko.game_timer.interval)
        self.game_interval.blockSignals(False)
        self.ai.setChecked(self.neko.ai_enabled)
        self.reactivity.setChecked(self.neko.reactive)
        self.fullscreen.setChecked(self.neko.hide_fullscreen)
        self.update_stats()
        self.timer.start(1000)
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def update_stats(self):
        n = self.neko
        self.update_journal()
        remaining = max(0, math.ceil(n.game_timer.due - time.monotonic())) if math.isfinite(n.game_timer.due) else 0
        self.game_status.setText(f"Automatic play: {n.game_timer.reason or 'cooldown'}\nCooldown remaining: {remaining} sec")
        self.play.setText("End game" if n.game and n.game.phase not in ("curl", "comfort") else "Play · Catch the Cursor")
        self.keepsakes.setText(f"{n.total_pets + n.companion.pets} little pets   ·   "
                               f"{n.total_naps + n.companion.naps} cozy naps\n"
                               f"{n.games_played} games played   ·   {n.games_won} Neko wins")
        self.status.setText(self.startup_error or n.ai_status)
        self.mood.setText({
            NekoState.IDLE: "happy to keep you company.",
            NekoState.TYPING: "helping with the important paw-work.",
            NekoState.CURIOUS: "oh? something happening over there?",
            NekoState.GROOMING: "washing these very important little paws.",
            NekoState.STRETCHING: "a biiig little stretch.",
            NekoState.YAWNING: "just resting my eyes...",
            NekoState.WAKING: "back from a little dream.",
            NekoState.SLEEPING: "somewhere soft, in a dream.",
            NekoState.FALLING_ASLEEP: "curling up for a little dream.",
            NekoState.HAPPY: "yes. right there. purrr.",
            NekoState.PEEKING: "just checking you're still there.",
            NekoState.CHIN_SCRITCH: "oh. just under the little chin. purrr.",
            NekoState.ROLLING: "a happy little roll, just for you.",
            NekoState.PAW_OFFER: "one little paw. for your company.",
            NekoState.EAR_RUB: "these very small ears approve.",
            NekoState.PLAYING: "that little arrow is mine!",
            NekoState.DISAPPOINTED: "a little disappointed. a pet would help.",
            NekoState.COMFORTING: "one more cuddle. feeling better already.",
        }.get(n.companion.state, "a little cat, doing little cat things."))

    def update_journal(self):
        if not hasattr(self, "activity_log"):
            return
        journal = self.neko.journal
        text = journal.text(self.log_filter.currentText())
        if text != self.activity_log.toPlainText():
            scroll = self.activity_log.verticalScrollBar()
            at_end, position = scroll.value() == scroll.maximum(), scroll.value()
            self.activity_log.setPlainText(text)
            scroll.setValue(scroll.maximum() if at_end else position)
        self.log_status.setText("Log file unavailable; events remain visible here." if journal.error else
                                "Local activity log · latest 50 events\nOlder events are deleted automatically")
        self.log_status.setToolTip((journal.error + "\n" if journal.error else "") + str(journal.path))

    def change_startup(self, enabled):
        try:
            set_autostart(enabled)
            self.startup_error = ""
        except OSError:
            self.startup.blockSignals(True)
            self.startup.setChecked(autostart_enabled())
            self.startup.blockSignals(False)
            self.startup_error = "Couldn't change Windows startup. You can try again later."
        self.update_stats()


class NekoWidget(QWidget):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings if settings is not None else QSettings("DesktopNeko", "Neko")
        log_root = (Path(self.settings.fileName()).parent if self.settings.format() == QSettings.IniFormat else
                    Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)))
        self.journal = EventLog(log_root / "neko-events.jsonl")
        self.journal.add("System", "session", "Neko started")
        self.logged_state = self.logged_game = None
        self.pending_reaction = None
        self.companion = Companion(time.monotonic())
        try:
            interval = max(30, min(600, int(self.settings.value("game_interval", 90))))
        except (ValueError, TypeError, OverflowError):
            interval = 90
        self.game_timer = GameTimer(time.monotonic(), self.settings.value("auto_games", True, type=bool), interval,
                                    record=lambda action, detail: self.journal.add("Game", action, detail))
        self.journal.add("Game", "configuration", f"automatic={self.game_timer.enabled}; interval={interval} sec")
        self.game = None
        self.game_interaction = None
        self.outcome_bags = {}
        self.last_outcome = {}
        for key in ("games_played", "games_won"):
            try:
                value = max(0, int(self.settings.value(key, 0)))
            except (TypeError, ValueError, OverflowError):
                value = 0
            setattr(self, key, value)
        self.games_won = min(self.games_won, self.games_played)
        self.last_keyboard = -math.inf
        for key, (default, minimum, maximum) in TIMING_LIMITS.items():
            try:
                value = int(self.settings.value(key, default))
            except (ValueError, TypeError, OverflowError):
                value = default
            setattr(self.companion, key, max(minimum, min(maximum, value)))
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.companion.next_idle = time.monotonic() + self.companion.idle_seconds
        self.dialogue = OfflineDialogue()
        self.last_words = -math.inf
        self.last_ai_attempt = -math.inf
        self.last_cursor = QCursor.pos()
        self.arrival_target = None
        self.arrival_top = 0
        self.arrival_left = 0
        self.departure_origin = None
        self.departure_target = None
        self.lifecycle_area = None
        self.departure_direction = 1
        self.last_title_stamp = None
        self.quiet = self.settings.value("quiet", False, type=bool)
        self.motion = self.settings.value("motion", True, type=bool)
        self.sounds_enabled = self.settings.value("sounds_enabled", False, type=bool)
        self.last_sound = -math.inf
        self.reactive = self.settings.value("reactive", True, type=bool)
        self.hide_fullscreen = self.settings.value("hide_fullscreen", False, type=bool)
        self.ai_enabled = self.settings.value("ai_enabled", False, type=bool)
        self.total_pets = max(0, self.settings.value("pets", 0, type=int))
        self.total_naps = max(0, self.settings.value("naps", 0, type=int))
        self.is_manually_hidden = False
        self.fullscreen = False
        self.last_window = 0
        self.current_executable = ""
        self.app_context = None
        self.brain_worker = None
        self.ai_generation = 0
        self.ai_status = "Offline company is always available."
        self.last_pet_words = -math.inf
        self.drag_origin = None
        self.dragged = False
        self.press_started = 0
        self.carry_path = []
        self.carry_path_clip = None
        self.carry_path_started = 0
        self.carry_return = []
        self.carry_resume = []
        self.carry_clock_offset = 0
        self.carry_released_elapsed = None
        self.closing = False
        self.quit_pending = False
        self.started = time.monotonic()
        self.pose_started = self.started
        self.look_direction = -1
        self.last_pin = 0
        self.stats_window = None
        self.setWindowTitle("Desktop Neko")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
                            | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.setAccessibleName("Neko, your desktop companion")
        self.setAccessibleDescription("Click to pet, drag to move, or right-click for Neko's nook.")
        self.assets = {}
        self.movies = {}
        self.atlas = SpriteAtlas(ASSET_ROOT)
        for name in ("idle", "sleep", "happy", "peek", "curious"):
            self.assets[name] = QPixmap(str(ASSET_ROOT / f"neko_{name}.png"))
            movie = QMovie(str(ASSET_ROOT / f"neko_{name}.gif"))
            if movie.isValid():
                movie.frameChanged.connect(self.update)
                self.movies[name] = movie
        self.current_asset = "idle"
        self.current_clip = "idle"
        self.bubble = ThoughtLabel()
        self.thought_channel = "thought"
        self.bubble.shown.connect(lambda text: self.journal.add("Thought", "shown", f"{self.thought_channel}: {text}"))
        self.bubble.dismissed.connect(lambda text: self.journal.add("Thought", "hidden", f"{self.thought_channel}: {text}"))
        shadow = QGraphicsDropShadowEffect(self.bubble)
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor("#33261f"))
        self.bubble.setGraphicsEffect(shadow)
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setTimerType(Qt.PreciseTimer)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.bubble.hide)
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(500)
        self.invitation_timer = QTimer(self)
        self.invitation_timer.timeout.connect(self.poll_game)
        self.invitation_timer.start(100)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
        self.pet_cursors = petting_cursors()
        self.pet_cursor_step = 0
        self.pet_cursor_timer = QTimer(self)
        self.pet_cursor_timer.timeout.connect(self.advance_pet_cursor)
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.setTimerType(Qt.PreciseTimer)
        self.hold_timer.timeout.connect(self.check_hold)
        self.setCursor(Qt.OpenHandCursor)
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_preferences)
        self.save_timer.start(60000)
        self.init_tray()
        saved = self.settings.value("position", None)
        self.position_to_bottom_right()
        if isinstance(saved, QPoint):
            self.move(saved - QPoint(CANVAS_PADDING, CANVAS_TOP))
            self.clamp_position()
        app = QApplication.instance()
        app.primaryScreenChanged.connect(self.screen_changed)
        app.screenRemoved.connect(self.screen_changed)
        self.activity = ActivityMonitor()
        self.activity.enabled = self.reactive
        self.activity.start(int(self.winId()))
        self.destroyed.connect(self.activity.close)
        self.sync_animation()
        self.transition_timer = QTimer(self)
        self.transition_timer.setSingleShot(True)
        self.transition_timer.timeout.connect(self.finish_transition)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon(str(ICON_PATH)), self)
        self.tray_icon.setToolTip("Neko · a little company")
        self.menu = QMenu()
        self.overlay_timer = QTimer(self)
        self.overlay_timer.setSingleShot(True)
        self.overlay_timer.timeout.connect(self.place_menu)
        self.menu.aboutToShow.connect(self.prepare_menu)
        self.menu.aboutToHide.connect(self.overlay_timer.stop)
        self.menu.addAction("Neko's nook…", self.open_stats_window)
        self.play_action = self.menu.addAction("Play · Catch the Cursor", self.request_game)
        self.game_stats_action = self.menu.addAction("")
        self.game_stats_action.setEnabled(False)
        self.update_game_stats()
        self.auto_game_action = self.menu.addAction("Automatic cursor games")
        self.auto_game_action.setCheckable(True)
        self.auto_game_action.setChecked(self.game_timer.enabled)
        self.auto_game_action.toggled.connect(self.set_auto_games)
        self.quiet_action = self.menu.addAction("Quiet company")
        self.quiet_action.setCheckable(True)
        self.quiet_action.setChecked(self.quiet)
        self.quiet_action.toggled.connect(self.set_quiet)
        self.hide_action = self.menu.addAction("Hide Neko", self.toggle_visibility)
        self.menu.addSeparator()
        self.menu.addAction("Let her go · quit", self.quit_neko)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def update_game_stats(self):
        self.game_stats_action.setText(f"{self.games_played} games played · {self.games_won} Neko wins")

    def prepare_menu(self):
        self.update_game_stats()
        ready = self.game_timer.enabled and (self.game_timer.pending == "automatic" or time.monotonic() >= self.game_timer.due)
        self.auto_game_action.setText("Automatic cursor games · ready" if ready else "Automatic cursor games")
        self.cancel_pickup()
        self.dismiss_bubble()
        self.play_action.setText("End game" if self.game and self.game.phase not in ("curl", "comfort") else "Play · Catch the Cursor")
        self.overlay_timer.start(0)

    def place_menu(self):
        if self.menu.isVisible() and self.menu.geometry().intersects(self.frameGeometry()):
            screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
            self.menu.move(adjacent_position(self.frameGeometry(), self.menu.size(), screen.availableGeometry()))

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_neko()
            self.open_stats_window()

    def set_quiet(self, enabled):
        self.quiet = enabled
        self.quiet_action.setChecked(enabled)
        self.ai_generation += 1
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        if enabled:
            self.dismiss_bubble()
            self.stop_sound()
            if self.game and self.game.source == "automatic" and self.game.phase not in ("curl", "comfort"):
                self.end_game()
        self.save_preferences()

    def set_motion(self, enabled):
        if self.game and self.game.phase not in ("curl", "comfort"):
            self.end_game(immediate=True)
        self.motion = enabled
        if not enabled:
            if self.quit_pending:
                self.finish_quit()
                return
            self.companion.pet_pending = False
            self.reset_pet_cursor()
            if self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
                self.finish_transition()
            if self.companion.state == NekoState.SETTING_DOWN:
                self.finish_pickup()
            if self.drag_origin is not None:
                self.setCursor(Qt.ClosedHandCursor)
        self.sync_animation()
        self.save_preferences()

    def set_sounds(self, enabled):
        self.sounds_enabled = enabled
        if not enabled:
            self.stop_sound()
        self.save_preferences()

    def stop_sound(self):
        try:
            winsound.PlaySound(None, 0)
        except (RuntimeError, OSError):
            pass

    def play_sound(self, kind, prompted=False):
        now = time.monotonic()
        if (kind not in ("mew", "chirp", "purr") or not self.sounds_enabled
                or self.closing or self.is_manually_hidden or not self.isVisible() or self.fullscreen
                or (not prompted and (self.quiet or self.app_context in ("music", "video")))
                or now - self.last_sound < (6 if prompted else 45)):
            return False
        try:
            winsound.PlaySound(str(ASSET_ROOT / "sounds" / f"{kind}.wav"),
                               winsound.SND_FILENAME | winsound.SND_ASYNC
                               | winsound.SND_NODEFAULT | winsound.SND_NOSTOP)
        except (RuntimeError, OSError):
            return False
        self.last_sound = now
        return True

    def set_timing(self, key, value):
        _, minimum, maximum = TIMING_LIMITS[key]
        setattr(self.companion, key, max(minimum, min(maximum, value)))
        now = time.monotonic()
        if key == "sleep_seconds" and self.companion.next_nap > now:
            self.companion.next_nap = now + self.companion.sleep_seconds
        if key == "chatter_seconds":
            self.companion.next_comment = now + self.companion.chatter_seconds
        if key == "idle_seconds":
            self.companion.next_idle = now + self.companion.idle_seconds
        self.journal.add("System", "timer changed", f"{key} = {getattr(self.companion, key)} sec")
        self.save_preferences()

    def set_auto_games(self, enabled):
        self.game_timer.configure(time.monotonic(), enabled, self.game_timer.interval)
        self.journal.add("Game", "configuration", f"automatic={enabled}; interval={self.game_timer.interval} sec")
        self.auto_game_action.setChecked(enabled)
        self.save_preferences()

    def set_game_interval(self, value):
        self.game_timer.configure(time.monotonic(), self.game_timer.enabled, value)
        self.journal.add("Game", "configuration", f"interval={self.game_timer.interval} sec")
        self.save_preferences()

    def request_game(self):
        if self.game:
            if self.game.phase not in ("curl", "comfort"):
                self.end_game()
            elif self.game.phase == "curl":
                self.say("A little cuddle first?", prompted=True)
            return
        if not self.game_art_ready():
            self.say("My play drawings are missing. I can still keep you company.", prompted=True)
            return
        self.game_timer.request(time.monotonic(), manual=True)
        if self.companion.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP):
            self.tray_icon.showMessage("Catch the Cursor", "Play is waiting. Pet Neko to wake her, or let her nap.",
                                       QSystemTrayIcon.Information, 4000)
        # Menu callbacks complete before eligibility is checked; the nook may stay open for manual play.
        if self.stats_window:
            self.stats_window.close()
        QTimer.singleShot(0, self, self.tick)

    def game_art_ready(self):
        return all((f"game-{bank}", i // 4, i % 4) in self.atlas.frames
                   for bank, rows in GAME_ROWS.items() for i in range(rows * 4))

    def game_runway(self):
        area = (QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()).availableGeometry()
        lift = max(0, min(110, self.y() - area.top())) if self.motion else 0
        return Runway(area.left(), area.right() - self.width() + 1, self.y(), lift)

    def poll_game(self):
        now = time.monotonic()
        manual = self.game_timer.pending == "manual"
        nook_editing = (self.stats_window and self.stats_window.isVisible()
                        and self.stats_window.tabs.currentWidget() != self.stats_window.journal_tab)
        reason = next((text for blocked, text in (
            (self.game is not None, "game already active"),
            (self.closing or self.quit_pending, "closing"),
            (self.is_manually_hidden or not self.isVisible(), "hidden"),
            (self.fullscreen, "fullscreen"), (self.menu.isVisible(), "menu open"),
            (nook_editing and not manual, "Nook controls open; Journal can monitor play"),
            (self.companion.state not in (NekoState.IDLE,) + IDLE_STATES, self.companion.state.name.lower()),
            (self.drag_origin is not None, "being held"),
            (bool(QApplication.mouseButtons()) or any(ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000 for key in (1, 2, 4, 5, 6)), "mouse button held"),
            (now - self.last_keyboard < 2, "recent typing"),
            (now - self.companion.last_interaction < 2, "recent cuddle"),
            (self.quiet and not manual, "quiet company")) if blocked), "")
        eligible = not reason
        if eligible and (self.game_timer.pending or now >= self.game_timer.due):
            idle, _, fullscreen = desktop_activity()
            if fullscreen or (not manual and idle >= self.companion.sleep_seconds and now >= self.companion.next_nap):
                eligible, reason = False, "fullscreen" if fullscreen else "nap due"
        cursor = QCursor.pos()
        in_zone = self.game_runway().invites((cursor.x(), cursor.y()), self.x(),
                    8 if self.game_timer.entered_at is not None else 0) if eligible else False
        if eligible and QApplication.screenAt(cursor) != QApplication.screenAt(self.geometry().center()):
            eligible, in_zone, reason = False, False, "cursor on another monitor"
        source = self.game_timer.tick(now, eligible, in_zone, can_start=self.companion.state == NekoState.IDLE,
                                      blocked_reason=reason)
        if source:
            self.start_game(now, source)


    def start_game(self, now, source):
        if not self.game_art_ready():
            self.journal.add("Game", "not started", "game artwork unavailable")
            self.game_timer.reset(now)
            return False
        area = (QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()).availableGeometry()
        lift = min(110, self.y() - area.top()) if self.motion else 0
        if area.width() < 560 or (self.motion and lift < 16):
            self.journal.add("Game", "not started", "not enough room for a safe runway")
            self.game_timer.reset(now)
            if source == "manual":
                self.say("I need a little more room above me to jump. Move me lower?", prompted=True)
            return False
        self.dismiss_bubble()
        self.reset_pet_cursor()
        self.ai_generation += 1
        self.companion.pet_pending = False
        self.companion.pending_window = None
        runway = Runway(area.left(), area.right() - self.width() + 1, self.y(), lift)
        self.game = CursorGame(now, (self.x(), self.y()), runway, self.motion, source)
        self.journal.add("Game", "session created", source)
        self.game.direction = -1 if QCursor.pos().x() < self.x() + self.width() // 2 else 1
        self.companion.pose(NekoState.PLAYING, now, math.inf)
        self.play_action.setText("End game")
        self.refresh_asset()
        self.advance_game(now)
        return True

    def game_clip(self):
        if self.game is None:
            return "idle"
        phase = self.game.phase
        if not self.game.motion and phase in ("run", "turn", "prepare", "jump", "miss", "home"):
            return "game_gentle_reach" if phase == "jump" else "game_gentle_rest"
        if phase in ("win", "loss"):
            return f"game_{phase}_{self.game.variant if self.game.variant is not None else 0}"
        if phase == "go":
            return "game_go"
        if phase == "ready_cancel":
            return "game_ready_cancel"
        if phase == "home":
            return "walk"
        if phase == "done":
            return "idle"
        return "game_" + phase

    def game_contact(self, now, cursor):
        game = self.game
        if game.phase != "jump" or game.result is not None:
            return False
        index = CLIPS["game_jump"].frame_index(now - game.since) if game.motion else 19
        # Author-reviewed forepaw boxes, then alpha-test the actual drawing (never head/tail/margins).
        regions = {18: (41, 87, 61, 100), 19: (42, 78, 58, 94),
                   20: (52, 114, 70, 128), 21: (52, 114, 70, 130)}
        if index not in regions:
            return False
        x, y = game.position_at(now)
        px, py = round(cursor[0] - round(x)), round(cursor[1] - round(y) + 1)
        if game.direction > 0:
            px = 191 - px
        left, top, right, bottom = regions[index]
        if not (left <= px <= right and top <= py <= bottom):
            return False
        frame = self.atlas.frame("game_jump" if game.motion else "game_gentle_reach", now - game.since).toImage()
        return frame.pixelColor(px, py).alpha() >= 128

    def advance_game(self, now):
        game = self.game
        cursor = QCursor.pos()
        point = (cursor.x(), cursor.y())
        game.update(now, point, self.game_contact(now, point))
        self.move(round(game.x), round(game.y))
        if game.phase == "done":
            self.journal.add("Game", "finished", f"{game.source}; result={game.result or 'unscored'}")
            interaction, self.game_interaction = self.game_interaction, None
            self.game = None
            self.play_action.setText("Play · Catch the Cursor")
            self.companion.state = NekoState.IDLE
            self.companion.last_interaction = now
            self.companion.next_nap = now + self.companion.sleep_seconds
            if interaction == "sleep":
                self.companion.next_nap = now
            self.companion.next_idle = now + self.companion.idle_seconds
            self.companion.next_comment = now + self.companion.chatter_seconds
            self.game_timer.finish(now, game.started)
            self.pose_started = now
            self.dismiss_bubble()
            self.refresh_asset()
            if interaction == "pet":
                self.pet_reaction()
            elif interaction == "pickup" and self.drag_origin is not None and QApplication.mouseButtons() & Qt.LeftButton:
                self.drag_offset = self.drag_origin - self.pos()
                self.begin_pickup()
            self.save_preferences()
            return
        self.companion.state = (NekoState.DISAPPOINTED if game.phase == "curl" else
                                NekoState.COMFORTING if game.phase == "comfort" else NekoState.PLAYING)
        self.current_clip = self.game_clip()
        self.pose_started = game.since
        if game.started and not game.counted:
            game.counted = True
            self.games_played += 1
            self.save_preferences()
        if game.result == "win" and not game.win_counted:
            game.win_counted = True
            self.games_won += 1
            self.save_preferences()
        if game.phase in ("win", "loss") and game.variant is None:
            bag = self.outcome_bags.setdefault(game.phase, [])
            if not bag:
                bag.extend(range(3))
                self.companion.rng.shuffle(bag)
                if bag[-1] == self.last_outcome.get(game.phase):
                    bag[0], bag[-1] = bag[-1], bag[0]
            game.variant = bag.pop()
            self.last_outcome[game.phase] = game.variant
            game.outcome_seconds = sum(CLIPS[self.game_clip()].durations) / 1000
            self.current_clip = self.game_clip()
        self.update_game_stats()
        line = game.take_line()
        if line and line.startswith("protest_") and QApplication.screenAt(cursor) != QApplication.screenAt(self.geometry().center()):
            line = "protest_monitor"
        if line and (line != "pursuit" or not self.bubble.isVisible()):
            countdown = line in ("3…", "2…", "1…")
            text = line if countdown else self.dialogue.pick("game_" + line)
            shown = self.say(text, prompted=game.source == "manual", hold_ms=1000 if countdown else 800 if line == "announce" else None,
                             kind="game_" + line)
            if shown and (countdown or line in ("announce", "go")):
                # Each beat starts after its label has actually been presented.
                game.since = game.last = time.monotonic()
                if line == "go":
                    game.deadline = game.since + 45

    def end_game(self, checked=False, immediate=False, clear_mood=False):
        if self.game is None:
            return
        game = self.game
        if game.phase in ("curl", "comfort") and not clear_mood:
            return
        self.journal.add("Game", "stop requested", "immediate" if immediate else "finish supported recovery")
        now = time.monotonic()
        if immediate:
            game.x, game.y = game.origin
            game.enter("done", now)
            game.last = now
        else:
            self.dismiss_bubble()
            if self.game_interaction:
                game.origin = (game.end_x if game.phase == "jump" else game.x, game.runway.y)
            game.cancel(now)
        self.advance_game(now)

    def animate(self):
        now = time.monotonic()
        if self.quit_pending and now >= self.companion.pose_until:
            self.quit_pending = False
            self.companion.state = NekoState.SLEEPING if self.companion.state == NekoState.FALLING_ASLEEP else NekoState.IDLE
            self.quit_neko()
            return
        if self.game and self.companion.state in GAME_STATES:
            self.advance_game(now)
            self.update()
            return
        if self.drag_origin is not None and not self.dragged:
            self.update()
            return
        if self.companion.state == NekoState.SETTING_DOWN and now >= self.companion.pose_until:
            self.finish_pickup()
        if (self.companion.state == NekoState.HELD and self.companion.carry_rest is not None and self.carry_path_clip
                and now - self.carry_path_started >= sum(self.carry_path_clip.durations) / 1000):
            sleeping = self.companion.carry_rest[0] in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP)
            self.current_clip = held_clip(self.carry_elapsed(now), sleeping)[0]
        if self.companion.state in PET_STATES and now >= self.companion.pose_until:
            self.companion.finish_pet(now)
            self.pose_started = now
            self.refresh_asset()
        if self.arrival_target is not None or self.departure_origin is not None:
            # Startup work must not consume the fall before Qt can animate it.
            if not self.transition_timer.isActive():
                self.pose_started = time.monotonic()
                duration = sum(CLIPS[self.current_clip].durations)
                self.companion.pose_until = self.pose_started + duration / 1000
                self.transition_timer.start(duration)
            elapsed = time.monotonic() - self.pose_started
            if self.arrival_target is not None:
                progress = drop_progress(elapsed)
                y = self.arrival_top + (self.arrival_target.y() - self.arrival_top) * progress
                x = self.arrival_left + (self.arrival_target.x() - self.arrival_left) * progress
                self.move(round(x), round(y))
            else:
                progress = departure_progress(elapsed)
                distance = self.departure_target.y() - self.departure_origin.y()
                y = self.departure_origin.y() + departure_drop(progress, distance)
                x = self.departure_origin.x() + (self.departure_target.x() - self.departure_origin.x()) * progress
                self.move(round(x), round(y))
        self.update()

    def set_reactivity(self, enabled):
        self.reactive = enabled
        self.companion.pending_window = None
        self.activity.enabled = enabled and not self.fullscreen and not self.is_manually_hidden
        self.activity.consume(time.monotonic())
        self.save_preferences()

    def set_hide_fullscreen(self, enabled):
        self.hide_fullscreen = enabled
        if enabled and self.fullscreen and self.quit_pending:
            self.finish_quit()
            return
        if enabled and self.fullscreen and self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
            self.finish_transition()
        self.dismiss_bubble()
        self.setVisible(not self.is_manually_hidden and not self.closing
                        and not (enabled and self.fullscreen))
        self.sync_animation()
        self.pin_to_top(force=True)
        self.save_preferences()

    def pin_to_top(self, force=False):
        now = time.monotonic()
        if (QApplication.platformName() != "windows" or not self.isVisible()
                or self.menu.isVisible()
                or QApplication.activePopupWidget() is not None
                or (self.stats_window is not None and self.stats_window.isVisible())
                or self.is_manually_hidden or self.closing or (not force and now - self.last_pin < 5)):
            return
        try:
            # Reassert the native z-order without taking the user's keyboard focus.
            win32gui.SetWindowPos(int(self.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                 win32con.SWP_NOACTIVATE | win32con.SWP_NOSIZE
                                 | win32con.SWP_NOMOVE | win32con.SWP_NOOWNERZORDER)
            self.last_pin = now
        except win32gui.error:
            pass

    def set_ai(self, enabled):
        self.ai_enabled = enabled
        self.ai_generation += 1
        self.ai_status = ("Observations are rare and quiet; an API key is needed."
                          if enabled else "Offline company is always available.")
        self.save_preferences()

    def sync_animation(self):
        active = self.isVisible() and not self.is_manually_hidden and not self.closing
        if active and (self.motion or self.game is not None):
            interval = (20 if self.companion.state in GAME_STATES else
                        33 if self.current_clip in ("arrive", "depart") else
                        50 if self.companion.state in PET_STATES + CARRY_STATES
                        or self.current_clip in ("tail_chase", "tail_catch") else 100)
            self.animation_timer.setTimerType(Qt.PreciseTimer if self.companion.state in PET_STATES + CARRY_STATES + GAME_STATES else Qt.CoarseTimer)
            self.animation_timer.start(interval)
        else:
            self.animation_timer.stop()
        for name, movie in self.movies.items():
            if active and self.motion and name == self.current_asset and self.companion.state not in CARRY_STATES:
                movie.start()
            else:
                movie.stop()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.journal.add("System", "visibility", "shown")
        if self.game and self.game.phase == "comfort":
            now = time.monotonic()
            self.game.since += max(0, now - self.game.last)
            self.game.last = now
        if hasattr(self, "animation_timer"):
            self.sync_animation()

    def dismiss_bubble(self):
        self.bubble_timer.stop()
        self.bubble.hide()

    def tick(self):
        if (self.closing or self.quit_pending or self.is_manually_hidden
                or self.companion.state == NekoState.LEAVING):
            return
        now = time.monotonic()
        idle, window, fullscreen = desktop_activity()
        self.activity.enabled = (self.reactive or self.game_timer.enabled or self.game is not None) and not fullscreen
        keyboard_events, window_event = self.activity.consume(now)
        if keyboard_events:
            self.last_keyboard = now
            if self.game and self.game.source == "automatic" and self.game.phase not in ("curl", "comfort"):
                self.end_game()
        if fullscreen and self.game and self.game.phase not in ("curl", "comfort"):
            self.end_game(immediate=True)
        fullscreen_changed = fullscreen != self.fullscreen
        if self.reactive and not fullscreen and window:
            try:
                title = win32gui.GetWindowText(window)
                stamp = (window, hash(title))
                if not self.last_title_stamp or window != self.last_title_stamp[0]:
                    self.current_executable = foreground_executable(window)
                self.app_context = app_kind(self.current_executable, title)
                if self.last_title_stamp and stamp[0] == self.last_title_stamp[0] and stamp != self.last_title_stamp:
                    window_event = window_event or "tab"
                self.last_title_stamp = stamp
            except win32gui.error:
                self.last_title_stamp = None
                self.current_executable = ""
                self.app_context = None
        else:
            self.last_title_stamp = None
            self.current_executable = ""
            self.app_context = None
        if fullscreen_changed:
            self.reset_pet_cursor()
            self.fullscreen = fullscreen
            if fullscreen and self.hide_fullscreen and self.companion.state == NekoState.ARRIVING:
                self.finish_transition()
            self.ai_generation += 1
            self.companion.next_comment = now + self.companion.chatter_seconds
            self.companion.next_idle = now + self.companion.idle_seconds
            self.dismiss_bubble()
            self.stop_sound()
            self.companion.pending_window = None
            self.last_words = now
            keyboard_events, window_event = 0, None
            self.setVisible(not (fullscreen and self.hide_fullscreen))
            self.sync_animation()
        if fullscreen and self.hide_fullscreen:
            self.last_window = window
            return
        if self.drag_origin is not None or self.companion.state in CARRY_STATES:
            if self.companion.state == NekoState.HELD and not QApplication.mouseButtons() & Qt.LeftButton:
                self.hold_timer.stop()
                self.drag_origin = None
                self.release_pickup()
                self.clamp_position()
                self.save_preferences()
                self.reset_pet_cursor()
            self.last_window = window
            return
        if self.game is not None:
            if (self.game.phase == "curl" and idle >= self.companion.sleep_seconds
                    and now >= self.companion.next_nap):
                self.game_interaction = "sleep"
                self.game.enter("comfort", now)
                self.companion.state = NekoState.COMFORTING
                self.refresh_asset()
            if self.reactive and window_event and self.companion.activity_ready(now):
                self.companion.pending_window = (window_event, now, self.app_context)
                self.game_timer.note(now, "coalesced", "window reaction")
            self.last_window = window
            return
        self.poll_game()
        if self.game:
            self.last_window = window
            return
        changed = bool(self.last_window and window != self.last_window)
        self.pin_to_top(force=changed)
        cursor = QCursor.pos()
        delta = cursor - (self.geometry().adjusted(0, CANVAS_TOP, 0, 0).center())
        distance = math.hypot(delta.x(), delta.y())
        moved = (cursor - self.last_cursor).manhattanLength() >= 20
        self.last_cursor = cursor
        action = self.companion.tick(now, idle, self.quiet or fullscreen,
                                     cursor_near=moved and distance < 150 and not fullscreen,
                                     window_changed=changed and self.reactive and not fullscreen and not fullscreen_changed,
                                     keyboard_events=keyboard_events if self.reactive else 0, window_event=window_event if self.reactive else None,
                                     app_kind=self.app_context)
        self.last_window = window
        if action and action != "comment":
            self.pose_started = now
            if action == "curious":
                self.look_direction = -1 if QCursor.pos().x() < self.geometry().center().x() else 1
            self.refresh_asset()
            if action == "sleep":
                self.ai_generation += 1
                self.dismiss_bubble()
            elif action == "typing":
                self.pending_reaction = "typing burst"
                self.offline_line("typing")
            elif action == "curious":
                self.pending_reaction = self.companion.reaction_kind
                self.offline_line(self.companion.reaction_kind)
            elif action == "fidget":
                self.offline_line(self.current_clip)
        self.poll_idle_thought(now)

    def poll_idle_thought(self, now):
        if now < self.companion.next_comment:
            return
        if (self.companion.state not in (NekoState.IDLE,) + IDLE_STATES or self.quiet
                or self.fullscreen or self.is_manually_hidden or self.quit_pending
                or now - self.companion.last_interaction < 15):
            self.journal.add("Thought", "general idle waiting", self.companion.state.name.lower() if not self.quiet else "quiet company", changed=True)
            return
        if self.ai_enabled and self.brain_worker is not None:
            self.journal.add("Thought", "general idle waiting", "AI observation pending", changed=True)
            return
        if not (self.ai_enabled and self.trigger_ai_brain()):
            self.random_dialogue()

    def record_state(self):
        if not self.isVisible():
            return
        marker = self.companion.state, self.rendered_clip, self.motion
        state = self.companion.state
        if marker != self.logged_state:
            self.logged_state = marker
            category = ("Sleep" if state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.WAKING) else
                        "Idle" if state in (NekoState.IDLE,) + IDLE_STATES else
                        "Game" if state in GAME_STATES else
                        "Lifecycle" if state in (NekoState.ARRIVING, NekoState.LEAVING) else "Care")
            self.journal.add(category, "state", f"{state.name.lower()} · {self.rendered_clip}" + (" · still pose" if not self.motion else ""))
        if self.pending_reaction:
            self.journal.add("Activity", "reaction", f"{self.pending_reaction} · {self.rendered_clip}")
            self.pending_reaction = None
        if self.game:
            marker = id(self.game), self.game.phase, self.game.result
            if marker != self.logged_game:
                self.logged_game = marker
                self.journal.add("Game", "phase", f"{self.game.source}: {self.game.phase}; result={self.game.result or 'pending'}")
        else:
            self.logged_game = None

    def refresh_asset(self):
        self.pending_reaction = None
        if self.game and self.companion.state in GAME_STATES:
            self.current_clip = self.game_clip()
            self.current_asset = "idle"
            self.sync_animation()
            return
        self.current_clip = {
            NekoState.SLEEPING: "sleep", NekoState.PEEKING: "peek",
            NekoState.FALLING_ASLEEP: "fall_asleep",
            NekoState.CURIOUS: "look_left" if self.look_direction < 0 else "look_right",
            NekoState.HAPPY: "happy", NekoState.GROOMING: "groom",
            NekoState.STRETCHING: "stretch", NekoState.TYPING: "typing",
            NekoState.YAWNING: "yawn", NekoState.WAKING: "wake",
            NekoState.TAIL_SWISH: "tail", NekoState.EAR_FLICK: "ears",
            NekoState.SNIFFING: "sniff", NekoState.LOAFING: "loaf",
            NekoState.CHEEK_RUB: "nuzzle",
            NekoState.KNEADING: "knead",
            NekoState.CHIN_SCRITCH: "chin_scritch", NekoState.ROLLING: "roll",
            NekoState.PAW_OFFER: "paw_offer", NekoState.EAR_RUB: "ear_rub",
            NekoState.PET_STRETCH: "pet_stretch", NekoState.BACK_ARCH: "back_arch",
            NekoState.HAPPY_HOP: "happy_hop", NekoState.SIDE_FLOP: "side_flop",
            NekoState.SHOULDER_PEEK: "shoulder_peek",
            NekoState.TAIL_CHASE: "tail_chase", NekoState.TAIL_CATCH: "tail_catch",
            NekoState.ARRIVING: "arrive", NekoState.LEAVING: "depart",
            NekoState.HELD: "pickup", NekoState.SETTING_DOWN: "set_down",
        }.get(self.companion.state, "idle")
        if self.companion.state in PET_STATES or (CLIPS[self.current_clip].bank.startswith("idle-v2-")
                                                  and not CLIPS[self.current_clip].loop):
            self.companion.pose_until = self.pose_started + sum(CLIPS[self.current_clip].durations) / 1000
        self.current_asset = {
            NekoState.SLEEPING: "sleep", NekoState.PEEKING: "peek",
            NekoState.CURIOUS: "curious", NekoState.HAPPY: "happy",
            NekoState.GROOMING: "peek",
        }.get(self.companion.state, "idle")
        self.sync_animation()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.lifecycle_area is not None:
            painter.setClipRect(self.lifecycle_area.translated(-self.x(), -self.y()))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        now = time.monotonic()
        elapsed = now - self.pose_started
        state = self.companion.state
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(75, 55, 48, 18))
        if (state not in (NekoState.ARRIVING, NekoState.LEAVING) + CARRY_STATES
                and not (self.game and self.game.phase == "jump")):
            painter.drawEllipse(QRectF(28 + CANVAS_PADDING, 99 + CANVAS_TOP, 56, 5))
        painter.save()
        painter.translate(self.width() // 2, 99 + CANVAS_TOP)
        movie = None if state in (NekoState.ARRIVING, NekoState.LEAVING) + CARRY_STATES + GAME_STATES else self.movies.get(self.current_asset)
        pixmap = self.current_frame(now)
        # Keep the visible origin stable when transparent top padding is added.
        top = -100 - CANVAS_TOP
        if movie and not movie.currentPixmap().isNull():
            pixmap = movie.currentPixmap().scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.rendered_clip = f"asset {self.current_asset}"
            top = -pixmap.height()
        elif pixmap.isNull():
            pixmap = self.assets[self.current_asset].scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.rendered_clip = f"fallback {self.current_asset}"
            top = -pixmap.height()
        if pixmap.isNull():
            self.rendered_clip = "text fallback"
            painter.setPen(QColor("#a67671"))
            painter.drawText(QRectF(-45, -85, 90, 85), Qt.AlignCenter, "=^·ω·^=")
        else:
            if (self.game and state in GAME_STATES and self.game.direction > 0
                    and self.game.phase not in ("loss", "loss_finish", "curl", "comfort", "win")):
                painter.scale(-1, 1)
            elif (state == NekoState.LEAVING and self.departure_direction < 0
                  and CLIPS["depart"].frame_index(elapsed) not in (0, 1, 2, 16)):
                painter.scale(-1, 1)
            painter.drawPixmap(-pixmap.width() // 2, top, pixmap)
        painter.restore()
        if state in PET_STATES:
            painter.setPen(QColor("#cf9699"))
            painter.setFont(QFont("Segoe UI Symbol", 12))
            painter.drawText(QRectF(78 + CANVAS_PADDING, 12 + CANVAS_TOP - (elapsed * 4 if self.motion else 0), 22, 24), "♡")
        painter.end()
        self.record_state()

    def say(self, text, prompted=False, hold_ms=None, kind="thought"):
        if (self.closing or self.is_manually_hidden or self.fullscreen
                or not self.isVisible() or (self.quiet and not prompted)
                or self.companion.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP,
                                            NekoState.ARRIVING, NekoState.LEAVING) + CARRY_STATES):
            self.journal.add("Thought", "suppressed", f"{kind}: quiet/hidden/fullscreen or incompatible pose", changed=True)
            return False
        text = " ".join(str(text).split())[:140]
        if not text:
            return False
        self.bubble.hide()
        self.bubble.setText(text)
        self.bubble.adjustSize()
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        x = max(area.left() + 6, min(self.x() + self.width() // 2 - self.bubble.width() // 2,
                                    area.right() - self.bubble.width() - 6))
        y = self.y() + CANVAS_TOP - self.bubble.height() - 4
        if y < area.top():
            y = self.geometry().bottom() + 4
        y = max(area.top(), min(y, area.bottom() - self.bubble.height()))
        self.bubble.move(x, y)
        self.bubble.prepare_backdrop()
        self.thought_channel = "gesture" if kind in GESTURE_THOUGHTS else "general idle" if kind in ("idle", "ai_idle") else kind
        self.bubble.show()
        self.bubble_timer.start(hold_ms if hold_ms is not None else max(5500, min(10000, len(text) * 75)))
        self.companion.comments += 1
        if kind not in GESTURE_THOUGHTS:
            self.last_words = time.monotonic()
        if kind in ("idle", "ai_idle"):
            self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        return True

    def offline_line(self, kind, prompted=False):
        pause = self.companion.chatter_seconds
        independent = kind == "idle" or kind in GESTURE_THOUGHTS
        if kind in GESTURE_THOUGHTS and self.current_clip != kind:
            self.journal.add("Thought", "expired gesture", kind)
            return False
        if not prompted and (self.bubble.isVisible() or (not independent and time.monotonic() - self.last_words < pause)):
            self.journal.add("Thought", "deferred", f"{kind}: existing thought" if self.bubble.isVisible() else f"{kind}: activity cooldown", changed=True)
            return False
        hold = None
        if kind in GESTURE_THOUGHTS:
            hold = max(1, round(min(sum(CLIPS[kind].durations) / 1000, self.companion.pose_until - time.monotonic()) * 1000))
        if self.say(self.dialogue.pick(kind), prompted=prompted, hold_ms=hold, kind=kind):
            self.ai_generation += 1
            if kind == "hello":
                self.play_sound("chirp")
            return True
        return False

    def random_dialogue(self):
        return self.offline_line("idle")

    def pet_reaction(self):
        if self.quit_pending:
            return
        if self.game_interaction == "sleep":
            self.game_interaction = "pet"
        if self.game:
            if self.game.phase == "curl":
                if self.game.comfort(time.monotonic()):
                    self.companion.pets += 1
                    self.journal.add("Care", "pet accepted", "comfort")
                    self.companion.state = NekoState.COMFORTING
                    self.advance_game(time.monotonic())
                return
            if self.game.phase == "comfort":
                return
            self.game_interaction = "pet"
            self.journal.add("Care", "pet requested", "waiting for safe game recovery")
            self.end_game()
            return
        if self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING) + CARRY_STATES:
            return
        now = time.monotonic()
        was_sleeping = self.companion.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP)
        self.ai_generation += 1
        started = self.companion.pet(now)
        self.journal.add("Care", "pet accepted", "wake" if was_sleeping else "queued" if self.companion.pet_pending else self.companion.state.name.lower())
        self.play_sound(random.choice(("mew", "purr")), prompted=True)
        if not started:
            return
        self.pose_started = now
        self.refresh_asset()
        if now - self.last_pet_words >= 6:
            self.offline_line("wake" if was_sleeping else "pet", prompted=True)
            self.last_pet_words = now

    def trigger_ai_brain(self):
        if (self.game is not None or self.brain_worker is not None or not self.ai_enabled or self.quiet
                or self.fullscreen or self.is_manually_hidden
                or self.bubble.isVisible()
                or time.monotonic() - self.last_words < self.companion.chatter_seconds
                or time.monotonic() - self.last_ai_attempt < 600):
            return False
        from llm_brain import AIBrainWorker
        try:
            title = win32gui.GetWindowText(win32gui.GetForegroundWindow())[:240]
        except win32gui.error:
            return
        self.request_generation = self.ai_generation
        self.request_started = time.monotonic()
        self.last_ai_attempt = self.request_started
        self.brain_worker = AIBrainWorker(title, parent=self)
        self.brain_worker.finished_thinking.connect(self.on_brain_finished)
        self.brain_worker.finished.connect(self.release_brain)
        self.brain_worker.start()
        self.journal.add("Thought", "AI requested", "optional observation; no title recorded in journal")
        return True

    def on_brain_finished(self, text, success):
        if self.closing:
            return
        self.journal.add("Thought", "AI result", "received" if success else "unavailable; offline fallback")
        self.ai_status = ("AI is connected. Window titles only." if success else
                          "AI is unavailable. Check your API key or connection; offline company continues.")
        if (self.request_generation != self.ai_generation or not self.ai_enabled
                or self.quiet or time.monotonic() - self.request_started > 25
                or self.bubble.isVisible()
                or time.monotonic() - self.last_words < self.companion.chatter_seconds):
            return
        # Recheck the foreground window: a game may have opened during the request.
        if desktop_activity()[2]:
            return
        if success:
            self.say(text, kind="ai_idle")
        else:
            self.random_dialogue()

    def release_brain(self):
        self.brain_worker.deleteLater()
        self.brain_worker = None
        if self.closing:
            QApplication.quit()

    def reset_pet_cursor(self):
        self.pet_cursor_timer.stop()
        self.setCursor(Qt.OpenHandCursor)

    def current_frame(self, now):
        self.rendered_clip = self.current_clip
        if self.game and self.companion.state in GAME_STATES:
            self.rendered_clip = self.game_clip()
            elapsed = now - self.game.since
            if self.game.phase == "ready_cancel":
                elapsed += (15 - self.game.cancel_index) * .06
            if not self.game.motion:
                clip = CLIPS[self.game_clip()]
                if self.game.phase == "win":
                    pose = (19, 6, 8)[self.game.variant or 0]
                    elapsed = sum(clip.durations[:clip.order.index(pose)]) / 1000
                elif self.game.phase in ("loss", "loss_finish"):
                    elapsed = sum(clip.durations) / 1000
                elif self.game.phase in ("ready", "three", "two", "one", "go"):
                    elapsed = 0
            return self.atlas.frame(self.game_clip(), elapsed, True)
        if self.companion.state not in CARRY_STATES:
            if self.drag_origin is not None and not self.dragged:
                now = self.press_started
            return self.atlas.frame(self.current_clip, now - self.pose_started, self.motion)
        if self.companion.carry_rest is None:
            self.rendered_clip = "idle"
            return self.atlas.frame("idle", 0, self.motion)
        if not self.motion:
            sleeping = self.companion.carry_rest[0] in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.DISAPPOINTED)
            self.rendered_clip = "held_sleepy" if sleeping else "held_calm"
            return self.atlas.frame("held_sleepy" if sleeping else "held_calm", 0)
        elapsed = max(0, now - self.carry_path_started)
        if self.carry_path and (elapsed < sum(self.carry_path_clip.durations) / 1000
                                or self.companion.state == NekoState.SETTING_DOWN):
            return self.carry_path[self.carry_path_clip.frame_index(elapsed)]
        sleeping = self.companion.carry_rest[0] in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.DISAPPOINTED)
        clip, elapsed = held_clip(self.carry_elapsed(now), sleeping)
        self.rendered_clip = clip
        return self.atlas.frame(clip, elapsed)

    def set_carry_path(self, frames, now, durations=None):
        self.carry_path = frames
        self.carry_path_clip = Clip("", 0, tuple(durations or [50] * len(frames)), tuple(range(len(frames))))
        self.carry_path_started = now

    def carry_elapsed(self, now):
        return max(0, now - self.companion.carry_started - self.carry_clock_offset)

    def check_hold(self):
        if self.drag_origin is not None:
            if not QApplication.mouseButtons() & Qt.LeftButton:
                self.cancel_pickup()
                return
            remaining = self.press_started + 0.25 - time.monotonic()
            if remaining > 0:
                self.hold_timer.start(max(1, math.ceil(remaining * 1000)))
            else:
                self.begin_pickup()

    def begin_pickup(self):
        if self.game and self.game.phase != "curl":
            if self.game.phase != "comfort":
                self.game_interaction = "pickup"
                self.dragged = True
                self.hold_timer.stop()
                self.end_game()
            return
        if self.companion.state == NekoState.HELD:
            return
        if ("carry-lift", 0, 0) not in self.atlas.frames:
            self.dragged = True
            return
        now = time.monotonic()
        source = self.current_frame(now)
        resuming = self.companion.state == NekoState.SETTING_DOWN and bool(self.carry_path)
        if resuming:
            index = self.carry_path_clip.frame_index(now - self.carry_path_started)
            frames = list(reversed(self.carry_path[:index + 1])) + self.carry_resume
            self.carry_return = self.carry_path[index + 1:]
        else:
            self.carry_clock_offset = 0
            self.carry_released_elapsed = None
            old_clip, old_elapsed = self.current_clip, now - self.pose_started
            clip = CLIPS[old_clip]
            index = clip.frame_index(old_elapsed)
            last = max(i for i, value in enumerate(clip.order) if value == index)
            self.carry_return = ([self.atlas.frames[clip.bank, clip.row + i // 4, i % 4]
                                  for i in clip.order[last + 1:]] if not clip.loop else [])
            if not self.carry_return:
                self.carry_return = [self.atlas.frame("sleep" if self.companion.state == NekoState.SLEEPING else "idle", 0)]
            bounds = sprite_bounds(source.toImage())
            state = self.companion.state
            if state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.DISAPPOINTED):
                family = "side"
            elif state in (NekoState.SIDE_FLOP, NekoState.ROLLING) and bounds.height() < 75:
                family = "side" if state == NekoState.SIDE_FLOP else "roll"
            elif state == NekoState.LOAFING and bounds.height() < 70:
                family = "side"
            elif bounds.width() > 87 and state in (NekoState.PET_STRETCH, NekoState.STRETCHING):
                family = "low"
            else:
                family = "lift"
            bank = f"carry-{family}"
            frames = [self.atlas.frames.get((bank, i // 4, i % 4), source) for i in range(8)]
            shift = bounds.center() - sprite_bounds(frames[0].toImage()).center()
            frames = [offset_frame(frame, QPoint(round(shift.x() * (1 - i / 7)),
                                                  round(shift.y() * (1 - i / 7))))
                      for i, frame in enumerate(frames)]
            frames[0] = source
            if family == "side" and state not in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.DISAPPOINTED):
                frames += [self.atlas.frames["carry-bridges", 2, i] for i in (1, 2, 3)]
        if not self.companion.begin_carry(now):
            return
        self.hold_timer.stop()
        self.dragged = True
        self.ai_generation += 1
        self.dismiss_bubble()
        self.set_carry_path(frames, now)
        if resuming:
            # Preserve the displayed expression while retracing the release back into the hold.
            self.carry_clock_offset = (now + sum(self.carry_path_clip.durations) / 1000
                                       - self.companion.carry_started - max(0.4, self.carry_released_elapsed))
        self.pose_started = now
        self.refresh_asset()

    def release_pickup(self):
        if self.companion.state != NekoState.HELD:
            return
        if self.companion.carry_rest is None:
            self.finish_pickup()
            return
        now = time.monotonic()
        elapsed = max(0, now - self.carry_path_started)
        source = self.current_frame(now)
        durations = None
        self.carry_resume = []
        if self.carry_path and elapsed < sum(self.carry_path_clip.durations) / 1000:
            if self.carry_released_elapsed is None:
                self.carry_released_elapsed = self.carry_elapsed(now)
            index = self.carry_path_clip.frame_index(elapsed)
            self.carry_resume = self.carry_path[index + 1:]
            frames = list(reversed(self.carry_path[:index + 1])) + self.carry_return
        else:
            self.carry_released_elapsed = self.carry_elapsed(now)
            frames = [source]
            sleeping = self.companion.carry_rest[0] in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.DISAPPOINTED)
            if sleeping and ("carry-side", 0, 0) in self.atlas.frames:
                frames += [self.atlas.frames["carry-side", i // 4, i % 4] for i in range(7, -1, -1)]
                previous, deadline = self.companion.carry_rest
                landing = now + (len(frames) + 1) * 0.05
                if previous == NekoState.DISAPPOINTED:
                    frames.append(self.atlas.frame("game_curl", 0))
                elif previous == NekoState.FALLING_ASLEEP and landing < deadline:
                    frames.append(self.atlas.frame("fall_asleep", landing - (deadline - 2.6)))
                else:
                    nap_started = deadline if previous == NekoState.FALLING_ASLEEP else self.companion.nap_started
                    frames.append(self.atlas.frame("sleep", landing - (nap_started or landing)))
            else:
                name, phase = held_clip(self.carry_elapsed(now))
                if name == "carry_yawn":
                    index = CLIPS[name].frame_index(phase)
                    frames += [self.atlas.frames["carry-sleepy", 0, i] for i in range(index, -1, -1)]
                if name != "held_excited" or CLIPS[name].frame_index(phase) in (2, 3):
                    frames += [self.atlas.frames["carry-bridges", 2, i] for i in (1, 2, 3)]
                frames = [frames[0]] + [offset_frame(frame, QPoint(0, min(3, i)))
                                        for i, frame in enumerate(frames[1:], 1)]
                durations = [50] * len(frames) + list(CLIPS["set_down"].durations)
                frames += [offset_frame(self.atlas.frames["carry-lift", i // 4, i % 4],
                                        QPoint(0, max(0, 11 - i))) for i in range(8, 17)]
        self.set_carry_path(frames, now, durations)
        self.companion.release_carry(now, sum(self.carry_path_clip.durations) / 1000)
        self.pose_started = now
        self.refresh_asset()
        if not self.motion:
            self.finish_pickup()

    def finish_pickup(self):
        now = time.monotonic()
        self.companion.finish_carry(now)
        if self.companion.state in CARRY_STATES:
            self.companion.state = NekoState.IDLE
        self.carry_path = []
        self.carry_return = []
        self.carry_resume = []
        self.carry_clock_offset = 0
        self.carry_released_elapsed = None
        self.pose_started = now
        if self.companion.state in (NekoState.WAKING, NekoState.FALLING_ASLEEP):
            self.pose_started = self.companion.pose_until - 2.6
        elif self.companion.state == NekoState.SLEEPING:
            self.pose_started = self.companion.nap_started if self.companion.nap_started is not None else now
        self.refresh_asset()
        if self.game and self.companion.state == NekoState.DISAPPOINTED:
            if (self.x(), self.y()) != (round(self.game.x), round(self.game.y)):
                self.game.origin = (self.x(), self.y())
            self.game.x, self.game.y = self.x(), self.y()
            self.game.runway = Runway(self.game.runway.left, self.game.runway.right, self.y(), self.game.runway.lift, self.game.runway.paw)
            self.game.last = now

    def cancel_pickup(self):
        self.hold_timer.stop()
        self.drag_origin = None
        if self.companion.state in CARRY_STATES:
            self.finish_pickup()
        if QWidget.mouseGrabber() is self:
            self.releaseMouse()
        self.reset_pet_cursor()

    def advance_pet_cursor(self):
        if self.pet_cursor_step >= len(self.pet_cursors):
            self.reset_pet_cursor()
            return
        self.setCursor(self.pet_cursors[self.pet_cursor_step])
        self.pet_cursor_step += 1

    def leaveEvent(self, event):
        self.reset_pet_cursor()
        if self.drag_origin is not None:
            self.setCursor(Qt.ClosedHandCursor)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.quit_pending or self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self.reset_pet_cursor()
            self.setCursor(Qt.ClosedHandCursor)
            self.drag_origin = event.globalPosition().toPoint()
            self.drag_offset = self.drag_origin - self.pos()
            self.dragged = False
            self.press_started = time.monotonic()
            if self.companion.state == NekoState.SETTING_DOWN:
                self.begin_pickup()
            else:
                self.hold_timer.start(250)
            event.accept()
        elif event.button() == Qt.RightButton:
            self.cancel_pickup()
            screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
            self.menu.exec(adjacent_position(self.frameGeometry(), self.menu.sizeHint(), screen.availableGeometry()))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_origin is not None:
            point = event.globalPosition().toPoint()
            if (point - self.drag_origin).manhattanLength() >= QApplication.startDragDistance():
                self.begin_pickup()
            if self.dragged:
                self.dismiss_bubble()
                self.move(point - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_origin is not None:
            self.hold_timer.stop()
            if self.dragged:
                self.release_pickup()
                self.clamp_position()
                self.save_preferences()
            else:
                self.pet_reaction()
            self.reset_pet_cursor()
            if not self.dragged and self.motion:
                self.pet_cursor_step = 0
                self.advance_pet_cursor()
                self.pet_cursor_timer.start(70)
            self.drag_origin = None

    def event(self, event):
        if (event.type() == QEvent.UngrabMouse and hasattr(self, "hold_timer")
                and self.drag_origin is not None):
            self.cancel_pickup()
        return super().event(event)

    def hideEvent(self, event):
        if self.game and self.game.phase not in ("curl", "comfort"):
            self.end_game(immediate=True)
        if hasattr(self, "hold_timer"):
            self.cancel_pickup()
        super().hideEvent(event)
        self.logged_state = self.logged_game = None
        self.journal.add("System", "visibility", "hidden")

    def screen_changed(self, *args):
        self.end_game(immediate=True)
        self.cancel_pickup()
        self.clamp_position()

    def position_to_bottom_right(self):
        self.end_game(immediate=True)
        area = QApplication.primaryScreen().availableGeometry()
        self.move(area.right() - self.width() - 24, area.bottom() - self.height() - 12)
        self.dismiss_bubble()

    def clamp_position(self, *args):
        if self.quit_pending or self.companion.state == NekoState.LEAVING:
            self.finish_quit()
            return
        if self.companion.state == NekoState.ARRIVING:
            self.finish_transition()
        self.restore_arrival_position()
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        self.move(max(area.left(), min(self.x(), area.right() - self.width() + 1)),
                  max(area.top(), min(self.y(), area.bottom() - self.height() + 1)))

    def toggle_visibility(self):
        if self.is_manually_hidden:
            self.show_neko()
        else:
            self.hide_neko()

    def hide_neko(self):
        self.cancel_pickup()
        self.companion.pet_pending = False
        self.reset_pet_cursor()
        self.restore_arrival_position()
        if self.quit_pending or self.companion.state == NekoState.LEAVING:
            self.finish_quit()
            return
        if self.companion.state == NekoState.ARRIVING:
            self.transition_timer.stop()
            self.companion.state = NekoState.IDLE
            self.refresh_asset()
        self.stop_sound()
        self.is_manually_hidden = True
        self.activity.enabled = False
        self.activity.consume(time.monotonic())
        self.ai_generation += 1
        self.dismiss_bubble()
        self.hide()
        self.hide_action.setText("Show Neko")
        self.sync_animation()

    def show_neko(self, greet=False):
        if self.closing or self.quit_pending or self.companion.state == NekoState.LEAVING:
            return
        self.is_manually_hidden = False
        self.journal.add("System", "visibility", "show requested")
        self.hide_action.setText("Hide Neko")
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.fullscreen = desktop_activity()[2]
        self.activity.enabled = self.reactive and not self.fullscreen
        visible = not (self.fullscreen and self.hide_fullscreen)
        if greet and visible:
            if self.motion and not self.atlas.frame("arrive", 0).isNull():
                self.start_transition(NekoState.ARRIVING, "arrive")
        self.setVisible(visible)
        if greet and visible and self.companion.state != NekoState.ARRIVING:
            self.offline_line("hello")
        self.sync_animation()
        self.pin_to_top(force=True)

    def open_stats_window(self):
        if self.closing or self.quit_pending or self.companion.state == NekoState.LEAVING:
            return
        self.dismiss_bubble()
        if self.stats_window is None:
            self.stats_window = StatsWindow(self)
        self.stats_window.show()
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        self.stats_window.move(adjacent_position(self.frameGeometry(), self.stats_window.frameGeometry().size(),
                                                screen.availableGeometry()))
        self.stats_window.raise_()
        self.stats_window.activateWindow()

    def save_preferences(self):
        self.settings.remove("follow_mouse")
        for key, value in {"quiet": self.quiet, "motion": self.motion,
                           "sounds_enabled": self.sounds_enabled,
                           "games_played": self.games_played, "games_won": self.games_won,
                           "auto_games": self.game_timer.enabled, "game_interval": self.game_timer.interval,
                           "sleep_seconds": self.companion.sleep_seconds,
                           "sleep_duration": self.companion.sleep_duration,
                           "chatter_seconds": self.companion.chatter_seconds,
                           "reaction_seconds": self.companion.reaction_seconds,
                           "idle_seconds": self.companion.idle_seconds,
                           "reactive": self.reactive, "hide_fullscreen": self.hide_fullscreen,
                           "ai_enabled": self.ai_enabled,
                           "position": (QPoint(round(self.game.origin[0]), round(self.game.origin[1])) if self.game else
                                        self.arrival_target if self.arrival_target is not None else
                                        self.departure_origin if self.departure_origin is not None else self.pos())
                                       + QPoint(CANVAS_PADDING, CANVAS_TOP),
                           "pets": self.total_pets + self.companion.pets,
                           "naps": self.total_naps + self.companion.naps}.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def quit_neko(self):
        if self.closing or self.quit_pending or self.companion.state == NekoState.LEAVING:
            return
        compatible = self.companion.state not in CARRY_STATES + GAME_STATES
        self.cancel_pickup()
        self.end_game(immediate=True, clear_mood=True)
        self.restore_arrival_position()
        if (compatible and self.motion and self.isVisible() and not (self.fullscreen and self.hide_fullscreen) and not self.is_manually_hidden
                and not self.atlas.frame("depart", 0).isNull()):
            self.drag_origin = None
            self.ai_generation += 1
            self.dismiss_bubble()
            self.stop_sound()
            self.menu.hide()
            if self.stats_window:
                self.stats_window.close()
            if self.companion.state == NekoState.SLEEPING:
                now = time.monotonic()
                self.companion.wake(now)
                self.pose_started = now
                self.refresh_asset()
            if self.companion.state not in (NekoState.IDLE, NekoState.ARRIVING):
                # Let the authored recovery finish rather than snapping a moving pose to seated goodbye.
                self.quit_pending = True
                self.companion.pet_pending = False
                self.companion.pending_window = None
                self.companion.pose_until = self.pose_started + sum(CLIPS[self.current_clip].durations) / 1000
            else:
                self.start_transition(NekoState.LEAVING, "depart")
        else:
            self.finish_quit()

    def restore_arrival_position(self):
        if self.arrival_target is not None:
            self.move(self.arrival_target)
            self.arrival_target = None
        if self.departure_origin is not None:
            self.move(self.departure_origin)
            self.departure_origin = None
        self.departure_target = None
        self.lifecycle_area = None

    def start_transition(self, state, clip):
        self.reset_pet_cursor()
        self.transition_timer.stop()
        self.restore_arrival_position()
        now = time.monotonic()
        duration = sum(CLIPS[clip].durations)
        self.companion.pose(state, now, duration / 1000)
        self.pose_started = now
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        self.lifecycle_area = screen.geometry()
        if state == NekoState.ARRIVING:
            self.arrival_target = self.pos()
            # Trace the drawn down-right reach back to the first upper/left boundary.
            fall = min(self.y() + 120 - self.lifecycle_area.top(),
                       (self.x() + 150 - self.lifecycle_area.left()) / 0.8)
            self.arrival_top = round(self.y() - fall)
            self.arrival_left = round(self.x() - fall * 0.8)
            self.move(self.arrival_left, self.arrival_top)
        else:
            self.departure_origin = self.pos()
            self.departure_direction = -1 if self.geometry().center().x() > screen.geometry().center().x() else 1
            center = self.geometry().center().x()
            near_side = min(center - screen.geometry().left(), screen.geometry().right() - center)
            if screen.geometry().bottom() - (self.y() + 130) > near_side:
                self.departure_direction = -self.departure_direction
                x = screen.geometry().right() + 1 if self.departure_direction > 0 else screen.geometry().left() - self.width()
                fall = max(96, round(abs(x - self.x()) * 0.65))
                self.departure_target = QPoint(x, min(self.y() + fall, screen.geometry().bottom() + 1))
            else:
                fall = screen.geometry().bottom() + 1 - self.y()
                x = self.x() + self.departure_direction * max(96, round(fall * 0.8))
                x = max(self.lifecycle_area.left(), min(x, self.lifecycle_area.right() - self.width() + 1))
                self.departure_target = QPoint(x, screen.geometry().bottom() + 1)
        self.refresh_asset()

    def finish_transition(self):
        self.transition_timer.stop()
        if self.companion.state == NekoState.LEAVING:
            self.finish_quit()
        elif self.companion.state == NekoState.ARRIVING:
            self.restore_arrival_position()
            now = time.monotonic()
            self.companion.state = NekoState.IDLE
            self.game_timer.reset(now)
            self.companion.next_nap = now + self.companion.sleep_seconds
            self.companion.next_idle = now + self.companion.idle_seconds
            self.companion.next_comment = now + self.companion.chatter_seconds
            self.companion.pending_window = None
            self.activity.consume(now)
            self.pose_started = now
            self.refresh_asset()
            if not self.fullscreen:
                self.offline_line("hello")

    def finish_quit(self):
        if not self.closing:
            self.journal.add("Lifecycle", "quit", "finished")
        self.quit_pending = False
        self.reset_pet_cursor()
        self.restore_arrival_position()
        self.transition_timer.stop()
        self.closing = True
        self.stop_sound()
        self.activity.close()
        self.tick_timer.stop()
        self.animation_timer.stop()
        self.dismiss_bubble()
        self.hide()
        self.tray_icon.hide()
        if self.stats_window:
            self.stats_window.close()
        self.save_preferences()
        if self.brain_worker is not None:
            self.brain_worker.requestInterruption()
        else:
            QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide_neko()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Desktop Neko")
    app.setOrganizationName("DesktopNeko")
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    data_dir.mkdir(parents=True, exist_ok=True)
    instance_lock = QLockFile(str(data_dir / "neko.lock"))
    instance_lock.setStaleLockTime(0)
    if not instance_lock.tryLock(0):
        if instance_lock.error() != QLockFile.LockFailedError:
            QMessageBox.warning(None, "Desktop Neko", "Couldn't open Neko's local settings folder.")
        sys.exit(0)
    neko = NekoWidget()
    app.aboutToQuit.connect(neko.save_preferences)
    neko.show_neko(greet=True)
    sys.exit(app.exec())
