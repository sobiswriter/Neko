"""Catch the Cursor timing and geometry. No desktop input ownership or saved history."""
from collections import deque
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Runway:
    left: float
    right: float
    y: float
    lift: float
    paw: tuple = (49, 80)

    def contains(self, cursor, tolerance=0):
        x, y = cursor
        return (self.left + self.paw[0] - tolerance <= x <= self.right + 191 - self.paw[0] + tolerance
                and self.y + self.paw[1] - self.lift - tolerance <= y
                <= self.y + 124 + tolerance)

    def jump(self, x, cursor, direction):
        for fraction, paw in ((.5, self.paw), (.8, (59, 124))):
            px = paw[0] if direction < 0 else 191 - paw[0]
            dx = cursor[0] - x - px
            height = (self.y + paw[1] - cursor[1]) / (4 * fraction * (1 - fraction))
            end = x + dx / fraction
            if (abs(end - x) <= 140 and 0 <= height <= self.lift
                    and self.left <= end <= self.right):
                return end, height
        return None


class GameTimer:
    """One coalesced intent; manual requests promote an automatic request."""
    def __init__(self, now, enabled=True, interval=90):
        self.enabled, self.interval = enabled, interval
        self.due = now + interval
        self.pending = None
        self.log = deque(maxlen=64)

    def request(self, now, manual=False):
        source = "manual" if manual else "automatic"
        if manual or self.pending is None:
            self.pending = source
            self.log.append((now, "queued", source))

    def tick(self, now, eligible):
        if self.enabled and now >= self.due and self.pending is None:
            self.request(now)
        if eligible and self.pending:
            source, self.pending = self.pending, None
            self.due = math.inf
            self.log.append((now, "started", source))
            return source
        return None

    def reset(self, now):
        self.pending = None
        self.due = now + self.interval

    def configure(self, now, enabled, interval):
        self.enabled = enabled
        self.interval = max(30, min(600, interval))
        if self.pending == "automatic":
            self.pending = None
        self.due = now + self.interval


