"""Catch the Cursor timing and geometry. No desktop input ownership or saved history."""
from collections import deque
from dataclasses import dataclass
import math

# Declaration, countdown and pursuit: the phases where the user is actually playing.
ACTIVE_PHASES = ("declare", "ready", "three", "two", "one", "go", "run", "turn", "prepare", "jump", "miss")
# She announces the game, holds that thought long enough to read, then starts the countdown.
DECLARE_SECONDS = 1.8
# Trips home: a bounding run (the chase's own gallop) covers the distance, then she walks the
# last stretch at the authored stroll so the walk cycle and its settle keep their place.
RUN_HOME_FROM = 160   # Farther than this, she runs.
WALK_HOME_WITHIN = 120  # Closer than this, she walks.
RUN_SPEED, RUN_ACCELERATION, WALK_SPEED = 210, 700, 180


# The play area: she can jump this high above her home ground and hop this far down below it.
MAX_LIFT = 140
MAX_DROP = 80
REACH_LOW = 124   # Lowest arrow she can touch from a ground (her landing paw, below the ground line).


@dataclass(frozen=True)
class Runway:
    left: float
    right: float
    y: float
    lift: float
    paw: tuple = (49, 80)
    drop: float = 0   # How far below home ground (y) she may hop down.

    def invites(self, cursor, origin_x, tolerance=0):
        left = (self.left + self.paw[0], origin_x - 40)
        right = (origin_x + 192 + 40, self.right + 191 - self.paw[0])
        return self.contains(cursor, tolerance) and any(b - a >= 120 and a - tolerance <= cursor[0] <= b + tolerance for a, b in (left, right))

    def contains(self, cursor, tolerance=0):
        x, y = cursor
        return (self.left + self.paw[0] - tolerance <= x <= self.right + 191 - self.paw[0] + tolerance
                and self.y + self.paw[1] - self.lift - tolerance <= y
                <= self.y + REACH_LOW + self.drop + tolerance)

    def jump(self, x, cursor, direction, ground=None, landing=None):
        """A pounce from `ground` to `landing` (window y of her feet line) whose paw meets the arrow.
        Returns (end_x, height) or None. Heights are measured above the straight take-off/landing line."""
        g0 = self.y if ground is None else ground
        g1 = g0 if landing is None else landing
        top = self.y - self.lift   # The highest the arc may reach (the play area's top).
        for fraction, paw in ((.5, self.paw), (.8, (59, 124))):
            px = paw[0] if direction < 0 else 191 - paw[0]
            dx = cursor[0] - x - px
            line = g0 + (g1 - g0) * fraction
            height = (line + paw[1] - cursor[1]) / (4 * fraction * (1 - fraction))
            end = x + dx / fraction
            apex = (g0 + g1) / 2 - height   # Window y at the top of the arc.
            if abs(end - x) <= 150 and 0 <= height and apex >= top and self.left <= end <= self.right:
                return end, height
        return None


