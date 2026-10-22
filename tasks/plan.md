# Animation rebuild

## Reference-led lifecycle v2 — delivered, 2026-10-23

Implementation authorized by the user's “Well let's hope you don't disappoint this time.” Latest direction requires one graceful diagonal leap per action. Delivered reference-led key art, face-hidden review, connected poses, planted contacts and diagonal routes; prior release/provenance preserved. [Current evidence](../docs/lifecycle-v2-validation.md).

Final steering adds sad ears/eyes/head before a graceful exit pose: eight new expression/turn slots, then supported load/push and one diagonal leap. Departure20 selected entries/2.20s; arrival19/1.98s. Front sadness remains unmirrored until the authored turn.120 focused checks plus one final seam regression, four package checks, native coverage and2.209s local UI readiness are recorded; the flat release retains its verified predecessor.

User rejected the delivered visitor acting and supplied a video plus four motion-study images. Originals are preserved and indexed in [the motion library](../references/motion/README.md); Frame Master requires reference/support/spine study before any motion. [Revised plan](../docs/lifecycle-motion-v2-plan.md): side-biased reach → planted forepaws → spine fold/pelvis follow-through → gathered landing → supported recovery; departure look-back → hindquarter wind-up → planted hind push → stretched leap → tuck/reach → attached tail follow-through. Arrival has one landing and no second bounce; high departures use a nearer side. Technical verification remains separate from the user's judgement of appeal.

## Entrance and goodbye — delivered, 2026-10-23

User approved the research with “DO me proud.” [Original research/storyboards](../docs/arrival-goodbye-research.md) and [delivery, previews, correction and verification](../docs/visitor-validation.md). A curious supported lean replaces an uncomfortable hanging grip; entrance lands and recovers through 20 poses/2.15s. Goodbye uses a drawn slow blink and actual window travel through 16 poses/1.8s. The original undersized recovery was redrawn and calibrated as a separate batch. First-tick timing, resting origin, prompt close and build-time baking are preserved. All 741 previous frames/63 unrelated clips remain identical. Older open work below is preserved.

## Startup correction — 2026-10-22

Profile before changing behavior; move proven source-sheet preprocessing into the release build, retain source fallback and compare every final frame exactly. Measure actual executable UI readiness before/after, check packaged contents/icon/instance handling and preserve the verified immediate predecessor. [Evidence and limits](../docs/startup-performance-validation.md).

## Gallop/timer/sleep correction — authorized, 2026-10-22

Delivered: [fixes, previews, focused verification and release identities](../docs/run-timer-sleep-fix.md). Extended play-testing remains with the user as requested.

User requests a fast fix with focused checks, leaving extended play-testing to them. Use the supplied eight-frame100ms gallop as the mechanics reference, preserving Neko's identity and scale. One12-slot bank: neutral calibration; eight connected gallop poses (hind load/push, gathered ascent, reaching flight, full extension, fore contact, yielded support, hind gathering, hind load); three supported braking/turn poses ending near-front. Keep drawn excited squeezed eyes across the first four poses (360ms at90ms/pose), then reopen for landing/support across four poses. One720ms loop; only airborne flight poses receive small fixed5/8px registration offsets. Ground contacts stay planted; no face glyphs or per-pose scaling. Preserve jump/contact and outcome artwork. Review one native-size light/dark strip and short production-timing GIF, run focused timer/sleep/atlas regressions, build flat current/previous releases and inspect resources. Broad native play-through/full suite intentionally deferred to the user.

## Cursor play v2 — approved, 2026-10-22

The user approved the [complete v2 design](../docs/cursor-play-v2-plan.md). Delivery and verification are complete: [final report, previews and release](../docs/cursor-play-v2-validation.md). Unrelated open work below is preserved.

Native-size source review found the new loss endpoints look down, whereas the retained curl/comfort looks outward. The implemented eight-slot common bridge uses neutral calibration; lowered curled hold; ears lifting; head tilting outward; chin rising; and settling into the actual curl. Seven used drawings at 120ms each play after each complete loss and before the retained curl loop. Ground/support stays fixed, hidden legs remain tucked, forepaws support the chin and one tail wraps the haunch. All three entry seams, actual curl endpoint, existing comfort/carry and actual native-painted entries are verified in the final report. The prototype is now tested practice recorded in Frame Master.

## Catch the Cursor — dedicated planning revision, 2026-10-22