class CursorGame:
    def __init__(self, now, origin, runway, motion=True, source="manual"):
        self.origin, self.runway, self.motion, self.source = origin, runway, motion, source
        self.x, self.y = origin
        self.phase, self.since, self.last = "ready", now, now
        self.deadline = math.inf
        self.direction = -1
        self.velocity = 0.0
        self.outside = None
        self.protested = False
        self.last_protest = -math.inf
        self.result = None
        self.line = "Here I come! That cursor is mine!"
        self.history = deque(maxlen=4)
        self.end_x, self.height, self.start_x = self.x, 0, self.x
        self.after_landing = None
        self.log = deque([(now, "ready")], maxlen=128)

    def enter(self, phase, now, line=None):
        self.phase, self.since = phase, now
        self.log.append((now, phase))
        if line:
            self.line = line

    def take_line(self):
        line, self.line = self.line, None
        return line

    def cancel(self, now):
        self.result = "cancel"
        self.line = None
        if self.phase == "jump":
            self.after_landing = "home"
        elif self.phase in ("win", "loss"):
            # Finish supported hops/folding before a queued deliberate interaction.
            return
        elif self.phase not in ("curl", "comfort", "done"):
            self.enter("home", now)

    def comfort(self, now):
        if self.phase != "curl":
            return False
        self.enter("comfort", now, "Okay… one more cuddle.")
        return True

    def position_at(self, now):
        if self.phase != "jump":
            return self.x, self.y
        t = max(0, min(1, (now - self.since) / .64))
        return (self.start_x + (self.end_x - self.start_x) * t,
                self.runway.y - 4 * self.height * t * (1 - t))

    def update(self, now, cursor, contact=False):
        dt, self.last = now - self.last, now
        if self.phase == "curl":
            return
        if dt < 0 or dt > 0.5:
            self.cancel(now)
            self.y = self.runway.y
            self.enter("home", now)
            return
        elapsed = now - self.since
        self.history.append(cursor)
        if self.phase in ("run", "turn", "prepare", "jump", "miss"):
            inside = self.runway.contains(cursor, 8 if self.outside is None else 0)
            self.outside = None if inside else (self.outside if self.outside is not None else now)
            outside_time = 0 if self.outside is None else now - self.outside
            if outside_time >= 1.5 and not self.protested and now - self.last_protest >= 8:
                reason = "Too high!" if cursor[1] < self.runway.y + self.runway.paw[1] - self.runway.lift else "Over here!"
                self.line = "No fair, you cheated! " + reason
                self.protested = True
                self.last_protest = now
                if self.phase in ("run", "turn", "miss"):
                    self.start_x = self.end_x = self.x
                    self.height = min(50, self.runway.lift) if self.motion else 0
                    self.enter("prepare", now)
                    return
            if inside:
                self.protested = False
            # A real visible contact wins the same instant as a deadline.
            if self.phase == "jump" and contact and self.result is None:
                self.result, self.after_landing = "win", "win"
            if self.result is None and (now >= self.deadline or outside_time >= 4):
                self.result = "loss"
                if self.phase == "jump":
                    self.after_landing = "loss"
                else:
                    self.enter("loss", now, "I almost had it…")
                return
        if self.phase == "ready" and elapsed >= 1.4:
            self.deadline = now + 45
            self.enter("run", now)
        elif self.phase == "run":
            target = self.history[0]
            desired = -1 if target[0] < self.x + 96 else 1
            if desired != self.direction and abs(self.velocity) > 10:
                self.velocity = 0
                self.enter("turn", now)
                return
            self.direction = desired
            solution = self.runway.jump(self.x, target, self.direction)
            if not self.motion:
                solution = (self.x, 0) if abs(target[0] - (self.x + (self.runway.paw[0] if desired < 0 else 191 - self.runway.paw[0]))) < 14 and abs(target[1] - self.runway.y - self.runway.paw[1]) < 14 else None
            if solution:
                self.start_x, (self.end_x, self.height) = self.x, solution
                self.velocity = 0
                self.enter("prepare", now)
            elif self.motion:
                self.velocity = min(210, self.velocity + 700 * dt)
                # Approach from the side with room for a complete landing.
                destination = max(self.runway.left, min(self.runway.right, target[0] - 96))
                delta = destination - self.x
                self.x += math.copysign(min(abs(delta), self.velocity * dt), delta) if delta else 0
        elif self.phase == "turn" and elapsed >= .35:
            self.direction *= -1
            self.enter("run", now)
        elif self.phase == "prepare" and elapsed >= .2:
            self.enter("jump", now)
        elif self.phase == "jump":
            t = min(1, elapsed / .64)
            self.x, self.y = self.position_at(now)
            if t >= 1:
                phase = self.after_landing or "miss"
                self.enter(phase, now, "Gotcha! I knew I could!" if phase == "win" else "I almost had it…" if phase == "loss" else None)
                self.after_landing = None
        elif self.phase == "miss" and elapsed >= .45:
            self.enter("run", now)
        elif self.phase == "win" and elapsed >= (4.342 if self.motion else 1.5):
            self.enter("home", now)
        elif self.phase == "home":
            self.y = self.runway.y
            delta = self.origin[0] - self.x
            self.direction = -1 if delta < 0 else 1
            self.x += math.copysign(min(abs(delta), 180 * dt), delta) if delta and self.motion else delta
            if abs(self.x - self.origin[0]) < 1:
                self.enter("settle", now)
        elif self.phase == "settle" and elapsed >= .5:
            self.enter("done", now)
        elif self.phase == "loss" and elapsed >= 1.8:
            self.enter("comfort" if self.result == "cancel" else "curl", now)
        elif self.phase == "comfort" and elapsed >= 2:
            self.enter("home", now)
