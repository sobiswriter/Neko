# Pickup, held moods and gentle set-down

**Status: approved and implemented, 2026-10-22.** This document preserves the agreed design targets. See [final behavior and verification](pickup-validation.md) for measured timings, completed checks and the delivered build.

This is a strong extension of direct interaction: the same drag becomes a little performance whose expression responds to time spent together. The important design decision is to keep one continuous physical hold underneath the changing expressions. A longer hold should reveal more personality without making release wait for a long movie to finish.

Use [Frame Master](../framemaster.md) for artwork, calibration and review. The user's supplied photograph informs the upright dangling silhouette: compact head, connected shoulders/torso, two hanging forepaws, two hindpaws and an attached curved tail. Translate that silhouette into Neko's existing pixel design. Keep the palm as the cursor; do not add a photographic hand, background or reference-image markings to the sprite.

## Baseline and agreed interaction

Before this revision, `main.py` stored the press position/offset, starts dragging after `QApplication.startDragDistance()`, shows `CURIOUS` while moving and `PEEKING` after release. A press without sufficient movement becomes a pet on release. Actual sleeping/falling-asleep/waking states are preserved when dragged. There was no distinct pickup state, elapsed hold sequence or set-down animation.

Proposed input rules:

- A short left click remains petting, including its existing palm stroke and count behavior.
- Crossing Qt's drag-distance threshold starts pickup immediately. A stationary press becomes pickup at approximately **250ms**, so holding her without moving also works. The threshold is a prototype target and will be checked against normal click use.
- Once pickup starts, releasing never also pets her, even if she was not moved. Holding and moving do not increment pet counts or enqueue pet reactions.
- Keep the open-palm hover and closed-hand hold cursor with a stationary hotspot. Do not move the real pointer to align it with a drawing.
- Existing arrival/departure input lock remains. Awake holding follows the mood sequence below. An already sleeping kitten gets a quiet carried version and remains in her existing nap lifecycle; this preserves the current promise that dragging does not wake her.
- Reduced motion keeps direct placement, using one stable held drawing and immediate safe placement without sway/drop animation. Existing nap state remains respected.

## Visual story and expression schedule

The awake hold clock starts once pickup is recognized, not on every mouse move or every loop. Mood progression is monotonic during that hold, measured from monotonic elapsed time. Mouse movement or pausing does not restart it. A fresh pickup after a completed set-down starts a new story.

| Stage | Proposed elapsed hold | Body and face | What makes it distinct |
| --- | --- | --- | --- |
| Lift / “ooh!” | First 0.3–0.5s | Shoulders rise first; hindpaws lose contact last; tail follows. Eyes open attentively with a brief excited squeeze. | Actual weight transfer into the suspended pose, without a neck stretch or duplicate grounded paws. |
| Excited | 0–3s, including lift | Ears perk, paws curl slightly, tiny asymmetric toe movement, brief bright-eye accent. | An eager discovery beat, rather than constant kicking. |
| Calm | 3–10s | Forepaws loosen, lids soften, tiny breath and delayed tail-tip sway. | Wider, slower spacing and a quieter face. |
| Mildly unimpressed | 10–20s | Level half-lids, tiny flat mouth, one restrained ear adjustment and occasional tail-tip flick. | A playful “still up here?” look; no angry snarling, distressed flailing or guilt-driven response. |
| Sleepy | 20s onward, indefinitely | Heavy lids, slow blink, a small supported head dip; a single yawn on entry followed by a quiet breathing loop. | The yawn completes once rather than repeating every two seconds. This is held drowsiness, not the actual nap state. |

These times are starting points for native-size review, not final constants. Stage changes use **2–4 drawn expression bridges**, around 0.2–0.4s where needed: soften/reopen lids, settle ears and close the jaw. Preserve eye/nose spacing and head volume. Expressions combine face, ears and restrained gesture; avoid four versions distinguished only by smiling versus closed eyes.

The loop should be around **2–3s**, with roughly **8–12 body phases**, tuned by measured playback. The shoulder/grip reference stays steady while small paw/tail movements lag the body. Keep two forelegs and two hindlegs anatomically accounted for with natural overlap. No rotational flipping of the whole kitten, exaggerated neck stretching or large repeated bouncing.

All four mood sets share corresponding body phases and the same scale, camera and attachment reference. Mood changes retain the running phase rather than restarting the body at frame zero. Generate expression variants against the reviewed body drawings and compare overlays; do not assume ImageGen will preserve geometry merely because the prompt requests it. If a variant drifts, redraw or register the batch from measured landmarks before accepting it. Only the intended small expressive gestures may differ.

## Release must work from every moment

Release is an input event with priority over entry, held-loop completion, mood transition and the one-time yawn. It must begin its visible response on the next animation update, nominally within 50ms; it never waits for the current multi-second loop to finish.

