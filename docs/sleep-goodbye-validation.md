# Sleeping goodbye · 2026-10-23

The user requests **wake → sad → single diagonal drop** when choosing Let her go during sleep. Previously all three sleep states were explicitly excluded from goodbye. The verified replaced executable closes from sleep/curl in7–11ms with no wake or departure paint. Three source regressions fail before correction.

## Assembly and runtime correction

No generation prompt, new artwork, import or calibration change is needed. Reuse `wake` from `transitions`, row2, order0–7, durations350/220/220/250/250/250/300/500ms:2.34s. Then reuse the existing sad expression/turn/load/push and continuous diagonal `depart` selection:17 entries/2.20s. Historical [art provenance](lifecycle-v2-prompts.json) and [departure selection](dropout-fix-selection.json) remain intact. All839 imported frames and65 clip definitions remain unchanged.

`quit_neko` now wakes a visible sleeping kitten and queues the existing finite recovery path. An ongoing curl reaches its supported sleep endpoint before waking; an ongoing wake retains its current clock and finishes. The actual clip sum owns the deadline, avoiding an extra pause from the behavior model's2.6s normal wake fallback. The first departure animation tick still starts its full sad/leap clock. Repeated quit, pets, auto games and normal behavior ticks cannot interrupt the pending goodbye. Existing hidden/reduced-motion/fullscreen-hiding/monitor-change escape paths still close promptly. Held and game quits retain their prior immediate behavior. Neither pets nor naps are invented; saved home remains protected.

Reject both the old immediate sleeping close and replacing the sleep drawing directly with seated sadness. No second jump, body resizing, new gait or tail-chase change is introduced. State/clip changes continue through the existing Nook Journal.

[Actual-controller scene](sleep-goodbye-scene.gif) samples the production menu/animate/painter path at30fps, with a0.6s initial sleep hold, full wake, sadness and one leap; it repeats only for review. It uses a synthetic360×320 monitor and temporary settings. The reviewed key samples show curl, supported seated wake, lowered ears/eyes and extended flight. Native-size frames retain the full192×144 canvas. This is an assembly check, not new artistic approval.

## Verification

- 164 source checks pass across `test_main`, `test_animations` and `test_behavior`, including sleep menu→full wake→sad departure→one cleanup, duplicate/pet/tick suppression, unchanged counts/home, partial wake and partial curl, prior lifecycle interruption/trajectory checks and existing sleep/frame checks.
- The retained bundled-menu probe adds sleeping and partial-curl cases, observing actual wake and departure paints under real Qt timers. It executes the executable's own main/animation bytecode and bundled resources under installed Python/Qt, separately from the bootloader startup smoke check.
- All five final package checks pass: resources/credential exclusion, icon/manifest, all-frame baked/source equality, actual executable startup/second-instance handling and the extended bundled-menu check. A separate [native Windows menu/timer run](sleep-goodbye-native.json) paints all8 wake and17 departure poses in order, closing sleeping/curl cases in4.682/4.884s with home and counts preserved. Idle, awake gesture and deliberately visible fullscreen cases also retain all17 departure poses.
- The baked PNG/manifest and animation module compare identically to the replaced executable. [Exact release/source identities and check record](sleep-goodbye-release.json) include one native UI-ready measurement of2.758s. This single observation is not a comparative startup benchmark. The prior verified release was preserved before replacement, then rotated to `dist/DesktopNeko-previous.exe` only after package checks passed. Only that predecessor and `dist/DesktopNeko.exe` remain in dist; intermediates stay under ignored build storage.

## Limits

No physical pointer menu selection, mixed-DPI/multi-monitor hardware trial or long-session soak was added. Automated Qt menu/timer tests and controller preview do not replace the user's visual judgement. Existing wake artwork is reused; no new expressive drawings are claimed. The separately proposed idle animation refresh still awaits review.
