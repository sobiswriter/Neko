# Gallop, automatic invitations and unattended sleep — 2026-10-22

User requested a fast correction with necessary checks only, leaving extended verification to them.

The new run follows the supplied eight-frame gallop's gathering/extension and supporting legs. One ImageGen call produced a 12-slot bank: calibration, eight run drawings and three brake/turn drawings. All other artwork, including jump contacts, is retained. The 720ms cycle draws excited eyes through four consecutive poses (360ms), then reopens for four landing/support poses. Flight poses 3/4 receive fixed 5/8px offsets; grounded contacts stay at 130. No pasted glyphs or per-pose fitting. [Short production-timing preview](gallop-fix.gif), [native-size light/dark strip](gallop-fix-frames.png), [exact prompt, references, source path, crop regions and hash](run-timer-sleep-prompts.json). Current atlas 741 entries; 212 game source slots.

Two reproducible control failures were fixed:

- Idle gestures discarded an armed side-entry proof. Qualification now survives a casual idle gesture, while actual launch waits for its completion. Petting, carrying, sleep, typing, menus and fullscreen still invalidate entry. The ordinary automatic-play menu item shows **ready** once the cooldown is armed. The 90s timer still waits for a fresh side approach; it does not force a chase at expiry.
- A persistent disappointed curl bypassed the sleep state machine indefinitely. At the configured unattended nap deadline, Neko silently uses her existing supported get-up/home sequence, then falls asleep. This is not counted as petting; a real pet overrides the pending nap and counts normally.

Read-only preferences inspection found sleep delay 40s, nap duration 90s, automatic games enabled, game interval 90s and quiet mode off. These user preferences were preserved. With these settings, an unattended Neko can nap before the first 90s invitation; the timer must wait for wake and a fresh approach. The fixes do not remove that requested nap protection.

Verification: three failing reproductions were recorded before the fix. The targeted timer/game/desktop/behavior batch passed 71 tests; the additional real-pet override passed separately. All 12 imported source slots passed the existing game bounds/significant-component test; eight run poses also received explicit margin/baseline checks and visual light/dark review. New expressions were inspected at desktop size. No full suite, extended native game playback, 90s wall-clock wait, mixed-DPI hardware or sleep soak was run, per the user's request. Generated preview/assembly helpers remain under ignored `build/run-fix`; exact assembly regions and final assets are tracked.

Release complete: the executable passed both bundle-resource and supplied-icon/normal-user-manifest checks. The verified preceding executable was then preserved as `dist/DesktopNeko-previous.exe`. Only these two executables remain in `dist`; build intermediates remain outside it. [Exact executable identities and source hashes](run-timer-sleep-release.json).

- Current: 112730633 bytes; SHA256 `31933e124f5464da4517742772ea7c42194dc181cad4d3ee3191886dbe588797`.
- Previous: 111857913 bytes; SHA256 `b968569ac7ea611e1587e593ce4499446809e0ed834a5bd7f707a81a98b9ec3f`.
