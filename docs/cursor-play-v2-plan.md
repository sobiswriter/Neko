# Catch the Cursor v2: playful idle company — approval proposal, 2026-10-22

Status: **awaiting the user's approval; no v2 gameplay, animation or dialogue implementation yet**. Startup repair and adoption of the supplied `neko_sleep.ico` are separately authorized maintenance work, reported independently. This proposal supersedes the corresponding rules of the first Catch design only after approval. Historical validation reports remain evidence of their own releases.

## The experience we are aiming for

Neko should feel like a kitten who occasionally notices a tempting arrow while sharing the desktop. The user invites that moment by moving into a suitable place beside her. They do not enter an arena or watch a score/clock. Her eyes, paws, anticipation, little boasts and reactions communicate the play. Petting, holding and ordinary work continue to take priority.

The supplied walking crop identifies the old walk as needing replacement. The wide screenshot identifies the intrusive guide/status/End-game overlay to remove. The annotated left/right rectangles describe invisible invitation zones **beside** the kitten, separated from her petting/pickup space. They are explanatory markings, never production artwork.

## Decisions proposed for approval

| Request | Proposed delivery |
| --- | --- |
| Better walk; remove idle following | Author a complete light-footed walk with proper support and turns. Use it for returning home/recovery. Remove ordinary cursor-following, its checkbox, scheduling, state/callers and obsolete tests/dialogue. Cursor movement cannot make an idle Neko stroll after it outside an actual chase. |
| Playful running/jumping, including `>_<` | Draw brief squeezed-eye effort, attentive reopens, ear changes and tail lag into connected poses. No face glyphs pasted onto an unchanged sprite and no permanently closed-eye pursuit. |
| More victory/loss variety | Three independently authored victory stories and three loss entries, selected with separate shuffle bags and no immediate repeat. Every loss still joins the same compatible quiet curl/comfort ownership. |
| More lines | Context-specific announcement, pursuit, victory, unreachable/protest, loss and comfort bags. Keep speech sparse and never obscure a meaningful countdown/outcome with ambient chatter. |
| Remove intrusive UI | Remove the entire guide/status/countdown-clock overlay and its floating End-game button. No replacement arena, floating score or persistent range marker. Keep manual play and a neutral stop action inside the normal right-click/tray menu. |
| Side-zone automatic trigger | Cooldown expiry arms an invitation; a **fresh valid entry** into an invisible left/right zone starts anticipation. The zone excludes the kitten and a care margin. |
| Real countdown | Notice/announce → individually timed **3 → 2 → 1 → Here I come!** with corresponding physical anticipation → pursuit. Each numeral actually appears for its own interval. |
| Sleep deferral | An expired cooldown waits through a real nap, wake recovery and all other ownership gates, then still requires a fresh valid side-zone entry. No forced wake or accumulated rounds. |
| Games played/won in menu | Persist two simple local counters, show them in the normal menu and nook, and count each started chase/contact win once. No gameplay HUD or currency system. |

## 1. Invisible invitation geometry

Keep the actual resting baseline and current monitor's available work area as the geometry source. The two zones use the existing measured vertical reach band, recalibrated after the new drawings are accepted. They never span monitors or extend into taskbar/reserved areas. The body remains at retained scale.

Proposed initial horizontal definition: take the full fixed kitten interaction canvas, then add **40 logical pixels of clear space** on each side before a zone begins. Extend each zone outward to the safe runway limit on that side. This deliberately conservative inner gap keeps petting/embracing away from an invitation; transparent padding does not secretly become an invitation. The attached diagram's asymmetric available space is natural: a zone near an edge can be shorter or absent. Do not move or shrink Neko to manufacture a zone. Defer automatic play if neither side has useful reach (initial trial: at least 120px of usable width).

The care exclusion is used only to begin a chase. Once play has begun, the cursor can come close enough for a real paw catch. Entering the care margin during actual play does not itself mean cheating. Existing deliberate click/hold handling remains the owner of petting/pickup.

Initial anti-accident tuning proposal, to be proved in a geometry preview:

