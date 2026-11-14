"""Restless kitten: when ignored for a while she roams, pounces and grows jealous of the arrow.

The mood escalates through stages, each with its own rhythm: she acts, pounces a little, stops,
says something and relaxes, then pounces again, gradually more agitated, until petted. After a
long unanswered demand she curls up and sulks until someone pets her (the soft cap). Pets calm
her stage by stage; when satisfied she forgives you and goes home.

She moves only with her original drawings: the stroll, the chase gallop and the Catch pounce
(prepare + jump) for bouncy hops and for leaps to a new height. Her acting reuses her own
gestures: a bored yawn, the focused hunting crouch toward the arrow, an offered paw, a nuzzle.

Pure timing and geometry. The desktop supplies the cursor, the monitor work area (window
coordinates for her 192 x 144 canvas) and whether a button is held or the user is typing.
"""
import math
import random

from animations import CLIPS

# (name, seconds in stage before the next, pets needed to forgive, rest range between bursts)
STAGES = (("restless", 90, 1, (25, 40)), ("pouncy", 120, 2, (12, 20)),
          ("jealous", 150, 3, (6, 10)), ("demanding", 600, 4, (2, 4)), ("sulk", math.inf, 5, (0, 0)))
STAGE_NAMES = tuple(s[0] for s in STAGES)
CURSOR_GAP = 140          # She never rests closer than this to the arrow (body centre to arrow).
BODY = (96, 92)           # Body centre inside her canvas.
WALK, GALLOP = 120, 210   # px/s, matching the walk and gallop cadence used in Catch.
PREPARE = sum(CLIPS["game_prepare"].durations) / 1000      # crouch before a bound
FLIGHT = sum(CLIPS["game_jump"].durations) / 1000          # the pounce drawing, launch to landing
BOUND = PREPARE + FLIGHT
HOP_DISTANCE, HOP_HEIGHT = 110, 22                          # one playful bound
MAX_LEAP = 120            # Height of one leap (px); bigger changes take several leaps.
PET_PAUSE = 60            # After a pet she won't escalate further for this long.

# Her acting, all original drawings: (clip, seconds shown; a held last drawing fills any extra).
ACTS = {
    "sigh": ("yawn", None),             # bored, a little lonely
    "jealous": ("game_ready", 2.2),     # hunting crouch, staring the arrow down
    "demand": ("paw_offer", None),      # offers a paw: "pet me"
    "calm": ("ear_rub", None),          # a pet helped; a little softer
    "forgive": ("nuzzle", None),        # forgiven, with hearts
    "stop": ("game_settle", None),      # comes to a stop and sits
    "ready": ("game_prepare", 0.4),     # gathers before a burst
}
ACT_SECONDS = {name: seconds if seconds is not None else sum(CLIPS[clip].durations) / 1000
               for name, (clip, seconds) in ACTS.items()}
