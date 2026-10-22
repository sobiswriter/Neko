# Catch the Cursor — dedicated proposal, 2026-10-22

Status: **implemented, 2026-10-22**, following the user's subsequent authorization. See [delivery and verification](catch-validation.md) for tested behavior, previews and remaining limits. The design below preserves the original targets; measured implementation details in the report take precedence. This supersedes the Catch portion of [the portfolio proposal](minigames-plan.md). Other games remain future ideas.

## Requested experience

Neko automatically invites a chase about once every minute or two, announces herself in an eager ready stance, runs only straight left/right on her current resting level and jumps to catch the pointer. The reference image describes a horizontal runway and an upper jump limit; its red annotations are explanatory, not production artwork.

One genuine cursor touch wins the round for Neko. She celebrates with three excited little jumps. If time expires or the cursor stays unreachable, she protests, then becomes disappointed, curls up and stays there until petted. A pet comforts her through a proper recovery. Other activities use a bounded intent queue so they cannot cut into an animation or silently disappear.

All timings and distances below are starting targets requiring native-size animation and play-testing. The [Frame Master](../framemaster.md) governs character identity, scale, supported poses, transitions, provenance and verification. Keep accepted tail/pet/pickup artwork unchanged.

## 1. Discovery, settings and scheduling

- Add **Play → Catch the Cursor** to the tray/right-click menu and a matching control in Neko's nook. An active game changes the menu entry to **End game**.
- Add **Automatic cursor games**, enabled by default, including when an existing installation has no value for the new preference. The user's explicit request authorizes this default.
- Add **Time between games**, initially **90 seconds**, editable from **30–600 seconds**. Explain that this is the minimum wait after a completed interaction/recovery, not a promise to interrupt whatever she is doing every 90 seconds. No random extra delay initially.
- Start the initial countdown when arrival finishes. Use a monotonic due time, never wall-clock time or a countdown reset by every mouse-move event. Save only the enabled flag and interval, not pending rounds or old deadlines.
- When due, enqueue **one** automatic-game intent. Multiple elapsed intervals do not accumulate rounds. A manual start consumes any equivalent pending automatic request.
- Automatic play waits while a reaction/carry/nap/lifecycle transition owns Neko, while menus/settings are open, during fullscreen/hiding, in quiet mode or while recent keyboard activity indicates ongoing typing. Existing keyboard counts are enough; no key values or additional activity collection.
- Once eligible, begin at the next supported idle boundary, with approximately two seconds of keyboard quiet. Ordinary pointer movement does not postpone the game indefinitely: the moving pointer is its target.
- After win recovery, manual cancellation or comforting a loss, schedule the next automatic opportunity from that completion. Do not repeatedly schedule while she is curled and waiting for a pet.
- Disabling automatic games removes their queued intent. It does not cut a manual game off; the explicit End game control remains available. Interval edits recompute one future due time, without creating duplicates.

## 2. Geometry: a runway and real jump reach

**Grounded movement is horizontal only.** Capture the actual resting baseline at start. Running preserves that screen y; it never follows the cursor vertically, climbs windows or changes monitors. The resting baseline is a fictional desktop plane at her current position, not necessarily the taskbar.