Status: implementation subsequently authorized and delivered. See [verification](../docs/catch-validation.md) and [Catch the Cursor](../docs/catch-the-cursor-plan.md). Automatic play defaults on at a configurable 90s interval, running is horizontal only, jumps use measured reach, one genuine contact wins, unreachable play/timeouts lead to a disappointed curl until petted, and bounded/coalesced intents protect naps and complete transitions.

Delivery order: lateral geometry/contact trial → one complete hunt art path → manual playable slice → native checkpoint → full win/loss/comfort art → bounded scheduler and settings → interruption/accessibility/release checks. Eight-direction locomotion and Dodge's click-interception trial are not dependencies of this revised first game. The user requested only this plan and the thought-backdrop implementation today.

Thought backdrop: implemented as a compact rounded, click-through frosted label, keeping sharp text and existing timing/quiet rules. See its [verification](../docs/thought-backdrop-validation.md). Catch the Cursor now has its own runtime and artwork; other games remain proposals.

## Mini-games — proposed, 2026-10-22

Status: Catch the Cursor subsequently implemented under its dedicated design; the remaining portfolio is research/planning only. See the [complete mini-games design](../docs/minigames-plan.md) for the other games and candidates. Previous completed work remains below.

Recommendation: Catch the Cursor (Neko hunts), Run Away / Kitten Tag (player pursues) and Dodge Clicks (aim/timing), followed by Yarn Rally and then Peek-a-Box. Prototype native transparent click ownership and directional movement before producing full game art. Zero-alpha desktop regions normally pass clicks through; Dodge must not ship until in-area misses can be consumed and outside input/teardown are verified.

Dependency order: input feasibility trial → directional run/turn/contact trial → complete Catch slice → compatibility checkpoint → Run Away slice → gated Dodge slice → distinctness/accessibility checkpoint → native/source/packaged release proof. Pointer-only games can proceed if the click-input trial fails; click games remain deferred. See the new section in [the task list](todo.md) for concrete acceptance checks.

Preserve current 192 × 144 canvas/character scale, accepted tail/pet/pickup sequences, nap/pet counts, saved home and background-free thoughts. Use explicit finite opt-in sessions; no new dependency, permanent mouse recorder or progression economy. All proposed timings/frame budgets require prototype/play-test validation. This plan makes no new claim about verified animation practice.

## Pickup animation — approved, 2026-10-22

Status: approved and implemented. Final source, native and packaged checks pass; see [verification](../docs/pickup-validation.md). The delivered build is `dist/pickup-qol/DesktopNeko.exe`. Previous completed plans are preserved below.

The full [pickup design](../docs/pickup-animation-plan.md) defines the storyboard, input/state rules, pose budgets, release/cancel behavior, dependency-ordered slices and acceptance matrix. [Frame Master](../framemaster.md) records the verified production method, and root `AGENTS.md` directs animation work to consult and maintain it.

### Goal and decisions

Turn existing click-hold dragging into a suspended kitten performance. Preserve quick-click petting and drag counts/nap rules. Crossing the normal drag distance starts pickup immediately; a stationary hold starts at a proposed 250ms. Awake mood targets are excited 0–3s, calm 3–10s, mildly unimpressed 10–20s and sleepy thereafter. These share compatible body phases, keep the pointer hotspot fixed and progress by elapsed time rather than mouse events. A pre-existing nap remains a nap during quiet carrying.

Release interrupts every lift/loop/expression phase on the next nominal 50ms update and connects through drawn lowering/contact/recovery to canonical idle at the user's chosen location. Early release, mid-yawn and re-grab need explicit bridges. A real sleeping kitten returns to appropriate supported nap/wake transitions. No fixed long film may delay release.

Measure the tall pose at canonical scale first. Increase fixed transparent vertical space only if necessary; preserve saved visible origins, tray crop, click-through padding and old positions. Separate logical resting placement from temporary drawn lift so saving during hold cannot store an airborne offset.

### Ordered slices and checkpoints

1. Prove held silhouette, opposite sway extremes, mid-lift and contact; document measured canvas/anchor decision.
2. Author one complete calm entry/loop/release path, including all phase connections and full idle recovery.
3. Import/calibrate it and update previews; implement any measured canvas compatibility separately.
4. Add click/hold/drag ownership, arbitrary release and re-grab; prove awake starting posture-family bridges.
5. **Checkpoint A:** native calm pickup → carry → set-down is complete, stable and interruptible before expanding artwork.
6. Author excited, mildly unimpressed and sleepy variants plus drawn expression bridges, one mood per small slice.
7. Connect monotonic mood progression without resetting body phase; release during every bridge/yawn.
8. Finish real-nap/timed-wake rules and desktop cancellation/save paths in separate slices.
9. **Checkpoint B:** full source regression and native interruption matrix pass.
10. Render complete previews/contact sheets, update provenance/Frame Master/README and verify a fresh executable.

