"""Restless kitten (Neko 1.3): when ignored for a while she gets restless, in levels.

After the "Restless after" time she starts at level 1 and climbs a level every few minutes
(the "More restless every" setting, 5 min by default) until petted:

1. agitated: fidgets, flicks her tail and ears, glances at you, now and then runs off and back;
2. pouncy: bursts of running and pouncing to grab your attention, excited hops;
3. demanding: comes over to the arrow (keeping a polite gap), stares it down, offers a paw;
4. sad (the last level): comes as close to the arrow as she can, curls up under a rain cloud and
   says small, sad, cute things now and then until you notice her.

Pets calm her: 2, 3 or 4 pets at levels 1-3, and 5 once she is curled up. Curled up, each pet
must come after she has said her line (one pet per line, not a quick burst); her words go from
sad to happy as you pet her. When she is satisfied she forgives you and goes home.

Movement grammar (her original drawings only): a change of height is always a pounce (the
Catch crouch + jump), left/right travel is always a run (the chase gallop), and she walks only
to cool down at the end of a run. Her acting reuses her own gestures.

Pure timing and geometry. The desktop supplies the cursor, the monitor work area (window
coordinates for her 192 x 144 canvas) and whether a button is held or the user is typing.
"""
import math
import random

from animations import CLIPS

# (name, pets needed to forgive, rest range between bursts in seconds)
STAGES = (("agitated", 2, (16, 26)), ("pouncy", 3, (8, 13)), ("demanding", 4, (3, 6)), ("sad", 5, (0, 0)))
STAGE_NAMES = tuple(s[0] for s in STAGES)
SAD = len(STAGES) - 1
LEVEL_SECONDS = 300        # Default time at each level before the next.
CURSOR_GAP = 140           # Levels 1-3: she never rests closer than this to the arrow (body centre).
SAD_GAP = 96               # The sad level: as close as she can get without covering the arrow.
BODY = (96, 92)            # Body centre inside her canvas.
WALK, RUN = 120, 210       # px/s, matching the walk and gallop cadence used in Catch.
WALK_TAIL = 70             # A run longer than RUN_SPLIT ends with this much cool-down walking.
RUN_SPLIT = 150
PREPARE = sum(CLIPS["game_prepare"].durations) / 1000      # crouch before a pounce
FLIGHT = sum(CLIPS["game_jump"].durations) / 1000          # the pounce drawing, launch to landing
BOUND = PREPARE + FLIGHT
MAX_LEAP = 120             # Height of one pounce (px); bigger changes take several pounces.
LEAP_REACH = 100           # Sideways distance covered by one pounce.
PET_PAUSE = 60             # After a pet she won't climb a level for this long.
LISTEN_SECONDS = 2.6       # Curled up: the next pet counts once she has said her line.
GUILT_FIRST, GUILT_EVERY = (14, 22), (32, 50)
BURST_LINES, BURST_LINE_GAP = ("pounce", "jealous", "demand"), 14
LAUGH_CHANCE = 0.5         # Excited moments that come with a playful laugh (the 45 s pause applies).

# Her acting, all original drawings: (clip, seconds shown; None = the clip's own length).
ACTS = {
    "sigh": ("yawn", None),             # bored, a little lonely
    "fidget": ("tail", None),           # agitated tail flick
    "ears": ("ears", None),             # irritated ear twitch
    "look_left": ("look_left", None),   # glances over at you
    "look_right": ("look_right", None),
    "jealous": ("game_ready", 2.2),     # hunting crouch, staring the arrow down
    "demand": ("paw_offer", None),      # offers a paw: "pet me"
    "excited": ("happy_hop", None),     # bouncing for attention
    "calm": ("ear_rub", None),          # a pet helped; a little softer
    "forgive": ("nuzzle", None),        # forgiven, with hearts
    "stop": ("game_settle", None),      # comes to a stop and sits
    "ready": ("game_prepare", 0.4),     # gathers before a burst
    "sad_0": ("game_loss_0", None),     # sad drawings before she curls up
    "sad_1": ("game_loss_1", None),
    "sad_2": ("game_loss_2", None),
    "curl_down": ("game_loss_finish", None),
    "uncurl": ("game_comfort", None),   # gets up from the curl, cheered up
}
ACT_SECONDS = {name: seconds if seconds is not None else sum(CLIPS[clip].durations) / 1000
               for name, (clip, seconds) in ACTS.items()}