- Use the current monitor's available work area, excluding the taskbar/reserved edges. Horizontal limits include the entire kitten canvas and braking clearance, not just her head center.
- Draw thin, unfilled runway/jump-ceiling guides inspired by the reference: a baseline, an upper reach limit and faint sloped side guides. Use a restrained warm accent with a dark/light contrast edge; do not paint thick red lines or fill the desktop.
- Show the guides clearly during announcement, then reduce their emphasis. A small Stop affordance and short remaining-time text remain available. All guide/control placement is clamped to the monitor.
- Derive the upper reach from **measured forepaw geometry plus the allowed body lift**, rather than declaring a large clickable rectangle. Initial body-lift trial: about 100–120 logical pixels; initial horizontal pounce travel: up to about 140px. These are prototype budgets, not promises before the new drawings exist.
- Distinguish the **play band** (positions she can eventually approach along the runway) from the **immediate pounce envelope** (positions the current jump can actually reach). Only highlight a catch opportunity when the trajectory/contact solver agrees.
- The sloping guide motif must not imply that she can instantly reach the far side of the display. Running first closes the distance; a jump covers the remaining reachable distance/height.
- If the cursor is above her but reachable, run underneath and perform an upright jump. At her level, use a short forward pounce. Higher lateral targets get a longer arc. Use distinct authored effort/reach/contact poses with shared anatomy, not one drawing rotated or stretched into every jump.
- Preserve the 192 × 144 sprite canvas and existing scale initially. The pet window travels along a temporary world-space arc; the drawn airborne pose and world offset must not both apply the same jump height. Do not resize the window or save airborne coordinates as her resting home.
- Reduce the available lift near the top of a monitor. If there is insufficient safe space even for the smallest jump, defer automatic play and explain a manual-start refusal; never clip ears/paws, move her home without consent or shrink her to fit.
- A cursor below the runway, beyond the safe horizontal extent, too high or on another monitor is outside the reachable play band. Never warp/confine the pointer or move Neko across monitors to pursue it.

## 3. Complete round flow

### A. Announce and prepare — approximately 1.2–1.6 seconds

Connect actual idle into an attentive stand: ears lead, eyes focus, forepaws plant, shoulders lean, hindquarters prepare. Hold the silhouette long enough to recognize it. Say **“Here I come! That cursor is mine!”** Show the range and a brief ready cue.

Start the 45-second active clock only after this preparation. Give the player another approximately 1.5 seconds to bring the cursor into the band before out-of-range penalties begin. The clock does not run during loading, queued activities or announcement.

### B. Approach and choose an opportunity

Face the target using a supported turn, then accelerate along the baseline. Initial speed trial: about 180–220 logical px/s, with measured acceleration/braking. Reuse the current walk for a quiet recovery only if appropriate; author a proper faster side-run cycle for pursuit.

React to a short history of cursor positions, with bounded prediction and a small perception delay. Do not know the player's future movement. Replan between steps/attempts, not by instantly flipping the body at every mouse sample. A cursor teleport is a new observation, not a trail of intermediate catchable points.

Create opportunities by approaching beneath a reachable cursor, alternating short forward and taller upward attempts, and including short land/reassess beats. Give a nearby stationary cursor a genuinely catchable approach instead of running forever at a fixed gap. No arbitrary cap of three attempts: multiple attempts can fit in the round, each with complete contact and recovery.

### C. Commit and pounce

At a feasible opportunity, plant the rear paws and compress for roughly 150–250ms. Commit to the sampled target and direction, then use a roughly 450–650ms airborne/contact/landing path. The target cannot pull her sideways midair. Cursor movement during the commitment can produce a real miss.

Resolve a catch against an authored forepaw contact region and the real cursor hotspot at the matching monotonic time. Transparent margins, tail contact, the thought label and an enclosing rectangle do not count. Continuous movement checks must respect actual sampled positions and measured contact windows, not invent cursor movement across a jump.

An empty-paw landing gets a quick puzzled glance or determined squint, then supported recovery into another approach. Vary two or three reviewed effort/recovery beats so a long round does not become an identical hop loop.

### D. Outside range: protest, try, then lose fairly

Use a **continuous** outside-range timer with a boundary tolerance; briefly crossing the guide must not immediately lose the round.

1. After about **1.5 seconds** continuously outside, orient toward the cursor, narrow the eyes in playful frustration and say **“No fair, you cheated! Too high!”** Adapt the last phrase for another boundary; do not call a low target “too high.”
2. Make one or two safe frustrated reach-jumps, landing on the same runway. Her paws stop at real physical reach; do not stretch anatomy, clip the monitor or pretend she touched an unreachable target.
3. If the cursor returns in range before approximately **4 seconds** continuously outside, clear the protest timer and resume through an authored ready bridge. If airborne, land first. Avoid repeated chatter around the boundary with hysteresis and a protest cooldown.
4. At four seconds outside, mark the round lost due to unreachable play. Stop new attempts, finish the current safe landing and enter the disappointed outcome. A timeout independently loses at 45 active seconds. Missing mouse samples or an application stall are technical cancellations, not cheating.

