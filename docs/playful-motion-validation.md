# Playfulness revision verification — 2026-10-21

## Direct attached GIF correction (current)

The user rejected the earlier tucked-tail movement and attached the actual reference GIF. It contains eleven frames at 50ms each, a 550ms turn. Every frame was inspected in sequence. The v4 tail sheet now follows its low curved running body, closed determined eyes, alternating paw contacts and long outward trailing tail. The cycle has eleven distinct runtime drawings, repeated twice for chase and three times for catch. Intro/recovery use five other source poses; total atlas entries remain 150.

Chase lasts 2.28s; catch lasts 3.34s, then rests for the remainder of the six-second idle slot. Tail playback alone uses a 50ms timer (20 FPS); walking and other ordinary gestures retain 100ms. The tail-only documentation GIF uses exact 50ms samples, so the reference cadence is visible without resampling to 30 FPS.

All used source silhouettes were reviewed for extra paws, tail continuity, complete extremities and the full turn. Review caught a tail tip crossing its nominal column: horizontal padding plus connected-silhouette extraction now retains it, with a common sampling scale across all cells. Arrival, goodbye, swish, petting and palm artwork are unchanged. The v3 tail sheet is removed from the bundle; v4 replaces it. Source art was produced using built-in ImageGen; scripts only extract/render runtime frames.

Native Windows checks passed for the new tail timer versus walking speed, all-state rendering, and uncut silhouette borders. An isolated in-memory mutation reverting the tail timer to 100ms made the new regression fail as expected; production files were untouched.

Current checks: 123 discovered tests, 121 passed and two packaging checks skipped during the source run; those two packaging checks subsequently passed against the rebuilt executable. Three selected native Windows tests passed. PyInstaller clean build and diff whitespace validation passed. No new physical multi-monitor run was performed.

![Corrected tail playback](neko-tail-reference-preview.gif)

## Earlier revision verification

Branch: `codex/animation-rebuild`. This revision supersedes the original one-turn/seated-catch and neutral-goodbye storyboards.

## Visual review

| Sequence | Inspection result |
| --- | --- |
| Tail cycle, source indices 0–7 | Eight compact stepping views progress right/front through rear and left back to front. Two initially ambiguous rear views were corrected through ImageGen. One continuous rump-attached tail; no duplicate forelegs observed. |
| Tail preparation/payoff, indices 8–15 | Notice/crouch, low pounce, two-paw catch, escape, head tilt and sitting recovery. Rear legs remain tucked/occluded where appropriate. No extra planted paws observed. Canonical idle replaces the first/last seated source candidates. |
| Chase and catch timing | Exact eight-view cycle repeated twice/three times respectively, without sitting between rotations. Chase 4.11s; catch 5.42s; both finish before their six-second idle slots. |
| Arrival, eight poses | Four-leg airborne reach, forepaw contact, hindpaw settling, compression, cheerful rebound and sit. Oversized tails were corrected through ImageGen. Row-boundary clipping of paws was caught in runtime review and fixed with padded source sampling. |
| Sad farewell, first two candidates | Mild downturned mouth/eyebrows, lowered ears and downcast second pose. No tears/text. Size remains close to seated idle. The other two source candidates are deliberately not imported. |
| Retained hop, six poses | Original crouch, push and airborne silhouettes remain; the existing arc now begins after the one-second sad pause plus 200ms crouch. |
| Runtime frames/scene | Reviewed the complete source contact sheet, translated lifecycle strip and sampled monitor-scene sequence. Whole-source silhouettes fit within transparent borders. Arrival enters across the monitor top, lands and recovers; farewell pauses, rises slightly and drops out. |
| Previous petting and palm behavior | All twelve head-size/anchor calibrations still pass. Native cursor checks confirm local hand animation, leave cancellation and reduced-motion/hide behavior. |

The source/runtime contact sheets are generated from the actual `SpriteAtlas`, not separate illustrative artwork. The monitor scene uses production `drop_progress` and poses at 112px. Generated anatomy remains a visual assessment; tests cannot prove that no perceptual anomaly exists.

## Automated and native checks

- `python -m unittest discover`: **122 tests run, 120 passed, 2 packaging checks skipped** pending the new executable.
- Ten selected tests with `QT_QPA_PLATFORM=windows`: **10 passed**. Covers real window movement, monitor-edge ink clipping, saved landing position, hide/motion/fullscreen/quit interruption, hop repaint, pet size, palm movement and cancellation.
- `python -m PyInstaller --noconfirm --clean main.spec`: **passed**; output `dist/DesktopNeko.exe`.
- `NEKO_TEST_EXE=dist/DesktopNeko.exe python -m unittest test_packaging -v`: **2 passed**, including new art/bundled modules, exclusion of retired art/credentials, real cold startup, tray/window initialization and clean rejection of a second instance. Only the launched smoke-test processes were stopped.
- Isolated in-memory mutation: replaced the landing-target preference save with `self.pos()`. The focused regression failed with airborne versus saved coordinates as expected. Production files were never mutated.
- `git diff --check`: passed.

Previews were rendered to a temporary directory and copied into docs after OneDrive intermittently rejected Pillow's direct read/write file opens. No generated-art pixels were modified by scripts.

## Remaining limits

No physical stacked-monitor or mixed-DPI multi-monitor run was available. Monitor-edge clipping and interruption are tested with native Qt on the current display; physical monitor arrangements remain the outstanding hardware check. The new executable is in the repository's dist folder; an older standalone Desktop copy is not overwritten automatically.
