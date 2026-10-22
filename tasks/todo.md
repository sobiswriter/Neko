# Animation rebuild checklist

## Pickup animation — approved and completed

- [x] Create `framemaster.md` from the verified animation method, link it from README and require future animation agents to consult/update it through `AGENTS.md`.
- [x] Study current dragging, sleep preservation, cursor, clip timing and saved-position paths; record the detailed [pickup design](../docs/pickup-animation-plan.md) and plan summary.
- [x] User reviewed the pickup proposal and authorized implementation with “Do it then”.

### 1. Geometry and anchor trial

Description: prove the dangling pose and hardest lift/landing shapes at the retained character scale.

- [x] Acceptance: initial held/mid-lift/contact trial reviewed at native size; retained head 62px and hanging body about 100px require room above idle.
- [x] Verification: measured 32px top-padding decision; all 427 existing frame pixels and 32 clip definitions unchanged after padding removal; 98 focused animation/desktop tests pass.
- Dependencies: proposal review. Likely files: trial sheet, provenance, QA notes (3; medium).

### 2. One complete calm art path

Description: author calm lift, seamless loop and release entrances before multiplying moods.

- [x] Acceptance: every loop phase and early-lift phase connects to release; supported recovery reaches actual idle without snapping.
- [x] Verification: inspect every drawing, adjacent pair and loop/release seam; alpha/anatomy/scale review passes before import.
- Dependencies: 1. Likely files: up to 3 sheets plus provenance/QA (up to 5; split by entry/loop/release if needed).

### 3. Import and preview

- [x] Canvas slice, only if measured necessary: preserve logical visible origin in load/save, fixed footprint, tray framing and transparent-margin hit testing. Verify old position roundtrips and screen-edge clamping. Files: `animations.py`, `main.py`, associated tests (up to 4; medium).
- [x] Art slice: add calibrated held/release clips and complete preview sampling; scale, bounds, actual idle endpoint and unrelated animation pixel/cadence checks pass. Files: `animations.py`, `test_animations.py`, preview tool (3; medium).
- Dependencies: 2; measured canvas compatibility precedes final registration.

### 4. Input ownership and calm carry

Description: quick click pets; drag or stationary hold picks up; release/re-grab works without pet counts or cursor jumps.

- [x] Acceptance: 250ms and Qt drag-distance boundaries behave correctly; every lift/held phase releases promptly; re-grab continues from visible position with one active owner.
- [x] Verification: meaningful behavior/main tests around input boundaries, all release phases, external release and unchanged pet counts; native drag/save roundtrip.
- [x] Entry-art follow-through: classify current awake seated/crouched/side-lying/airborne postures; draw missing pickup connections rather than forcing idle. Verify interrupted roll/flop/hop plus representative idle entries. Keep each art/provenance/QA slice to 3–5 files.
- Dependencies: 3. Runtime files: `behavior.py`, `main.py`, focused tests (4; medium).

### Checkpoint A — calm path

- [x] Native pickup → calm loop → set-down plays completely, with arbitrary release/re-grab, no scale/anchor jump and correct saving. Common body and native calm-path review complete; expression variants are integrated and verified.

### 5. Expression artwork, one mood per slice

- [x] Excited: bright eyes/brief squeeze, perked ears and restrained curled-paw gesture; phase-matched geometry and gradual calm bridge reviewed.
- [x] Mildly unimpressed: level lids/tiny neutral mouth, restrained ear/tail accent; distinct native-size acting without distressed flailing.
- [x] Sleepy: heavy lids, one entry yawn with release-safe jaw closure, then quiet indefinite breathing loop.
- Verification per slice: every source/imported pose on light/dark backgrounds, phase overlays against calm body, no anatomical/feature drift, clean expression bridges.
- Dependencies: Checkpoint A. Each slice: mood sheet, provenance and QA notes (3; medium).

### 6. Elapsed mood progression

- [x] Acceptance: excited → calm → mildly unimpressed → sleepy progresses once by monotonic hold duration; body phase survives mood changes; sleepy loop runs indefinitely and release overrides all bridges/yawn.
- [x] Verification: just-before/at/after 3/10/20s boundaries, long holds, sparse mouse events, every expression/release phase; inspect actual native playback.
- Dependencies: 5. Likely files: behavior/atlas/main and focused tests (split to at most 5 files per slice).

