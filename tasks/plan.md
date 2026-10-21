# Animation rebuild

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