Detailed acceptance, file scopes and dependencies are in the full design and [working checklist](todo.md). No new dependency, settings panel, background thought panel, sound library or physics system is proposed.

### Risks and unresolved measurements

Tall silhouette bounds, final frame budgets, timing thresholds and posture-family bridge count require prototype evidence. Highest risks are geometry drift between mood variants, release from mid-yawn or side-lying poses, temporary offsets leaking into saved positions and held drowsiness interfering with real naps. Native DPR 1.0 can be checked locally; physical mixed-DPI/multi-monitor behavior needs appropriate hardware and must otherwise remain an explicit limit.

---

## Petting revision: readable acting, expressions and complete recovery

Status: approved and implemented, 2026-10-22. The user reviewed the plan before authorizing artwork/runtime changes. See [final per-reaction verification](../docs/petting-revision-validation.md) and [native/release measurements](../docs/petting-revision-native.json). The delivered build is `dist/expressive-petting/DesktopNeko.exe`. Earlier implementation/validation records below describe preceding revisions.

### Goal and design decisions

Make all twelve pet reactions readable at desktop size, with individual physical actions, facial acting and a complete return to the idle kitten. Replace Tiny blep with a playful roll. Preserve the accepted tail animation as the cadence/continuity reference. Use the existing atlas, per-pose timings, precise 50 ms pet repaint timer and bounded pending-click behavior; add no dependencies or settings.

The current paw offer/nuzzle are each 1.72 seconds; front stretch/arch are 2.45/2.46 seconds; hop is 1.51 seconds. These totals leave too little room for anticipation, an expressive action and recovery. Extra time must contain deliberate motion, readable expression holds and physical settling, rather than merely displaying one drawing for two more seconds. Connecting drawings need the same pose-to-pose care as the tail chase, although a relaxed gesture should have its own slower rhythm.

### Proposed timing and pose budgets

Durations include entry and final seated settling. They are storyboard targets to tune against native-size playback. Pose budgets count unique source slots including endpoints, not the number of 50 ms repaints; repeated kneading cycles reuse a reviewed cycle. Allocate more drawings where joints change direction or overlap, rather than filling a quota. Do not force every action into the old 12/16-slot sheet layout.

| Reaction | Current | Target | Source-pose budget | Character/expression |
| --- | ---: | ---: | ---: | --- |
| Head pats | 1.53 s | 2.8 s | 12–16 | Soft forehead dip; half-lidded contentment and slow blink. |
| Cheek nuzzle | 1.72 s | 3.7 s | 16–20 | Affectionate cheek press; contact-side eye softens, then a little wink. |
| Kneading | 2.98 s | 5.8 s | 20–24 | Four clear left/right pairs; relaxed, absorbed half-lidded face. |
| Chin scritches | 1.87 s | 3.0 s | 12–16 | Chin-up bliss; closed eyes, tiny relaxed mouth and slow release. |
| Playful roll (replaces blep) | 1.73 s blep | 5.8 s | 24–32 | Excited invitation, belly-up curiosity, playful eye squeeze. |
| Paw offer | 1.72 s | 3.6 s | 16–20 | Tentative/hopeful look; offered paw, small beckon, wink. |
| Ear rubs | 1.84 s | 3.0 s | 12–16 | One eye closes on the rubbed side; asymmetric ear melt and recovery. |
| Front stretch | 2.45 s | 5.2 s | 20–24 | Eager/excited effort during the reach; relaxed face during release. |
| Back arch | 2.46 s | 4.9 s | 20–24 | Comfortable effort, then half-lidded relief; no frightened puff-up. |
| Tiny hop | 1.51 s | 5.0 s | 28–36 | Three connected hops; excited squeezed eyes, open eyes on contact. |
| Side flop | 2.87 s | 6.8 s | 24–28 | Brief sleep, one-eye wink, drowsy waking and supported get-up. |
| Shoulder peek | 1.82 s | 6.4 s | 24–28 | Curious left/right looks, a full yawn, then a readable `=_=` face. |

Expression glyphs describe the acting, not literal text painted over the face. Keep the canonical eye spacing, head volume, ear shapes and mouth placement. A wink, relaxed lids and excited eye squeeze must remain distinguishable at the actual displayed size. Closed eyes alone do not make every emotion the same: ear angles, mouth, posture and timing carry the distinction too.