- Require entry into a side zone after it has been outside for about 150ms, then about 250ms of stable presence. Small boundary jitter uses roughly 8px hysteresis. These are tuning targets, not validated constants.
- No mouse button may be down, no pending press/hold/drag may exist, and allow at least two seconds after a deliberate care interaction/recovery.
- Side-zone entry must occur while awake/eligible. Do not save an entry that happened while asleep, carried, hidden, typing, in a menu or otherwise busy.
- Build this as a pure geometry/entry check first. Native-size debug previews may show the zone for our verification; shipping runtime draws none of it.

## 2. Cooldown, fresh entry and sleep: exact proposed semantics

Use the existing default-on persisted 90-second setting and 30–600-second range. Cooldown is a minimum rest after the previous started chase and its recovery/comfort, not a periodic command to start chasing. An ordinary standalone pet/hold delays eligibility until recovery plus the care margin; it does not repeatedly restart the whole 90-second interval.

| State/event | Required behavior |
| --- | --- |
| Cooldown running | No automatic countdown/chase, even if the cursor enters a side zone. Do not remember that entry for later. |
| Cooldown expires with cursor already in a zone | Become armed, remain quiet. Wait for the cursor to leave and **enter again after expiry**; a stationary cursor does not launch play at the deadline. |
| Cooldown expires while cursor is outside | Become armed and wait for a fresh qualified entry. There is no timeout on this quiet waiting state. |
| Cooldown expires in a real nap | Keep one armed/pending intent, let her sleep, and preserve timed wake/pet-to-wake behavior. After complete waking, require eligibility and a new entry; never start immediately just because the old deadline passed. |
| Cursor enters while she is busy | No queued surprise countdown when she finishes. Re-establish outside/inside entry after she becomes eligible. |
| Valid entry while armed and eligible | Lock the resting runway/direction, announce, and begin the real countdown. Consume one invitation, not multiple elapsed intervals. |
| Manual Play selected | Bypass cooldown and the automatic fresh-entry requirement; retain space/ownership checks and the same announcement/countdown. Manual play can promote one pending auto intent. |
| Auto disabled / quiet mode / fullscreen / hidden | Suppress automatic invitation. Disabling removes its pending intent. Re-enabling gets a fresh interval; returning from quiet/hidden/fullscreen cannot reuse a stale entry. |
| Preference interval edited | Recompute one due time from the edit, clear prior entry qualification and avoid duplicates. |
| Win, supported neutral cancellation of an already-started chase, or comfort completes | Schedule the next interval from completion. A countdown-only cancellation instead returns to quiet armed waiting after care recovery and requires a fresh entry. No interval accumulation during a curl or long session pause. |

The proposed core state flow is `cooling → armed/waiting for fresh entry → announcing/counting → pursuing → outcome/recovery → cooling`. Real nap/care/lifecycle ownership gates sit above it. The existing bounded game intent and bounded transition/reason logs are sufficient; this does not need a new general event framework.

## 3. Announcement and a countdown that is actually performed

First aim: roughly 0.7–1.0s of noticing/announcement, then three distinct one-second beats, followed by a short “Here I come!” launch accent. Final pacing must be reviewed at native size.

1. **Notice:** eyes/ears lead toward the inviting side, weight transfers into planted forepaws, tail gives one eager response. One line such as “Psst… I see that little arrow.”
2. **3:** the existing small thought label shows only “3…” for its own interval; she turns into a supported ready stance.
3. **2:** replace it with “2…” after the actual first interval; hindquarters gather and an attentive glance keeps the target alive.
4. **1:** replace it with “1…” after the next interval; compress into the first push, with a brief excited eye squeeze and planted support.
5. **Go:** “Here I come!” connects directly into the first run step. Only now start the active chase/deadline and increment games played.

Drive beats from controller phases/monotonic timing and the actual animation clock, not a single text string containing the countdown and not delayed independent callbacks. Countdown thought durations must override the ordinary minimum thought hold just for these cues; normal speech timing stays intact. Verify every digit and preparation beat through the native event loop. A stall must cancel safely rather than flash past missing digits.

