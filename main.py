import sys
import random
import os
import winshell
from win32com.client import Dispatch
from enum import Enum, auto
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, 
    QMenu, QSystemTrayIcon, QStyle
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QIcon

class NekoState(Enum):
    IDLE = auto()
    TALKING = auto()
    SLEEPING = auto()

class NekoWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.state = NekoState.IDLE
        self.drag_position = QPoint()
        
        self.init_ui()
        self.load_assets()
        self.init_tray()
        self.init_timers()
        
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
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        idle_path = os.path.join(base_path, 'assets', 'neko_idle.png')
        sleep_path = os.path.join(base_path, 'assets', 'neko_sleep.png')
        happy_path = os.path.join(base_path, 'assets', 'neko_happy.png')
        
        self.idle_pixmap = QPixmap(idle_path)
        self.sleep_pixmap = QPixmap(sleep_path)
        self.happy_pixmap = QPixmap(happy_path)
        
        # Scale if necessary
        if not self.idle_pixmap.isNull():
            self.idle_pixmap = self.idle_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.sleep_pixmap.isNull():
            self.sleep_pixmap = self.sleep_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        if not self.happy_pixmap.isNull():
            self.happy_pixmap = self.happy_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)

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

    def set_next_dialogue_timer(self):
        # 2 to 5 minutes
        ms = random.randint(120000, 300000)
        self.dialogue_timer.start(ms)

    def reset_sleep_timer(self):
        # 0.5 minute = 30000 ms
        self.sleep_timer.start(30000)
        if self.state == NekoState.SLEEPING:
            self.wake_up()

    def do_greeting(self):
        greetings = ["mrrp… hello", "you’re back, meow", "hi hi", "mew~", "oh! there you are"]
        self.say(random.choice(greetings))

    def random_dialogue(self):
        if self.state == NekoState.SLEEPING:
            self.set_next_dialogue_timer()
            return
            
        lines = [
            "mew?", "what are you doing", "mrrp", "i’m watching", 
            "you look busy", "meow meow", "hm…", "don’t mind me"
        ]
        self.say(random.choice(lines))
        self.set_next_dialogue_timer()

    def pet_reaction(self):
        lines = ["mrrrow~", "hehe meow", "again again", "purrr…", "that’s nice", "more pets pls"]
        self.set_image(self.happy_pixmap)
        self.say(random.choice(lines))

    def wake_up(self):
        self.state = NekoState.IDLE
        self.setWindowOpacity(1.0)
        self.set_image(self.idle_pixmap)
        
        wake_lines = ["m… meow?", "did i sleep", "oh hi", "i was dreaming"]
        self.say(random.choice(wake_lines))

    def go_to_sleep(self):
        self.state = NekoState.SLEEPING
        self.set_image(self.sleep_pixmap)
        self.setWindowOpacity(0.7)
        self.hide_bubble()

    def say(self, text):
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

    # Window Movement & Interaction
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
            # Interaction Logic
            if self.state == NekoState.SLEEPING:
                self.reset_sleep_timer()
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

    def show_context_menu(self, pos):
        menu = QMenu(self)
        hide_action = menu.addAction("Hide")
        exit_action = menu.addAction("Exit")
        
        action = menu.exec(pos)
        if action == hide_action:
            self.hide()
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
        exit_action = tray_menu.addAction("Exit")
        
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
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
                
                # Use pythonw.exe to run silently without a console window
                pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
                shortcut.Targetpath = pythonw_path if os.path.exists(pythonw_path) else sys.executable
                
                script_path = os.path.abspath(__file__)
                shortcut.Arguments = f'"{script_path}"'
                shortcut.WorkingDirectory = os.path.dirname(script_path)
                
                # Use python icon or just default
                shortcut.IconLocation = sys.executable
                shortcut.save()
        except Exception as e:
            print(f"Failed to set up autostart: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Needs to stay running when main window hides
    QApplication.setQuitOnLastWindowClosed(False)
    
    neko = NekoWidget()
    neko.show()
    
    sys.exit(app.exec())