### Individual storyboards

1. **Paw offer — 3.6 seconds.** 0.0–0.6: notice the pet, shift weight onto the supporting foreleg and lift the other forepaw. 0.6–2.2: reach toward the viewer, pause long enough to see it, curl the wrist in one small beckoning motion and wink. 2.2–3.1: uncurl/retract the same paw, place it down and redistribute weight. 3.1–3.6: settle into the actual idle. Keep one supporting foreleg and one offering foreleg throughout; the old grounded position of the moving paw must disappear.

2. **Cheek nuzzle — 3.7 seconds.** 0.0–0.6: eyes/ears lead a little tilt toward contact. 0.6–2.3: lean into the imagined hand, visibly press the cheek, make a small curved cheek rub and soften the contact-side eye. 2.3–3.2: ease pressure, give a little wink and retrace the neck/shoulder movement. 3.2–3.7: shoulders/head settle into idle. Keep the paws planted; do not turn this into a whole-body side-to-side sway.

3. **Playful roll — 5.8 seconds.** 0.0–0.7: lower the shoulder with an eager look. 0.7–1.8: tip onto one side with the paws beginning to tuck. 1.8–3.6: roll across the back with a brief belly-up pause, a small wriggle and excited/curious expression changes. 3.6–5.2: continue onto the other side, plant a forepaw, gather the hindlegs and push back up. 5.2–5.8: seated recovery. This is an active side-to-back-to-other-side roll, with no sleeping beat; the flop below owns the sleepy acting. Use a limb-visibility map for every turning pose: exactly four anatomical legs, with hidden legs occluded rather than added as extra paw shapes. Keep the tail attached and let it follow the rolling pelvis.

4. **Front stretch — 5.2 seconds.** 0.0–0.8: rise from sitting and plant the hindfeet. 0.8–1.9: walk/reach the forepaws farther forward as the chest lowers and hips remain high. 1.9–3.5: deepen the bow with excited effort, spread the toes and add one small farther reach; soften the face as the stretch releases. 3.5–4.6: bring the forepaws back, lift the chest and fold into sitting. 4.6–5.2: relaxed seated settling. Draw the extended spine, shoulders and forelegs explicitly; no whole-image stretching, head shrinking or forced frontal angle that hides the reach.

5. **Back arch — 4.9 seconds.** 0.0–0.8: rise onto four grounded paws. 0.8–1.8: round the back progressively, with the head lowering and tail following. 1.8–3.2: reach the comfortable high point, make a small weight shift through the shoulders and show effort changing to relaxed lids. 3.2–4.3: unroll the spine and lower into sitting. 4.3–4.9: settle. The front paws stay near their original support positions, making the silhouette clearly different from the forward-reaching bow. Preserve connected hips, normal fur and comfortable ears.

6. **Tiny hop — 5.0 seconds.** 0.0–0.6: excited look and crouch. 0.6–1.5: first small hop. 1.5–2.6: a slightly bouncier second hop. 2.6–3.5: a smaller third hop. 3.5–4.4: absorb the last landing, recover balance and sit. 4.4–5.0: seated settling. Every hop has its own push-off, readable airborne silhouette, descending contact and compression. Landings feed the next anticipation without idle snapping between hops. Vary height/timing subtly; do not replay one identical hop three times. Excited eyes lead takeoff; open eyes briefly clarify the landing.

7. **Kneading — ground-up remake, 5.8 seconds.** 0.0–0.7: lean into a low, comfortable stance with the hindquarters stable and both forepaws visible. 0.7–4.5: four left/right kneading pairs, approximately 0.95 seconds per pair. Each pair shows left pressure/right release, a neutral weight transfer, then right pressure/left release. Use shallow paw lifts, soft wrist flexion and a small corresponding shoulder movement. 4.5–5.3: both paws settle, shoulders rise and the torso returns to sitting. 5.3–5.8: idle settling. Keep a relaxed, almost absorbed expression. No crossed forelegs, floating replacement paws, head pumping or disconnected arm shapes. Start with one clean, anatomically legible pair before extending it into the full sequence.

8. **Shoulder peek — 6.4 seconds.** 0.0–1.3: eyes and ears lead a glance over one shoulder, then pause. 1.3–2.7: turn smoothly through center to the other shoulder and pause there. 2.7–3.2: face forward and droop slightly. 3.2–4.5: open into a full yawn, with closed eyes, then close the jaw. 4.5–5.4: hold the requested sleepy/deadpan `=_=` expression. 5.4–5.9: gently restore the neutral head/ear posture. 5.9–6.4: idle settling. The head turns within believable neck limits; the shoulders follow a little, while the paws stay planted. Give the jaw opening and closing actual connecting drawings.

