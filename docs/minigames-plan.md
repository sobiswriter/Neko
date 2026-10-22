# Neko mini-games — proposal, 2026-10-22

Status: portfolio proposal; **Catch the Cursor is now implemented** under the later dedicated design and subsequent user authorization. See [delivery and verification](catch-validation.md). Run Away, Dodge Clicks and the additional ideas remain proposals, unimplemented and untested.

Update, 2026-10-22: the [dedicated Catch the Cursor proposal](catch-the-cursor-plan.md) supersedes this document for that first game: default-on configurable automatic launches, horizontal running with jumps, one-contact victory, out-of-range protest, persistent disappointed curl/comfort and a bounded activity queue. Its rules replace the earlier opt-in-only/free-2D/three-catch design. The user's later approval of subtle frosted thoughts also supersedes the background-free text restriction below; other game ideas remain a portfolio proposal.

## Recommendation

Make three distinct short games: Neko hunts the pointer; the player tags Neko with the pointer; the player aims clicks while Neko performs readable evasions. Add **Yarn Rally** as the strongest subsequent game because batting a physical-looking object introduces a different interaction. **Peek-a-Box** is the next quiet alternative. Keep the other ideas as candidates until the first games are enjoyable.

The character performance is the reward: notice, anticipate, move, make contact, react and recover. The accepted tail chase sets the standard for connected drawings and rhythm. It remains unchanged; looping that turning cycle while translating her around would not create suitable pursuit animation.

All numbers below are initial tuning targets, not measured results. Frame counts are budgets, not quotas. Scope is local single-player play, with existing dependencies and no network requirement.

## Research and what it means for this design

Sources accessed on 2026-10-22:

