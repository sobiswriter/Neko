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


class Companion:
    def __init__(self, now, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.state = NekoState.IDLE
        self.pose_until = 0
        self.next_idle = now + self.rng.uniform(20, 40)
        self.next_comment = now + self.rng.uniform(720, 1200)
        self.last_curiosity = now
        self.last_interaction = now - 90
        self.last_idle = None
        self.pets = 0
        self.naps = 0
        self.comments = 0

    def pose(self, state, now, seconds):
        self.state = state
        self.pose_until = now + seconds
        self.next_idle = max(self.next_idle, now + 20)

    def pet(self, now):
        self.pets += 1
        self.last_interaction = now
        self.next_comment = max(self.next_comment, now + 240)
        self.pose(NekoState.HAPPY, now, 3.2)

    def tick(self, now, idle_seconds, quiet=False, cursor_near=False,
             window_changed=False):
        if idle_seconds >= 180:
            if self.state != NekoState.SLEEPING:
                self.state = NekoState.SLEEPING
                self.naps += 1
                return "sleep"
            return None

        if self.state == NekoState.SLEEPING:
            self.state = NekoState.IDLE
            self.next_idle = now + self.rng.uniform(20, 40)
            self.next_comment = max(self.next_comment, now + 240)
            self.last_curiosity = now
            return "wake"

        if self.state != NekoState.IDLE:
            if now >= self.pose_until:
                self.state = NekoState.IDLE
                return "idle"
            return None

        if (cursor_near or window_changed) and now - self.last_curiosity >= 45:
            self.last_curiosity = now
            self.pose(NekoState.CURIOUS, now, 2.8)
            return "curious"

        if now >= self.next_idle:
            choices = [s for s in (NekoState.STRETCHING, NekoState.GROOMING,
                                   NekoState.PEEKING) if s != self.last_idle]
            self.last_idle = self.rng.choice(choices)
            self.pose(self.last_idle, now, 3.5)
            self.next_idle = now + self.rng.uniform(25, 55)
            return "fidget"

        if (not quiet and idle_seconds < 120 and now >= self.next_comment
                and now - self.last_interaction >= 90):
            self.next_comment = now + self.rng.uniform(720, 1200)
            return "comment"
        return None