9. **Side flop — 6.8 seconds.** 0.0–0.9: ease the hip and shoulder to the floor. 0.9–2.5: close both eyes for a tiny snooze, with one subtle breathing cycle. 2.5–3.1: open one eye in a deliberate sleepy wink/peek. 3.1–3.7: wake and lift the head. 3.7–5.1: plant the forepaw, gather the legs and push upright. 5.1–6.2: unfold into the seated posture with a drowsy blink. 6.2–6.8: idle settling. This remains a pet reaction, not the real nap state; pet-count, nap timers and pending clicks must not treat the pretend snooze as actual sleep.

10. **Remaining seated reactions.** Head pats: accept contact, gently compress/dip, melt into half-lidded contentment, lift back and slow blink. Chin scritches: present the chin, relax the mouth/eyes during contact, then lower the connected neck/head gradually. Ear rubs: tilt toward one ear, soften that ear and eye asymmetrically, then let the ear perk before the head centers. Reuse clean body drawings where suitable and add only the expression/contact/recovery drawings each needs. Their identity comes from forehead compression, upward chin extension and asymmetric ear response respectively.

### Shared scale, space and transition contract

- Compare each reaction with the actual idle, not with another newly generated reaction. Keep the existing physical head/body scale and one fixed sequence calibration; changes in projected width during turns are natural. Do not normalize every pose to an identical bounding box.
- Start/end on the canonical idle. Draw the complete physical recovery before using the shared seated blink. The current unconditional penultimate-blink substitution is not sufficient when the preceding torso/head is still bent, airborne or lying down. Verify that adjacent poses already match the seated geometry.
- Grounded contacts retain their desktop ground line. A roll uses shoulder/hip support, a knead uses alternating forepaw pressure, and a hop uses deliberate airborne height; do not use a single lowest-pixel landmark that causes a rotating body/tail to drag the kitten vertically.
- Test the deepest stretch, widest roll and highest hop at the retained idle scale before finishing their sheets. The present 112 × 112 canvas may be restrictive. If their genuine silhouettes need more room, extend the transparent drawing area with a stable world-space body anchor. Do not shrink the kitten or hide its extension to pass the old canvas test. Any expansion must also preserve saved visible position, dragging, click targets, bubble placement and screen-edge handling; keep it constant during playback so the desktop window does not jitter with every pose.
- Use short connecting drawings and deliberate expression/contact holds. Longer holds include restrained breathing, pressure shifts or tiny paw/ear motion where appropriate. Keep movement readable rather than constantly wiggling every body part.
- Review the final-to-idle handoff and every loop seam at normal speed and slowed playback. No teleport, unrelated blink, tail snap or instant smile at the end.

### Scope and dependency map

Approved storyboard/face reference -> high-risk pose-space trials -> dedicated replacement art -> atlas/timing/state mappings -> runtime checks -> complete previews -> packaged validation.

Artwork: the twelve dedicated pet sheets; replace the blep sheet/runtime entry with a roll. Keep historical art recoverable in Git. Accepted tail and non-pet artwork/cadence remain the regression reference.

Runtime: `animations.py` (pose layout, registration, ordering and timings), `behavior.py` (rolling state and pet selection), `main.py` (mapping, description and measured clip deadline). Keep the twelve-item rotation; roll occupies blep's slot. Search all BLEPPING/blep references, including descriptions, tests, preview lists and required packaged assets. State enumeration is not a persisted animation selection, but verify preference loading before removing its old name.

Timing: the widget currently replaces the behavior's 5.8-second provisional duration with the actual clip sum. Check that longer clips use their true deadlines throughout queued handoffs and behavior ticks. Replace obsolete 5.8-second test assumptions with explicit approved clip budgets/completion checks. Do not simply enlarge every timeout indiscriminately or introduce a second timing system.

Supporting paths: `test_animations.py`, `test_behavior.py`, `test_main.py` and existing native probes, `test_packaging.py`, `tools/preview_animations.py`, catalog/QA/prompt records. Locate the specific test callers before each implementation slice. No new dialogue system, menu, setting or rendering dependency.

### Ordered implementation slices and checkpoints

Detailed executable tasks and acceptance/verification steps are in `tasks/todo.md` above the completed history.

