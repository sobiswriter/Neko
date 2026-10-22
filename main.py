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
from PySide6.QtCore import QLockFile, QPoint, QRect, QRectF, QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFont, QIcon, QMovie, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMenu, QMessageBox,
    QPushButton, QSpinBox, QFormLayout, QTabWidget, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from behavior import Companion, NekoState, PET_STATES
from activity import ActivityMonitor, foreground_executable
from app_context import app_kind
from animations import SpriteAtlas, CLIPS, drop_progress, CANVAS_WIDTH, CANVAS_PADDING, CANVAS_TOP, CANVAS_HEIGHT
from dialogue import OfflineDialogue
from cursors import petting_cursors


ASSET_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
TIMING_LIMITS = {"sleep_seconds": (180, 1, 3600),
                 "sleep_duration": (0, 0, 3600),
                 "chatter_seconds": (75, 15, 600), "idle_seconds": (14, 5, 120)}


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


def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, "DesktopNeko")
        return True
    except OSError:
        return legacy_shortcut().exists()


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
        company, settings = QWidget(), QWidget()
        tabs.addTab(company, "Company")
        tabs.addTab(settings, "Settings")
        company_layout, settings_layout = QVBoxLayout(company), QVBoxLayout(settings)
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
        self.follow = QCheckBox("Sometimes follow the little arrow")
        self.follow.setChecked(neko.follow_mouse)
        self.follow.toggled.connect(neko.set_follow_mouse)
        company_layout.addWidget(self.follow)
        timing = QFormLayout()
        self.timing = {}
        for key, label in (("sleep_seconds", "Inactivity before nap"),
                           ("sleep_duration", "Nap duration"),
                           ("chatter_seconds", "Thoughts every"),
                           ("idle_seconds", "Idle gestures every")):
            _, minimum, maximum = TIMING_LIMITS[key]
            spin = QSpinBox()
            spin.setRange(minimum, maximum)
            spin.setKeyboardTracking(False)
            spin.setToolTip(f"{minimum}–{maximum} seconds. Type a number, then press Enter or click elsewhere.")
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
        self.keepsakes.setText(f"{n.total_pets + n.companion.pets} little pets   ·   "
                               f"{n.total_naps + n.companion.naps} cozy naps")
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
        }.get(n.companion.state, "a little cat, doing little cat things."))

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
        self.companion = Companion(time.monotonic())
        for key, (default, minimum, maximum) in TIMING_LIMITS.items():
            try:
                value = int(self.settings.value(key, default))
            except (ValueError, TypeError, OverflowError):
                value = default
            setattr(self.companion, key, max(minimum, min(maximum, value)))
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.companion.next_idle = time.monotonic() + self.companion.idle_seconds
        self.follow_mouse = self.settings.value("follow_mouse", True, type=bool)
        self.dialogue = OfflineDialogue()
        self.last_words = -math.inf
        self.last_ai_attempt = -math.inf
        self.last_cursor = QCursor.pos()
        self.follow_origin = None
        self.arrival_target = None
        self.arrival_top = 0
        self.last_follow = time.monotonic() - 45
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
        self.closing = False
        self.started = time.monotonic()
        self.pose_started = self.started
        self.look_direction = -1
        self.last_pin = 0
        self.stats_window = None
        self.setWindowTitle("Desktop Neko")
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
        self.bubble = QLabel(None, Qt.ToolTip | Qt.FramelessWindowHint
                             | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
                             | Qt.WindowTransparentForInput)
        self.bubble.setAttribute(Qt.WA_ShowWithoutActivating)
        self.bubble.setAttribute(Qt.WA_TranslucentBackground)
        self.bubble.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.bubble.setTextFormat(Qt.PlainText)
        self.bubble.setWordWrap(True)
        self.bubble.setFixedWidth(270)
        self.bubble.setStyleSheet("background: transparent; color: #fffaf0; border: 0;"
                                 "padding: 6px; font: 600 16px 'Segoe UI';")
        shadow = QGraphicsDropShadowEffect(self.bubble)
        shadow.setBlurRadius(4)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor("#33261f"))
        self.bubble.setGraphicsEffect(shadow)
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.bubble.hide)
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(500)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
        self.pet_cursors = petting_cursors()
        self.pet_cursor_step = 0
        self.pet_cursor_timer = QTimer(self)
        self.pet_cursor_timer.timeout.connect(self.advance_pet_cursor)
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
        app.primaryScreenChanged.connect(self.clamp_position)
        app.screenRemoved.connect(self.clamp_position)
        self.activity = ActivityMonitor()
        self.activity.enabled = self.reactive
        self.activity.start(int(self.winId()))
        self.destroyed.connect(self.activity.close)
        self.sync_animation()
        self.transition_timer = QTimer(self)
        self.transition_timer.setSingleShot(True)
        self.transition_timer.timeout.connect(self.finish_transition)

    def init_tray(self):
        icon = self.atlas.frame("idle", 0).copy(CANVAS_PADDING, CANVAS_TOP, 112, 112)
        self.tray_icon = QSystemTrayIcon(QIcon(icon if not icon.isNull() else self.assets["idle"]), self)
        self.tray_icon.setToolTip("Neko · a little company")
        self.menu = QMenu()
        self.overlay_timer = QTimer(self)
        self.overlay_timer.setSingleShot(True)
        self.overlay_timer.timeout.connect(self.place_menu)
        self.menu.aboutToShow.connect(self.prepare_menu)
        self.menu.aboutToHide.connect(self.overlay_timer.stop)
        self.menu.addAction("Neko's nook…", self.open_stats_window)
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

    def prepare_menu(self):
        self.stop_following()
        self.dismiss_bubble()
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
        self.save_preferences()

    def set_motion(self, enabled):
        self.motion = enabled
        if not enabled:
            self.companion.pet_pending = False
            self.reset_pet_cursor()
            self.stop_following()
            if self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
                self.finish_transition()
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
        self.companion.next_comment = now + self.companion.chatter_seconds
        self.companion.next_idle = now + self.companion.idle_seconds
        self.save_preferences()

    def set_follow_mouse(self, enabled):
        self.follow_mouse = enabled
        if not enabled:
            self.stop_following()
        self.save_preferences()

    def stop_following(self):
        if self.companion.state == NekoState.FOLLOWING:
            self.companion.state = NekoState.IDLE
            self.pose_started = time.monotonic()
            self.refresh_asset()
        self.follow_origin = None

    def animate(self):
        now = time.monotonic()
        if self.companion.state in PET_STATES and now >= self.companion.pose_until:
            self.companion.finish_pet(now)
            self.pose_started = now
            self.refresh_asset()
        if self.arrival_target is not None:
            # Startup work must not consume the fall before Qt can animate it.
            if not self.transition_timer.isActive():
                self.pose_started = time.monotonic()
                duration = sum(CLIPS["arrive"].durations)
                self.companion.pose_until = self.pose_started + duration / 1000
                self.transition_timer.start(duration)
            progress = drop_progress(time.monotonic() - self.pose_started)
            y = self.arrival_top + (self.arrival_target.y() - self.arrival_top) * progress
            self.move(self.arrival_target.x(), round(y))
        elif self.companion.state == NekoState.FOLLOWING:
            cursor = QCursor.pos()
            delta = cursor - self.geometry().center()
            distance = math.hypot(delta.x(), delta.y())
            excursion = (self.pos() - self.follow_origin).manhattanLength() if self.follow_origin else 0
            if (self.drag_origin is not None or self.fullscreen or distance > 650
                    or not self.follow_mouse or not self.motion):
                self.stop_following()
            elif abs(delta.x()) <= 90 or excursion >= 220 or time.monotonic() >= self.companion.pose_until:
                self.stop_following()
                self.offline_line("follow")
            else:
                self.look_direction = -1 if delta.x() < 0 else 1
                self.move(self.x() + self.look_direction * 2, self.y())
                self.clamp_position()
        self.update()

    def set_reactivity(self, enabled):
        self.reactive = enabled
        self.companion.pending_window = None
        self.activity.enabled = enabled and not self.fullscreen and not self.is_manually_hidden
        self.activity.consume(time.monotonic())
        self.save_preferences()

    def set_hide_fullscreen(self, enabled):
        self.hide_fullscreen = enabled
        if enabled and self.fullscreen and self.companion.state == NekoState.ARRIVING:
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
        if active and self.motion:
            interval = (33 if self.current_clip in ("arrive", "depart") else
                        50 if self.companion.state in PET_STATES
                        or self.current_clip in ("tail_chase", "tail_catch") else 100)
            self.animation_timer.setTimerType(Qt.PreciseTimer if self.companion.state in PET_STATES else Qt.CoarseTimer)
            self.animation_timer.start(interval)
        else:
            self.animation_timer.stop()
        for name, movie in self.movies.items():
            if active and self.motion and name == self.current_asset:
                movie.start()
            else:
                movie.stop()
        self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "animation_timer"):
            self.sync_animation()

    def dismiss_bubble(self):
        self.bubble_timer.stop()
        self.bubble.hide()

    def tick(self):
        if (self.closing or self.is_manually_hidden or self.drag_origin is not None
                or self.companion.state == NekoState.LEAVING):
            return
        now = time.monotonic()
        idle, window, fullscreen = desktop_activity()
        self.activity.enabled = self.reactive and not fullscreen
        keyboard_events, window_event = self.activity.consume(now)
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
            self.stop_following()
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
        changed = bool(self.last_window and window != self.last_window)
        self.pin_to_top(force=changed)
        cursor = QCursor.pos()
        delta = cursor - self.geometry().center()
        distance = math.hypot(delta.x(), delta.y())
        moved = (cursor - self.last_cursor).manhattanLength() >= 20
        self.last_cursor = cursor
        was_following = self.companion.state == NekoState.FOLLOWING
        if was_following and keyboard_events >= 6:
            self.stop_following()
        if (self.follow_mouse and self.motion and not fullscreen and not keyboard_events
                and not self.menu.isVisible()
                and not (self.stats_window is not None and self.stats_window.isVisible())
                and not changed and not window_event and not self.bubble.isVisible()
                and self.companion.state == NekoState.IDLE and moved and abs(delta.x()) > 200 and distance < 520
                and now - self.last_follow >= 25):
            self.last_follow = now
            self.follow_origin = self.pos()
            self.companion.pose(NekoState.FOLLOWING, now, 6.5)
            self.pose_started = now
            self.refresh_asset()
        action = self.companion.tick(now, idle, self.quiet or fullscreen,
                                     cursor_near=moved and distance < 150 and not fullscreen,
                                     window_changed=changed and self.reactive and not fullscreen and not fullscreen_changed,
                                     keyboard_events=keyboard_events, window_event=window_event,
                                     app_kind=self.app_context)
        self.last_window = window
        if action == "comment":
            if not (self.ai_enabled and self.trigger_ai_brain()):
                self.random_dialogue()
        elif action:
            self.pose_started = now
            if action == "curious":
                self.look_direction = -1 if QCursor.pos().x() < self.geometry().center().x() else 1
            self.refresh_asset()
            if action == "sleep":
                self.ai_generation += 1
                self.dismiss_bubble()
            elif action == "typing":
                self.offline_line("typing")
            elif action == "curious":
                self.offline_line(self.companion.reaction_kind)
            elif action == "idle" and was_following:
                self.follow_origin = None
                self.offline_line("follow")
            elif action == "fidget":
                self.offline_line(self.current_clip)

    def refresh_asset(self):
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
            NekoState.KNEADING: "knead", NekoState.FOLLOWING: "walk",
            NekoState.CHIN_SCRITCH: "chin_scritch", NekoState.ROLLING: "roll",
            NekoState.PAW_OFFER: "paw_offer", NekoState.EAR_RUB: "ear_rub",
            NekoState.PET_STRETCH: "pet_stretch", NekoState.BACK_ARCH: "back_arch",
            NekoState.HAPPY_HOP: "happy_hop", NekoState.SIDE_FLOP: "side_flop",
            NekoState.SHOULDER_PEEK: "shoulder_peek",
            NekoState.TAIL_CHASE: "tail_chase", NekoState.TAIL_CATCH: "tail_catch",
            NekoState.ARRIVING: "arrive", NekoState.LEAVING: "depart",
        }.get(self.companion.state, "idle")
        if self.companion.state in PET_STATES:
            self.companion.pose_until = self.pose_started + sum(CLIPS[self.current_clip].durations) / 1000
        self.current_asset = {
            NekoState.SLEEPING: "sleep", NekoState.PEEKING: "peek",
            NekoState.CURIOUS: "curious", NekoState.HAPPY: "happy",
            NekoState.GROOMING: "peek",
        }.get(self.companion.state, "idle")
        self.sync_animation()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.arrival_target is not None:
            top = max(0, self.arrival_top + self.height() - self.y())
            painter.setClipRect(0, top, self.width(), max(0, self.height() - top))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        now = time.monotonic()
        elapsed = now - self.pose_started
        state = self.companion.state
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(75, 55, 48, 18))
        if state not in (NekoState.ARRIVING, NekoState.LEAVING):
            painter.drawEllipse(QRectF(28 + CANVAS_PADDING, 99 + CANVAS_TOP, 56, 5))
        painter.save()
        painter.translate(self.width() // 2, 99 + CANVAS_TOP)
        movie = None if state in (NekoState.ARRIVING, NekoState.LEAVING) else self.movies.get(self.current_asset)
        pixmap = self.atlas.frame(self.current_clip, elapsed, self.motion)
        # Keep the visible origin stable when transparent top padding is added.
        top = -100 - CANVAS_TOP
        if movie and not movie.currentPixmap().isNull():
            pixmap = movie.currentPixmap().scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
            top = -pixmap.height()
        elif pixmap.isNull():
            pixmap = self.assets[self.current_asset].scaled(88, 88, Qt.KeepAspectRatio, Qt.FastTransformation)
            top = -pixmap.height()
        if pixmap.isNull():
            painter.setPen(QColor("#a67671"))
            painter.drawText(QRectF(-45, -85, 90, 85), Qt.AlignCenter, "=^·ω·^=")
        else:
            if state == NekoState.FOLLOWING and self.look_direction > 0:
                painter.scale(-1, 1)
            painter.drawPixmap(-pixmap.width() // 2, top, pixmap)
        painter.restore()
        if state in PET_STATES:
            painter.setPen(QColor("#cf9699"))
            painter.setFont(QFont("Segoe UI Symbol", 12))
            painter.drawText(QRectF(78 + CANVAS_PADDING, 12 + CANVAS_TOP - (elapsed * 4 if self.motion else 0), 22, 24), "♡")

    def say(self, text, prompted=False):
        if (self.closing or self.is_manually_hidden or self.fullscreen
                or not self.isVisible() or (self.quiet and not prompted)
                or self.companion.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP,
                                            NekoState.ARRIVING, NekoState.LEAVING)):
            return False
        text = " ".join(str(text).split())[:140]
        if not text:
            return False
        self.bubble.setText(text)
        self.bubble.adjustSize()
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        area = screen.availableGeometry()
        x = max(area.left() + 6, min(self.x() + self.width() // 2 - self.bubble.width() // 2,
                                    area.right() - self.bubble.width() - 6))
        y = self.y() - self.bubble.height() - 4
        if y < area.top():
            y = self.geometry().bottom() + 4
        y = max(area.top(), min(y, area.bottom() - self.bubble.height()))
        self.bubble.move(x, y)
        self.bubble.show()
        self.bubble_timer.start(max(5500, min(10000, len(text) * 75)))
        self.companion.comments += 1
        self.last_words = time.monotonic()
        return True

    def offline_line(self, kind, prompted=False):
        pause = max(8, min(30, self.companion.chatter_seconds * 0.22))
        if not prompted and (self.bubble.isVisible() or time.monotonic() - self.last_words < pause):
            return False
        if self.say(self.dialogue.pick(kind), prompted=prompted):
            self.ai_generation += 1
            if kind == "hello":
                self.play_sound("chirp")
            return True
        return False

    def random_dialogue(self):
        self.offline_line("idle")

    def pet_reaction(self):
        if self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
            return
        now = time.monotonic()
        was_sleeping = self.companion.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP)
        self.ai_generation += 1
        started = self.companion.pet(now)
        self.play_sound(random.choice(("mew", "purr")), prompted=True)
        if not started:
            return
        self.pose_started = now
        self.refresh_asset()
        if now - self.last_pet_words >= 6:
            self.offline_line("wake" if was_sleeping else "pet", prompted=True)
            self.last_pet_words = now

    def trigger_ai_brain(self):
        if (self.brain_worker is not None or not self.ai_enabled or self.quiet
                or self.fullscreen or self.is_manually_hidden
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
        return True

    def on_brain_finished(self, text, success):
        if self.closing:
            return
        self.ai_status = ("AI is connected. Window titles only." if success else
                          "AI is unavailable. Check your API key or connection; offline company continues.")
        if (self.request_generation != self.ai_generation or not self.ai_enabled
                or self.quiet or time.monotonic() - self.request_started > 25):
            return
        # Recheck the foreground window: a game may have opened during the request.
        if desktop_activity()[2]:
            return
        if success:
            self.say(text)
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
        if self.companion.state in (NekoState.ARRIVING, NekoState.LEAVING):
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self.reset_pet_cursor()
            self.setCursor(Qt.ClosedHandCursor)
            self.stop_following()
            self.drag_origin = event.globalPosition().toPoint()
            self.drag_offset = self.drag_origin - self.pos()
            self.dragged = False
            event.accept()
        elif event.button() == Qt.RightButton:
            screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
            self.menu.exec(adjacent_position(self.frameGeometry(), self.menu.sizeHint(), screen.availableGeometry()))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_origin is not None:
            point = event.globalPosition().toPoint()
            if (point - self.drag_origin).manhattanLength() >= QApplication.startDragDistance():
                self.dragged = True
            if self.dragged:
                self.dismiss_bubble()
                if self.companion.state not in (NekoState.CURIOUS, NekoState.SLEEPING,
                                                NekoState.FALLING_ASLEEP, NekoState.WAKING):
                    now = time.monotonic()
                    self.companion.pose(NekoState.CURIOUS, now, 3)
                    self.pose_started = now
                    self.refresh_asset()
                self.move(point - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drag_origin is not None:
            if self.dragged:
                self.ai_generation += 1
                now = time.monotonic()
                if self.companion.state not in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.WAKING):
                    self.companion.pose(NekoState.PEEKING, now, 5)
                    self.pose_started = now
                self.companion.last_interaction = now
                self.refresh_asset()
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

    def position_to_bottom_right(self):
        area = QApplication.primaryScreen().availableGeometry()
        self.move(area.right() - self.width() - 24, area.bottom() - self.height() - 12)
        self.dismiss_bubble()

    def clamp_position(self, *args):
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
        self.companion.pet_pending = False
        self.reset_pet_cursor()
        self.restore_arrival_position()
        if self.companion.state == NekoState.LEAVING:
            self.finish_quit()
            return
        if self.companion.state == NekoState.ARRIVING:
            self.transition_timer.stop()
            self.companion.state = NekoState.IDLE
            self.refresh_asset()
        self.stop_following()
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
        if self.closing or self.companion.state == NekoState.LEAVING:
            return
        self.is_manually_hidden = False
        self.hide_action.setText("Hide Neko")
        self.companion.next_comment = time.monotonic() + self.companion.chatter_seconds
        self.fullscreen = desktop_activity()[2]
        self.activity.enabled = self.reactive and not self.fullscreen
        self.setVisible(not (self.fullscreen and self.hide_fullscreen))
        if greet and self.isVisible():
            if self.motion and not self.atlas.frame("arrive", 0).isNull():
                self.start_transition(NekoState.ARRIVING, "arrive")
            else:
                self.offline_line("hello")
        self.sync_animation()
        self.pin_to_top(force=True)

    def open_stats_window(self):
        if self.closing or self.companion.state == NekoState.LEAVING:
            return
        self.stop_following()
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
        for key, value in {"quiet": self.quiet, "motion": self.motion,
                           "sounds_enabled": self.sounds_enabled,
                           "follow_mouse": self.follow_mouse,
                           "sleep_seconds": self.companion.sleep_seconds,
                           "sleep_duration": self.companion.sleep_duration,
                           "chatter_seconds": self.companion.chatter_seconds,
                           "idle_seconds": self.companion.idle_seconds,
                           "reactive": self.reactive, "hide_fullscreen": self.hide_fullscreen,
                           "ai_enabled": self.ai_enabled,
                           "position": (self.arrival_target if self.arrival_target is not None else self.pos())
                                       + QPoint(CANVAS_PADDING, CANVAS_TOP),
                           "pets": self.total_pets + self.companion.pets,
                           "naps": self.total_naps + self.companion.naps}.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def quit_neko(self):
        if self.closing or self.companion.state == NekoState.LEAVING:
            return
        self.restore_arrival_position()
        if (self.motion and self.isVisible() and not self.fullscreen and not self.is_manually_hidden
                and not self.atlas.frame("depart", 0).isNull()):
            self.stop_following()
            self.drag_origin = None
            self.ai_generation += 1
            self.dismiss_bubble()
            self.stop_sound()
            self.menu.hide()
            if self.stats_window:
                self.stats_window.close()
            self.start_transition(NekoState.LEAVING, "depart")
        else:
            self.finish_quit()

    def restore_arrival_position(self):
        if self.arrival_target is not None:
            self.move(self.arrival_target)
            self.arrival_target = None

    def start_transition(self, state, clip):
        self.reset_pet_cursor()
        self.transition_timer.stop()
        self.restore_arrival_position()
        now = time.monotonic()
        duration = sum(CLIPS[clip].durations)
        self.companion.pose(state, now, duration / 1000)
        self.pose_started = now
        if state == NekoState.ARRIVING:
            self.arrival_target = self.pos()
            screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
            self.arrival_top = screen.geometry().top() - self.height()
            self.move(self.arrival_target.x(), self.arrival_top)
        self.refresh_asset()
        if state != NekoState.ARRIVING:
            self.transition_timer.start(duration)

    def finish_transition(self):
        self.transition_timer.stop()
        if self.companion.state == NekoState.LEAVING:
            self.finish_quit()
        elif self.companion.state == NekoState.ARRIVING:
            self.restore_arrival_position()
            now = time.monotonic()
            self.companion.state = NekoState.IDLE
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