### 7. Real nap and cancellation slices

- [x] Nap slice: existing sleeping/falling-asleep/waking behavior is deliberately handled; carrying does not count another nap or wake on drag; a due timed wake waits for supported placement. Verify counts, timer rules and subsequent idle/nap scheduling. Files: behavior/main and tests (up to 4).
- [x] Desktop slice: hide/show, lost capture/button release outside, fullscreen policy, motion toggle, screen change, menu/quit clear ownership safely; save the logical rest origin even during lift/descent. Verify no stuck cursor/capture/state, stale pending pets or double departure trajectory. Files: main and focused tests (2–3).
- Dependencies: 4 and 6.

### Checkpoint B — complete interruption matrix

- [x] Full regression suite: 171 run, 169 passed, 2 opt-in package checks skipped; both packaged checks then passed. All 86 release samples, 14 native release cases, 4 re-grabs and 4 posture families pass. Physical mixed-DPI/multi-monitor and long-session limits are recorded.

### 8. Artifacts and release verification

- [x] Render runtime-derived normal/slow catalogs, every-pose sheets and native light/dark captures; verify decoded duration and pose coverage. Save exact prompts/selections/calibration and update Frame Master findings plus README.
- [x] Build a distinct executable; both opt-in package checks pass; bundled art hashes match final sheets; record source commit/hash and stop only test-owned processes.
- Dependencies: Checkpoint B. Split preview/provenance/docs and build verification into separate reviewable slices.

Delivered: `dist/pickup-qol/DesktopNeko.exe`. See [final verification](../docs/pickup-validation.md) and [native/release measurements](../docs/pickup-native.json).

---

## Expressive petting revision — approved and completed

- [x] Inspect the current timings, shared idle handoff, canvas/registration, behavior deadlines, preview sampling and packaging references; record the detailed revised plan in `tasks/plan.md`.
- [x] User reviewed the proposed plan and authorized implementation; expression/gesture study added to the first slice.

### 1. Native-size expression and pose-space trial

Description: establish relaxed, wink, excited, sleepy and yawning faces plus roll/knead/deep-stretch key poses at the canonical idle scale.

- [x] Acceptance: expressions read at native size; key poses have coherent anatomy; deepest silhouettes fit without shrinking the kitten or concealing the reach.
- [x] Verification: review idle-overlaid contact sheets and proposed support/limb-visibility maps; measure transparent-space needs. Record the canvas decision before integration.
- Dependencies: plan review. Likely files: trial art and revision QA notes (2–4 files; medium).

### 2. Playful roll replaces Tiny blep

Description: make the complete 5.8-second side/back/other-side/upright story replace blep within the existing twelve-reaction rotation. Split the work into art, runtime mapping and packaging follow-through as below.

- [x] Art acceptance/verification: draw/review 24–32 pose slots including support, tuck, belly-up wriggle and supported rise; inspect every adjacent handoff at native/enlarged size. Files: roll sheet, prompt/QA record (2–3; small).
- [x] Runtime acceptance/verification: replace BLEPPING/blep selection, clip, mapping and description; true clip deadline and canonical idle endpoints pass focused behavior/animation tests. Files: `behavior.py`, `animations.py`, `main.py`, focused tests (up to 5; medium).
- [x] Packaging acceptance/verification: preview/required-asset lists use roll, blep is no longer selectable; asset-presence and full-preview checks pass. Files: preview tool, packaging tests (2; small).
- Dependencies: task 1; complete art before runtime calibration. If task 1 requires expanded transparent space, first implement and test the minimal fixed-anchor canvas change as a separate slice before mapping roll.

### 3. Kneading rebuilt from one clean alternating pair

Description: establish left pressure/right release and right pressure/left release, then play four pairs with a relaxed face and full entry/recovery, targeting 5.8 seconds.

- [x] Acceptance: two connected forelegs, alternating pressure, stable hindquarters and no head pumping; four pairs; complete seated recovery.
- [x] Verification: inspect a slowed single pair and every seam, then full native playback; cycle/order/deadline and endpoint checks pass.
- Dependencies: task 1 and task 2's shared importer/space decisions. Files: knead sheet, `animations.py`, focused animation tests, prompt/QA record (4–5; medium).

