import sys
import random
import os
import winshell
import win32gui
from win32com.client import Dispatch
from enum import Enum, auto
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, 
    QMenu, QSystemTrayIcon, QStyle, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QIcon

class NekoState(Enum):
    IDLE = auto()
    TALKING = auto()
    SLEEPING = auto()
    PEEKING = auto()

class StatsWindow(QWidget):
    def __init__(self, neko_ref):
        super().__init__()
        self.neko = neko_ref
        self.init_ui()
        
        # Timer to refresh stats periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_stats)
        self.refresh_timer.start(1000) # Every 1 second
        
    def init_ui(self):
        self.setWindowTitle("Neko Stats")
        self.setFixedSize(250, 180)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        
        layout = QGridLayout()
        
        self.lbl_attention = QLabel("Attention Meter:")
        self.val_attention = QLabel("0.0")
        
        self.lbl_level = QLabel("Attention Level:")
        self.val_level = QLabel("LOW")
        
        self.lbl_pets = QLabel("Pets Received:")
        self.val_pets = QLabel("0")
        
        self.lbl_sleeps = QLabel("Times Slept:")
        self.val_sleeps = QLabel("0")
        
        self.lbl_lines = QLabel("Lines Spoken:")
        self.val_lines = QLabel("0")
        
        # Styling
        font = self.lbl_attention.font()
        font.setPointSize(10)
        
        for lbl in [self.lbl_attention, self.val_attention, self.lbl_level, self.val_level,
                    self.lbl_pets, self.val_pets, self.lbl_sleeps, self.val_sleeps,
                    self.lbl_lines, self.val_lines]:
            lbl.setFont(font)
            
        layout.addWidget(self.lbl_attention, 0, 0)
        layout.addWidget(self.val_attention, 0, 1)
        
        layout.addWidget(self.lbl_level, 1, 0)
        layout.addWidget(self.val_level, 1, 1)
        
        layout.addWidget(self.lbl_pets, 2, 0)
        layout.addWidget(self.val_pets, 2, 1)
        
        layout.addWidget(self.lbl_sleeps, 3, 0)
        layout.addWidget(self.val_sleeps, 3, 1)
        
        layout.addWidget(self.lbl_lines, 4, 0)
        layout.addWidget(self.val_lines, 4, 1)
        
        self.setLayout(layout)
        self.update_stats()
        
    def update_stats(self):
        self.val_attention.setText(f"{self.neko.attention_meter:.1f} / 100")
        self.val_level.setText(self.neko.attention_level)
        self.val_pets.setText(str(self.neko.stats_pets_received))
        self.val_sleeps.setText(str(self.neko.stats_times_slept))
        self.val_lines.setText(str(self.neko.stats_lines_spoken))

class NekoWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.state = NekoState.IDLE
        self.drag_position = QPoint()
        
        self.last_active_window = 0
        self.window_change_count = 0
        
        # --- NEW: Attention Meter System ---
        self.attention_meter = 0.0  # 0 to 100
        self.high_attention_unanswered_time = 0
        self.giving_up = False
        self.is_manually_hidden = False
        self.temp_unhidden_for_dialogue = False
        
        self.stats_pets_received = 0
        self.stats_times_slept = 0
        self.stats_lines_spoken = 0
        self.stats_window = None
        # -----------------------------------
        
        self.init_ui()
        self.load_assets()
        self.init_timers()
        self.init_tray()
        
        # Initial position - bottom right
        self.position_to_bottom_right()
        
        # Start the inactivity/sleep tracking
        self.reset_sleep_timer()
        
        # Startup greeting timer (5 seconds)
        QTimer.singleShot(5000, self.do_greeting)
        
        # Ensure it runs on startup
        self.setup_autostart()
        
        # Enable mouse tracking so enterEvent detects hover without clicking
        self.setMouseTracking(True)

    def init_ui(self):
        # Frameless, Always on Top, Tool window (no taskbar icon)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Speech bubble
        self.bubble = QLabel("")
        self.bubble.setAlignment(Qt.AlignCenter)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 220);
                border: 2px solid #aaa;
                border-radius: 12px;
                padding: 6px 12px;
                font-family: 'Segoe UI', Arial;
                font-weight: bold;
                font-size: 13px;
                color: #333;
            }
        """)
        
        # Prevent layout from shifting when the bubble hides/shows
        size_policy = self.bubble.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.bubble.setSizePolicy(size_policy)
        
        self.bubble.hide()
        
        # Neko image
        self.neko_image = QLabel()
        self.neko_image.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.bubble)
        self.layout.addWidget(self.neko_image)
        self.layout.setAlignment(self.bubble, Qt.AlignBottom | Qt.AlignHCenter)
        self.layout.setAlignment(self.neko_image, Qt.AlignTop | Qt.AlignHCenter)
        
        self.setLayout(self.layout)
        
        self.setFixedSize(160, 200)

    def load_assets(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        idle_path = os.path.join(base_path, 'assets', 'neko_idle.png')
        sleep_path = os.path.join(base_path, 'assets', 'neko_sleep.png')
        happy_path = os.path.join(base_path, 'assets', 'neko_happy.png')
        peek_path = os.path.join(base_path, 'assets', 'neko_peek.png')
        curious_path = os.path.join(base_path, 'assets', 'neko_curious.png')
        agitated_path = os.path.join(base_path, 'assets', 'neko_agitated.png')
        
        self.idle_pixmap = QPixmap(idle_path)
        self.sleep_pixmap = QPixmap(sleep_path)
        self.happy_pixmap = QPixmap(happy_path)
        self.peek_pixmap = QPixmap(peek_path)
        self.curious_pixmap = QPixmap(curious_path)
        self.agitated_pixmap = QPixmap(agitated_path)
        
        # Scale if necessary
        if not self.idle_pixmap.isNull():
            self.idle_pixmap = self.idle_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.sleep_pixmap.isNull():
            self.sleep_pixmap = self.sleep_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.happy_pixmap.isNull():
            self.happy_pixmap = self.happy_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.peek_pixmap.isNull():
            self.peek_pixmap = self.peek_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.curious_pixmap.isNull():
            self.curious_pixmap = self.curious_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.agitated_pixmap.isNull():
            self.agitated_pixmap = self.agitated_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.set_image(self.idle_pixmap)

    def set_image(self, pixmap):
        if not pixmap.isNull():
            self.neko_image.setPixmap(pixmap)
        else:
            self.neko_image.setText("[NEKO]")
            self.neko_image.setStyleSheet("color: white; background-color: black; padding: 10px;")

    def init_timers(self):
        # Speech bubble timer
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.hide_bubble)
        
        # Random dialogue timer (every 2-5 minutes)
        self.dialogue_timer = QTimer(self)
        self.dialogue_timer.timeout.connect(self.random_dialogue)
        self.set_next_dialogue_timer()
        
        # Sleep timer (3 minutes of inactivity)
        self.sleep_timer = QTimer(self)
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.go_to_sleep)
        
        # Active window tracker (polls every 2 seconds to reduce noise)
        self.window_tracker_timer = QTimer(self)
        self.window_tracker_timer.timeout.connect(self.check_active_window)
        self.window_tracker_timer.start(2000)
        
        # Window change reset timer
        self.window_change_reset_timer = QTimer(self)
        self.window_change_reset_timer.setSingleShot(True)
        self.window_change_reset_timer.timeout.connect(self.reset_window_change_count)
        
        # Peek back-to-sleep timer
        self.peek_timer = QTimer(self)
        self.peek_timer.setSingleShot(True)
        self.peek_timer.timeout.connect(self.end_peek)
        
        # --- NEW: Attention Tracker Update Loop ---
        self.attention_tracker_timer = QTimer(self)
        self.attention_tracker_timer.timeout.connect(self.update_attention)
        self.attention_tracker_timer.start(10000)  # Every 10 seconds

    def set_next_dialogue_timer(self):
        if self.attention_level == "HIGH":
            # 15 to 30 seconds
            ms = random.randint(15000, 30000)
        elif self.attention_level == "MEDIUM":
            # 30 to 60 seconds
            ms = random.randint(30000, 60000)
        else:
            # 1 to 2 minutes
            ms = random.randint(60000, 120000)
        self.dialogue_timer.start(ms)

    def reset_sleep_timer(self):
        if self.attention_level == "HIGH":
            self.sleep_timer.start(90000) # Resist sleeping (1.5 minutes)
        elif self.attention_level == "MEDIUM":
            self.sleep_timer.start(45000) # (45 seconds)
        else:
            self.sleep_timer.start(30000) # (30 seconds)
            
        if self.state in [NekoState.SLEEPING, NekoState.PEEKING]:
            self.wake_up()

    def check_active_window(self):
        # We track window changes in IDLE and TALKING
        if self.state not in [NekoState.SLEEPING, NekoState.PEEKING, NekoState.IDLE, NekoState.TALKING]:
            return
            
        current_window = win32gui.GetForegroundWindow()
        
        if current_window and self.last_active_window and current_window != self.last_active_window:
            
            # Action if IDLE or TALKING
            if self.state in [NekoState.IDLE, NekoState.TALKING]:
                self.window_change_count += 1
                self.reset_sleep_timer()  # Keep it awake like an interaction
                
                if self.window_change_count == 3:
                    # Speak on 3rd window switch (more stable than 2)
                    self.set_image(self.curious_pixmap)
                    lines = [
                        "Are you working?", "ooh, new app", "whatcha lookin at?", 
                        "switchy switchy", "working hard?", "so many windows!"
                    ]
                    self.say(random.choice(lines))
                    # Wait 8 seconds to turn back to idle (or get dizzy if 3 more changes)
                    self.window_change_reset_timer.start(8000)
                    
                elif self.window_change_count >= 6:
                    # Agitated state! Fast switching within the 8 seconds
                    self.set_image(self.agitated_pixmap)
                    lines = [
                        "wat r u doin?!", "my head's spinnin!", "slow down >_<", 
                        "too many screens!", "stahp switchin!", "ahhhhhhh!"
                    ]
                    self.say(random.choice(lines))
                    self.window_change_count = 0  # Reset after scolding
                    self.window_change_reset_timer.stop()
            
            # Action if SLEEPING or PEEKING
            else:
                self.window_change_count += 1
                
                # Start timer for full wake reset
                if self.window_change_count == 1:
                    self.window_change_reset_timer.start(12000)
                    
                if self.window_change_count >= 3:
                    # Wake up fully if frantic typing/switching is happening
                    self.wake_up()
                    self.say(random.choice(["woah, meow 0w0", "slow down!", "what's going on?", "you woke me -w-"]))
                    self.window_change_count = 0
                    self.window_change_reset_timer.stop()
                elif self.window_change_count >= 1 and self.state == NekoState.SLEEPING:
                    # Just peek if it's a minor change
                    self.start_peek()
                
        self.last_active_window = current_window

    def update_attention(self):
        if self.giving_up:
            return  # Paused attention math while ignoring

        # Base increase
        delta = 2.0 # Way faster base increase
        
        # Modifiers based on states
        if self.state in [NekoState.IDLE, NekoState.TALKING]:
            if self.window_change_count > 0:
                delta += 4.0  # Watching you be busy rapidly scales it
            else:
                delta += 1.0  # You are also idle
        elif self.state == NekoState.SLEEPING:
            delta += 0.8  # Slow increase while sleeping
            
        self.attention_meter += delta
        
        # Clamp bounds
        if self.attention_meter > 100.0:
            self.attention_meter = 100.0
            
        # Track decay if at HIGH
        if self.attention_level == "HIGH":
            self.high_attention_unanswered_time += 10
            
            # 5 minutes of no interaction at max level = decay (300 seconds)
            if self.high_attention_unanswered_time >= 300:
                self.trigger_giving_up()
        else:
            self.high_attention_unanswered_time = 0
            
    def trigger_giving_up(self):
        self.giving_up = True
        self.attention_meter = 10.0  # Drop back down to sad/content range
        self.high_attention_unanswered_time = 0
        if self.state in [NekoState.IDLE, NekoState.TALKING]:
             self.say("...nevermind")
             QTimer.singleShot(4000, self.go_to_sleep)

    @property
    def attention_level(self):
        if self.attention_meter <= 30:
            return "LOW"
        elif self.attention_meter <= 70:
            return "MEDIUM"
        else:
            return "HIGH"

    def reset_window_change_count(self):
        self.window_change_count = 0

    def start_peek(self):
        self.state = NekoState.PEEKING
        self.set_image(self.peek_pixmap)
        self.setWindowOpacity(0.9)
        self.peek_timer.start(3000)  # Peek for 3 seconds then go back to sleep

    def end_peek(self):
        if self.state == NekoState.PEEKING:
            self.go_to_sleep()

    def do_greeting(self):
        greetings = ["mrrp… hello", "you’re back, meow", "hi hi", "mew~", "oh! there you are"]
        self.say(random.choice(greetings))

    def random_dialogue(self):
        # If sleeping, there's a chance it wakes up just to talk
        if self.state == NekoState.SLEEPING:
            # Only wake occasionally if attention is high/medium
            if self.attention_level == "LOW" and random.random() < 0.8:
                self.set_next_dialogue_timer()
                return # stays asleep

            self.wake_up()
            lines = [
                "m... mrrp?", "i'm awake now", "where am i...",
                "just checking in", "is it time for treats?"
            ]
        else:
            if self.attention_level == "HIGH":
                lines = [
                    "hey…", "mrrp?", "look at me", "pet me?", 
                    "you forgot me", "i’m still here", "pay attention to me!",
                    "notice me...", "don't ignore me", "i want pets!", 
                    "play with me?", "meow meow meow!!"
                ]
            elif self.attention_level == "MEDIUM":
                lines = [
                    "mew?", "what are you doing", "i’m watching you", 
                    "busy?", "needs pets", "whatcha doing there", 
                    "interesting...", "i'm bored", "is that work?", 
                    "can I help?", "hmmm"
                ]
            else:
                lines = [
                    "mrrp", "comfy…", "i’m here", "needs muffins",
                    "so cozy", "warm...", "zzz...", "peaceful", 
                    "good human", "purr"
                ]
                
        self.say(random.choice(lines))
        self.set_next_dialogue_timer()

    def pet_reaction(self):
        self.stats_pets_received += 1
        
        # Satisfaction Event
        dropped_a_lot = False
        if self.attention_meter >= 25.0:
            dropped_a_lot = True

        self.attention_meter = max(0.0, self.attention_meter - 25.0)
        self.giving_up = False # Reset from sad state
        self.high_attention_unanswered_time = 0

        if dropped_a_lot:
            lines = ["purrr…", "hehe", "that’s nice", "stay…"]
        else:
            lines = ["mrrrow~", "hehe meow", "again again", "more pets pls"]
            
        self.set_image(self.happy_pixmap)
        self.say(random.choice(lines))

    def wake_up(self):
        self.state = NekoState.IDLE
        self.setWindowOpacity(1.0)
        self.set_image(self.idle_pixmap)
        
        wake_lines = ["m… meow?", "did i sleep", "oh hi", "i was dreaming"]
        self.say(random.choice(wake_lines))

    def go_to_sleep(self):
        self.stats_times_slept += 1
        self.state = NekoState.SLEEPING
        self.set_image(self.sleep_pixmap)
        self.setWindowOpacity(0.7)
        self.hide_bubble()

    def say(self, text):
        self.stats_lines_spoken += 1
        
        if self.is_manually_hidden:
            self.show()
            self.temp_unhidden_for_dialogue = True

        self.bubble.setText(text)
        self.bubble.show()
        self.state = NekoState.TALKING
        self.bubble_timer.start(4000)
        self.reset_sleep_timer()

    def hide_bubble(self):
        self.bubble.hide()
        if self.state == NekoState.TALKING:
            self.state = NekoState.IDLE
            self.set_image(self.idle_pixmap)
            
        if self.temp_unhidden_for_dialogue:
            self.hide()
            self.temp_unhidden_for_dialogue = False

    # Window Movement & Interaction
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
            # If she's temporarily unhidden for dialogue and user clicks her, unhide her completely.
            if self.temp_unhidden_for_dialogue:
                self.is_manually_hidden = False
                self.temp_unhidden_for_dialogue = False
            
            # Interaction Logic
            if self.state == NekoState.SLEEPING:
                self.reset_sleep_timer()
                self.giving_up = False
            else:
                self.pet_reaction()
                self.reset_sleep_timer()
                
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            self.reset_sleep_timer()

    def enterEvent(self, event):
        # Hover tracking for waking up
        self.reset_sleep_timer()
        super().enterEvent(event)

    def position_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.width() - self.width() - 50
        y = screen.height() - self.height() - 50
        self.move(x, y)

    def hide_neko(self):
        self.is_manually_hidden = True
        self.hide()

    def show_neko(self):
        self.is_manually_hidden = False
        self.temp_unhidden_for_dialogue = False
        self.show()

    def open_stats_window(self):
        if not self.stats_window:
            self.stats_window = StatsWindow(self)
        self.stats_window.show()
        self.stats_window.raise_()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        if self.is_manually_hidden:
            toggle_action = menu.addAction("Unhide")
        else:
            toggle_action = menu.addAction("Hide")
            
        stats_action = menu.addAction("Stats")
        exit_action = menu.addAction("Exit")
        
        action = menu.exec(pos)
        if action == toggle_action:
            if self.is_manually_hidden:
                self.show_neko()
            else:
                self.hide_neko()
        elif action == stats_action:
            self.open_stats_window()
        elif action == exit_action:
            QApplication.quit()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        if not self.idle_pixmap.isNull():
            icon = QIcon(self.idle_pixmap)
        
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Neko")
        hide_action = tray_menu.addAction("Hide Neko")
        stats_action = tray_menu.addAction("Stats")
        exit_action = tray_menu.addAction("Exit")
        
        show_action.triggered.connect(self.show_neko)
        hide_action.triggered.connect(self.hide_neko)
        stats_action.triggered.connect(self.open_stats_window)
        exit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_autostart(self):
        try:
            startup_path = winshell.startup()
            shortcut_path = os.path.join(startup_path, "DesktopNeko.lnk")
            
            if not os.path.exists(shortcut_path):
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                
                if getattr(sys, 'frozen', False):
                    # If running as PyInstaller executable
                    shortcut.Targetpath = sys.executable
                    shortcut.Arguments = ""
                    shortcut.WorkingDirectory = os.path.dirname(sys.executable)
                else:
                    # If running as Python script
                    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
                    shortcut.Targetpath = pythonw_path if os.path.exists(pythonw_path) else sys.executable
                    
                    script_path = os.path.abspath(__file__)
                    shortcut.Arguments = f'"{script_path}"'
                    shortcut.WorkingDirectory = os.path.dirname(script_path)
                
                # Use python icon or just default
                shortcut.IconLocation = sys.executable
                shortcut.save()
        except Exception as e:
            pass # Ignore print in noconsole mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Needs to stay running when main window hides
    QApplication.setQuitOnLastWindowClosed(False)
    
    neko = NekoWidget()
    neko.show()
    
    sys.exit(app.exec())
