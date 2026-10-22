# Petting speed adjustment — 2026-10-22

The user requested slightly faster petting and a flat `dist` containing only the latest and immediately preceding releases.

## Change

All twelve pet clips divide their durations by 1.15, rounded to integer milliseconds and floored at 50ms. This is approximately 15% faster playback; kneading's existing 50ms drawings stay at 50ms. Source artwork, pose order, alternating kneads, three hop arcs, complete recovery and canonical endpoints are unchanged. Comparing against the previous release's clip definitions confirms that every non-pet duration is unchanged, including tail, pickup, arrival and departure.

Total pet durations now range from 2.432s to 5.910s. The regenerated [pet catalog](neko-pet-catalog.gif) decodes to eight seconds. A 50ms sampling check covers every selected drawing in all twelve clips. No generated artwork changed, so prior anatomy/assembly provenance remains applicable; the preview now demonstrates the updated timing.

## Focused verification

- 37 animation/behavior checks passed: timing bounds and the 50ms floor, every selected drawing, idle endpoints, three grounded hop arcs and the complete behavior test module.
- Four desktop checks passed: clip-derived completion/cadence, queued/repeated pets, sleepy-flop recovery and click versus drag. The flop test originally assumed a six-second story; it now checks just before the actual deadline, preserving its purpose with the shorter clip. Its corrected case was rerun successfully; the other three passed unchanged.
- Both opt-in packaging checks passed against `dist/DesktopNeko.exe`: bundled resources/art hashes and native startup/tray/topmost/single-instance behavior. Only test-owned processes were stopped.
- Full discovery and a new native animation timing study were not run for this timing-only adjustment. Existing artwork and geometry were not modified.

## Release layout

Only two executables belong directly in `dist`; build intermediates stay in `build`. Preserve the prior verified current release before replacing it. Historical reports retain the original delivery paths, which no longer need to remain on disk.

- Current: `dist/DesktopNeko.exe`, 100,250,724 bytes. SHA-256: `f79ff6adf911d053d3defc268af9dbcbe26119c62cb568766f34177c597d8277`.
- Previous: `dist/DesktopNeko-previous.exe`, the verified pickup release, 100,251,184 bytes. SHA-256: `78da7654dd1450d3c0b8755c7fd731a60125e6ffe9f9c04d8f3fb3346e42b918`.

README, root agent instructions and Frame Master describe this flat layout for future builds. The proposed mini-games build command also uses it; mini-games remain unimplemented.
