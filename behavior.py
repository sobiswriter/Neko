"""The quiet part of Neko: timing and moods, independent of the desktop UI."""

from enum import Enum, auto
import random


class NekoState(Enum):
    IDLE = auto()
    SLEEPING = auto()
    PEEKING = auto()
    CURIOUS = auto()
    STRETCHING = auto()
    GROOMING = auto()
    HAPPY = auto()
    TYPING = auto()
    YAWNING = auto()
    WAKING = auto()
    TAIL_SWISH = auto()
    EAR_FLICK = auto()
    SNIFFING = auto()
    CHEEK_RUB = auto()
    WAVING = auto()
    KNEADING = auto()
    LOAFING = auto()
    FOLLOWING = auto()


PET_STATES = (NekoState.HAPPY, NekoState.CHEEK_RUB, NekoState.WAVING, NekoState.KNEADING)
IDLE_STATES = (NekoState.STRETCHING, NekoState.GROOMING, NekoState.PEEKING,
               NekoState.YAWNING, NekoState.TAIL_SWISH, NekoState.EAR_FLICK,
               NekoState.SNIFFING, NekoState.LOAFING, NekoState.CURIOUS)
APP_MOODS = {"music": NekoState.TAIL_SWISH, "video": NekoState.LOAFING,
             "coding": NekoState.TYPING, "drawing": NekoState.CURIOUS,
             "writing": NekoState.TYPING, "chat": NekoState.WAVING,
             "game": NekoState.PEEKING, "files": NekoState.SNIFFING,
             "terminal": NekoState.EAR_FLICK}


class Companion:
    def __init__(self, now, rng=None, sleep_seconds=180, chatter_seconds=75, idle_seconds=14):
        self.rng = rng if rng is not None else random.Random()
        self.sleep_seconds = sleep_seconds
        self.chatter_seconds = chatter_seconds
        self.idle_seconds = idle_seconds
        self.state = NekoState.IDLE
        self.pose_until = 0
        self.sleep_until = 0
        self.next_nap = 0
        self.next_idle = now + self.idle_seconds
        self.next_comment = now + self.chatter_seconds
        self.last_curiosity = now - 18
        self.last_typing = now - 45
        self.drowsy = False
        self.last_interaction = now - 90
        self.last_idle = None
        self.last_pet = None
        self.pending_window = None
        self.reaction_kind = "switch"
        self.pets = 0
        self.naps = 0
        self.comments = 0

    def pose(self, state, now, seconds):
        self.state = state
        self.pose_until = now + seconds
        self.next_idle = max(self.next_idle, now + self.idle_seconds)

    def pet(self, now):
        self.pets += 1
        self.last_interaction = now
        if self.state == NekoState.SLEEPING:
            return
        self.next_comment = max(self.next_comment, now + 15)
        self.last_pet = self.rng.choice([s for s in PET_STATES if s != self.last_pet])
        self.pose(self.last_pet, now, 5.8)

    def tick(self, now, idle_seconds, quiet=False, cursor_near=False,
             window_changed=False, keyboard_events=0, window_event=None, app_kind=None):
        if idle_seconds < 10:
            self.drowsy = False
        if window_event or window_changed:
            self.pending_window = (window_event or "switch", now, app_kind)
        if self.pending_window and now - self.pending_window[1] > 7:
            self.pending_window = None

        if self.state == NekoState.SLEEPING:
            self.pending_window = None
            if now < self.sleep_until:
                return None
            self.pose(NekoState.WAKING, now, 6)
            self.next_nap = now + self.sleep_seconds
            self.next_idle = now + self.idle_seconds
            self.next_comment = max(self.next_comment, now + 15)
            self.last_curiosity = now
            return "wake"

        if idle_seconds >= self.sleep_seconds and now >= self.next_nap:
            self.pending_window = None
            self.state = NekoState.SLEEPING
            self.sleep_until = now + 90
            self.naps += 1
            return "sleep"

        if self.state != NekoState.IDLE:
            if now >= self.pose_until:
                self.state = NekoState.IDLE
                return "idle"
            return None

        if keyboard_events >= 6 and now - self.last_typing >= 30:
            self.last_typing = now
            self.pose(NekoState.TYPING, now, 5.5)
            return "typing"

        if self.pending_window and now - self.last_curiosity >= 8:
            self.reaction_kind = self.pending_window[0]
            context = self.pending_window[2] if self.reaction_kind in ("open", "switch", "tab") else None
            self.reaction_kind = context or self.reaction_kind
            self.pending_window = None
            self.last_curiosity = now
            state = APP_MOODS.get(context, NekoState.PEEKING if self.reaction_kind == "close" else NekoState.CURIOUS)
            self.pose(state, now, 6)
            return "curious"

        if cursor_near and now - self.last_curiosity >= 18:
            self.reaction_kind = "cursor"
            self.last_curiosity = now
            self.pose(NekoState.SNIFFING, now, 5.5)
            return "curious"

        if idle_seconds >= self.sleep_seconds * 0.55 and not self.drowsy:
            self.drowsy = True
            self.pose(NekoState.YAWNING, now, 5.5)
            return "fidget"

        if now >= self.next_idle:
            choices = [s for s in IDLE_STATES if s != self.last_idle]
            self.last_idle = self.rng.choice(choices)
            self.pose(self.last_idle, now, 8 if self.last_idle == NekoState.LOAFING else 6)
            self.next_idle = now + self.idle_seconds * self.rng.uniform(0.8, 1.3)
            return "fidget"

        if (not quiet and idle_seconds < self.sleep_seconds * 0.8 and now >= self.next_comment
                and now - self.last_interaction >= 15):
            self.next_comment = now + self.chatter_seconds * self.rng.uniform(0.8, 1.3)
            return "comment"
        return None