- [Cats Protection: Cats and Play](https://www.cats.org.uk/help-and-advice/cat-behaviour/cats-and-play) describes stalking, pouncing, chasing and batting, occasional successful catches, variety and short play sessions. Design inference: give Neko anticipation and a satisfying payoff, rather than endless pursuit. Our 30–60 second game targets are product choices, not animal-care prescriptions.
- [RSPCA NSW: Cat Enrichment](https://www.rspcansw.org.au/news-and-updates/what-does-enrichment-mean/) discusses prey-like movement and toys disappearing/reappearing. Design inference: hesitation, direction changes, partial concealment and brief pauses can make an animated kitten interesting without constant maximum speed. These observations inspire fictional acting; they do not validate a virtual game's enjoyment.
- [oneko neko's official site](https://onekoneko.app/) presents pointer following and box naps. [My Desktop Cat's developer description on Steam](https://store.steampowered.com/app/5031490/) describes pointer-led toy chasing, grooming paths and mini-games. These establish existing interaction examples, not proof that our proposals will be fun. Our recommended rules and priorities below are original design proposals.
- [Microsoft: Window Features](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features) explains that zero-alpha parts of layered windows pass mouse messages through. A transparent Qt rectangle alone cannot be assumed to absorb missed game clicks.
- [Microsoft: LowLevelMouseProc](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc) documents mouse-event interception and callback timing constraints. A temporary, narrowly scoped mouse hook is a possible click-game implementation, requiring a native prototype and cleanup tests before adoption.
- [Qt: QWidget mouse capture](https://doc.qt.io/qt-6/qwidget.html#grabMouse) documents capture delivery. Whole-desktop capture would conflict with our goal of keeping the rest of the desktop usable; it is not the proposed permanent input model.

## Existing project: useful parts and limits

Reviewed `behavior.py`, `main.py`, `animations.py`, `activity.py`, README, [Frame Master](../framemaster.md) and the [current pickup verification](pickup-validation.md).

- Current following is optional, occasional **horizontal** movement: two pixels per animation update, a limited excursion, a stop gap and a short deadline. Reuse cursor sampling, screen selection and clamping concepts; do not remove those limits from ordinary following to manufacture a game.
- Existing walking art is directional by horizontal mirroring. Free movement across a two-dimensional play area needs authored front/rear/diagonal poses and turning, rather than a side-facing kitten sliding vertically.
- Current native pet window is 192 × 144 logical pixels, with retained character scale, 32px top padding, canonical ground y=130 and seated head about 62px wide. Game rendering preserves those measurements.
- `Companion` already owns behavioral timing and nap/pet counts. Carry states suppress competing actions; that ownership pattern is useful, but pickup and games must remain separate interactions.
- Ordinary short click pets; hold for 250ms or move past the drag threshold picks up. These remain unchanged outside an explicitly started game.
- Thoughts already have shared visibility/timing rules. Game lines should remain background-free and sparse, with outline/contrast treatment checked against light and dark content.
- `ActivityMonitor` reads keyboard headers, not characters, and window events. Do not expand it into a permanent click recorder. Any click-game interception is a separate temporary facility.

## Common experience

### Start, field and finish

1. Add **Let's play…** to Neko's nook/tray menu. Choose a game, read one sentence, press Start. No automatic games or invitations that demand attention.
2. Start only from supported awake idle. If she is asleep, explain that she is napping; the ordinary wake interaction remains available. Arrival, departure, carrying and an active reaction must finish before starting.
3. Reserve a small play area on Neko's current monitor that contains her starting resting position: initial target 720 × 420 logical pixels, clamped to available work area. Minimal corner marks indicate its extent; there is no filled backdrop. Never cover taskbar/reserved areas or span monitors.
4. Minimum usable field is provisionally 560 × 320; prove turning and full-sprite clearance there. If it does not fit, explain why the movement game is unavailable rather than shrinking Neko or clipping her. Final sizes depend on the movement prototype.
5. Neko moves on the play area's implied desktop plane at constant character scale. Screen y movement represents movement across that plane, not repeated airborne leaps. An actual pounce/hop adds a separate drawn airborne arc and supporting contact.
6. A small text-only status and clearly drawn Stop control sit at its edge. The focused play controller handles Escape; losing that focus ends the round. Stop and tray End game remain available. Do not claim an unfocused Qt shortcut will receive global Escape.
7. Each round is finite. At normal finish, brake, show the final reaction for roughly 1–1.5 seconds, then walk back to the starting resting position and settle. Avoid teleporting to idle or saving temporary chase coordinates as her home.
8. End immediately on hide, fullscreen, display change, shutdown or focus loss. Release input ownership first; preserve/restore a valid resting position and complete visible recovery only where appropriate. Fullscreen pauses games even if ordinary Neko is configured to remain visible.

Outside the marked area, input stays with the desktop. Pointer-only games pause immediately when the pointer leaves; after five seconds outside, end the round. No score or clock advances while paused. Re-entry uses a short ready beat, not an immediate pounce. Clicking outside the area ends play before normal application interaction continues.

### Input and ownership

- Catch and Run Away require only pointer movement. Inside their area, disable ordinary pet/pickup initiation; right-click opens End game. An explicit **Pick her up** control ends the game at the visible pose and then hands off to the existing carry interaction on the next deliberate press. Do not make the same press both score and pick up.
- Dodge and later click games must consume in-area attempts, including misses. Prototype a temporary Windows mouse hook restricted to the marked field while the game controller is active. Forward unrelated/outside events unchanged, and never move, hide or confine the real pointer.
- The callback only decides ownership and queues a bounded event; Qt performs game logic and rendering. Validate press/release pairing, release outside the field, cancellation during a held button, callback loss and teardown. Fail closed by ending the click game if interception health cannot be established. Do not keep a hook installed between rounds or log pointer paths.
- A hook can observe events globally before filtering: this is a technical cost, not a claim of purely local event delivery. Require proof that both in-area misses and outside-app use behave correctly. If this cannot be made dependable with true transparency, hold the click game back; a filled panel or nearly invisible click-catching background is not an assumed fallback.
- Suspend ordinary following, idle stories, nap selection, pending pet/window reactions and unsolicited AI/typing reactions while a session owns Neko. Invalidate stale AI responses. Gameplay never increments pet/nap counts. Schedule ordinary deadlines from completion; a real nap is never silently overwritten at start.
- Quiet mode suppresses optional game chatter and automatic sounds. All cues remain visible without sound. Reuse existing thought styling; no thought panels or filled score cards.
- No daily chores, currencies, unlock grind, online scores or saved play history in this release. Session-only scores are enough.

## 1. Catch the Cursor — Neko is the hunter

**Feeling:** eager, concentrated kitten hunting something just out of reach. **Round:** up to 45 seconds or three catches. **Player challenge:** keep the cursor away; optionally slow down to let her win. Display time evaded and Neko's catches without moralizing either outcome.

### Play loop

1. A 0.6–0.9s ready beat: ears orient, eyes focus, weight shifts forward, small hindquarter preparation. Line: “That little arrow is mine!”
2. Run toward the cursor's recent position using acceleration and a bounded turn rate. Use a short perception delay and a capped look-ahead, so she can overshoot or be outwitted rather than track perfectly.
3. Within a reachable pounce range, plant the hind paws and anticipate for about 200–300ms. Commit to a target snapshot after that cue. Moving the pointer during commitment can make her miss.
4. Play a 350–500ms reach/contact/landing. A catch requires actual forepaw contact with the cursor hotspot at the appropriate contact phase; a bounding rectangle overlapping the arrow is insufficient. A pointer jump is not a swept trail of catchable cursor positions.
5. On success, hold the proud two-paw catch for roughly 650–900ms, glance up, then let the imaginary prize escape. Do not seize or visually hide the real pointer. Line: “Gotcha! …almost kept it.”
6. On a miss, land, look at the empty paw, give one quick puzzled blink, then recover into pursuit. Line: “Wait—come baaack!” A miss never abruptly resets to sitting.

**Fairness:** initial speed about 180–220 logical px/s with limited acceleration is a trial range. Score one catch per committed pounce; rearm only after cursor/kitten separate by a measured threshold. A stationary cursor cannot award catches every frame. Near edges, brake and turn visibly; do not snap the target to another monitor. Prove collision at variable frame rates.

**Distinct art:** low stalking, directional run, planted turn, pounce anticipation, airborne reach, contact/compression, proud grasp, empty-paw blink, recovery. Focused eyes become excited briefly at contact; the miss is curious rather than distressed.

**Reduced motion:** a stationary reach game: move the pointer to the indicated reachable side, then evade the gently timed paw reach. No chase translation or airborne arc; use a separate comparable contact count, without pretending it is the same timed difficulty.

## 2. Run Away / Kitten Tag — the player is the hunter

**Feeling:** cheeky play invitation and short bursts of escape, not fear. **Round:** 45 seconds or three player tags. **Input:** move the cursor; no click is required.

### Play loop

1. Neko looks over one shoulder, gives a teasing half-turn and brief wink: “Bet you can't boop me!”
2. She strolls or waits while the pointer is distant. Entering an initial 140–180px threat radius triggers a readable 180–250ms preparation, then a short escape burst.
3. Select a reachable destination away from the pointer with enough braking room, using a few candidate routes rather than an elaborate pathfinding system. Commit briefly before replanning. Prefer a curved route toward open space; a corner triggers a planted turn, never jitter or teleportation.
4. A deliberate approximately 120ms overlap with the current nose/upper-head target counts as a gentle tag. Show that small target through an occasional subtle highlight; transparent margins and tail contact do not count.
5. On tag, stop through supported footwork, squeeze the eyes, blink and show a pleased little hop or head dip: “Eep! You got me.” Resume only after recovery and separation; use about one second of tag protection.
6. Between escapes she may look back with relaxed lids. After a successful evasive stretch, one playful prance is enough. Line: “Too slooow~”

**Fairness:** Neko cannot outrun arbitrary mouse speed, so this is a readable tagging challenge, not an unbeatable AI. Reaction delay, committed turns and rest beats create chances. Anti-repeat separation prevents farming one stationary overlap. Crossing the field boundary pauses rather than generating an escape route outside it.

**Distinct art:** shoulder look, side-step weight shift, escape burst, planted U-turn, look-back, boop recoil and playful reset. Ears remain curious/neutral; no frightened crouch, pain expression or chronic annoyance.

**Reduced motion:** stationary “find the boop” rounds: the indicated cheek/nose target changes after a relaxed pause. Count accurate pointer dwell rather than movement speed.

## 3. Dodge Clicks / Can't Boop This — aim and timing

**Feeling:** nimble, mischievous kitten performing readable dodges. **Round:** eight attempts or 30 seconds. **Player goal:** land five gentle boops. **Technical gate:** prove safe transparent input before producing the full art set.

### Play loop

1. Show a short ready stance and “Try booping me!” Every in-area left press becomes one attempt, never a pet, drag or desktop click.
2. Hovering the aim near her for about 250–350ms produces a visible tell: ear glance, planted paw and a lean in the chosen direction. She then commits to a 250–400ms side-step, duck or small hop. She does not inspect a future click to choose a guaranteed escape.
3. Resolve a click against the visible eligible body/head silhouette at its timestamp, using the same geometry as rendering. Draw a brief unfilled poke ring at that fixed point. Tail, transparent padding and ring animation are not hit targets. No delayed invisible hitbox.
4. A hit gets a soft blink/head recoil and pleased reset: “Hehe, that tickles.” A miss lets her finish the existing dodge, then a short wink: “Missed meee!”
5. Give each dodge a recovery/cooldown of roughly 700–1000ms so she cannot chain perfect evasions. Accept a maximum of one attempt per deliberate press and initially at most one per 300ms; show readiness so rapid extra presses are not silently charged as attempts.
6. At the last attempt/deadline, freeze further scoring immediately, finish safe supported recovery, and show boops/attempts. No sudden fall, scared running or punishment for losing.

**Fairness:** input and animation use one monotonic timebase. Define simultaneous deadline/click ordering in tests. Double-clicks must not enter ordinary double-click/pet paths or count extra through duplicate native/Qt delivery. Pose or input latency must not secretly move the hit target after a click.

**Distinct art:** lateral weight shift, cross-step/side-step, duck with forelegs accounted for, one small hop with compression, playful near-miss glance, gentle boop reaction and canonical recovery. Do not stretch/rotate an entire sprite to fake evasion.

**Reduced motion:** fixed kitten with clearly signaled boop/rest windows, no hopping, ducking or moving targets. Use longer windows and no rapid-click requirement.

## Additional games worth considering

| Candidate | What the player does | Neko's distinct performance | Round / implementation cost | Recommendation |
| --- | --- | --- | --- | --- |
| **Yarn Rally** | Drag a yarn ball briefly to aim a gentle roll; release. Neko bats it back. Intercept/redirect for a shared rally. Reset an escaped ball rather than losing a life. | Tracks ball, yields a shoulder, alternates paw taps, makes one delighted two-paw save, looks proud after a rally. | 45–60s; medium/high: toy movement, pointer capture during deliberate ball drag, paw-contact timing and safe click ownership. | Best extra. Introduces reciprocal play and a real object, beyond another pointer chase. |
| **Peek-a-Box** | Follow a toy mouse disappearing behind a small authored box; click the side where its next peek is predicted. Neko pounces alongside the correct peek. Use a gentle hint after a miss. | One ear/eye peeks around an edge, crouches, reaches, then sits half-in the box with a wink. | Five rounds; medium: prop occlusion, left/right peeks and transparent click input. | Best quiet follow-up. A small box is a game prop, not a filled thought/desktop background. |
| **Copycat Paws** | Watch a short left/right paw-tap sequence, then tap two drawn paw targets in that order. Begin at two steps, cap at four. Replay is free. | Deliberate alternating taps, listening head tilt, little approval squeeze, relaxed reset. | Three short patterns; medium: modest new art and simple memory logic, click ownership still required. | Strong accessible candidate; use shape/position cues as well as color. |
| **Butterfly Patrol** | Guide a slow butterfly with the pointer; let Neko make three gentle catches and releases. No escape score. | Upward gaze, grounded tracking, brief measured reach, nose sniff, release and relaxed blink. | 45–60s; medium after Catch, with added toy/vertical reach art. | Cozy alternative, but defer until it offers more than a reskin of Catch. |
| **Find the Bell** | Watch a bell hidden under one of two cups, then choose after a slow swap. Increase to three cups only after easy rounds. Neko reveals it with a paw. | Focused gaze follows the correct cup, paw reveal, puzzled tilt on a miss and a little pleased reveal. | Five rounds; medium: cup props/occlusion, clear motion and memory tracking. | Later: overlaps Copycat's memory appeal and risks making Neko a spectator unless the reveal performance is strong. |

No new game needs a hunger system, inventory, expensive physics engine, persistent leaderboard or daily reward loop. Avoid using live application windows as obstacles in this first update; reliable window-edge interaction and occlusion would be another project.

## Animation production and quality contract

Read and follow [Frame Master](../framemaster.md) for actual production. This proposal adds no verified authoring discovery.

1. Prototype difficult poses before a large sheet: rear/diagonal running, planted reversal, maximum pounce, cross-step dodge and two-paw catch. Check silhouette and anatomy at native size.
2. Directional locomotion trial: five authored views (front, front three-quarter, side, rear three-quarter, rear), using horizontal mirrors only for corresponding left/right views. Initial budget six–eight drawings per view, approximately 30–40 unique run drawings. Keep diagonal/away motion on the correct view; do not flip front into rear. Review cost/readability before committing to all views.
3. Budget separate banks for pursuit anticipation/contact/recovery (roughly 16–24 source slots), tag invitation/reaction/recovery (12–20), and each dodge family (8–12 including entry/recovery). Budget explicit turning and stopping drawings, not only loops. These are provisional and may be redrawn/reduced after the prototype.
4. Draw eyes/ears/jaw as subtle acting connected to effort. Focus before chase, excited squeeze at successful contact, cheeky glance while escaping, brief wink after a dodge, relaxed lids after recovery. Do not reuse the same permanent smile or stamp expression glyphs onto the face.
5. Keep head/body volume, outlines and alpha stable. Maintain exactly four anatomical legs, two ears and one attached tail; map which limb bears weight and which is occluded in every difficult pose. A raised paw replaces its grounded counterpart.
6. Reuse fixed-batch import calibration and support landmarks. Grounded travel uses world position; a leap uses its own pose/arc offset. Do not count the same offset twice or rescale per frame. Test true contact against the drawn paw/target, not the whole 192 × 144 canvas.
7. Preserve accepted tail, petting, pickup and lifecycle pixels/timing. New game art is separate. If any view exceeds the current canvas, first measure the problem; a global footprint change is not pre-approved by this proposal.
8. Every entry begins from the actual visible supported pose. Every loop, direction change, outcome and cancel has a drawn connection; normal finish ends at actual idle. Picking up during an explicit game exit must use a valid current-pose carry bridge or finish supported recovery before allowing the next press.
9. Use normal 50ms visual cadence as a starting point, and elapsed-time movement independent of timer frequency. Bound delayed-frame catch-up so a stalled GUI cannot launch Neko across the field. If the loop falls too far behind, pause instead of scoring unobserved contacts.
10. Review all drawings and adjacent pairs, complete normal/slow playback, native light/dark backgrounds, every directional seam and interruption phase. Numerical connected-component checks do not certify attached anatomy.

## Smallest architecture and affected surfaces

- Add one bounded, Qt-independent `games.py` session model and one companion game ownership state. Store game kind, phase, monotonic deadlines, limited input/position history, score and seedable randomness. Avoid separate behavioral states for every animation frame or a generic game-engine/plugin framework.
- `behavior.py`: start/end ownership, competing-action exclusion, deadlines and untouched nap/pet semantics. `main.py`: game lifecycle, menu/control integration, drawing, cursor sampling, coordinate mapping, input routing, return-home and preferences compatibility.
- `animations.py`, `assets/`: separate game clips, view selection, support/contact landmarks and fallback. Incomplete/corrupt game banks disable the affected game with a clear menu explanation; ordinary Neko must still load and work.
- Only add a narrow `game_input.py` if the native click-input trial succeeds. Do not enlarge `activity.py` to collect unrelated events. Pair event routing with current phase ownership to prevent duplicate native and Qt attempts.
- `dialogue.py`: a few local per-game cue/outcome lines. At most a start line, a rate-limited mid-round line and an end line; never one sentence per footstep/click. Ordinary thoughts resume after a cooldown. No AI call is needed to play.
- `test_games.py`: seeded pure game timing, boundaries, fairness and outcomes. Existing `test_behavior.py`, `test_animations.py`, `test_main.py`, `test_packaging.py`: state ownership, imported geometry, native interaction and exact bundled resources.
- `tools/preview_games.py`, `docs/`: actual-controller previews, normal/slow playback, source sheets, contact/turn/cancel coverage, exact prompts and accepted/rejected assembly records. README and Frame Master only receive verified implementation claims after checks pass.
- Existing `main.spec` asset collection should be reused; inspect whether a change is actually required. No new configuration, export layer or runtime dependency is proposed.

## Delivery order and acceptance gates

The actionable task list is in [tasks/todo.md](../tasks/todo.md). Build vertical slices; do not create art for all eight ideas before proving the first game.

1. **Input feasibility trial:** prove transparent in-area click suppression, normal outside interaction, controller focus/Escape and every teardown path on native Windows. Document the result before selecting the click-game input mechanism. Failure defers Dodge/click extras, not pointer-only games or the existing app.
2. **Movement/art trial:** prove a short diagonal run, planted turn, pounce and supported return at current scale. Prove bounded movement at 20/30/60Hz, delayed frames, corners and minimum field size. Select final direction/pose budgets from this evidence.
3. **Catch vertical slice:** menu → field → one complete hunt/contact/miss loop → result → return to actual idle. Include reduced motion and cancellation. Then tune the 45s/three-catch loop.
4. **Checkpoint:** native source check; ordinary click/hold/nap/lifecycle still work, field/cursor remain aligned, and the hunt is readable and escapable. Continue only with a recorded passing slice.
5. **Run Away slice:** distinct invitation, escape routing, planted turns, dwell tag, reaction and recovery; reuse only the proven movement/session parts.
6. **Dodge slice:** after the input gate, add the tell/commit/cooldown loop, timestamped silhouette hits, eight-attempt round and no duplicate click paths. Include press-held-cancel and pointer crossing tests.
7. **Checkpoint:** all three differ in agency and rhythm, scores reflect visible contact, cancellation leaves no input capture, and reduced-motion versions work without continuous travel.
8. **Release proof:** all artwork/transition review, deterministic and Qt integration checks, native input/time observations, then full discovery, fresh executable and both packaging checks. Preserve the pickup release; document exact new build/source/hash and untested hardware.
9. **Additional content:** choose Yarn Rally first, Peek-a-Box next, based on the first release's actual feel. They are recommendations, not part of an already approved build scope.

## Verification matrix for implementation

| Area | Required evidence |
| --- | --- |
| Timing and fairness | Seeded tests; committed targets; no perfect instant turns; no repeat scores while overlapping; deadline/input ordering; frame-rate independent movement. |
| Contact | Paw/hotspot catches, dwell boops and click silhouette hits match current rendered poses; no canvas-padding/tail hits; no catches on fictitious cursor trails. |
| Input isolation | Native misses over a disposable test-owned underlying window do not activate it; outside interactions do; duplicate delivery/held buttons/cancel/focus loss/hook failure leave no capture or stuck input. Never test misses against a user's unsaved document. |
| Ownership | Click/hold/pickup, naps/counts, pending pets, AI, quiet mode, menus, hide/show, fullscreen, display changes, quit and return-home are individually exercised. No idle/typing story interrupts a game. |
| Geometry | Full silhouette plus stopping distance fits every edge/corner; actual pointer, drawn target and collision agree at DPR 1.0 and other available display scales; negative screen origins covered. |
| Art | All selected source drawings, light/dark imported sprites, each directional seam and normal/slow complete sequences reviewed; no observed extra limbs or detached fragments; retained canonical scale/idle endpoints. |
| Accessibility | Text cues without sound/color dependence, explicit Stop and focused Escape, reduced-motion alternatives, calm timing with no rapid-click requirement. |
| Compatibility | Existing tail/pet/carry frames and clips preserved; missing game banks fall back safely; no preference migration/data loss; exact package resources/hashes verified. |
| Resource use | Bounded history and hook lifetime; repeated start/stop cycles and a long-session probe measured; no unattended active games. |

Candidate commands after implementation (run focused checks first):

```powershell
.venv\Scripts\python.exe -m unittest test_games test_behavior test_animations test_main -v
.venv\Scripts\python.exe tools/preview_games.py
.venv\Scripts\python.exe -m unittest discover -v
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist main.spec
$env:NEKO_TEST_EXE = 'dist\DesktopNeko.exe'
.venv\Scripts\python.exe -m unittest test_packaging -v
Remove-Item Env:NEKO_TEST_EXE
```

`test_games` and `tools/preview_games.py` are proposed files and do not exist yet. Native tests must be test-owned and preserve user settings/processes.

## Remaining uncertainties

- True-transparent click interception is the main technical uncertainty; documentation identifies a viable candidate, not a verified implementation. Native proof comes first.
- Directional art readability at the current size and the minimum useful field require visual prototypes. Do not promise a fixed frame count or delivery date before those trials.
- Scores, ranges, dwell times and session lengths need play-testing. Research supports the behavioral inspiration, not these specific tuning values or player preference.
- Mixed-DPI multi-monitor behavior remains a hardware validation item; confining a round to one monitor reduces scope but does not prove every display transition.
