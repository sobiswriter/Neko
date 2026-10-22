# Cursor play v2 verification — 2026-10-22

The user approved the [v2 plan](cursor-play-v2-plan.md). Source/art and visible Windows playback are verified; final executable packaging checks are in progress. Earlier reports remain historical evidence of their releases.

## Delivered behavior

Catch the Cursor is now an occasional interaction with the kitten. The old guide/status/clock/floating End windows and their module are removed. Manual play and stop remain in the ordinary cat/tray menu and nook. Ordinary idle cursor following, its state, checkbox, scheduling and dialogue are removed.

Automatic play defaults on with a 90s cooldown, configurable from 30–600s. Expiry arms one intent. A fresh outside-to-side-zone entry is required after expiry and eligibility: outside at least 150ms, entry at least 250ms, sampled every 100ms, with 8px exit hysteresis. Being inside at expiry cannot launch play. Zones exclude the entire 192px canvas plus 40px care space per side, use the actual reachable height band, require 120px useful width and stay on the kitten's monitor. Sleep, care, held buttons, carrying, reactions, menus, quiet company, recent typing, hidden/fullscreen and wake recovery discard entry qualification. The next eligible fresh entry is required; no launch backlog accumulates. A live Windows button-state read also protects drags in other apps, without a mouse hook or recording.

An 800ms notice leads into separately timed 3, 2, 1 phases, one second each, then a 350ms launch cue. Every stage has drawn changes. Clocks begin after presentation of the actual thought label. Leaving the reachable band for 600ms during countdown reverses the ready poses and cancels neutrally, preserving the original cooldown and counting no play. A stall cancels instead of scoring. The 45s chase clock and played count begin at the launch cue. A real forepaw alpha contact latches exactly one win; a cancelled started chase remains played. Nonnegative local counters migrate from zero and clamp wins to played; both appear in the normal menu/nook.

Neko has an eight-pose supported walk, playful run/reach eye squeezes and reopens, three victory stories and three loss stories. Independent outcome bags exhaust all variants and avoid immediate repeats across refills. Local speech has 68 new lines across notice, launch, pursuit, victory, four protest contexts, loss and comfort; each bank also avoids immediate repeats. Pursuit permits at most two asides, at least six seconds apart, without replacing countdown/outcome cues. A common drawn look-up connects the new lowered-face curls to the retained quiet curl/comfort and curled carrying. Reduced motion uses supported still celebration poses and stationary reach, with real countdown timing.

## Artwork and continuity

- [Normal-speed controller preview](cursor-play-v2.gif), [half speed](cursor-play-v2-slow.gif).
- [All six outcome stories](cursor-play-v2-outcomes.gif), [half speed](cursor-play-v2-outcomes-slow.gif).
- [All 176 new imported slots on light](cursor-play-v2-frames.png) and [dark](cursor-play-v2-frames-dark.png). Slots include intentional holds/calibration/endpoints; these are not 176 unique drawings.
- [Exact prompts, selected output paths, crop regions, rejections, calibration, clip definitions and hashes](cursor-play-v2-prompts.json).

The current 729-entry atlas contains 200 game source slots (176 new plus 24 retained curl/comfort) and one appended walk idle. The 552 retained entries and 41 unaffected non-game/non-walk clip definitions compare unchanged against `d63d5cb`. Petting, tail play, pickup and original curl/comfort retain their artwork and timing. The original walk clip is intentionally replaced; old source rows remain available for historical comparison.

All game slots pass complete bounds and significant-component checks. The actual painter's y−1 offset and horizontal mirror are included in contact tests. New author-reviewed forepaw regions are18:(41,87,61,100),19:(42,78,58,94),20:(52,114,70,128),21:(52,114,70,130); high/low/distant stationary targets and both directions are genuinely catchable. Near-neutral victory/walk drawings retain62±4px head width, crown 48±2 and head center 90.5±2 before canonical idle.

Rejected approaches: keeping generated labels/grid/matte; clipping the ready tail at384px; per-pose fitting to conceal loss-c growth; using the too-tall grasp final sit; keeping the short walk final neutral; cutting directly from lowered-face curl to the retained outward-looking curl. Corrections are recorded in the provenance. Ready uses448px packed cells and one repeated complete gathering hold. Grasp recovers through14→13→2→1→generated neutral→actual idle. Walk packed15 selects its original generated neutral0, followed by actual idle 16. An eight-slot authored bridge supplies the curl look-up. Whole-batch +2px registration corrects hop/grasp neutral centers. No anatomy or expressions were painted in extraction code.

## Checks

Full discovery: 215 tests, 212 passed and three opt-in executable checks skipped. Coverage includes all new phase boundaries, short outside flicker, inside-at-expiry, sleep/care qualification, interval edits during cancelled countdown, cross-app button holds, manual promotion, counts/reload/invalid settings, all outcome bag refills, drawn recovery landmarks, actual contacts, all jump cancellation samples, curl carrying/comfort, fullscreen/hiding and existing companion behavior. Immutable atlas fixtures are shared in rendering tests; each test still gets a fresh widget, controller and preferences.

[Visible Windows Qt measurements](cursor-play-v2-native.json) record real cue presentation, every countdown/hunt/walk/recovery drawing and every used drawing of all six outcomes. The native run includes one real controller/alpha-contact chase and six explicitly staged outcome performances. Median observation interval 19.9995ms, maximum 65.75ms; numeral durations 1.0314s, 1.0331s, 1.0511s. Foreground remains unchanged, no game overlay exists, and native hit testing passes through the thought window. Scripted pointer observations never move/capture the real pointer. Physical hardware: one monitor, DPR 1.0. Deterministic invitation geometry tests cover both sides and narrow areas; physical mixed-DPI/multi-monitor behavior was not exercised.

Reproduce previews/native checks with:

```powershell
.venv\Scripts\python.exe -m unittest discover -v
.venv\Scripts\python.exe tools/preview_catch.py
.venv\Scripts\python.exe tools/preview_catch.py --native
```

The source diff was reviewed for the approved scope, interruption/counter correctness, bounded storage, no cursor control/new hooks, no new runtime dependency and removal of retired callers. Numerical checks do not certify anatomy or subjective fun; every selected source/runtime drawing was also reviewed on light/dark backgrounds and in production-timing playback.

## Release

Final packaging record will be added after the exact `dist/DesktopNeko.exe` passes resource/icon/manifest and native startup/tray/single-instance checks. The verified pre-v2 current executable is preserved outside `dist` before replacement; the prior rollback file stays untouched until those checks pass. Release files remain flat.

The earlier [startup/icon repair](startup-icon-validation.md) remains included: supplied `neko_sleep.ico`, correctly quoted startup registration, targeted removal of Neko's `RUNASADMIN` compatibility flag, and ordinary-user manifest. No sign-out/reboot/next-logon trial was performed.

Limits: native gameplay uses test-owned windows and scripted observations; no extended human dodge-play session, physical mixed-DPI/multiple monitors or long-session resource soak. Faint source alpha and attached anatomy still require human visual judgement. The current thought backdrop remains a static local sample until that thought closes.

Windows button-state behavior was checked against the primary [GetAsyncKeyState documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate); only the current-down high bit of the five fixed mouse-button codes is queried.