class GameTimer:
    """One coalesced intent; manual requests promote an automatic request."""
    def __init__(self, now, enabled=True, interval=90, record=None):
        self.enabled, self.interval = enabled, interval
        self.due = now + interval
        self.pending = None
        self.log = deque(maxlen=50)
        self.outside_since = None
        self.entered_at = None
        self.previous_due = self.due
        self.record, self.reason = record, ""

    def note(self, now, action, detail, journal=True):
        self.log.append((now, action, detail))
        if self.record and journal:
            self.record(action, detail)

    def armed(self, now):
        """An invitation is (or is about to be) waiting for a fresh approach."""
        return self.pending is not None or (self.enabled and now >= self.due)

    def waiting(self, now, reason):
        if reason != self.reason:
            self.reason = reason
            # Before the cooldown ends, blockers such as typing or a held button cannot delay play,
            # so they stay in the internal diagnostics instead of flooding the user's journal.
            self.note(now, "waiting", reason,
                      journal=self.armed(now) or reason in ("cooldown", "automatic games disabled"))

    def request(self, now, manual=False):
        source = "manual" if manual else "automatic"
        if manual or self.pending is None:
            self.pending = source
            self.note(now, "queued", source)

    def tick(self, now, eligible, in_zone=False, can_start=True, blocked_reason="not eligible"):
        if self.enabled and now >= self.due and self.pending is None:
            self.request(now)
        if not self.enabled and self.pending is None:
            self.outside_since = self.entered_at = None
            self.waiting(now, "automatic games disabled")
            return None
        if not eligible:
            self.outside_since = self.entered_at = None
            self.waiting(now, blocked_reason)
            return None
        invited = self.pending == "manual"
        if not invited:
            if not in_zone:
                if self.outside_since is None or self.entered_at is not None:
                    self.outside_since = now
                    self.note(now, "side area", "outside; fresh approach can qualify", journal=self.armed(now))
                self.entered_at = None
            elif self.outside_since is not None:
                if self.entered_at is None:
                    if now - self.outside_since < .15:
                        self.outside_since = None
                    else:
                        self.entered_at = now
                        self.note(now, "side area", "entered; checking stable hover", journal=self.armed(now))
                invited = (self.entered_at is not None and self.entered_at >= self.due
                           and now - self.entered_at >= .25)
        if not self.pending:
            self.waiting(now, "cooldown" if self.enabled else "automatic games disabled")
            return None
        if invited and can_start:
            source, self.pending = self.pending, None
            self.previous_due = self.due
            self.due = math.inf
            self.outside_since = self.entered_at = None
            self.reason = "started"
            self.note(now, "invitation accepted", source)
            return source
        self.waiting(now, "gesture recovery" if invited else
                     "stable hover" if self.entered_at is not None and self.entered_at >= self.due else "fresh side entry")
        return None

    def reset(self, now):
        self.pending = None
        self.due = now + self.interval
        self.outside_since = self.entered_at = None
        self.waiting(now, "cooldown")
        self.note(now, "cooldown", f"{self.interval} sec from completion/reset")

    def finish(self, now, started):
        self.reset(now)
        if not started:
            self.due = self.previous_due
            self.note(now, "cooldown", "unplayed invitation; previous deadline restored")

    def configure(self, now, enabled, interval):
        self.enabled = enabled
        self.interval = max(30, min(600, interval))
        if self.pending == "automatic":
            self.pending = None
        self.due = now + self.interval
        self.outside_since = self.entered_at = None
        self.previous_due = self.due