1. Lock native-size expression studies and high-risk key poses; settle whether more transparent drawing room is necessary.
2. Implement the roll as one complete vertical slice, replacing blep everywhere it is selectable/displayed/packaged.
3. Remake kneading as one readable pair, then four pairs with entry/recovery. Checkpoint: inspect roll/knead source and runtime playback before producing the remaining full sheets.
4. Extend front stretch, then back arch, using the agreed scale/space contract.
5. Build the three-hop story and validate each launch/landing. Checkpoint: inspect all three body reactions against the accepted tail's continuity.
6. Extend paw offer and cheek nuzzle with their contact/expression/recovery stories.
7. Build the two-direction peek/yawn/deadpan and sleepy flop/wink/wake stories. Checkpoint: check expression order and complete recovery in native playback.
8. Refine head pats/chin/ear reactions so all twelve have distinct facial acting and adequate recovery.
9. Validate the complete rotation, render full-length previews, run the regression/native checks, rebuild and verify the executable. Record results and remaining physical-display limits honestly.

### Acceptance and verification

- Review every source pose and imported pose, plus every adjacent pair in playback. Reject extra/missing anatomical parts, detached tails, stray paw remnants, eye duplication, mouth drift and opaque background haze. Occluded limbs need a consistent visibility map; counting four visible paws is not a valid anatomy rule.
- Verify exactly three launches/landings for hop, four complete left/right pairs for kneading, both shoulder directions followed by yawn/closed jaw/deadpan, and side flop's sleep -> wink -> wake -> supported rise order. Rolling must visibly pass through both sides and belly-up.
- Inspect actual desktop size on light/dark surfaces, then enlarged/slowed playback for joint continuity. Faces must read without zooming; zoomed anatomy checks alone cannot establish that.
- Assert complete finite clips, consistent timings/order, actual idle endpoints, retained body scale, intentional ground contacts and transparent margins. Update shape/count assertions to the reviewed artwork; do not loosen anatomy/scale checks merely to accommodate a failed draft.
- Exercise repeated petting throughout the longest clips. Every click counts and gets immediate palm feedback; at most one reaction waits, and it starts only after the current recovery. Verify nap deadlines, hiding/showing, motion disabled, dragging, quit and startup still behave correctly. Include a pure behavior/widget deadline check beyond 5.8 seconds.
- Every preview must include idle before the action, the entire action and at least 0.8 seconds of live idle afterward. Derive preview length from the longest clip; the current fixed eight-second catalog may truncate the new flop/peek. Check that every used pose is sampled.
- Compare accepted tail/non-pet art and cadence with the baseline. Run focused checks during slices, full discovery once integrated, then PyInstaller and both opt-in packaging checks. Native runtime playback and packaged cold-start checks are required before declaring delivery.

### Risks and remaining design questions

The roll's occlusion and kneading's alternating support are the highest anatomy risks, so they are the first complete trials. Deeper extensions may require more transparent space; resolve this from actual silhouettes, not a premature canvas size promise. Longer reactions increase queue waiting, so keep the existing one-pending limit and immediate cursor response. Generated drawings can drift between poses; reject/regenerate the affected passage rather than hide it with image distortion or a long static hold. Timing/pose budgets remain adjustable after preview, while the requested story beats, counts, expressions and idle-size consistency are acceptance requirements.

## Twelve smooth, distinct pet reactions

Implement the approved [motion study](../docs/petting-motion-study.md). Generate dedicated sequences from the canonical idle identity, starting with cheek nuzzle and tiny hop, then complete all twelve. Use 8–16 source drawings per reaction, shared idle endpoints, consistent head calibration, planted-paw registration and 50 ms pet repaints. Give large actions drawn entry/contact/recovery and give every gesture its own rhythm. Retain the accepted tail artwork and cadence.

Verify each source pose and every adjacent handoff at native and enlarged sizes. Add regression checks for shared idle endpoints, full-sequence scale/clipping, finite motion, normal blink after settling, and repeated clicks that wait for a safe return instead of cutting through an airborne/lying pose. Keep the twelve-item shuffled rotation, sleeping/waking, reduced motion, palm cursor and background-free thoughts intact. Refresh runtime catalogs, record exact prompts and per-reaction QA, run the regression/native checks, then rebuild and inspect the executable.

Completed: [per-reaction QA and verification](../docs/petting-rebuild-validation.md). All twelve are integrated; the final build is `dist/petting-qol/DesktopNeko.exe`.

## Startup and text-only correction

