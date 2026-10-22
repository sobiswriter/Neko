# Twelve smooth petting reactions — 2026-10-22

Historical record of the first rebuild. The [later expressive revision](petting-revision-validation.md) supersedes its timings, pose counts and handoff policy. Linked catalog images now show the current revision.

![All twelve reactions at production timing](neko-pet-catalog.gif)

[All imported poses](neko-pet-frames.png) · [First six](neko-pet-frames-a.png) · [Last six](neko-pet-frames-b.png) · [Native light/dark rendering](neko-petting-native.png)

## What changed

All twelve pet reactions were rebuilt from the [motion study](petting-motion-study.md), using the actual idle kitten as the identity reference. Twelve dedicated sheets provide 160 source pose slots. The runtime atlas now has 307 entries: 147 preserved non-pet entries plus 160 pet slots. Each pet sequence shares the exact canonical idle at its start/end and the existing seated blink immediately before its final idle.

The old four-frame pet rows are no longer loaded. Their files remain as historical source/reference material. No retired wave or malformed paw row enters playback. No new reactions were added to the twelve-item rotation.

Pet rendering uses a 50 ms precise Qt timer. Connecting drawings typically hold for 60–150 ms, with longer contact/rest holds selected for each action. Each reaction finishes at its own clip deadline, then resumes normal idle blinking instead of remaining frozen for the old 5.8-second slot. Kneading uses three finite alternating cycles rather than an endless neutral-to-smile loop.

## Individual sequences and review

The table describes the accepted runtime sequences. Counts include shared seated endpoints/blink; duration includes the final seated hold. The pose sheets expose every slot, including the shared frames, in source-index order. Playback order is chronological except for the deliberate three-cycle kneading section.

| Reaction | Slots | Duration | Distinct motion, recovery and review focus |
| --- | ---: | ---: | --- |
| Head pats | 12 | 1.53 s | Forehead rises toward contact, dips under a gentle pat, releases and makes a smaller contented dip. Forepaws stay grounded. Reviewed head volume, downward movement and the return through the actual idle blink. |
| Cheek nuzzle | 12 | 1.72 s | One-sided cheek lean/press, with a small shoulder follow and release along the same path. Reviewed planted paws and the head arc; it does not rock repeatedly from side to side. |
| Kneading | 12 | 2.98 s | Shoulders lean forward and the existing left/right forepaws alternate pressure for three cycles. Both paws then settle and the torso sits back. The source was revised to clarify floor-level pressure and remove ambiguous extra-paw readings. |
| Chin scritches | 12 | 1.87 s | Nose lifts, neck extends and the chin presents upward, followed by a gentle lowering. Distinct from the forehead-down head pat. A fresh redraw replaced the hazy-background draft. Reviewed the neck connection and seated paws. |
| Tiny blep | 12 | 1.73 s | Small tongue peek, soft blink, retraction and shy head angle. The body stays quiet so the mouth movement reads at desktop size. Reviewed tongue retraction and face consistency. |
| Paw offer | 12 | 1.72 s | Weight shifts onto the supporting forepaw; the same opposite foreleg lifts, offers forward, withdraws and returns to the floor. Revised to leave clear space where the lifted foreleg's grounded version used to be. Reviewed the shoulder/wrist connection throughout the raised-paw passage. |
| Ear rubs | 12 | 1.84 s | One ear softens as the head tilts into contact, then perks again during recovery. The other ear stays more upright. Reviewed asymmetric ear movement and distinction from the cheek press. |
| Front stretch | 16 | 2.45 s | Supported rise, forepaw reach, chest-lowering bow with hips high, retraction and return to sitting. Redrawn with a more frontal perspective after the longer draft exceeded the canvas at the retained head scale. Reviewed near/far foreleg occlusion, rear support and intact tail/paws. |
| Back arch | 16 | 2.46 s | Sit-to-stand anticipation, gradual rounded spine, delayed tail lift, relaxation and sit-down. Forepaws do not reach forward as they do in the front stretch. Reviewed four-paw support, hip/shoulder connections and a comfortable expression. |
| Tiny hop | 16 | 1.51 s | Perk, crouch, takeoff, tucked ascent/apex, descent, forepaw contact, landing compression, small rebound and seated recovery. Reviewed tucked/occluded hindlegs, absence of grounded duplicates in flight and landing contact. |
| Side flop | 16 | 2.87 s | Hip shift, elbow/shoulder lowering, side rest and a separate planted-forepaw push-up. Recovery uses new drawings rather than reversing the descent. A fresh transparent redraw replaced the hazy draft. Reviewed overlapping forelegs, tucked hindquarters and the get-up supports. |
| Shoulder peek | 12 | 1.82 s | Ears/eyes lead a limited shoulder glance; the shoulders follow slightly, then unwind toward the viewer. Reviewed natural neck rotation, planted paws and its distinction from a cheek tilt. |