class CursorGame:
    kind = "catch"
    round_seconds = 45
    FIXED_FACING = ("loss", "loss_finish", "curl", "comfort", "win")

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
        self.started = False
        self.counted = self.win_counted = False
        self.variant = None
        self.outcome_seconds = 3
        self.cancel_index = 0
        self.asides = 0
        self.last_aside = now
        self.line = "announce"
        self.history = deque(maxlen=4)
        self.end_x, self.height, self.start_x = self.x, 0, self.x
        # Ground she is standing on (window y). She starts on her home ground and may hop down a
        # little (runway.drop) to reach a low arrow, then hops back up before going home.
        self.ground = self.start_ground = self.end_ground = runway.y
        self.after_landing = None
        self.comfort_requested = False
        self.phase = "declare"
        self.log = deque([(now, "declare")], maxlen=50)

    def enter(self, phase, now, line=None):
        self.phase, self.since = phase, now
        self.log.append((now, phase))
        if line:
            self.line = line

    def hold(self, now):
        """Freeze the game clock (a menu is open or the app stalled) without changing any outcome."""
        dt = max(0, now - self.last)
        self.since += dt
        if math.isfinite(self.deadline):
            self.deadline += dt
        if self.outside is not None:
            self.outside += dt
        self.last_aside += dt
        self.last_protest += dt
        self.last = now

    def take_line(self):
        line, self.line = self.line, None
        return line

    def cancel(self, now):
        self.line = None
        if self.phase in ("win", "settle", "return", "home", "curl", "comfort", "done", "ready_cancel"):
            # Already recovering or celebrating; keep the real result.
            return
        if self.phase in ("loss", "loss_finish"):
            # Finish the supported folding, then accept comfort instead of sulking.
            self.comfort_requested = True
            return
        if self.phase == "jump" and self.result == "win":
            return  # The paw already touched the arrow: celebrate, then recover.
        self.result = "cancel"
        if self.phase == "declare":
            self.enter("done", now)  # Still seated: nothing to unwind.
        elif self.phase in ("ready", "three", "two", "one"):
            stage = ("ready", "three", "two", "one").index(self.phase)
            self.cancel_index = stage * 4 + min(3, int((now - self.since) / (.2 if stage == 0 else .25)))
            self.enter("ready_cancel", now)
        elif self.phase == "jump":
            self.after_landing = "home"
        else:
            self.enter("home", now)

    def comfort(self, now):
        if self.phase != "curl":
            return False
        self.enter("comfort", now, "comfort")
        return True

    def position_at(self, now):
        if self.phase != "jump":
            return self.x, self.y
        t = max(0, min(1, (now - self.since) / .64))
        line = self.start_ground + (self.end_ground - self.start_ground) * t
        return (self.start_x + (self.end_x - self.start_x) * t, line - 4 * self.height * t * (1 - t))

    def plan_hop(self, end_x, height, landing, then=None):
        """Prepare a pounce/hop from the current ground to `landing`."""
        self.start_x, self.end_x, self.height = self.x, end_x, height
        self.start_ground, self.end_ground = self.ground, landing
        self.after_landing = then
        self.velocity = 0

    def climb_home(self, now):
        """Lowered after a hop down: a small hop back up to her home ground first."""
        if not self.motion or self.ground <= self.runway.y + 1:
            return False
        step = self.direction * 40 if self.direction else 40
        end = max(self.runway.left, min(self.runway.right, self.x + step))
        self.plan_hop(end, 14, self.runway.y, then=self.phase if self.phase in ("home", "return") else "home")
        self.enter("prepare", now)
        return True

    def update(self, now, cursor, contact=False):
        dt = now - self.last
        if dt < 0 or dt > 0.5:
            # A stall (lock screen, suspend, a busy system) cannot score or punish. Active play is
            # called off; celebrations, sulks and recoveries simply resume where they were.
            if self.phase in ACTIVE_PHASES:
                self.last = now
                self.cancel(now)
                self.after_landing = None
                self.x, self.y = self.x, self.ground
                self.enter("home", now)
            else:
                self.hold(now)
            return
        self.last = now
        if self.phase == "curl":
            return
        elapsed = now - self.since
        self.history.append(cursor)
        if self.phase in ("declare", "ready", "three", "two", "one"):
            inside = self.runway.contains(cursor, 8)
            self.outside = None if inside else (self.outside if self.outside is not None else now)
            if self.outside is not None and now - self.outside >= .6:
                self.cancel(now)
                return
            stages = {"declare": (DECLARE_SECONDS, "ready", None),
                      "ready": (.8, "three", "3…"), "three": (1, "two", "2…"),
                      "two": (1, "one", "1…"), "one": (1, "go", "go")}
            duration, next_phase, cue = stages[self.phase]
            if elapsed >= duration:
                self.enter(next_phase, now, cue)
                if next_phase == "go":
                    self.started = True
                    self.deadline = now + 45
                    self.last_aside = now
            return
        if self.phase in ("run", "turn", "prepare", "jump", "miss"):
            inside = self.runway.contains(cursor, 8 if self.outside is None else 0)
            self.outside = None if inside else (self.outside if self.outside is not None else now)
            outside_time = 0 if self.outside is None else now - self.outside
            if outside_time >= 1.5 and not self.protested and now - self.last_protest >= 8:
                self.line = ("protest_high" if cursor[1] < self.runway.y + self.runway.paw[1] - self.runway.lift
                             else "protest_low" if cursor[1] > self.runway.y + REACH_LOW + self.runway.drop
                             else "protest_side")
                self.protested = True
                self.last_protest = now
                if self.phase in ("run", "turn", "miss"):
                    self.plan_hop(self.x, min(50, self.runway.lift) if self.motion else 0, self.ground)
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
                    self.enter("loss", now, "loss")
                return
            if self.line is None and self.asides < 2 and now - self.last_aside >= 6 and inside:
                self.line = "pursuit"
                self.asides += 1
                self.last_aside = now
        if self.phase == "go" and elapsed >= .35:
            self.enter("run", now)
        elif self.phase == "ready_cancel" and elapsed >= (self.cancel_index + 1) * .06:
            self.enter("home", now)
        elif self.phase == "run":
            target = self.history[0]
            desired = -1 if target[0] < self.x + 96 else 1
            if desired != self.direction:
                self.velocity = 0
                self.enter("turn", now)
                return
            self.direction = desired
            # Lowered and the arrow is back up at home height: the pounce lands back up there.
            landing = (self.runway.y if self.ground > self.runway.y and target[1] < self.runway.y + REACH_LOW
                       else self.ground)
            solution = self.runway.jump(self.x, target, self.direction, self.ground, landing)
            if not self.motion:
                solution = (self.x, 0) if abs(target[0] - (self.x + (self.runway.paw[0] if desired < 0 else 191 - self.runway.paw[0]))) < 14 and abs(target[1] - self.runway.y - self.runway.paw[1]) < 14 else None
                landing = self.ground
            if solution:
                self.plan_hop(solution[0], solution[1], landing)
                self.enter("prepare", now)
            elif (self.motion and target[1] > self.ground + REACH_LOW - 6
                  and self.ground < self.runway.y + self.runway.drop - 8
                  and abs(target[0] - (self.x + 96)) < 220):
                # The arrow is just below her reach: hop down a little toward it.
                lower = min(self.runway.y + self.runway.drop, max(self.ground + 24, target[1] - REACH_LOW + 30))
                step = max(self.runway.left, min(self.runway.right, self.x + self.direction * 50))
                self.plan_hop(step, 16, lower)
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
                self.ground = self.y = self.end_ground
                phase = self.after_landing or "miss"
                self.enter(phase, now, phase if phase in ("win", "loss") else None)
                self.after_landing = None
        elif self.phase == "miss" and elapsed >= .45:
            self.enter("run", now)
        elif self.phase == "win" and elapsed >= self.outcome_seconds:
            self.enter("home", now)
        elif self.phase == "return":
            if self.climb_home(now):
                return
            self.y = self.ground = self.runway.y
            delta = self.origin[0] - self.x
            self.direction = -1 if delta < 0 else 1
            self.velocity = min(RUN_SPEED, self.velocity + RUN_ACCELERATION * dt)
            self.x += math.copysign(min(abs(delta), self.velocity * dt), delta) if delta else 0
            if abs(self.origin[0] - self.x) <= WALK_HOME_WITHIN:
                self.enter("home", now)
        elif self.phase == "home":
            if self.climb_home(now):
                return
            self.y = self.ground = self.runway.y
            delta = self.origin[0] - self.x
            if self.motion and abs(delta) > RUN_HOME_FROM:
                self.velocity = 0
                self.enter("return", now)
                return
            self.direction = -1 if delta < 0 else 1
            self.x += math.copysign(min(abs(delta), WALK_SPEED * dt), delta) if delta and self.motion else delta
            if abs(self.x - self.origin[0]) < 1:
                self.enter("settle", now)
        elif self.phase == "settle" and elapsed >= .72:
            self.enter("done", now)
        elif self.phase == "loss" and elapsed >= self.outcome_seconds:
            self.enter("loss_finish", now)
        elif self.phase == "loss_finish" and elapsed >= .84:
            self.enter("comfort" if self.comfort_requested else "curl", now)
        elif self.phase == "comfort" and elapsed >= 2:
            self.enter("home", now)
