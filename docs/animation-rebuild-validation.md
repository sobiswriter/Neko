# Animation rebuild verification — 2026-10-21

## Visual review

The built-in ImageGen source sheets, all 40 used atlas pose slots, native-size
output, enlarged runtime sheets and intermediate flight positions were inspected.
No duplicated foreleg, detached tail or missing body part was observed in the
accepted runtime frames. This is visual assessment, not an automated anatomy guarantee.

| Action | Inspected behavior | Correction / result |
| --- | --- | --- |
| Arrival | Two forelegs reaching, contact, crouch, recovery and neutral sit | Entire kitten drawn before viewport clipping; continuous accelerating fall; final drawing equals idle |
| Departure | Neutral sit, glance, crouch, connected push-off and airborne silhouette | Relaxed face; small arc; tail trails; viewport becomes empty before cleanup |
| Tail swish | Stationary seated body, one attached changing tail | Registered frames to hold head position within one pixel; one sweep then rest |
| Tail chase | Front, right, rear-right, back, rear-left, left and seated return | One direction; occluded legs stay behind the visible silhouette; common idle endpoints |
| Tail catch | One supporting foreleg and one sliding/reaching foreleg | First draft rejected; corrected lower eight drawings remove the duplicate planted-leg impression and move the tip under the reaching paw |

[Used source poses](neko-tail-life-source-frames.png) ·
[flight positions at 100ms intervals](neko-lifecycle-flight.png) ·
[native playback](neko-tail-life-native.gif) ·
[enlarged playback](neko-tail-life-preview.gif)

## Automated and native checks

- Full unittest discovery: **111 tests, 109 passed, two opt-in packaging tests skipped**.
- After strengthening the distinct-pose assertion, its focused test passed.
- Six lifecycle tests passed again with `QT_QPA_PLATFORM=windows`: actual repaint,
  arrival/greeting ordering, departure cleanup/position, independent quit timer,
  hiding/reduced-motion handling and disabling motion mid-departure.
- An intentional inversion of the arrival/departure branch made the regression
  test fail; production source was restored byte for byte afterward.
- Clean PyInstaller build succeeded: `dist/DesktopNeko.exe`.
- The packaged archive test passed separately. All three new PNG payloads match
  the reviewed workspace assets byte for byte; old lifecycle/tail-play sheets
  and local credentials are excluded.
- Native rebuilt-executable second-instance launch exited successfully while the
  user's existing desktop copy held the instance lock.
- All four regenerated catalog GIFs decoded successfully and retained their exact
  six/eight-second duration after GIF frame coalescing.
- `git diff --check` passed.

## Limits

The user's existing Neko was left running. A fresh packaged-app startup was not
tested because it would require closing that copy. Native Windows source rendering
and the rebuilt executable's archive and instance-lock path were tested instead.
No live AI requests, startup registration changes or long-duration soak run were needed.
