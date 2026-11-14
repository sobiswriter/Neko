# Animation work

Resting idle has first priority in idle refreshes. Every animation brief must specify readable, action-specific eye, ear, mouth and head expressions, their held duration and drawn transitions; expressions are a standing requirement, not an optional polish pass. Review them at native desktop size and normal speed. Preserve quiet holds and supported anatomy. For replacements, retain and show synchronized old/new comparisons. Never change the accepted tail chase/catch incidentally.

Resting idle must not use breathing, a chest-shading pulse, whole-body translation/scaling or an eye-only freeze. Use small connected seated joint/shoulder movements over exact planted contacts, with a quiet head, readable expressions and brisk blinks between long holds. Matching bounds alone does not prevent redraw wobble; review the actual contours, contact joins and loop seam at native size.

Before planning, generating or modifying Neko animations, read [framemaster.md](framemaster.md) and the current validation report it links. Follow its character, anatomy, scale, transition, runtime and verification guidance.

When animation work produces a verified discovery, update the relevant section of `framemaster.md` and its dated findings log. Record the evidence, correction, rejected approach and remaining limits; keep proposed techniques distinct from tested practice. Update affected prompts/assembly records, previews, tests and README descriptions together. Preserve historical validation reports.

# Release layout

Build directly to `dist/DesktopNeko.exe`; do not create release subfolders inside `dist`.
Keep only the current executable and its immediate predecessor, `dist/DesktopNeko-previous.exe`.
Exception (user request, 2026-11-14): the experimental Neko 1.2 line builds to the single flat file `dist/DesktopNeko-1.2.exe`, replaced in place on each 1.2 build; it never replaces or rotates the stable pair.
Preserve the verified current release before replacing it, and clean older outputs only after the new build passes its checks. Keep intermediate build files outside `dist`.