The range/deadline rules are shown briefly before the first round. These numbers need testing; she should feel determined and slightly dramatic rather than punitive about a tiny pointer slip.

### E. Win: three delighted jumps

The first valid forepaw/cursor contact immediately latches the win, before any later timeout check for that instant. Disable further scoring. Finish contact/landing, show a proud grasp, then perform **three small victory hops** with separate grounded compression between them. Face excitedly squeezes, reopens at landings and finishes with a pleased blink. Line: **“Gotcha! I knew I could!”**

Budget approximately 2–3 seconds of celebration, followed by a complete supported sit. Return to the saved resting origin through a visible horizontal walk if pursuit moved her. The win sequence ends in actual canonical idle; it never teleports from an airborne pose. A deliberate pet/pickup can interrupt via a supported handoff, without counting another catch.

### F. Loss: disappointed curl until comforted

After safe landing, ears soften sideways, head lowers, gaze drops, shoulders yield and she folds into a compact curl. Use drawn forepaw/hindquarter placement. Budget approximately 1.5–2.5 seconds for settling, then a quiet breathing loop. Line: **“I almost had it…”** Only one outcome line; no recurring guilt messages.

This is **disappointment, not a real nap**: no nap count, timed automatic wake or ordinary sleep deadline takes control. She remains curled until petted, including after hide/show. Pause automatic invitations and spontaneous idle gestures in this state. The round is already finished; her curled pose must not keep its timers or pursuit active.

A quick pet produces an acknowledging ear/eye response immediately, then an approximately 1.5–2 second comfort story: eyes reopen, slow blink, cheek/paw response, supported uncurl/rise and neutral sit. Line: **“Okay… one more cuddle.”** Count the deliberate pet once. Coalesce extra quick pets while recovering; do not restart the uncurl endlessly.

Dragging a disappointed kitten uses the appropriate quiet curled carry entry and returns to the disappointed curl on release; moving her alone does not count as comforting. Preserve that mood separately from real nap state. A new manual game is unavailable until comfort recovery completes. Quit remains immediate/normal; no attempt to trap the user in this state.

## 4. Activity queue: record intent, not stale animation clocks

Use one bounded queue of meaningful pending actions and a bounded in-memory transition log. Store action kind, source (manual/automatic), enqueue time, priority and reason. Do not store pointer trails, typed content or an unbounded history. No new visible queue dashboard is required.

| Priority / ownership | Rule |
| --- | --- |
| Safety/lifecycle | Hide, fullscreen, display loss and quit cancel active play immediately and release its overlays/input/timers. They never enqueue a later surprise replay of that interrupted round. |
| Deliberate interaction | A pet/pickup/menu action takes priority. Complete only the necessary supported landing/bridge, then service the interaction once. A click is never both a game action and a pet. |
| Current atomic action | Finish a planted step, committed jump, pet reaction or recovery before a queued autonomous action starts. Do not pause a clip and resume an obsolete pose clock later. |
| Real nap | A sleeping kitten stays asleep. A queued game waits until real timed wake or deliberate pet and its recovery; it must not wake her automatically. A still-valid nap request can follow a game outcome, except while disappointment explicitly owns the curl. |
| Pending game | At most one game intent. Serve after current eligible action/care; manual intent can promote the existing automatic intent rather than add another round. |
| Idle/context reaction | Keep at most one intent per category, coalescing repeated events. Revalidate on execution; stale app curiosity or an obsolete sleep request must not replay after circumstances change. |

At every completion, choose the next eligible intent by priority and FIFO within equal priority. A queue does not make an impossible action eligible: sleeping, carrying, open menus, fullscreen, hidden state, insufficient space, quiet mode for automatic play, and disappointed curl are explicit gates.

If sleep becomes due during a game, retain a pending nap intent; re-evaluate actual inactivity after landing/outcome. Active play/petting may make that old request no longer appropriate. Do not force a stale nap simply because it was once queued. On loss, defer all autonomous work until comfort completes, then revalidate it. Repeated intervals or activity events cannot grow the queue indefinitely.

## 5. Interruption decisions

