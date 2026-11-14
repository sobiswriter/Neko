"""Restless kitten: when ignored for a while she roams, pounces and grows jealous of the arrow.

The mood escalates through stages, each with its own rhythm: she acts, pounces a little, stops,
says something and relaxes, then pounces again, gradually more agitated, until petted. After a
long unanswered demand she curls up and sulks until someone pets her (the soft cap). Pets calm
her stage by stage; when satisfied she forgives you and goes home.

Pure timing and geometry. The desktop supplies the cursor, the monitor work area (window
coordinates for her 192 x 144 canvas) and whether a button is held or the user is typing.
"""
import math
import random

# (name, seconds in stage before the next, pets needed to forgive, rest range between bursts)
STAGES = (("restless", 90, 1, (25, 40)), ("pouncy", 120, 2, (12, 20)),
          ("jealous", 150, 3, (6, 10)), ("demanding", 600, 4, (2, 4)), ("sulk", math.inf, 5, (0, 0)))
STAGE_NAMES = tuple(s[0] for s in STAGES)
CURSOR_GAP = 140          # She never rests closer than this to the arrow (body centre to arrow).
BODY = (96, 92)           # Body centre inside her canvas.
WALK, HOP, GALLOP = 90, 230, 260   # px/s
HOP_CYCLE = 0.42          # roam_hop cycle length (s); each cycle is one bound.
LEAP_FLIGHT = {"up": (0.65, 0.96), "down": (0.60, 0.90)}
# Lengths of the drawn clips in animations.CLIPS (checked by test_restless).
LEAP_SECONDS = {"up": 1.75, "down": 1.75}
ACT_SECONDS = {"sigh": 4.95, "jealous": 3.97, "demand": 4.0, "forgive": 4.95, "calm": 1.6,
               "stop": 0.65, "turn": 0.48, "ready": 0.4}
PET_PAUSE = 60            # After a pet she won't escalate further for this long.
MAX_LEAP = 200            # Height of one leap (px); bigger changes take several leaps.