If the user pets/picks her up during anticipation, cancel neutrally and hand off once. If the pointer leaves the whole reachable band during countdown for a short grace (initial trial 0.6s), cancel the invitation neutrally and re-arm for a later fresh entry: no played count, loss, cheating line or full cooldown consumed before actual pursuit. Mere movement from a side zone toward her within reachable play space is allowed. Hiding/fullscreen/display loss also cancel neutrally.

## 4. Movement and expression storyboard

All art follows [Frame Master](../framemaster.md): white/gray/pink identity, hard pixel clusters, exactly four anatomical legs with natural occlusion, one attached tail, stable head volume, canonical scale, actual supported entry/recovery and native light/dark review. New drawings use ImageGen after approval; this planning turn produces none.

| Family | Physical story and expression | Initial source budget / review focus |
| --- | --- | --- |
| Walk | Idle → side stand → rear push → opposite forepaw contact/support → pass/gather → next support; shorten stride, brake and sit. Head interested, tail gently follows rather than rigidly sticking up. | About 12 cycle poses plus 4–8 entry/brake/sit drawings. Prototype planted contacts and loop seam first. |
| Playful run | Hindquarter push, low reach, supported forepaw catch of weight, gather, next push. Alert eyes lead; a short `>_<`-style drawn squeeze accents effort, followed by a real reopen. Ears/tail trail changes of speed. | About 10–12 body phases with a small number of body-matched expression alternatives. Do not turn every stride into the same head bob or select faces per repaint. |
| Jump/reach/miss | Plant/compress → push → excited reach/squeeze → eyes open toward contact/landing → forepaw contact → hindquarter compression → reassess. High and low efforts must have honest paw reach. | About 12–16 per necessary family; prototype highest reach and lowest landing before the full bank. Re-measure every used forepaw box/solver anchor. |
| Turn | Shorten stride, plant, transfer weight, head leads, body follows, depart or settle. | About 6–8 connecting poses; both directions, edges and turn-to-pounce seam. |
| Countdown | Notice, orient, supported ready, gather, compress, launch-ready, with three readable anticipation stages. | About 12–16 total slots; each visible beat connects, no whole-sprite scaling/bouncing trick. |

Couple movement cadence to measured stride/ground contacts so paws do not skate over the desktop. Initial trial speeds: recovery walk about 90–120 logical px/s; lively run about 140–210px/s with acceleration/braking. These are adjustable trial values, not a demand to force the art to match arbitrary speed. Keep the 20ms game update for travel while authored pose holds remain readable. No permanent idle following remains.

## 5. Three victory stories and three loss entries

Choose a variant once at the outcome boundary and keep it through that story. Use separate shuffled bags for win and loss; show all three before recycling and avoid an immediate repeat across bag boundaries. A shuffled frame list or whole-sprite mirror is not a distinct authored performance.

| Outcome | Story |
| --- | --- |
| Win A — “I did it!” | Proud contact → grounded compression → three distinct excited small hops → pleased open-eye landing/blink → supported sit. Preserve the fun of the current win while improving the connection from pursuit. |
| Win B — “My prize!” | Two-paw imaginary grasp → affectionate little squeeze → one small delighted spring → curious look at the empty paws → contented release/sit. Never hide, grab or move the real pointer. |
| Win C — “Obviously a professional.” | Safe contact/landing → proud little chest lift → paw lift/flick and brief wink → tail flourish → bashful softened eyes → supported rest. A quieter contrast to repeated hopping. |
| Loss A — “So close…” | Look at empty paws, ears soften, head yields, fold into curl. |
| Loss B — “Tiny huff.” | Supported landing, briefly tuck/overlap forepaws with a soft unimpressed glance, release the tension, curl. No pain/fear/angry distortion. |
| Loss C — “I meant to rest.” | Slow planted half-turn, one sideways glance back at the arrow, head lowers, settle into curl. |

Plan roughly 16–24 source slots per outcome story initially; final counts follow the motion, not a quota. All loss entries join one compatible quiet breathing loop so petting/curled carrying still work from every loop phase. Reuse the current comfort/rise only if the new curl landmarks connect cleanly; otherwise author the missing bridge. Do not paste canonical idle between incompatible poses.