| Event | Proposed response |
| --- | --- |
| Pet during announcement/run | Cancel the round neutrally, connect into the deliberate pet once; no loss curl. |
| Pet/pickup during a jump | Stop pursuit/scoring immediately; take the shortest authored landing or verified carry bridge into that action. Show a quick acknowledgment while completing support. |
| Hide/fullscreen/screen reconfiguration | Cancel neutrally, remove guides and reset to a valid resting placement; no “cheating” outcome. An existing disappointed curl remains a mood when shown again. |
| Tray/right-click End game | Cancel neutrally with supported recovery. Re-arm automatic play only after a full configured interval. Offer disabling automatic games beside it. |
| Typing starts during an automatic round | End neutrally after safe recovery so a work activity does not provoke a loss. Do not keep chasing during continuous typing. |
| Window switch without typing | Keep the pointer-only round running if still visible/eligible; it does not own application clicks. Fullscreen/hide rules still take precedence. |
| Pointer moves to another monitor | Count as out of range after the normal grace period; never transfer the runway to follow it. Display removal is instead a technical cancellation. |
| Reduced motion on | Use a stationary readiness/reach variant with no run/jump translation, no bouncing guides and longer opportunity windows. Win uses an excited held expression/paw lift; loss/comfort use calm supported poses. Do not silently enable motion. |
| Long GUI stall / suspend-resume | Cancel or pause safely; do not advance unseen catches, snap through a jump or accuse the user of cheating on resume. |
| Damaged/missing game art | Disable game/menu/scheduling safely with a short explanation; preserve ordinary Neko and avoid endless retry announcements. |

Guides and announcement thoughts are click-through. This first game needs no desktop click suppression, global mouse hook, keyboard hook, pointer capture or focus stealing. The actual kitten keeps deliberate pet/drag handling with phase-aware ownership. Escape ends play only when a Neko control actually has focus; the tray/right-click End game is always the reliable route.

## 6. Animation storyboard and first art budgets

Generate and inspect anatomy under the existing method; these are source-slot budgets, not final counts. Author lateral views and mirror left/right only where appropriate. **No eight-direction run set is needed for this game.**

| Family | Story / expression | Initial source budget |
| --- | --- | --- |
| Ready / announcement | Actual idle → stand/ears orient → focused gaze → hindquarter preparation → run-ready; reverse/bridge on cancel. | 12–16 |
| Side run | Connected rear-paw push, reach, support and gather; body volume stable, ears alert, tail lags effort. | 8–12 cycle drawings |
| Turn / brake | Shorten stride, plant support, transfer weight, turn head then body, depart the other way or sit. | 8–12 |
| Pounce / high reach | Compress → launch → extend forepaws → readable apex/contact → gather legs → forepaw landing → hindpaw compression → recover. Trial forward and upright reach separately. | 12–16 per required family |
| Frustrated attempt | Focus narrows, small ear flick, determined safe reach, miss, supported landing and “not fair” glance. | 12–16 |
| Win | Proud contact/grasp → launch/compress for three distinct small hops → satisfied blink → supported sit. | 20–28 including recovery; reuse a reviewed cycle intentionally |
| Loss / curl | Empty-paw glance → ears/head lower → fold forepaws → hindquarters settle → quiet curled breathing. | 16–24 plus 4–8 loop phases |
| Comfort / rise | Actual curled phase → acknowledge pet → reopen/blink → affectionate response → plant paws → uncurl/rise → idle. | 12–20 |

Prototype maximum reach, landing and curl-to-carry/comfort first. Verify exactly four anatomical limbs, one attached tail, two ears and stable head volume; occluded limbs remain hidden. Never add a second grounded paw below the one reaching. Plan support/occlusion per difficult pose before generating a full bank.

Preserve expression changes through drawn lids/ears/jaw; no expression glyph pasted on top. Review every loop seam, left/right turn, miss → new pursuit, out-of-range → reachable recovery, arbitrary interruption, curl loop → comfort and actual-idle handoff at native size and slow playback.

## 7. Implementation slices and acceptance

The task summary is recorded in [tasks/todo.md](../tasks/todo.md). The following slices are now delivered; hardware limits and tuning differences are recorded in [verification](catch-validation.md).

