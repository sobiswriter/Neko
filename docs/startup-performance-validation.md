# Startup preprocessing correction — 2026-10-22

The user reported slow startup and requested a focused investigation. No animation artwork, clip timing, game rules, preferences or startup registrations were changed.

## Cause and correction

Before showing the kitten, `SpriteAtlas` imported and calibrated every source sheet on every launch. Profiling recorded 728 connected-silhouette scans and approximately 33.6 million Python calls. The profiled atlas took 11.84s; an unprofiled repeat took 5.04s. Both existing executables reached their Qt tray at about seven seconds, so the latest twelve gallop slots alone did not explain the accumulated latency.

`main.spec` now runs `tools/bake_atlas.py` during every build, using the existing importer without changing its calibration. It packages a lossless sheet containing all 741 final frames and their ordered keys. At startup, `SpriteAtlas` loads those frames directly. Missing, invalid or incomplete packed resources fall back to the existing source importer. The source sheets remain bundled and available for that fallback; authoring/source launches continue using the original importer. No new dependency or persistent user cache was added. Rebuilding on every package avoids stale imported artwork.

Changing animation timing or reducing frame count was rejected: neither addresses unnecessary startup preprocessing. Existing artwork provenance and previews remain valid because every packed frame compares pixel-identically with its source-imported counterpart.

## Focused verification

- Before packaging: two focused tests pass, checking equality of all 741 frames while forbidding silhouette analysis in the packed path, plus malformed/empty/incomplete metadata and missing-image fallback.
- Exact executable: four package tests pass, checking original source assets/modules/no credentials, supplied icon/normal-user manifest, all 741 packed frames against source import, and native startup plus second-instance rejection.
- Actual executable UI readiness, measured from process launch to its owned `QTrayIconMessageWindow`: previous current build **6.965s**, its predecessor **6.884s**, corrected build **2.140s**. This is approximately a 69% reduction relative to the replaced current build. Only probe-owned process trees were stopped.
- Same-process atlas timing: source import **5.4885s**, packed load **0.2745s**. This isolates the corrected bottleneck; it is not the complete executable launch time.
- PyInstaller build succeeded. After package checks passed, the verified replaced executable was preserved as `dist/DesktopNeko-previous.exe`; only current and previous executables remain directly in `dist`. [Hashes, sizes and measurement records](startup-performance-release.json).

Measurements are single local runs with normal filesystem caches, not reboot-cold benchmarks or a performance guarantee. The one-file executable still unpacks its Python/Qt runtime, and Windows security scanning/storage can affect launch time. A pre-existing running Neko initially prevented an independent probe through the normal instance lock; successful measurements were taken after no existing Neko remained. User processes were not terminated. No full gameplay regression, reboot/logon trial or long-session soak was performed, following the user's request to keep checks focused. Temporary profiling/build/probe records remain under ignored `build/startup-fix`.
