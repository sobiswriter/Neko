"""Dodge the Cursor: the player tries to tag Neko with the arrow; she teases, tells, then dodges.

Cat logic: approach-avoid. She creeps toward the arrow to get its attention, play-bows when it
hangs back, and bolts when it rushes her. Before every escape she shows a short tell (the
player's window to tag her) and afterwards needs a recovery beat, so she cannot chain perfect
dodges. The player needs three real tags in 30 seconds; brushes and the after-tag grace do not
count. Touching her before "Go!" or running away are fouls that make her sad, ending in the
shared disappointed curl until she is comforted.

Pure timing/geometry; the desktop layer supplies the cursor, the visible-body contact test and
the screen runway (the same Runway type as Catch the Cursor).
"""
from collections import deque
import math

from games import RUN_HOME_FROM, RUN_SPEED, RUN_ACCELERATION, WALK_HOME_WITHIN, WALK_SPEED

TAGS_TO_WIN = 3
ROUND_SECONDS = 30
TAG_HOLD = 0.12          # A tag needs the arrow on her body this long; less is a brush.
TAG_GRACE = 1.2          # After a tag she can't be tagged again while she flees.
TELL = (0.25, 0.35)      # Warning lean before an escape: the player's window.
RECOVERY = (0.7, 1.0)    # After an escape she can't dodge again for this long.
THREAT_DISTANCE = 110    # Arrow this close to her body centre triggers a tell.
RUSH_SPEED = 600         # Or the arrow rushing straight at her (px/s).
APPROACH_GAP = 180       # She creeps to this distance to get the arrow's attention.
TEASE_AFTER = 3.0        # Arrow hanging back this long: she creeps closer again.
FAR = 700                # Arrow this far away counts as running away...
FAR_WARN, FAR_FAIL = 1.5, 4.0
BORED_SECONDS = 8.0      # Arrow motionless this long during play: game over, no score.
CREEP_SPEED, HOP_SPEED = 60, 300
SIDESTEP = (40, 70)
DASH = (150, 300)
BODY = (96, 92)          # Her body centre inside the 192 x 144 canvas, from her top-left.

# Beats before play. (phase, seconds, next phase, line spoken on entry of the next phase)
OPENING = {"notice": (0.6, "announce", "announce"), "announce": (2.0, "three", "3…"),
           "three": (1.0, "two", "2…"), "two": (1.0, "one", "1…"), "one": (1.0, "go", "go")}
PLAY_PHASES = ("approach", "prowl", "tell", "sidestep", "duck", "dash", "tagged", "recover")
ACTIVE = ("notice", "announce", "three", "two", "one", "go") + PLAY_PHASES
# Lengths of the drawn escapes in animations.CLIPS (checked by test_dodge).
CLIP_SECONDS = {"sidestep": 1.42, "duck": 1.78, "tagged": 2.31}
ROUND_PHASES = ("three", "two", "one")