Checkpoint: inspect roll and knead source/runtime previews before generating the remaining full sheets. Reject anatomy drift and repair the affected passage.

### 4. Extended stretches (two separate slices)

Description: build front stretch's farther reach/deep bow/release (5.2 seconds), then arch's gradual rounding/comfortable effort/unroll (4.9 seconds).

- [x] Front acceptance/verification: longer forward reach is visible with fixed hind support; effort becomes relaxed; native slow/normal playback and scale/contact/endpoint checks pass.
- [x] Arch acceptance/verification: four-paw rounded-spine action stays distinct from bowing and fear; face relaxes before sitting; the same checks pass.
- Dependencies: task 1 and shared importer decisions. Per slice files: one sheet, `animations.py`, animation tests, prompt/QA record (4–5; medium).

### 5. Three connected excited hops

Description: create three subtly different hops with shared ground support and complete final recovery, targeting 5.0 seconds.

- [x] Acceptance: exactly three push-offs/airborne arcs/landings; second hop slightly bouncier; excited eyes with readable landing glances; no seated snap between hops.
- [x] Verification: review each takeoff/contact/compression and native full playback; launch count, deliberate lift, grounded recovery and real deadline checks pass.
- Dependencies: task 1 and shared importer decisions. Files: hop sheet, `animations.py`, animation tests, prompt/QA record (4–5; medium).

Checkpoint: review stretches/hops at native scale against idle and tail playback; check reach, continuity and transparent edges before smaller contact gestures.

### 6. Paw offer and cheek nuzzle (two separate slices)

Description: make offer 3.6 seconds and nuzzle 3.7 seconds using animated contact/expressions and gradual withdrawal.

- [x] Paw acceptance/verification: supporting paw stays grounded; offered paw has one small beckon and a wink, then plants cleanly. Source/runtime adjacent-pose review and timing/contact checks pass.
- [x] Nuzzle acceptance/verification: visible cheek pressure/curved rub, contact-side eye softness, wink and shoulder release; planted support and smooth idle handoff pass the same review/checks.
- Dependencies: task 1; reuse established import/space. Per slice files: one sheet, `animations.py`, animation tests, prompt/QA record (4–5; medium).

### 7. Shoulder story and sleepy flop (two separate slices)

Description: peek both directions, yawn, close the mouth and hold `=_=` (6.4 seconds); separately flop, briefly sleep, wink, wake and rise (6.8 seconds).

- [x] Peek acceptance/verification: both glances and yawn/deadpan are readable in order; connected neck/jaw and planted paws pass source/runtime review and ordered-phase/deadline checks.
- [x] Flop acceptance/verification: sleep precedes wink/wake; supported rise precedes idle; this remains a pet state. Review occlusion/get-up and test the >5.8-second queued-pet/nap boundary.
- Dependencies: task 1 and shared deadline decisions. Per slice files: one sheet, `animations.py`, focused animation/behavior tests, prompt/QA record (up to 5; medium).

Checkpoint: native playback proves every expression beat remains visible and the body finishes recovering before the shared idle blink appears.

### 8. Remaining seated facial acting (one reaction per slice)

Description: refine head pats (2.8 seconds), chin scritches (3.0 seconds) and ear rubs (3.0 seconds), reusing clean body art and drawing missing face/contact/recovery passages.

- [x] Acceptance: forehead-down contentment, chin-up bliss and asymmetric ear/eye melt read as distinct actions without relying on the same smile; all three return smoothly to idle.
- [x] Verification: compare native light/dark previews side by side; per-reaction timing, scale and handoff checks pass.
- Dependencies: task 1. Per reaction files: one sheet, `animations.py`, animation tests, prompt/QA record (4–5; medium).

### 9. Complete previews and delivery validation (sequential slices)