# Clips drawn facing left; they turn toward her travel or toward the arrow.
SIDE_CLIPS = {"walk", "game_run", "game_prepare", "game_jump", "game_ready", "game_settle"}
MOVES = ("travel", "leap")


class RestlessMood:
    def __init__(self, now, home, area, motion=True, rng=None, level_seconds=LEVEL_SECONDS):
        self.rng = rng or random.Random()
        self.home = home
        self.area = area                     # (left, top, right, bottom) allowed window positions
        self.motion = motion
        self.level_seconds = level_seconds
        self.x, self.y = home
        self.ground = home[1]
        self.stage = 0
        self.stage_since = now
        self.pets = 0
        self.last_pet = -math.inf
        self.listen_until = -math.inf
        self.next_guilt = math.inf
        self.direction = -1
        self.cursor = (home[0] + BODY[0], home[1])
        self.plan = []                       # queued steps
        self.step = None                     # (kind, data, started, seconds)
        self.last = now
        self.line = "start"
        self.last_said = now
        self.sound = None                    # A one-off sound cue for the desktop to play.
        self.forgiven = False
        self.quietly = False
        self.done = False
        self.log = [(now, "restless")]
        self.rest(now, 2.0)

    # Clock and level ---------------------------------------------------------------------------
    @property
    def stage_name(self):
        return STAGE_NAMES[self.stage]

    @property
    def level(self):
        return self.stage + 1

    @property
    def pets_needed(self):
        return STAGES[self.stage][1]

    @property
    def curled(self):
        return self.step is not None and self.step[0] == "sulk"

    @property
    def moving(self):
        return self.step is not None and self.step[0] in MOVES

    @property
    def playful(self):
        """She'd still love a game: not sad (a pet first), not already forgiven and heading home."""
        return not (self.done or self.forgiven or self.stage == SAD)

    @property
    def resting(self):
        """Seated between bursts on her current ground, so a game can start without a pose jump."""
        return self.playful and self.step is not None and self.step[0] == "rest"

    def seconds_to_next_level(self, now):
        if self.forgiven or self.stage == SAD:
            return None
        return max(0.0, self.level_seconds - (now - self.stage_since))

    def settle_soon(self):
        """A game was asked for: finish the current move, then sit and wait for it."""
        self.plan = [("rest", 30)]

    def hold(self, now):
        dt = max(0, now - self.last)
        self.stage_since += dt
        self.listen_until += dt
        self.next_guilt += dt
        if self.step:
            kind, data, started, seconds = self.step
            self.step = (kind, data, started + dt, seconds)
        self.last = now

    def escalate(self, now):
        if self.forgiven or self.stage == SAD:
            return
        if now - self.stage_since >= self.level_seconds and now - self.last_pet >= PET_PAUSE:
            self.stage += 1
            self.stage_since = now
            self.pets = 0
            self.log.append((now, self.stage_name))
            if self.stage != SAD:          # The sad level speaks once she has curled up beside you.
                self.line = self.stage_name
                self.last_said = now
            if self.stage == SAD:
                # Whatever she was doing, she now goes to the arrow to be sad there. A pounce or
                # run already under way finishes first.
                self.plan = []
                if not self.moving:
                    self.next_step(now, self.cursor)

    # Interactions -----------------------------------------------------------------------------
    def pet(self, now):
        """One pet. Returns 'forgiven', 'progress', or 'wait' (curled up and still talking)."""
        if self.stage == SAD:
            if now < self.listen_until:
                return "wait"
            self.pets += 1
            self.last_pet = now
            self.stage_since = now
            if self.pets >= self.pets_needed:
                self.forgive(now)
                return "forgiven"
            self.line = f"sad_{self.pets}"
            self.listen_until = now + LISTEN_SECONDS
            self.next_guilt = max(self.next_guilt, now + self.rng.uniform(*GUILT_EVERY))
            return "progress"
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
        if self.stage == 0 or self.stage == SAD:
            self.forgive(now)
            return
        self.stage -= 1
        self.stage_since = now
        self.pets = 0

    def _getting_up(self):
        """Steps that bring her out of the curl, if she is curled (or curling) up."""
        if self.curled or (self.step and self.step[0] == "act" and self.step[1] in ("curl_down", "sad_0", "sad_1", "sad_2")):
            return [("act", "uncurl")]
        return []

    def _trip_home(self):
        trip = self.route(*self.home)
        if any(kind in MOVES for kind, _ in trip):
            trip = [("act", "ready")] + trip
        return trip + [("arrive", None)]

    def forgive(self, now):
        sad = self.stage == SAD
        self.forgiven = True
        self.line = "sad_done" if sad else "calm_done"
        self.plan = self._getting_up() + [("act", "forgive")] + self._trip_home()
        self.step = None
        self.next_step(now)
        self.log.append((now, "forgiven"))

    def go_home(self, now):
        """You stepped away: she quietly heads home without forgiving you (no words)."""
        self.forgiven = self.quietly = True
        self.line = None
        self.plan = self._getting_up() + self._trip_home()
        self.step = None
        self.next_step(now)
        self.log.append((now, "away"))

    def moved(self, x, y, now):
        """She was carried somewhere else: the mood carries on from there."""
        curled = self.curled
        self.x, self.y, self.ground = x, y, y
        self.plan = []
        self.step = None
        if self.forgiven:
            self.plan = self._trip_home()
            self.next_step(now)
        elif curled:
            self.curl(now)                   # Still sad: she stays curled where you put her.
        else:
            self.rest(now, 1.5)

    # Planning ---------------------------------------------------------------------------------
    def rest(self, now, seconds=None):
        low, high = STAGES[self.stage][2]
        self.step = ("rest", None, now, seconds if seconds is not None else self.rng.uniform(low, high))

    def curl(self, now):
        self.plan = []
        self.step = ("sulk", None, now, math.inf)
        self.next_guilt = now + self.rng.uniform(*GUILT_FIRST)

    def clamp_x(self, x):
        return max(self.area[0], min(self.area[2], x))

    def clamp_y(self, y):
        return max(self.area[1], min(self.area[3], y))

    def perch_near(self, cursor, gap=CURSOR_GAP):
        """A resting spot on her side of the arrow, about the arrow's height, `gap` from it."""
        side = -1 if cursor[0] < self.x + BODY[0] else 1   # She stays on her side of the arrow.
        x = self.clamp_x(cursor[0] + (gap + 20) * (-side) - BODY[0])
        if abs(x + BODY[0] - cursor[0]) < gap:             # Clamped against an edge: go round.
            x = self.clamp_x(cursor[0] + (gap + 20) * side - BODY[0])
        y = self.clamp_y(cursor[1] - BODY[1])
        if abs(y - self.ground) < 40:
            y = self.ground
        return x, y

    def sad_perch(self, cursor):
        """As close to the arrow as she can get without covering it."""
        side = -1 if cursor[0] < self.x + BODY[0] else 1
        x = self.clamp_x(cursor[0] + SAD_GAP * (-side) - BODY[0])
        if abs(x + BODY[0] - cursor[0]) < SAD_GAP - 4:
            x = self.clamp_x(cursor[0] + SAD_GAP * side - BODY[0])
        y = self.clamp_y(cursor[1] - BODY[1])
        if abs(y - self.ground) < 30:
            y = self.ground
        return x, y

    def route(self, x, y, settle=True):
        """Steps from where she is to (x, y): pounces for a change of height, a run for left/right
        travel with a short cool-down walk at the end of a long run, then (settle) she sits."""
        steps = []
        ground, here = self.ground, self.x
        x, y = self.clamp_x(x), self.clamp_y(y)
        while self.motion and abs(y - ground) >= 30:
            rise = max(-MAX_LEAP, min(MAX_LEAP, y - ground))
            ground += rise
            if abs(y - ground) < 30:
                ground = y
            here = self.clamp_x(here + max(-LEAP_REACH, min(LEAP_REACH, x - here)))
            steps.append(("leap", (here, ground)))
        distance = x - here
        if abs(distance) >= 30:
            if abs(distance) > RUN_SPLIT:
                cool = x - math.copysign(WALK_TAIL, distance)
                steps.append(("travel", ("run", cool)))
                steps.append(("travel", ("walk", x)))
            else:
                steps.append(("travel", ("run", x)))
        if settle and steps:
            steps.append(("act", "stop"))
        return steps

    def look_at(self, cursor):
        return "look_left" if cursor[0] < self.x + BODY[0] else "look_right"

    def excited(self):
        if self.rng.random() < LAUGH_CHANCE:
            self.sound = "laugh"

    def plan_burst(self, now, cursor):
        name, rng = self.stage_name, self.rng
        if name == "agitated":
            pick = rng.random()
            if pick < 0.35:
                self.plan = [("act", rng.choice(("fidget", "ears"))), ("act", self.look_at(cursor)), ("rest", None)]
            elif pick < 0.55:
                self.plan = [("act", self.look_at(cursor)), ("act", "sigh"), ("rest", None)]
            else:
                start = self.x
                there = self.clamp_x(self.x + rng.choice((-1, 1)) * rng.uniform(150, 260))
                self.plan = ([("act", "ready")] + self.route(there, self.ground)
                             + [("act", rng.choice(("fidget", "ears"))), ("rest", 2.5), ("act", "ready")]
                             + self._route_from(there, self.ground, start, self.ground)
                             + [("act", "sigh"), ("rest", None)])
        elif name == "pouncy":
            if rng.random() < 0.55 or not self.motion:
                there = self.clamp_x(self.x + rng.choice((-1, 1)) * rng.uniform(200, 420))
                self.plan = ([("act", "ready"), ("sound", "run")] + self.route(there, self.ground)
                             + [("act", "excited"), ("say", "pounce"), ("rest", None)])
            else:
                # Pounce up toward the arrow's height, bounce for attention, pounce back down.
                up = self.clamp_y(min(self.ground - 60, cursor[1] - BODY[1]))
                if self.ground - up < 40:
                    up = self.clamp_y(self.ground - 80)
                side = -1 if cursor[0] < self.x + BODY[0] else 1
                across = self.clamp_x(self.x + side * rng.uniform(60, 140))
                ground = self.ground
                up_steps = self.route(across, up)
                back = self.clamp_x(across + side * rng.uniform(40, 120))
                self.plan = ([("act", "ready")] + up_steps + [("act", "excited"), ("say", "pounce"), ("act", "ready")]
                             + self._route_from(across, up, back, ground) + [("rest", None)])
        elif name == "demanding":
            x, y = self.perch_near(cursor)
            act = rng.choice(("demand", "demand", "jealous", "excited"))
            self.plan = ([("act", "ready")] + self.route(x, y)
                         + [("face", cursor), ("act", act),
                            ("say", "jealous" if act == "jealous" else "demand"), ("rest", None)])
        else:  # sad
            x, y = self.sad_perch(cursor)
            approach = self.route(x, y, settle=False)
            self.plan = (([("act", "ready")] if approach else []) + approach
                         + [("face", cursor), ("act", f"sad_{rng.randrange(3)}"), ("say", "sad"),
                            ("act", "curl_down"), ("curl", None)])

    def _route_from(self, x0, y0, x, y):
        """route() as if she were already at (x0, y0) (planning a return before she leaves)."""
        saved = self.x, self.ground
        self.x, self.ground = x0, y0
        try:
            return self.route(x, y)
        finally:
            self.x, self.ground = saved

    def next_step(self, now, cursor=None):
        cursor = cursor if cursor is not None else self.cursor
        if not self.plan:
            if self.forgiven:
                self.done = True
                return
            self.plan_burst(now, cursor)
        kind, data = self.plan.pop(0)
        if kind == "rest":
            self.rest(now, data)
        elif kind == "say":
            # Burst remarks are spaced out so she never chatters; level and pet lines always speak.
            if data not in BURST_LINES or now - self.last_said >= BURST_LINE_GAP:
                self.line = data
                self.last_said = now
            self.next_step(now, cursor)
        elif kind == "sound":
            self.excited()
            self.next_step(now, cursor)
        elif kind == "face":
            self.direction = -1 if data[0] < self.x + BODY[0] else 1
            self.next_step(now, cursor)
        elif kind == "arrive":
            self.done = True
        elif kind == "curl":
            self.curl(now)
        elif kind == "act":
            if data == "ready" and self.plan and self.plan[0][0] in MOVES:
                # Gather facing the way she is about to go, so she doesn't flip mid-burst.
                ahead = self.plan[0][1][1] if self.plan[0][0] == "travel" else self.plan[0][1][0]
                if ahead != self.x:
                    self.direction = -1 if ahead < self.x else 1
            if data == "excited":
                self.excited()
            self.step = ("act", data, now, ACT_SECONDS[data] if self.motion else min(2.0, ACT_SECONDS[data]))
        elif kind == "travel":
            mode, target = data
            target = self.clamp_x(target)
            if not self.motion or abs(target - self.x) < 1:
                self.x = target
                self.next_step(now, cursor)
                return
            self.direction = -1 if target < self.x else 1
            seconds = abs(target - self.x) / (WALK if mode == "walk" else RUN)
            self.step = ("travel", (mode, self.x, target), now, seconds)
        elif kind == "leap":
            x, y = data
            x, y = self.clamp_x(x), self.clamp_y(y)
            if not self.motion:
                self.x, self.y, self.ground = x, y, y
                self.next_step(now, cursor)
                return
            if x != self.x:
                self.direction = -1 if x < self.x else 1
            rise = max(0, self.ground - y)
            self.step = ("leap", (self.x, self.ground, x, y, 18 + rise * 0.6), now, BOUND)

    # Update -----------------------------------------------------------------------------------
    def update(self, now, cursor, paused=False):
        """paused: a mouse button is held or the user is typing; she waits where she is."""
        if self.done:
            return
        self.cursor = cursor
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
            self.y = self.ground
        elif kind == "leap":
            x0, y0, x1, y1, height = data
            f = max(0.0, min(1.0, (t - PREPARE) / FLIGHT))
            self.x = x0 + (x1 - x0) * f
            self.y = y0 + (y1 - y0) * f - 4 * height * f * (1 - f)
        elif kind == "sulk":
            if (not self.forgiven and now >= self.next_guilt and now >= self.listen_until
                    and now - self.last_pet >= 15):
                self.line = "guilt"
                self.next_guilt = now + self.rng.uniform(*GUILT_EVERY)
            return
        if t >= seconds:
            if kind == "leap":
                self.ground = self.y = data[3]
            elif kind == "travel":
                self.y = self.ground
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
            name = "walk" if data[0] == "walk" else "game_run"
        elif kind == "leap":
            name, t = ("game_prepare", t) if t < PREPARE else ("game_jump", t - PREPARE)
        elif kind == "act":
            name = ACTS[data][0]
        return name, t, name in SIDE_CLIPS and self.direction > 0

    def take_line(self):
        line, self.line = self.line, None
        return line

    def take_sound(self):
        sound, self.sound = self.sound, None
        return sound

    @property
    def effect(self):
        if self.curled:
            # The rain cloud clears once your pets start to cheer her up.
            return "sulk" if self.pets < 2 else None
        if self.forgiven:
            return None if self.quietly else "pet"
        return {"demanding": "grumpy"}.get(self.stage_name)