1. Capture the current body phase, expression, pose height and intended resting location when the button is released. Further cursor movement does not steer the released kitten.
2. Use the appropriate short drawn bridge from that physical pose toward set-down. Open paws and orient them for contact; close an interrupted yawn through a drawn jaw movement. Heavy lids can remain soft through landing.
3. Lower into a short controlled descent, forepaw contact followed by hindquarter settling, gentle compression and an attached-tail follow-through. The target is the location where the user placed her, rather than a fall to the taskbar or a replay of the startup drop.
4. Recover through near-seated drawings to the actual canonical idle. For a pre-existing nap, return through the corresponding supported sleepy/nap transition instead of forcing an awake idle.

Initial release budget: approximately **10–14 drawings / 0.5–0.8s**, including contact and recovery. Exact counts depend on the retained-scale height and support changes. Include early-release routes during lift, so releasing before the hindpaws fully leave the ground does not first teleport her to the highest held position.

Group compatible body phases into a small number of reviewed release entrances, with matching connecting drawings. Start by proving release from the two opposite sway extremes, neutral, mid-lift and mid-yawn. Expand only as necessary to eliminate visible jumps. Do not generate a separate full landing film for every mood/frame combination, and do not use crossfades or waiting for the next neutral phase to conceal a missing connection. The exact first release drawing must be close to the actual current pose.

Re-grabbing during descent should continue from the visible height/posture into lifting, with one active gesture owner and no forced idle frame in between. A new press during set-down consumes that press as pickup rather than launching a pet on release. Test rapid repeated grab/release around contact, because this is where duplicate timers and misplaced saved positions tend to show up.

## Position, canvas and control ownership

The dangling pose may be taller than the current 112px canvas at the correct head/body scale. **Measure a full held pose and release extremes before choosing dimensions.** Preserve the approximately 62px seated head reference. Add transparent vertical space if measurements require it; never shrink the whole kitten to fit. Use one fixed canvas during playback.

Retain a logical resting origin separate from the temporary drawn lift. At recognition, record the resting origin and press coordinates. While dragging:

```text
intended_rest_origin = original_rest_origin + (current_pointer - press_pointer)
```

The visual lift/sway happens relative to this origin through registered drawings. This keeps the user's familiar drag offset and avoids a window jump when pickup begins or moods change. The same held attachment reference is used across all variants; do not snap her head to the pointer when the user clicked her belly. The entry drawing must make the change of posture legible without warping the cursor.

On release, freeze the intended rest origin, clamp it to the selected monitor's available geometry and settle there. Save this final resting location; temporary lift/descent offsets must never enter preferences, including if Settings saves during a hold or quit occurs mid-release. If top padding is added, extend the existing visible-origin conversion in both load and save and test old saved positions. Preserve tray framing, click-through transparent margins and thought positioning. Do not choose a larger square canvas speculatively.

Input ownership runs through press candidate → lift → held → set-down → ordinary behavior. Represent only the minimum state/elapsed-time data the current architecture needs; reuse `Companion`, atlas/Clip timing and Qt repaint machinery. No physics engine, new dependency, preference panel or configurable mood system is required.

Pickup temporarily owns visible acting so idle, typing, window reactions, delayed pet playback and automatic nap gestures cannot overwrite it. Count real input as activity, discard stale pending pet reactions when pickup takes ownership and invalidate stale AI responses as existing deliberate interactions do. After a normal awake set-down, schedule future idle/nap activity from completion, avoiding immediate sleep or an old queued gesture on landing.

For a real nap, preserve sleep identity/counts and timing. If its timed wake becomes due while held, remember the wake request and complete the supported set-down before the usual wake transition. Do not count a held sleepy face as another nap.

Hide, fullscreen hiding, lost mouse capture, an observed released button outside the window, reduced-motion changes, screen removal and quit need explicit cleanup. Restore a safe logical position, stop gesture-owned timers/capture and clear pending pickup input. Show must not revive a stale hold. Ordinary focus changes alone should not be mistaken for lost capture: Neko is a non-focus-stealing desktop window. Quit hands off from a supported placement into existing departure where appropriate; it must not run two falling trajectories simultaneously. Fullscreen without the hide preference retains the current visible-placement policy.

## Ordered implementation plan

The following records the agreed implementation slices, now completed and verified. [tasks/todo.md](../tasks/todo.md) is the working checklist; each slice must remain small enough to review independently.

