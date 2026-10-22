# Activity reaction limits — 2026-10-22

The user reported excessive reactions to windows/work and requested a controllable limit plus access to editable lines.

## Correction

Previously, typing, window changes and cursor curiosity each had independent cooldowns (30/8/18 seconds); following had a separate 25-second rest. Different categories could therefore alternate quickly. A shared `Companion.last_activity_reaction` now gates all four categories, defaulting to **60 seconds**. **Neko's nook → Company → Activity reactions every** adjusts the shared minimum from **15 to 600 seconds**, using the existing bounded timing/preferences system. Following also retains its own existing 25-second minimum rest when the shared setting is shorter.

Cooldown starts when an activity response is selected. Events observed during the cooldown are discarded rather than queued to burst later. A genuinely new eligible event may react once the cooldown expires. An event received during another animation can still wait briefly under the existing seven-second expiry. Sleep, pet/carry ownership, idle artwork and their separate cadence are preserved. Waking establishes a fresh activity gap to avoid immediate distraction.

Idle matching thoughts were also using a shortened 8–30 second speech gap, even when **Thoughts every** was set to 75 seconds. Automatic offline lines now honor the full configured interval. Both optional AI request and completion paths respect the same interval and visible-caption rule; no AI/network call was needed for this change. Deliberate pet/wake replies can still respond independently.

## Editable voice

The existing [dialogue.py](../dialogue.py) `LINES` dictionary contains **346 offline phrases in 33 groups**. It is the actual source, not an exported duplicate. Edit one phrase per line inside each triple-quoted group, preserve names/quotes and keep phrases short (the existing quality check caps them at 110 characters). Restart source launches after edits; rebuilding is required for packaged executables. Optional AI-generated comments are separate.

The file was opened through Codex's file panel. No new editor, external data loader, dependency or duplicate dialogue file was introduced.

## Verification

- All **38 behavior/dialogue tests passed**, including a new fake-clock window → typing → cursor sequence proving the shared boundary, configurable shortening and absence of queued events during cooldown.
- **12 focused desktop tests passed**: the full automatic-thought interval and deliberate-reply bypass, AI cooldown guards, following's shared gate, existing speech/visible-caption rules, new-control apply/persist, corrupted saved value fallback, typing/window/media reactions, bounded following, quiet mode and the single-worker rule.
- The line inventory was counted from the actual `LINES` dictionary; no phrases were changed.
- Full discovery and extended native work-session testing were not repeated.

## Release

Both exact-executable packaging checks passed: bundled resources and native startup/tray/topmost/single-instance handling. Only test-owned processes were stopped.

- Current: `dist/DesktopNeko.exe`, 100,256,817 bytes; SHA-256 `526d469270318c5764f87565fa8c05ce2b7b7a2627b98c1cb6ec21c1b70efe61`.
- Previous: `dist/DesktopNeko-previous.exe`, 100,255,727 bytes; SHA-256 `e7794b04c72e3de8ab300b76d4d1feb2cbc210a24e06642c4ca01cc91f2d9aee`.