1. **C1 — geometry/contact trial:** prove lateral-only travel, three candidate arcs and solver/guide agreement at retained size. Focused files: proposed `games.py`, geometry tests, trial preview and QA record. Pass: no grounded y drift, no monitor clipping, targets in advertised immediate reach can be contacted.
2. **C2 — one complete hunt art path:** ready → run/turn → one pounce → miss/catch → supported return. Separate accepted bank, `animations.py`, prompt/assembly record and actual-atlas preview. Pass native light/dark anatomy, scale, contact and cancellation before more outcomes.
3. **C3 — manual playable slice:** add game ownership, menu start/stop and genuine single-contact win using C1/C2. Focused `behavior.py`, `main.py`, `games.py` and focused tests. Pass: no pet/carry/nap count or saved-position regression, no pointer warp/click capture.
4. **Checkpoint:** observe a native full round with a moving and stationary cursor, edge turns, reachable high targets, failed pounces and supported manual cancellation. Tune reach/speed before filling more art.
5. **C4 — full outcomes:** author/import frustrated attempts, three-hop win, disappointed curl/loop and pet comfort. Keep underlying nap/carry/mood ownership separate. Pass: no queued idle/wake interrupts the disappointed curl; pet responds once and recovers from every loop phase.
6. **C5 — bounded queue and automatic scheduling:** implement coalesced intents, eligibility priorities, 90s default-on setting and interval controls. Split settings from scheduler if this exceeds five files. Pass deterministic fake-clock tests for long naps, repeated due intervals, preference edits, quiet/fullscreen, comfort and manual override.
7. **Checkpoint:** repeat busy-work, nap, carry, menu and disappointment scenarios. Queue stays bounded; auto launch is discoverable and announced; ordinary work never produces accidental game input.
8. **C6 — verification/release:** reduced motion, native input/timing, geometry at available DPI settings, all selected frames/transition previews, missing-bank fallback and existing source tests. Build directly to `dist/DesktopNeko.exe`, keep only its immediate predecessor beside it, run both exact-package checks and record source/hash/limits. Update README, Frame Master only for verified findings, and provenance together.

## 8. Critical tests before shipping

- Automatic flag defaults on, 90s interval persists, disabling removes pending auto requests, edits do not duplicate, and no infinite backlog appears after a long nap/session pause.
- Real naps remain asleep; pet, pickup, sleep timing, idle selection and stale AI responses cannot fight game ownership. Every queued item is either serviced, explicitly coalesced or invalidated with a reason.
- All grounded movement has invariant baseline y. Flight begins/lands on that baseline, with actual support/compression; no canvas/ear/paw clipping at either edge or top clearance limit.
- Catch at matching paw/hotspot time, no transparent-area/tail hits, no fictitious cursor trail, no repeat win. Catch/deadline ordering and perception/commit boundaries are deterministic.
- Grace/hysteresis boundaries, return to range mid-jump, continuous unreachable duration, attempt cooldown, timeout and system suspend differ correctly from intentional End game.
- Win contains three separated supported hop arcs. Loss remains curled through ordinary inactivity/idle deadlines; pet acknowledgment/uncurl and curled carry return work from every phase without counting a nap.
- All current geometry, drawing scale, faster pet timing and accepted tail/carry/lifecycle behavior remain intact. Save/restart never restores an airborne/game coordinate.
- Real native click-through guides/thoughts, app focus, hide/fullscreen/monitor changes and safe teardown are observed, not inferred from offscreen images alone.
- Review normal/slow controller-derived previews, all source frames and light/dark imports. Inspect attached anatomy visually; numerical component checks cannot prove limb correctness.

## Remaining design decisions requiring prototype evidence

Exact paw reach/body lift, acceleration, protest grace and outcome durations need actual artwork and play-testing. Physical mixed-DPI hardware remains a validation item. The new queue is deliberately a bounded intent scheduler, not a blanket FIFO that must replay every obsolete idle or sleep event. The requested automatic launch and persistent disappointed curl supersede the older portfolio proposal's opt-in-only, always-return-to-idle rules specifically for this game.