No duplicated forelegs, floating paws or detached tails were observed in the accepted source/runtime reviews. This remains a visual assessment; frame-count and image-boundary tests do not certify anatomy.

## Scale, placement and transparency

Every runtime image remains 112 × 112 with transparent margins. Each sequence uses one calibration derived from its neutral seated source: a 62 px head-width reference and an 82 px full-height seated reference. Those scale factors stay fixed through its crouches, turns, reaches and lying poses. No per-frame whole-body fit shrinks the kitten to accommodate a raised tail.

Ground-contact landmarks register seated reactions to idle. Stretch/arch use the rear contact for their larger stance changes; the hop keeps the head axis registered and follows a small, explicitly timed 14 px maximum lift inside the same canvas. Complete poses receive a small horizontal placement correction when necessary to preserve the clear canvas margin. The desktop window itself does not move during petting.

Using the actual idle/blink images for the seated handoffs avoids a newly drawn face or body appearing at rest. The adjacent incoming poses are checked against idle's head width. Actual posture changes can lower or lift the head, so those are not normalized away.

The initial chin/flop drafts and their first attempted cleanup still had gray haze. They were rejected in favor of fresh reference-based transparent redraws. Paw offer/kneading were revised for leg readability; front stretch was revised for perspective/fit. Final source sheets and native widget captures were inspected, including light and dark backdrops. No backgrounds or speech panels were introduced.

Built-in ImageGen generated and revised the source sheets. [Initial exact prompts](petting-rebuild-prompts.json) and [revision/clean-redraw prompts](petting-rebuild-revisions.json) are saved. Scripts only extract/register/resize sprites and render previews; they do not paint replacement anatomy pixels.

## Repeated clicks and state transitions

- Every deliberate pet still increments the pet count immediately and acknowledges the input through the existing palm interaction.
- A click during an active reaction preserves its pose clock, takeoff/landing and get-up. Additional clicks coalesce into at most one pending reaction, which starts at the completed seated handoff.
- Starting the pending reaction does not count the click twice and does not consume the entire rotation in the background. All twelve still appear before the bag repeats.
- Hiding or disabling motion clears pending petting. Sleep/wake retains its dedicated behavior. A nap deadline waits for an active pet's recovery, preventing an in-flight hop from turning abruptly into a sleeping pose.
- Quiet controls, dragging separation, optional sound, local palm cursors and background-free thoughts retain their existing behavior. No dependencies or user settings were added.

## Verification

- New endpoint/pose-count, repeated-click, cadence/completion and nap-recovery regressions failed before implementation. The precise-timer assertion also reproduced the old coarse-timer behavior before the final timing fix.
- Animation/behavior checks: 51 passed after the accepted source revisions.
- Final full discovery after the precise-timer adjustment: 144 run, 142 passed, two opt-in packaging checks skipped. Both packaging checks were then enabled separately and passed against the final executable.
- Eight focused native Windows checks passed for all-sequence selection, scale, clear edges, shared idle endpoints, pending clicks, hiding/reduced motion and completion. The final precise/coarse timer transition check passed natively as well.
- The real native paint-event probe displayed all 16 hop poses and all 12 queued nuzzle poses, then idle. Both clicks counted; the first pose clock was preserved and the window stayed at its original position. A coarse-timer probe had skipped a short hop pose, motivating the pet-only precise timer.
- All 147 preserved non-pet runtime images and every non-pet clip definition were compared with the pre-rebuild source and remained byte-identical. Tail artwork, five-turn cycle and timing were preserved.
- An isolated in-memory mutation inverted the pending-pet condition; the repeated-click regression failed as intended. Production files were never mutated.
- PyInstaller rebuild passed. Both packaged checks passed: required assets/modules without credentials, native startup/tray/window initialization and clean rejection of a second instance.
- A separate cold executable probe observed falling positions from y=-112 to the saved landing y=938, including intermediate positions. Only the temporary test process was stopped.
- Runtime catalogs, split pose sheets, palm preview and native light/dark captures were refreshed.
- Preview sampling was checked against every distinct used pet drawing. An intro-subtraction rounding issue that omitted short hop poses was reproduced and fixed; all used pet drawings now appear in the 20 FPS sampler. GIF timing/decoding and whitespace checks passed.

## Delivery and limits

The executable is `dist/petting-qol/DesktopNeko.exe`. It uses the existing preferences and single-instance lock. Quit an older running Neko before launching this build.

Native verification used the current Windows display. Physical mixed-DPI/multi-monitor and long-duration resource-use checks were not available. New source anatomy was visually reviewed, not automatically proven correct.
