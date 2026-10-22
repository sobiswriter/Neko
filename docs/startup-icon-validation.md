# Startup repair and supplied icon — 2026-10-22

This maintenance release repairs Windows startup and adopts the supplied root `neko_sleep.ico`. The [cursor-play v2 proposal](cursor-play-v2-plan.md) is awaiting approval: no walking/running/outcome artwork, invitation/countdown behavior, dialogue, overlay removal or game counters from that proposal are implemented here. Existing gameplay remains the first release's behavior.

## Reproduced cause and repair

The existing per-user `Run` registration already points to the quoted, correct `dist/DesktopNeko.exe`. Its matching per-user application compatibility value was `~ RUNASADMIN`. A direct `subprocess.Popen` of that exact delivered path reproduced **WinError740: requested operation requires elevation**, consistent with the earlier Catch packaging report. The relevant original value was saved under ignored `build/startup-icon/compatibility-before.json` before changing it.

The repair removes **only `RUNASADMIN` for Neko's exact executable path**. Other compatibility flags/entries and Windows UAC policy are preserved. With no remaining flags, that one value is deleted. The existing startup command remains unchanged. Direct native launch, tray/window initialization, topmost behavior and second-instance rejection then passed on the actual `dist/DesktopNeko.exe` path, without a renamed copy or elevation prompt.

`set_autostart(True)` now performs the same targeted repair before registering its normal quoted command, preventing recurrence when startup is enabled again. Missing/non-elevated entries are unchanged; unexpected non-text data or access errors surface without overwriting it. Disabling startup still removes Neko's Run value and legacy shortcut. Registry regression tests mock writes and assert exact path targeting, preservation of other flags, missing/no-op cases and error handling.

Microsoft documents that per-user Run entries execute at user logon and may be delayed, rather than guaranteeing execution immediately on boot. Most desktop applications should use `asInvoker`; Neko's bundled manifest retains that normal-user execution level. [Run/RunOnce documentation](https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys), [execution-level documentation](https://learn.microsoft.com/en-us/windows/win32/secbp/running-with-administrator-privileges).

## Icon

The user's unchanged root `neko_sleep.ico` is the single canonical icon asset. It contains 16, 24, 32, 48, 64, 72, 96, 128 and 256px images. `main.spec` embeds it in the Windows executable resources and bundles it at the resource root. The application, Neko widget, nook and tray use this same asset. No sprite or animation artwork was changed to create the icon.

Qt checks compare the actual 32px pet/tray/nook images to the supplied ICO. Packaging checks compare bundled bytes and every ICO image payload against PE icon resources, and verify the normal-user manifest. Keep this root ICO with source releases; future builds use it automatically.

## Verification and release

- Seven focused final source checks passed: four startup repair regressions, existing startup enable/failure behavior, and supplied pet/tray/nook icon identity. The existing all-pose/nook render check also passed during this maintenance work.
- The original executable's repaired direct-launch native check passed before rebuilding. The fresh build was checked again at its actual delivered path, including new icon resources, asset hashes, manifest, native startup/tray/topmost and second-instance behavior.
- Unchanged-game regression exposed a deferred play tick running after the test-owned widget had been destroyed. Bind the zero-delay callback to its QObject context so Qt cancels it with that widget. The final 20 controller/desktop checks pass with no teardown traceback; no v2 gameplay feature is introduced by this lifetime correction.
- Build/runtime source: `f2fc9a1` (full hash and final build identities in the release record).
- Final checks: **7 focused source + 20 unchanged-game + all 3 exact-package checks passed**. The last package run took 11.832 seconds on the actual delivered path.
- Current: `dist/DesktopNeko.exe`, **102,553,575 bytes**, SHA-256 `0237d5d01723ff19c9e64b84885505b63c765373eb607b6783f7ffa19e5058d3`.
- Previous: `dist/DesktopNeko-previous.exe`, **102,341,889 bytes**, SHA-256 `de09d071198c4aaecffe50c075aa4064778a755546aa843a7f906f563e61eec9`.
- [Machine-readable release and startup record](startup-icon-release.json).

Builds go directly to `dist/DesktopNeko.exe`; the previously verified Catch build was preserved before replacement and is now `dist/DesktopNeko-previous.exe` after the new build passed. Intermediate files stay under `build/startup-icon/`. Prior validation reports remain historical and unchanged.

## Limits

No sign-out, reboot or actual next-logon launch was performed; doing so would interrupt the user's session. The elevation blocker was reproduced and removed, the existing Run registration was checked, and direct native launch was verified. Windows may delay startup; explicit Task Manager disabling or later re-enabling “Run as administrator” can affect future logons. Full source discovery and animation playback QA were not repeated for this narrowly scoped maintenance change; focused tests, unchanged-game regression and exact-package checks are the evidence for it.