Preserve the current “curl until petted” rule, with no repeated guilt lines and no automatic new chase while curled. This keeps the earlier requested emotional/comfort interaction; changing it to an automatic recovery would be a separate approval decision. Every victory can be interrupted through a supported landing; every loss/comfort/carry phase gets explicit handoff checks. Reduced motion has calm stationary alternatives without decorative translation.

## 6. Dialogue variety without a chatter stream

Reuse the existing local dialogue/shuffle infrastructure. Initial targets: about 8 announcement lines, 12 pursuit lines, 12 victory lines, context-appropriate protest bags (high/below/beyond-side/other monitor), 8 loss lines and 8 comfort lines. Variation should come from voice and acting, not an AI/network call.

Example tone, to refine during authoring:

| Moment | Examples |
| --- | --- |
| Pursuit | “Wait for these little legs!” / “Paws at full speed!” / “Almost… almost…!” |
| Victory | “Tiny paws. Big victory.” / “Mine! …Okay, you can have it back.” / “Did you see that?!” |
| Too high | “Hey! My paws don't go up there!” / “No fair—come back down here!” |
| Too far/other monitor | “This way, little arrow!” / “You changed neighborhoods!” |
| Loss | “It was right there…” / “My paws were this close.” / “A tiny tactical cuddle break.” |
| Comfort | “Okay… feeling brave again.” / “One cuddle. Very powerful.” |

Only one announcement, the actual countdown, at most two short optional pursuit asides, one protest per sustained excursion and one outcome line. Pursuit asides have at least about six seconds between them and cannot replace a live countdown/protest/outcome cue. Ambient/AI observations remain suppressed during play. Quiet mode suppresses automatic play and optional chatter; manual countdown can use minimal numerals/readiness cues. Body language remains readable without sound.

Retain continuous outside-range grace/hysteresis for an active chase; do not accuse a user during setup, petting, display changes or a typing-driven neutral cancellation. With no drawn boundaries, gaze and safe failed reach indicate why a target is unreachable; do not immediately punish a tiny boundary crossing. Tune the current 1.5s protest/4s loss targets through the invisible-range prototype and native review rather than silently tightening them.

## 7. Quiet UI and precise keepsake counters

Delete `GameOverlay`, its module/import/window lifecycle and floating button. Remove status text, remaining-time display, dashed/sloped guides and all shipping range drawings. Manual play, neutral **Stop playing** and the existing auto setting/interval stay in the normal menu/nook; there is no new foreground panel when play starts. The nook should explain the interaction in one short description, not a game dashboard.

Add two read-only local values to the normal cat menu and nook: **Chases played** and **Neko wins**. Proposed semantics:

- Increment played once when “Here I come!” transitions into actual pursuit. Requests, sleep waiting and abandoned countdowns do not count.
- Increment wins once on the first genuine paw/cursor contact. Misses, delayed callbacks and continued celebration cannot increment it again. A later interruption does not erase an already latched win.
- A chase cancelled after pursuit began remains played but is not a win; do not label that a loss or add a loss counter. Both manual and automatic play contribute.
- Persist promptly at those boundaries; loading validates nonnegative integers and `wins <= played`. Existing installs start at zero: no guessed history from pet/nap counts. No reset feature, stored timestamps or play-history database is needed.

## 8. Implementation slices after approval