# Clips drawn facing left; they turn toward her travel or toward the arrow.
SIDE_CLIPS = {"walk", "game_run", "game_prepare", "game_jump", "game_ready", "game_settle"}


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
        self.quietly = False
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

    @property
    def playful(self):
        """She'd still love a game: not sulking (a pet first), not already forgiven and heading home."""
        return not (self.done or self.forgiven or self.stage_name == "sulk")

    @property
    def resting(self):
        """Seated between bursts on her current ground, so a game can start without a pose jump."""
        return self.playful and self.step is not None and self.step[0] == "rest"

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
            if self.stage_name == "sulk" and self.step[0] not in ("travel", "leap"):
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
        """You stepped away: she quietly heads home without forgiving you (no words)."""
        self.forgiven = self.quietly = True
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
        if self.forgiven:
            self.plan = self.route(self.home[0], self.home[1], calm=True) + [("arrive", None)]
            self.next_step(now)
        else:
            self.rest(now, 1.5)

    # Planning ---------------------------------------------------------------------------------
    def rest(self, now, seconds=None):
        low, high = STAGES[self.stage][3]
        self.step = ("rest", None, now, seconds if seconds is not None else self.rng.uniform(low, high))

    def clamp_x(self, x):
        return max(self.area[0], min(self.area[2], x))

    def clamp_y(self, y):
        return max(self.area[1], min(self.area[3], y))

    def perch_near(self, cursor):
        """A resting spot on the arrow's side of the screen, about the arrow's height, keeping the gap."""
        side = -1 if cursor[0] < self.x + BODY[0] else 1   # She stays on her side of the arrow.
        x = self.clamp_x(cursor[0] + (CURSOR_GAP + 20) * (-side) - BODY[0])
        if abs(x + BODY[0] - cursor[0]) < CURSOR_GAP:      # Clamped against an edge: go round.
            x = self.clamp_x(cursor[0] + (CURSOR_GAP + 20) * side - BODY[0])
        y = self.clamp_y(cursor[1] - BODY[1])
        if abs(y - self.ground) < 60:
            y = self.ground
        return x, y

    def route(self, x, y, calm=False):
        """Steps from where she is to (x, y): kitten-sized leaps for a change of height, then travel."""
        steps = []
        ground, here = self.ground, self.x
        while self.motion and abs(y - ground) >= 30:
            rise = max(-MAX_LEAP, min(MAX_LEAP, y - ground))
            ground += rise
            if abs(y - ground) < 30:
                ground = y
            here = self.clamp_x(here + max(-100, min(100, x - here)))
            steps.append(("leap", (here, ground)))
            steps.append(("rest", 0.5))
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
                             ("act", "stop"), ("act", "sigh"), ("rest", None)]
        elif name == "pouncy":
            there = self.clamp_x(self.x + self.rng.choice((-1, 1)) * self.rng.uniform(110, 330))
            self.plan = [("act", "ready"), ("travel", (self.rng.choice(("hop", "hop", "gallop")), there)),
                         ("act", "stop"), ("say", "pounce"), ("rest", None)]
        elif name in ("jealous", "demanding"):
            x, y = self.perch_near(cursor)
            act = "jealous" if name == "jealous" else self.rng.choice(("demand", "demand", "jealous"))
            self.plan = [("act", "ready")] + self.route(x, y) + [("face", cursor), ("act", act),
                                                                 ("say", "jealous" if act == "jealous" else "demand"),
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
        elif kind == "face":
            self.direction = -1 if data[0] < self.x + BODY[0] else 1
            self.next_step(now, cursor)
        elif kind == "arrive":
            self.done = True
        elif kind == "act":
            if data == "ready" and self.plan and self.plan[0][0] in ("travel", "leap"):
                # Gather facing the way she is about to go, so she doesn't flip mid-burst.
                ahead = self.plan[0][1][1] if self.plan[0][0] == "travel" else self.plan[0][1][0]
                if ahead != self.x:
                    self.direction = -1 if ahead < self.x else 1
            self.step = ("act", data, now, ACT_SECONDS[data] if self.motion else min(2.0, ACT_SECONDS[data]))
        elif kind == "travel":
            mode, target = data
            if not self.motion:
                self.x = target
                self.next_step(now, cursor)
                return
            self.direction = -1 if target < self.x else 1
            distance = abs(target - self.x)
            if mode == "hop":
                bounds = max(1, round(distance / HOP_DISTANCE))
                seconds = bounds * BOUND
            else:
                seconds = distance / (WALK if mode == "walk" else GALLOP)
            self.step = ("travel", (mode, self.x, target), now, seconds)
        elif kind == "leap":
            x, y = data
            x, y = self.clamp_x(x), self.clamp_y(y)
            if not self.motion:
                self.x, self.y, self.ground = x, y, y
                self.next_step(now, cursor)
                return
            self.direction = -1 if x < self.x else 1
            rise = max(0, self.ground - y)
            self.step = ("leap", (self.x, self.ground, x, y, 18 + rise * 0.6), now, BOUND)

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
            if mode == "hop":
                # Each bound: crouch in place, then the pounce carries her one stretch forward.
                bounds = max(1, round(abs(target - start) / HOP_DISTANCE))
                index = min(bounds - 1, int(t / BOUND))
                local = t - index * BOUND
                flight = max(0.0, min(1.0, (local - PREPARE) / FLIGHT))
                self.x = start + (target - start) * min(1.0, (index + flight) / bounds)
                self.y = self.ground - 4 * HOP_HEIGHT * flight * (1 - flight)
            else:
                f = min(1.0, t / max(0.01, seconds))
                self.x = start + (target - start) * f
                self.y = self.ground
        elif kind == "leap":
            x0, y0, x1, y1, height = data
            f = max(0.0, min(1.0, (t - PREPARE) / FLIGHT))
            self.x = x0 + (x1 - x0) * f
            self.y = y0 + (y1 - y0) * f - 4 * height * f * (1 - f)
        if kind not in ("sulk",) and t >= seconds:
            if kind == "leap":
                self.ground = self.y = data[3]
            elif kind == "travel":
                self.y = self.ground
            if self.stage_name == "sulk" and not self.forgiven:
                self.plan = []
                self.step = ("sulk", None, now, math.inf)
                return
            self.next_step(now, cursor)

    # Rendering --------------------------------------------------------------------------------
    def clip(self, now):
        """(clip name, elapsed, mirrored)"""
        kind, data, started, seconds = self.step
        t = now - started
        name = "idle"
        if kind == "sulk":
            return "game_curl", t, False
        if kind == "travel":
            mode = data[0]
            if mode == "hop":
                local = t % BOUND
                name, t = ("game_prepare", local) if local < PREPARE else ("game_jump", local - PREPARE)
            else:
                name = "walk" if mode == "walk" else "game_run"
        elif kind == "leap":
            name, t = ("game_prepare", t) if t < PREPARE else ("game_jump", t - PREPARE)
        elif kind == "act":
            name = ACTS[data][0]
        return name, t, name in SIDE_CLIPS and self.direction > 0

    def take_line(self):
        line, self.line = self.line, None
        return line

    @property
    def effect(self):
        kind = self.step[0] if self.step else None
        if kind == "sulk":
            return "sulk"
        if self.forgiven:
            return None if self.quietly else "pet"
        return {"jealous": "grumpy", "demanding": "grumpy"}.get(self.stage_name)