Start the drop-in clock on the first animation tick, cover delayed and visible-fullscreen launches, and safely finish if fullscreen hiding or monitor changes interrupt arrival. Replace the cream thought panel with transparent, shadowed lettering while retaining wrapping, reading time and quiet controls. Verify native rendering, lifecycle regressions and the bundled source; deliver under `dist/updated` while the old executable is running. See [verification](../docs/startup-thought-validation.md).

## Personality for all other idles and readable thoughts

Rebuild grooming, stretch, loaf, sniff, ears, lazy swish, yawn, sleepy peek and directional looks as small stories with drawn entry/action/recovery. Three 4-column/6-row sheets supply eight drawings per action (directional looks share left/right alternatives). Keep the accepted tail games, pet reactions and lifecycle artwork. Retire replaced source rows from runtime import. Every spontaneous idle attempts an action-specific offline thought, subject to existing quiet/fullscreen/bubble/cooldown rules. Increase bubble font to 16px semibold, width to 270px, dark text/cream fill/clear border and reading time to 5.5–10s. Review each used pose and handoff, test state/line/visibility behavior, inspect actual bubble rendering, regenerate catalogs and rebuild.

## Longer chase and frequent special idles

Make chase longer than catch while preserving the accepted 50ms running poses. Chase takes five turns and catch two; both gain a drawn eager lean/crouch entry and a relaxed half-sit/blink recovery. Target 4.69s versus 3.68s, inside existing six-second slots. Generate eight transition poses without redrawing the running cycle. Give each tail game three times the ordinary idle selection weight, preserving no consecutive repeats and all other idles. Review anatomy/scale/handoffs, exercise selection and timing, regenerate previews and rebuild. Other-idle ideas are suggestions for the user, not additional animation changes in this revision.

## Playfulness revision requested after review

The user supplied a crouched tail-chasing GIF and a graceful cat landing reference.
The new acceptance criteria supersede the earlier seated tail trap and neutral departure:

1. Tail chase uses two full compact turns; tail catch uses three, followed by a crouched pounce/catch and recovery. After the direct GIF correction, use its eleven 50ms running poses: low stretched body, closed eyes, alternating scrambling paws and long tail trailing outside the turn. One attached tail and four anatomical legs; no sitting interruption between turns.
2. Arrival actually travels from above the target monitor's top edge to the saved position. New airborne/contact/compression/rebound poses add kitten playfulness. Position saves, hide, reduced motion, fullscreen and quit must never persist an intermediate airborne position.
3. Departure immediately shows a small sad expression and lowered ears before crouching. Preserve the existing accepted hop-down drawings and arc. No guilt text is added.
4. Inspect source drawings, actual-size runtime playback, complete turns, and a monitor-scene drop preview. Keep the new pet-size calibration and palm behavior intact. Run regression/native rendering checks, rebuild and inspect the executable.

Implementation order: generate three small sheets (tail game, arrival, sadness); test flight/persistence and spin counts; integrate; inspect and correct; update previews/notes; build and validate.

Completed: [revision verification](../docs/playful-motion-validation.md). The packaged cold-start and second-instance checks now pass as well.

## Earlier rebuild record

Rebuild arrival, departure, tail chase, tail catch and tail swish while retaining Neko's identity and existing interaction rules. Authorized for planning and implementation together; checkpoints are reviewed during execution.

Completed. See `docs/animation-rebuild-validation.md` for results and the fresh packaged-startup check that remains deferred while the user's existing Neko is running.

## Scope and dependencies

Generated sprite sheets -> atlas import and per-frame timing -> lifecycle translation -> desktop rendering -> tests -> documentation previews -> packaged executable.

Touches assets, animations.py, main.py, focused animation/desktop/packaging tests, README.md, Plan.txt and animation catalogs. No new dependencies, settings, AI changes or pet reactions.

## Ordered work

1. **Art and storyboards.** Generate transparent sheets using the existing seated kitten as reference. Arrival: fall/contact/compress/recover/sit. Departure: glance/crouch/push/arc/fall. Tail chase: notice/turn/one circle/settle. Tail catch: notice/reach/pin/escape/recover. Swish: small tail motion then rest. Inspect every frame before integration; reject duplicated limbs, detached tails, missing body parts and inconsistent head volumes.
2. **Lifecycle slice.** Import replacement art at a consistent scale, separate jump translation from poses, finish arrival on the normal idle drawing, finish departure fully invisible. Test continuous movement, contact, endpoints, reduced motion, hide/show and cleanup without moving the saved window position.
3. **Tail slice.** Replace both tail games and the basic swish. Avoid repetitive uniform motion, finish in the normal seated pose, preserve the twelve-pet rotation and idle slots. Test timing, frame completeness and pose endpoints.
4. **Visual and release verification.** Produce full source-frame contact sheets, native-size and enlarged runtime contact sheets and GIFs, inspect all of them, run unittest discovery, build with main.spec, inspect archive contents and run native packaging smoke checks when no existing Neko prevents them. Update art notes and catalogs with actual behavior, prompts and verification limits.