class RestlessMood:
    def __init__(self, now, home, area, motion=True, rng=None):
        self.rng = rng or random.Random()
        self.home = home
        self.area = area                     # (left, top, right, bottom) allowed window positions
        self.motion = motion
        self.x, self.y = home
        self.ground = home[1]
        self.stage = 0
        self.stage_since = now
        self.pets = 0
        self.last_pet = -math.inf
        self.direction = -1
        self.plan = []                       # queued steps
        self.step = None                     # (kind, data, started, seconds)
        self.last = now
        self.line = "start"
        self.forgiven = False
        self.done = False
        self.log = [(now, "restless")]
        self.rest(now, 2.0)

    # Clock and stage --------------------------------------------------------------------------
    @property
    def stage_name(self):
        return STAGE_NAMES[self.stage]

    @property
    def pets_needed(self):
        return STAGES[self.stage][2]

    def hold(self, now):
        dt = max(0, now - self.last)
        self.stage_since += dt
        if self.step:
            kind, data, started, seconds = self.step
            self.step = (kind, data, started + dt, seconds)
        self.last = now

    def escalate(self, now):
        if self.forgiven or self.stage >= len(STAGES) - 1:
            return
        if now - self.stage_since >= STAGES[self.stage][1] and now - self.last_pet >= PET_PAUSE:
            self.stage += 1
            self.stage_since = now
            self.pets = 0
            self.log.append((now, self.stage_name))
            self.line = "sulk" if self.stage_name == "sulk" else self.stage_name
            if self.stage_name == "sulk":
                self.plan = []
                self.step = ("sulk", None, now, math.inf)

    # Interactions -----------------------------------------------------------------------------
    def pet(self, now):
        """One pet. Returns 'forgiven' or 'progress'."""
        self.pets += 1
        self.last_pet = now
        self.stage_since = now
        if self.pets >= self.pets_needed:
            self.forgive(now)
            return "forgiven"
        self.line = "calm_progress"
        self.plan = [("act", "calm"), ("rest", 2.0)]
        self.next_step(now)
        return "progress"

    def calm_one_stage(self, now):
        """A finished game counts as attention."""
        if self.stage == 0 or self.stage_name == "sulk":
            self.forgive(now)
            return
        self.stage -= 1
        self.stage_since = now
        self.pets = 0

    def forgive(self, now):
        self.forgiven = True
        self.line = "calm_done"
        self.plan = [("act", "forgive")] + self.route(self.home[0], self.home[1], calm=True) + [("arrive", None)]
        self.step = None
        self.next_step(now)
        self.log.append((now, "forgiven"))

    def go_home(self, now):
        """You stepped away: she quietly heads home without forgiving you (no melt, no words)."""
        self.forgiven = True
        self.line = None
        self.plan = self.route(self.home[0], self.home[1], calm=True) + [("arrive", None)]
        self.step = None
        self.next_step(now)
        self.log.append((now, "away"))

    def moved(self, x, y, now):
        """She was carried somewhere else: the mood carries on from there."""
        self.x, self.y, self.ground = x, y, y
        self.plan = []
        self.step = None
        self.rest(now, 1.5)

    # Planning ---------------------------------------------------------------------------------
    def rest(self, now, seconds=None):
        low, high = STAGES[self.stage][3]
        self.step = ("rest", None, now, seconds if seconds is not None else self.rng.uniform(low, high))

    def clamp_x(self, x):
        return max(self.area[0], min(self.area[2], x))

    def perch_near(self, cursor):
        """A resting spot on the arrow's side of the screen, about the arrow's height, keeping the gap."""
        side = -1 if cursor[0] < self.x + BODY[0] else 1   # She stays on her side of the arrow.
        x = cursor[0] + (CURSOR_GAP + 20) * (-side) - BODY[0]
        x = self.clamp_x(x)
        if abs(x + BODY[0] - cursor[0]) < CURSOR_GAP:      # Clamped against an edge: go round.
            x = self.clamp_x(cursor[0] + (CURSOR_GAP + 20) * side - BODY[0])
        y = max(self.area[1], min(self.area[3], cursor[1] - BODY[1]))
        if abs(y - self.ground) < 70:
            y = self.ground
        return x, y

    def route(self, x, y, calm=False):
        """Steps from where she is to (x, y): bounded leaps for a change of height, then travel."""
        steps = []
        ground, here = self.ground, self.x
        while self.motion and abs(y - ground) >= 40:
            # One kitten-sized leap at a time (at most MAX_LEAP of height), drifting toward the target.
            rise = max(-MAX_LEAP, min(MAX_LEAP, y - ground))
            ground += rise
            if abs(y - ground) < 40:
                ground = y
            here = here + max(-140, min(140, x - here))
            steps.append(("leap", (here, ground)))
            steps.append(("rest", 0.6))
        kind = "walk" if calm else self.rng.choice(("hop", "gallop", "hop"))
        steps.append(("travel", (kind, x)))
        steps.append(("act", "stop"))
        return steps

    def plan_burst(self, now, cursor):
        name = self.stage_name
        if name == "restless":
            if self.rng.random() < 0.5:
                self.plan = [("act", "sigh"), ("rest", None)]
            else:
                there = self.clamp_x(self.x + self.rng.choice((-1, 1)) * self.rng.uniform(80, 150))
                self.plan = [("travel", ("walk", there)), ("act", "stop"), ("rest", 3), ("travel", ("walk", self.x)),
                             ("act", "sigh"), ("rest", None)]
        elif name == "pouncy":
            there = self.clamp_x(self.x + self.rng.choice((-1, 1)) * self.rng.uniform(100, 280))
            self.plan = [("act", "ready"), ("travel", (self.rng.choice(("hop", "gallop")), there)), ("act", "stop"),
                         ("say", "pounce"), ("rest", None)]
        elif name in ("jealous", "demanding"):
            x, y = self.perch_near(cursor)
            self.plan = [("act", "ready")] + self.route(x, y) + [("act", "jealous" if name == "jealous" else "demand"),
                                                                 ("say", "jealous" if name == "jealous" else "demand"),
                                                                 ("rest", None)]

    def next_step(self, now, cursor=(0, 0)):
        if not self.plan:
            if self.forgiven:
                self.done = True
                return
            self.plan_burst(now, cursor)
        kind, data = self.plan.pop(0)
        if kind == "rest":
            self.rest(now, data)
        elif kind == "say":
            self.line = data
            self.next_step(now, cursor)
        elif kind == "arrive":
            self.done = True
        elif kind == "act":
            self.step = ("act", data, now, ACT_SECONDS[data] if self.motion else min(2.0, ACT_SECONDS[data]))
        elif kind == "travel":
            mode, target = data
            if not self.motion:
                self.x = target
                self.next_step(now, cursor)
                return
            self.direction = -1 if target < self.x else 1
            self.step = ("travel", (mode, self.x, target), now, abs(target - self.x) / {"walk": WALK, "hop": HOP,
                                                                                         "gallop": GALLOP}[mode])
        elif kind == "leap":
            x, y = data
            x = self.clamp_x(x)
            way = "up" if y < self.ground else "down"
            if not self.motion:
                self.x, self.y, self.ground = x, y, y
                self.next_step(now, cursor)
                return
            self.direction = -1 if x < self.x else 1
            self.step = ("leap", (way, self.x, self.y, x, y), now, LEAP_SECONDS[way])

    # Update -----------------------------------------------------------------------------------
    def update(self, now, cursor, paused=False):
        """paused: a mouse button is held or the user is typing; she waits where she is."""
        if self.done:
            return
        dt = now - self.last
        if paused or dt < 0 or dt > 0.5:
            self.hold(now)
            return
        self.last = now
        self.escalate(now)
        kind, data, started, seconds = self.step
        t = now - started
        if kind == "travel":
            mode, start, target = data
            f = min(1.0, t / max(0.01, seconds))
            self.x = start + (target - start) * f
        elif kind == "leap":
            way, x0, y0, x1, y1 = data
            lift, land = LEAP_FLIGHT[way]
            f = max(0.0, min(1.0, (t - lift) / (land - lift)))
            arc = 4 * 26 * f * (1 - f)   # A small extra rise over the straight line.
            self.x = x0 + (x1 - x0) * f
            self.y = y0 + (y1 - y0) * f - arc
            if t >= seconds:
                self.ground = self.y = y1
        if kind != "sulk" and t >= seconds:
            self.next_step(now, cursor)

    # Rendering --------------------------------------------------------------------------------
    def clip(self, now):
        """(clip name, elapsed, mirrored)"""
        kind, data, started, seconds = self.step
        t = now - started
        if kind == "sulk":
            return "game_curl", t, False
        if kind == "rest":
            return "idle", t, False
        if kind == "travel":
            mode = data[0]
            return {"walk": "walk", "hop": "roam_hop", "gallop": "game_run"}[mode], t, self.direction > 0
        if kind == "leap":
            return f"roam_leap_{data[0]}", t, self.direction > 0
        name = {"sigh": "restless_sigh", "jealous": "restless_jealous", "demand": "restless_demand",
                "forgive": "restless_forgive", "calm": "restless_calm", "stop": "roam_stop",
                "turn": "roam_turn", "ready": "roam_ready"}[data]
        side = data in ("stop", "ready", "turn")
        return name, t, side and self.direction > 0

    def take_line(self):
        line, self.line = self.line, None
        return line

    @property
    def effect(self):
        kind = self.step[0] if self.step else None
        if kind == "sulk":
            return "sulk"
        if self.forgiven:
            return "pet"
        return {"jealous": "grumpy", "demanding": "grumpy"}.get(self.stage_name)