- [x] Preview acceptance/verification: derive duration from clip length, include >=0.8 seconds of idle after recovery, sample every used pose, refresh full catalog/contact sheets and inspect at native/enlarged/slow speed. Files: preview tool, catalogs and QA record (medium; split generated outputs from tool edits).
- [x] Interaction acceptance/verification: all twelve appear in rotation; clicks count immediately with at most one pending reaction; longer clips finish before queued pets/naps; hiding/motion/drag/position behavior passes focused native checks, followed by full test discovery. Files: relevant animation/behavior/widget tests, QA record (up to 5; medium).
- [x] Release acceptance/verification: accepted tail/non-pet art and cadence compare with baseline; rebuild executable, pass required-asset and native packaged startup/single-instance checks, document actual results and remaining display limits. Files: QA/delivery records plus build output (small).
- Dependencies: tasks 2–8; previews/interaction checks before release build. Completed: full discovery passed (147 tests; two packaged checks then passed separately), final native playback covered all 280 pet pose entries, and the final fragment regression/related rendering checks passed. See `docs/petting-revision-validation.md`.

## Smooth twelve-reaction petting rebuild

- [x] Read the study, runtime/import/selection paths, callers, previews and tests; record acceptance criteria.
- [x] Generate/review cheek nuzzle and hop pilots using canonical idle identity.
- [x] Generate/review the remaining ten distinct sequences; revise paw/knead anatomy, stretch fit and chin/flop transparency.
- [x] Integrate calibrated full sequences, precise 20 FPS playback, shared idle endpoints and safe repeated-pet handoffs with regressions.
- [x] Inspect every source/runtime pose and transition, refresh catalogs and record individual QA.
- [x] Run full checks (142 passed), focused native checks, mutation and byte-preservation checks; build and pass both packaged checks plus actual falling-window startup probe.

## Startup drop-in and background-free thoughts

- [x] Reproduce delayed-first-tick and visible-fullscreen startup skips with failing tests.
- [x] Start the arrival clock when Qt can animate; preserve hiding, saved position and reduced motion.
- [x] Replace the thought panel with transparent text and a small glyph shadow; inspect native light/dark rendering.
- [x] Finish regression (134 passed), native rendering, mutation, build and bundle checks; record that cold EXE startup remains blocked by the running copy.

## Other-idle personality and readable thoughts

- [x] Read art/idle selection, dialogue dispatch, bubbles and tests; define scope and failing regressions.
- [x] Generate/review idle stories with entry/recovery; integrate and retire old runtime rows. Retain verified swish with a new blink; reject its proportion-drifting draft.
- [x] Add matching playful thought banks and improve bubble font, contrast and reading time.
- [x] Inspect every used pose, transitions and native thought bubbles; run checks.
- [x] Update previews/notes, rebuild and verify packaged startup.

## Tail duration, transitions and frequency

- [x] Set timing and selection acceptance criteria; write failing regressions.
- [x] Generate and inspect eight entry/recovery drawings; preserve accepted running poses.
- [x] Verify longer chase, cute handoffs, weighted selection and regression suite.
- [x] Refresh previews, build, validate packaging and record ideas for other idles.

## Direct GIF correction

- [x] Inspect all eleven GIF frames and their 50ms durations.
- [x] Replace the tucked-tail turning cycle with low running poses and an outward trailing tail.
- [x] Match the reference cadence at 20 FPS and preserve two/three turns.
- [x] Review runtime poses, regenerate previews, run checks and rebuild the executable. Source suite: 121 passed; packaged checks: 2 passed; native checks: 3 passed.

## Playfulness revision

- [x] Inspect the supplied reference GIF and both attached pose images; record revised scope.
- [x] Generate and inspect full-body tail-game, graceful arrival and sad farewell art.
- [x] Implement two/three turns, real monitor-edge arrival, and safe saved-position restoration.
- [x] Inspect animation and monitor-scene previews; run regression/native checks.
- [x] Rebuild executable, verify bundle and update art/verification notes. Fresh packaged startup now passes.

- [x] Read current art, playback, callers, tests and packaging references; record scope and acceptance criteria.
- [x] Generate replacement art and inspect every source frame; reject and redraw the tail-catch draft.
- [x] Implement and test lifecycle translation and pose endpoints.
- [x] Implement and test tail motion and rest transitions, including a fixed head anchor during swishes.
- [x] Inspect all runtime frames plus native-size/enlarged playback previews; correct defects.
- [x] Run regression suite, build executable and verify packaging, native Qt rendering and second-instance launch. Cold packaged startup deferred because the user's existing copy is running.
- [x] Update prompts, animation catalogs and final validation notes.
