"""The quiet part of Neko: timing and moods, independent of the desktop UI."""

from enum import Enum, auto
import random


class NekoState(Enum):
    IDLE = auto()
    SLEEPING = auto()
    FALLING_ASLEEP = auto()
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
    KNEADING = auto()
    LOAFING = auto()
    FOLLOWING = auto()
    CHIN_SCRITCH = auto()
    ROLLING = auto()
    PAW_OFFER = auto()
    EAR_RUB = auto()
    PET_STRETCH = auto()
    BACK_ARCH = auto()
    HAPPY_HOP = auto()
    SIDE_FLOP = auto()
    SHOULDER_PEEK = auto()
    TAIL_CHASE = auto()
    TAIL_CATCH = auto()
    ARRIVING = auto()
    LEAVING = auto()


PET_STATES = (NekoState.HAPPY, NekoState.CHEEK_RUB, NekoState.KNEADING,
              NekoState.CHIN_SCRITCH, NekoState.ROLLING, NekoState.PAW_OFFER, NekoState.EAR_RUB,
              NekoState.PET_STRETCH, NekoState.BACK_ARCH, NekoState.HAPPY_HOP,
              NekoState.SIDE_FLOP, NekoState.SHOULDER_PEEK)
IDLE_STATES = (NekoState.STRETCHING, NekoState.GROOMING, NekoState.PEEKING,
               NekoState.YAWNING, NekoState.TAIL_SWISH, NekoState.EAR_FLICK,
               NekoState.SNIFFING, NekoState.LOAFING, NekoState.CURIOUS,
               NekoState.TAIL_CHASE, NekoState.TAIL_CATCH)
APP_MOODS = {"music": NekoState.TAIL_SWISH, "video": NekoState.LOAFING,
             "coding": NekoState.TYPING, "drawing": NekoState.CURIOUS,
             "writing": NekoState.TYPING, "chat": NekoState.CHEEK_RUB,
             "game": NekoState.PEEKING, "files": NekoState.SNIFFING,
             "terminal": NekoState.EAR_FLICK}


class Companion:
    def __init__(self, now, rng=None, sleep_seconds=180, chatter_seconds=75, idle_seconds=14,
                 sleep_duration=0):
        self.rng = rng if rng is not None else random.Random()
        self.sleep_seconds = sleep_seconds
        self.sleep_duration = sleep_duration
        self.nap_started = None
        self.chatter_seconds = chatter_seconds
        self.idle_seconds = idle_seconds
        self.state = NekoState.IDLE
        self.pose_until = 0
        self.next_nap = 0
        self.next_idle = now + self.idle_seconds
        self.next_comment = now + self.chatter_seconds
        self.last_curiosity = now - 18
        self.last_typing = now - 45
        self.drowsy = False
        self.last_interaction = now - 90
        self.last_idle = None
        self.last_pet = None
        self.pet_bag = []
        self.pet_pending = False
        self.pending_window = None
        self.reaction_kind = "switch"
        self.pets = 0
        self.naps = 0
        self.comments = 0

    def pose(self, state, now, seconds):
        if state not in PET_STATES:
            self.pet_pending = False
        self.state = state
        self.pose_until = now + seconds
        self.next_idle = max(self.next_idle, now + self.idle_seconds)

    def pet(self, now):
        if self.state in (NekoState.ARRIVING, NekoState.LEAVING):
            return False
        self.pets += 1
        self.last_interaction = now
        if self.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP):
            self.wake(now)
            return True
        if self.state == NekoState.WAKING:
            return False
        self.next_comment = max(self.next_comment, now + 15)
        if self.state in PET_STATES and now < self.pose_until:
            self.pet_pending = True
            return False
        self.start_pet(now)
        return True

    def start_pet(self, now):
        self.pet_pending = False
        if not self.pet_bag:
            self.pet_bag = list(PET_STATES)
            self.rng.shuffle(self.pet_bag)
            if self.pet_bag[-1] == self.last_pet:
                self.pet_bag[0], self.pet_bag[-1] = self.pet_bag[-1], self.pet_bag[0]
        self.last_pet = self.pet_bag.pop()
        self.pose(self.last_pet, now, 5.8)

    def finish_pet(self, now):
        pending = self.pet_pending
        self.pet_pending = False
        if pending:
            self.start_pet(now)
            return "pet"
        self.state = NekoState.IDLE
        return "idle"

    def wake(self, now):
        self.pending_window = None
        self.nap_started = None
        self.next_nap = now + self.sleep_seconds
        self.next_comment = max(self.next_comment, now + 15)
        self.last_curiosity = now
        self.pose(NekoState.WAKING, now, 2.6)

    def tick(self, now, idle_seconds, quiet=False, cursor_near=False,
             window_changed=False, keyboard_events=0, window_event=None, app_kind=None):
        if self.state in (NekoState.ARRIVING, NekoState.LEAVING):
            self.pending_window = None
            return None
        if idle_seconds < 10:
            self.drowsy = False
        if window_event or window_changed:
            self.pending_window = (window_event or "switch", now, app_kind)
        if self.pending_window and now - self.pending_window[1] > 7:
            self.pending_window = None

        if self.state in (NekoState.SLEEPING, NekoState.FALLING_ASLEEP, NekoState.WAKING):
            self.pending_window = None
            if self.state == NekoState.FALLING_ASLEEP and now >= self.pose_until:
                self.state = NekoState.SLEEPING
                self.nap_started = now
                return "settled"
            if (self.state == NekoState.SLEEPING and self.sleep_duration > 0
                    and self.nap_started is not None and now >= self.nap_started + self.sleep_duration):
                self.wake(now)
                return "wake"
            if self.state == NekoState.WAKING and now >= self.pose_until:
                self.state = NekoState.IDLE
                return "idle"
            return None

        if self.state in PET_STATES:
            return self.finish_pet(now) if now >= self.pose_until else None
        if idle_seconds >= self.sleep_seconds and now >= self.next_nap:
            self.pending_window = None
            self.pose(NekoState.FALLING_ASLEEP, now, 2.6)
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
            choices = [s for s in IDLE_STATES if s != self.last_idle
                       for _ in range(3 if s in (NekoState.TAIL_CHASE, NekoState.TAIL_CATCH) else 1)]
            self.last_idle = self.rng.choice(choices)
            self.pose(self.last_idle, now, 8 if self.last_idle == NekoState.LOAFING else 6)
            self.next_idle = now + self.idle_seconds * self.rng.uniform(0.8, 1.3)
            return "fidget"

        if (not quiet and idle_seconds < self.sleep_seconds * 0.8 and now >= self.next_comment
                and now - self.last_interaction >= 15):
            self.next_comment = now + self.chatter_seconds * self.rng.uniform(0.8, 1.3)
            return "comment"
        return None