class DodgeGame:
    kind = "dodge"
    round_seconds = ROUND_SECONDS
    # Front/seated drawings keep their facing; side views turn toward their travel.
    FIXED_FACING = ("notice", "announce", "tagged", "caught", "win", "loss", "loss_finish", "curl", "comfort")

    def __init__(self, now, origin, runway, motion=True, source="manual", rng=None):
        import random
        self.rng = rng or random.Random()
        self.origin, self.runway, self.motion, self.source = origin, runway, motion, source
        self.x, self.y = origin
        self.phase, self.since, self.last = "notice", now, now
        self.deadline = math.inf
        self.direction = -1
        self.velocity = 0.0
        self.result = None
        self.started = False
        self.counted = self.win_counted = False
        self.variant = None
        self.outcome_seconds = 3
        self.cancel_index = 0
        self.line = "notice"
        self.tags = 0
        self.touch_since = None
        self.last_brush = -math.inf
        self.grace_until = -math.inf
        self.ready_at = now          # Next moment she can start an escape.
        self.target_x = self.x
        self.tell_kind = None
        self.far_since = None
        self.warned_far = False
        self.still_since = now
        self.last_cursor = None
        self.history = deque(maxlen=6)
        self.warned_early = -math.inf
        self.time_cues = set()
        self.last_escape_line = -math.inf
        self.comfort_requested = False
        self.after_landing = None
        self.log = deque([(now, "notice")], maxlen=50)

    # Shared interface with CursorGame ---------------------------------------------------------
    def enter(self, phase, now, line=None):
        self.phase, self.since = phase, now
        self.log.append((now, phase))
        if line:
            self.line = line

    def take_line(self):
        line, self.line = self.line, None
        return line

    def hold(self, now):
        dt = max(0, now - self.last)
        for name in ("since", "ready_at", "grace_until", "still_since", "last_brush", "last_escape_line"):
            setattr(self, name, getattr(self, name) + dt)
        if math.isfinite(self.deadline):
            self.deadline += dt
        for name in ("far_since", "touch_since"):
            if getattr(self, name) is not None:
                setattr(self, name, getattr(self, name) + dt)
        self.last = now

    def position_at(self, now):
        return self.x, self.y

    def comfort(self, now):
        if self.phase != "curl":
            return False
        self.enter("comfort", now, "comfort")
        return True

    def cancel(self, now):
        """Neutral stop (pet, carry, End game, typing): no score, straight home."""
        self.line = None
        if self.phase in ("win", "caught", "settle", "return", "home", "curl", "comfort", "done"):
            return
        if self.phase in ("loss", "loss_finish"):
            self.comfort_requested = True
            return
        self.result = self.result or "cancel"
        self.y = self.runway.y
        self.enter("done" if self.phase in ("notice", "announce") else "home", now)

    # Geometry ---------------------------------------------------------------------------------
    @property
    def centre(self):
        return self.x + BODY[0], self.y + BODY[1]

    def clamp(self, x):
        return max(self.runway.left, min(self.runway.right, x))

    def away_from(self, cursor_x, distance):
        """Escape target away from the arrow; cornered against an edge, she slips past it."""
        side = -1 if cursor_x > self.centre[0] else 1
        target = self.x + side * distance
        if self.clamp(target) != target and abs(self.clamp(target) - self.x) < distance * 0.6:
            side, target = -side, self.x - side * (distance + 120)  # Cornered: past the arrow.
        return self.clamp(target), side

    # Update -----------------------------------------------------------------------------------
    def update(self, now, cursor, contact=False, far=False):
        """contact: the arrow is on her visible body. far: the arrow left her monitor."""
        dt = now - self.last
        if dt < 0 or dt > 0.5:
            if self.phase in ACTIVE:
                self.last = now
                self.cancel(now)
            else:
                self.hold(now)
            return
        self.last = now
        if self.phase == "curl":
            return
        elapsed = now - self.since
        self.history.append((now, cursor))
        # "Still" means the arrow stays near one spot; slow drifting still counts as playing.
        if self.last_cursor is None or math.hypot(cursor[0] - self.last_cursor[0], cursor[1] - self.last_cursor[1]) > 8:
            self.still_since = now
            self.last_cursor = cursor
        cx, cy = self.centre
        distance = math.hypot(cursor[0] - cx, cursor[1] - cy)

        if self.phase in ACTIVE:
            if self.watch_fouls(now, contact, distance, far):
                return
        if self.phase in OPENING:
            duration, following, line = OPENING[self.phase]
            if elapsed >= duration:
                self.enter(following, now, line)
                if following == "go":
                    self.started = True
                    self.deadline = now + ROUND_SECONDS
                    self.still_since = now   # Boredom only counts once play has started.
            return
        if self.phase == "go":
            if elapsed >= 0.35:
                self.enter("approach", now)
            return
        if self.phase in PLAY_PHASES:
            self.play(now, dt, cursor, contact, distance)
            return
        self.recover_home(now, dt, elapsed)

    def watch_fouls(self, now, contact, distance, far):
        before_go = self.phase in OPENING
        # Touches: before "Go!" a real touch is a false start; during play it may be a tag.
        if contact:
            if self.touch_since is None:
                self.touch_since = now
        elif self.touch_since is not None:
            touched, self.touch_since = now - self.touch_since, None
            if touched < TAG_HOLD and now - self.last_brush >= 4:
                self.last_brush = now
                self.line = "not_yet" if before_go else "brush"
        if before_go and self.touch_since is not None and now - self.touch_since >= TAG_HOLD:
            self.fail(now, "foul")
            return True
        # Running away: far from her (or onto another monitor) for too long.
        if far or distance > FAR:
            self.far_since = self.far_since if self.far_since is not None else now
            away = now - self.far_since
            if away >= FAR_FAIL:
                self.fail(now, "runaway")
                return True
            if away >= FAR_WARN and not self.warned_far:
                self.warned_far = True
                self.line = "runaway_warn"
        else:
            self.far_since, self.warned_far = None, False
        if self.started and self.phase in PLAY_PHASES:
            if now - self.still_since >= BORED_SECONDS:
                self.result = "bored"
                self.line = "bored"
                self.y = self.runway.y
                self.enter("home", now)
                return True
            if now >= self.deadline:
                self.result = "win"
                self.y = self.runway.y
                self.enter("win", now, "win")
                return True
            left = self.deadline - now
            for mark in (10, 3):
                if left <= mark and mark not in self.time_cues:
                    self.time_cues.add(mark)
                    self.line = self.line or "time"
        return False

    def fail(self, now, reason):
        """Fouls are fails: she is hurt, plays a sad drawing and curls up until comforted."""
        self.result = reason
        self.line = reason
        self.touch_since = None
        self.y = self.runway.y
        self.enter("loss", now)

    def play(self, now, dt, cursor, contact, distance):
        elapsed = now - self.since
        # Tags: a real hold on her body, outside the grace window and not while flattened.
        flat = self.phase == "duck" and 0.19 <= elapsed <= 0.69
        if (self.touch_since is not None and now - self.touch_since >= TAG_HOLD
                and now >= self.grace_until and self.phase != "tagged" and not flat):
            self.touch_since = None
            self.tags += 1
            self.grace_until = now + TAG_GRACE + CLIP_SECONDS["tagged"]
            if self.tags >= TAGS_TO_WIN:
                self.result = "caught"
                self.y = self.runway.y
                self.enter("caught", now, "caught")
                return
            self.enter("tagged", now, "last_chance" if self.tags == TAGS_TO_WIN - 1 else "tagged")
            return
        speed = self.approach_speed(cursor)
        threat = distance < THREAT_DISTANCE or speed > RUSH_SPEED
        if self.phase in ("approach", "prowl") and threat and now >= self.ready_at:
            self.tell_kind = ("duck" if cursor[1] < self.centre[1] - 30 and self.rng.random() < 0.5 or not self.motion
                              else "dash" if speed > RUSH_SPEED * 1.4 else "sidestep")
            self.enter("tell", now)
            self.tell_seconds = self.rng.uniform(*TELL)
            return
        if self.phase == "approach":
            gap = abs(cursor[0] - self.centre[0])
            if not self.motion or gap <= APPROACH_GAP:
                self.enter("prowl", now)
                return
            self.direction = -1 if cursor[0] < self.centre[0] else 1
            self.x = self.clamp(self.x + self.direction * CREEP_SPEED * dt)
        elif self.phase == "prowl":
            if self.motion and abs(cursor[0] - self.centre[0]) > APPROACH_GAP + 60 and elapsed >= TEASE_AFTER:
                self.line = "tease"
                self.enter("approach", now)
            elif elapsed >= TEASE_AFTER * 2 and now - self.last_escape_line >= 6:
                self.last_escape_line = now
                self.line = "tease"
                self.since = now
        elif self.phase == "tell":
            if elapsed >= self.tell_seconds:
                kind = self.tell_kind
                if kind == "duck":
                    self.enter("duck", now)
                else:
                    distance_range = DASH if kind == "dash" else SIDESTEP
                    self.target_x, side = self.away_from(cursor[0], self.rng.uniform(*distance_range))
                    self.direction = side
                    self.velocity = 0
                    self.enter("dash" if kind == "dash" else "sidestep", now)
        elif self.phase == "sidestep":
            if elapsed <= 0.3 and self.motion:
                self.x += (self.target_x - self.x) * min(1, dt / max(0.02, 0.3 - elapsed + dt))
            if elapsed >= CLIP_SECONDS["sidestep"]:
                self.escaped(now)
        elif self.phase == "duck":
            if elapsed >= CLIP_SECONDS["duck"]:
                self.escaped(now)
        elif self.phase == "dash":
            self.velocity = min(HOP_SPEED, self.velocity + 1400 * dt)
            delta = self.target_x - self.x
            self.x += math.copysign(min(abs(delta), self.velocity * dt), delta) if delta else 0
            if abs(self.target_x - self.x) < 1:
                self.escaped(now)
        elif self.phase == "tagged":
            if elapsed >= CLIP_SECONDS["tagged"]:
                # Flee to the far side, then carry on teasing.
                self.target_x, self.direction = self.away_from(cursor[0], self.rng.uniform(220, 360))
                self.velocity = 0
                self.enter("dash", now)
        elif self.phase == "recover":
            if elapsed >= 0.3:
                self.enter("prowl", now)

    def escaped(self, now):
        self.ready_at = now + self.rng.uniform(*RECOVERY)
        if now - self.last_escape_line >= 5 and self.rng.random() < 0.6:
            self.last_escape_line = now
            self.line = "escape"
        self.enter("recover", now)

    def approach_speed(self, cursor):
        """Arrow speed toward her body (px/s) over the recent samples."""
        if len(self.history) < 3:
            return 0
        (t0, c0), (t1, c1) = self.history[0], self.history[-1]
        if t1 - t0 <= 0:
            return 0
        cx, cy = self.centre
        before = math.hypot(c0[0] - cx, c0[1] - cy)
        after = math.hypot(c1[0] - cx, c1[1] - cy)
        return (before - after) / (t1 - t0)

    def recover_home(self, now, dt, elapsed):
        if self.phase in ("win", "caught") and elapsed >= self.outcome_seconds:
            self.enter("home", now)
        elif self.phase == "return":
            self.y = self.runway.y
            delta = self.origin[0] - self.x
            self.direction = -1 if delta < 0 else 1
            self.velocity = min(RUN_SPEED, self.velocity + RUN_ACCELERATION * dt)
            self.x += math.copysign(min(abs(delta), self.velocity * dt), delta) if delta else 0
            if abs(self.origin[0] - self.x) <= WALK_HOME_WITHIN:
                self.enter("home", now)
        elif self.phase == "home":
            self.y = self.runway.y
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