## Acceptance criteria

- Exactly one head, one torso, four anatomical limbs total and one attached tail. Hidden limbs stay hidden; a moving paw replaces its original position.
- Constant scale through crouch and rotation; no sudden enlargement, unrelated face change, sheet bleed or accidental crop. Lifecycle clipping happens only at the viewport boundary during entry/exit.
- First/last visible rest matches idle. Flight accelerates and follows a readable arc; anticipation and recovery hold longer than travel poses.
- Quiet/reduced-motion/fullscreen/hiding/quit and single-instance behavior remain covered by tests.
- Inspect source art AND the runtime output: numerical tests cannot certify anatomy. Revise rejected frames through ImageGen, never hide an anatomy defect with a passing test.

## Risks

Generated art can drift anatomically; use simple silhouettes and targeted regeneration. Automatic bounding boxes can shift the body when the tail moves; inspect anchored frames and use consistent sequence scale. Continuous jump translation must not alter saved desktop coordinates. Existing art remains available in Git for rollback.

## Validation commands

`.venv/Scripts/python.exe -m unittest test_animations -v`

`.venv/Scripts/python.exe -m unittest discover -v`

`.venv/Scripts/python.exe -m PyInstaller --noconfirm --clean main.spec`

`NEKO_TEST_EXE=dist/DesktopNeko.exe .venv/Scripts/python.exe -m unittest test_packaging -v`

## Catch the Cursor — implementation authorized, 2026-10-22

Deliver the dedicated proposal: manual menu/nook play, automatic games enabled at a persisted 90-second default (30–600 seconds), lateral runway, committed paw-contact jumps, three-hop win, protest/loss curl and deliberate-pet comfort. Use a bounded game intent and coalesced existing activity categories; revalidate eligibility rather than replay stale poses.

Scope: games.py controller/geometry; behavior.py ownership; animations.py and new authored assets; main.py menu/settings/input/lifecycle; focused game/integration/package tests; actual-controller previews; provenance, verification, README and Frame Master. Existing nap/pet/carry counts, saved origin, accepted tail artwork and animation scale are compatibility gates.

Storyboard: idle → attentive ready (1.4s) → supported side run/turn → crouch (0.2s) → committed reach/landing (0.6s) → puzzled miss/retry or proud grasp → retained reviewed three-hop celebration → walk home/sit. Continuous unreachable play gets one protest and safe attempt, then ears/head lower → supported curl/breathe until comfort. Pet: acknowledge → eyes reopen → uncurl/rise → canonical idle. Curl pickup uses the existing quiet side-entry bridge and returns to disappointed curl without creating a nap. Four anatomical limbs with occlusion, stable head volume, a single attached tail. New source banks use constant batch calibration; review all selected poses on light/dark and native playback.

Verify geometry/contact and scheduler first, one full manual path next, then outcomes/automatic scheduling/interruption and exact executable. Do not substitute rotating tail-chase art for a lateral run. No pointer warp/capture, global input hook, new runtime dependency or other mini-games.
## Current proposal: playful idle cursor interaction v2 — awaiting approval

The user requested a thorough plan before any v2 gameplay/art changes. Read [the complete v2 proposal](../docs/cursor-play-v2-plan.md): replace walking and remove idle cursor-following; playful run/jump acting; three victory and three loss stories; sparse varied lines; remove the game overlay; default-90s cooldown arms a fresh left/right side-zone entry outside care space; actual staged 3/2/1 countdown; defer through sleep and wake recovery; persist played/Neko-win keepsakes in the ordinary menu/nook. All new animation/geometry numbers are proposed trial targets, not tested findings.

Order after approval: V0 remove the play overlay → V1 invisible invitation/countdown → V2 walk/follow removal → V3 playful run/jump/contact → native review checkpoint → V4 outcomes/dialogue → V5 keepsake counters/menu copy → V6 verification/release. Existing release and historical findings remain the baseline. Startup repair and supplied-icon adoption are separately authorized maintenance, not approval to implement v2.