| Slice | Reach / dependencies | Acceptance and verification |
| --- | --- | --- |
| V0 — remove the play overlay | `main.py`, delete `game_overlay.py`, affected desktop/package tests and preview tool. First, before the invitation prototype. | No guide/status/clock/floating Stop window remains. Ordinary menu stop/manual settings still work; preview tooling can show debug geometry independently of shipping UI. |
| V1 — invitation and real countdown | `games.py`, focused timer/geometry tests, minimal `main.py` glue. Depends on V0; no full art bank yet. | Fake-clock checks prove post-cooldown fresh entry, exclusion of care/button holds, both sides/edges, sleeping/busy entry invalidation, one pending intent and every separate countdown beat. Initial native phase proof before full art. |
| V2 — replace walk/remove idle following | `animations.py`, new walk assets, `behavior.py`, `main.py`, affected `test_main.py`, `dialogue.py`, README and provenance. Depends on walk prototype. | No idle follow checkbox, state/callers/saved writes or motion initiation remain. New walk supports contact/cadence/turn/home/sit at retained scale. Manual game recovery and ordinary nap/pet/carry still work. Update old following tests to verify removal, not merely delete coverage. |
| V3 — playful run/jump | New art, atlas/contact mapping, existing controller travel, imported-frame tests, previews/provenance. Depends on V1 and high-risk pose review. | Native-size effort squeezes/reopens and connected support are visible; both mirrored paw contacts match rendering at low/high/edge targets. Miss/turn/retry and arbitrary cancellation have supported transitions. |
| Checkpoint | V1–V3 | Watch a complete silent-overlay-free invitation/countdown/hunt/return at normal and slow native size; prove no accidental chase through a pet/hold or stationary cursor at cooldown expiry. Tune before multiplying outcomes. |
| V4 — outcome and speech variety | Three win/three loss stories, common curl/comfort bridges, `dialogue.py`, controller selection and tests. Depends on accepted movement/contact. | Independent shuffle bags, genuine gesture differences, sparse context-correct lines, no per-frame rerolls; all variants connect to actual idle/curl and every care/release phase. |
| V5 — keepsake counters and quiet menu copy | `main.py`, preferences/menu/nook and focused desktop/persistence tests. Depends on counted phase boundaries in V1/V4. | Count transitions exactly once across cancellation/disable/quit/reload, manual and automatic paths; settings explain invitation briefly without introducing a dashboard. Confirm the V0 overlay deletion remains complete. |
| V6 — verify/release | Full source/targeted/native/package checks, actual-controller normal/slow/frame/transition previews, prompts/assembly/QA, README, Frame Master verified findings. Depends on all above. | Build directly to `dist/DesktopNeko.exe`, preserve the verified predecessor, only two release files after checks. Record exact source/asset/hash and physical hardware limits. |

The ordered slice list and approval gate are indexed in `tasks/plan.md` and `tasks/todo.md`. No new runtime dependency, mouse hook, cursor control, eight-direction movement system, leaderboard or other minigame is part of this proposal.

## 9. Required evidence before calling v2 complete

- Deterministic boundary matrix: before/at/after cooldown; inside at expiry vs fresh entry; left/right/corners; exclusion halo; button/hold/pickup; real/timed naps and wake recovery; long busy periods; quiet, menus, settings edits, hidden/fullscreen and display loss. No accumulated launches or stale entry replay.
- Every countdown numeral and physical stage is observed for its intended duration through a warmed visible native Qt window. Unseen skipped phases, stale callbacks and stalls do not start pursuit or count a play.
- New walk/run/jump and every outcome frame: scale/bounds/significant components plus visual four-limb/occlusion/tail/head review, normal/slow playback, loop seams, turns, alpha on light/dark and real forepaw contact. Numerical tests cannot prove anatomy or fun.
- Care always wins safely: pet, hold, early release/re-grab, curl carry, comfort, quiet/motion changes, hide/fullscreen, quit. Saved resting origin and original pet/nap counters remain sound.
- Native desktop checks show no retired guide/clock/Stop windows, no pointer changes/capture and no focus theft. Separate source/native evidence from packaged resource/startup checks; record what actual hardware was available.
- Played/won counters persist, migrate zero, never double count, and obey the proposed cancellation semantics. Dialogue and outcome bags avoid immediate repeats without enlarging the UI.
- Human review of the first complete chase and the outcome catalog is an explicit checkpoint: “more frames” alone is not acceptance if the character still feels stiff or repetitive.

## Approval scope

Approve or amend the philosophy, fresh-entry interpretation, proposed invisible gap/dwell, real countdown sequence, three-win/three-loss set, sparse dialogue, played/won definitions and retained quiet comfort curl. Approval authorizes the slices above; the numeric trial values remain subject to measured art/native tuning, with changes recorded rather than presented as already verified practice.