| Step | Deliverable / acceptance | Dependencies; likely scope | Verification |
| --- | --- | --- | --- |
| 1. Prove geometry | Reviewed upright held silhouette, opposing sway extremes, mid-lift and contact poses at canonical scale; measured canvas/anchor decision. | Plan review; trial sheet, provenance and QA notes (3 files). | Native-size light/dark and enlarged anatomy review; overlay landmarks and measure bounds. |
| 2. Author one complete calm path | Neutral entry, calm loop and release bridges covering every body phase; complete idle recovery. | 1; 2–3 sheets plus provenance/QA (up to 5 files). | Review all adjacent pairs, loop seam and release entrances. Reject extra limbs/scale drift before integration. |
| 3. Integrate calibrated artwork | Atlas/Clip entries and preview path preserve physical scale and existing animation pixels. Implement measured canvas compatibility separately first if needed. | 2; `animations.py`, `test_animations.py`, preview tool (3 files); optional canvas slice uses `main.py`/tests separately. | Endpoints, source coverage, alpha bounds, registration and non-pickup baseline comparisons. |
| 4. Implement input ownership | Click versus drag versus stationary hold, one calm loop, release from any phase and re-grab; actual duration/cadence drives playback. | 3; `behavior.py`, `main.py`, focused behavior/main tests (4 files). | Boundary tests before/at/after 250ms and drag threshold; every pose release; counts unchanged; arbitrary pointer movement. |
| Checkpoint A | One complete pickup → calm carry → set-down works before generating all moods. | 1–4. | Native event-loop replay, captured contact/idle handoff, position roundtrip and interruption tests. |
| 5. Author expressive variants | Excited, mild annoyed and sleepy sets, gradual facial bridges and one-time yawn aligned to the reviewed loop. | Checkpoint A; split each mood into a sheet + provenance/QA slice (3 files each). | Phase-matched body overlays; distinct expressions readable at native size; interrupted yawn closes cleanly. |
| 6. Connect elapsed moods | Progress once through four stages, retain body phase, loop sleepy indefinitely, stop at any time. | 5; behavior, atlas mapping, main clock and focused tests (up to 5 files per slice). | Just-before/at/after mood boundaries, long holds, low event frequency and release from bridges/extremes. |
| 7. Close lifecycle cases | Sleeping carry, timed-wake deferral, hidden/capture/motion/screen/quit cleanup and correct final saving. | 4 and 6; split nap rules and desktop cancellation into separate 2–4 file slices. | Existing nap/count invariants, external release, rapid re-grab, negative monitor coordinates and save during hold. |
| Checkpoint B | All phases, moods and cancellations behave without stale clocks, frame snaps or placement jumps. | 5–7. | Full regression suite plus native interruption matrix below. |
| 8. Preview and package | Complete timed previews/contact sheets, exact provenance, current Frame Master/README, fresh executable. | Checkpoint B; split artifact/docs and build verification. | Decoded durations/coverage, real native playback, bundled PNG hashes and both opt-in packaging checks. |

Pickup can interrupt awake pet/idle artwork, including a crouch, side flop, roll or airborne hop. Before step 4 is complete, classify these starting silhouettes and prove short pickup bridges from the actual displayed posture. Do not force a seated idle between the user's grab and the lift. Reuse compatible entry drawings where they genuinely connect; author missing connections through ImageGen. This additional art is contingent on measured pose differences, so its count is deliberately not guessed now.

## Acceptance and verification matrix

- **Body/anatomy:** inspect every source and imported drawing, all mood bridges and all entry/release pairs. Account for exactly four anatomical legs with natural occlusion, a connected neck/torso and one attached tail. Check duplicate paws left on the ground during lift and disappearing hindlegs during landing.
- **Scale:** compare native head/feature placement with idle; do not fit every bounding box independently. Inspect transparent boundaries and top/bottom space at both sway extremes and contact. Existing animations retain their accepted proportions/cadence.
- **Acting:** identify each mood without reading a label. Check subtle eyelids, jaw closure, ear changes and delayed tail movement on both light/dark backgrounds. The annoyed stage stays mild; the sleepy yawn is an entry beat.
- **Release:** systematic test at every loop frame, every entry/bridge frame and just before/at/after each mood boundary. Check the initial response within one nominal 50ms update and completion without waiting for the loop; observe native timing rather than assuming the timer guarantees it under load.
- **Input:** test short click, stationary long press, immediate drag, tiny jitter, release outside, lost capture and re-grab at descent/contact/recovery. A hold does not add pets or play the pet-stroke cursor.
- **State priority:** exercise pickup from idle, all pet posture families, real sleep/falling-asleep/waking and reduced motion. Test nap due during hold, timed wake due while carried, window/typing events and stale pending pets. Arrival/departure stay locked.
- **Desktop:** test save while held, release clamp, screen corners, negative-coordinate monitors, restart position, transparent hit testing, tray icon and no focus stealing. Physically test mixed-DPI/monitor transfer when hardware is available; otherwise explicitly report the limit.
- **Cancellation:** hide/show, fullscreen with/without hiding, motion toggled during lift/hold/release, screen removed, menu interruption and quit. No stuck closed-hand cursor, held state, mouse capture or temporary saved position.
- **Deliverable:** render normal/slow/ordered-frame previews from runtime clips, trace actual Windows paints, run full source tests and actual-executable packaging checks. Only stop test-owned processes. Record tested hardware, results and anything not exercised.

## Scope and unresolved measurements

The first version uses the four requested mood stages, existing cursor vocabulary and a short set-down at the chosen location. No new thought lines, background panels, sounds, inertia simulation or settings are needed. Her performance should work visually without extra chatter.

Frame counts, stage thresholds, release length, tall-canvas dimensions and number of posture-family bridges remain prototype decisions. The largest risks are expression-generation geometry drift, tall-pose clipping, release from mid-yawn/side-lying entry and accidental interference with the real nap lifecycle. Steps 1–4 expose those risks before investing in the complete mood library.
