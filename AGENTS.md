# Animation work

Resting idle has first priority in idle refreshes. Every animation brief must specify readable, action-specific eye, ear, mouth and head expressions, their held duration and drawn transitions; expressions are a standing requirement, not an optional polish pass. Review them at native desktop size and normal speed. Preserve quiet holds and supported anatomy. For replacements, retain and show synchronized old/new comparisons. Never change the accepted tail chase/catch incidentally.

Resting idle must include newly authored, subtle local breathing and happy blink acting rather than an eye-only freeze. Keep the seated position, head height/outline, paws, tail and physical scale anchored; animate only reviewed chest/shoulder and expression regions. Matching bounding boxes alone does not prevent redraw wobble. Keep blinks brisk and review breathing at native size and normal speed.

Before planning, generating or modifying Neko animations, read [framemaster.md](framemaster.md) and the current validation report it links. Follow its character, anatomy, scale, transition, runtime and verification guidance.

When animation work produces a verified discovery, update the relevant section of `framemaster.md` and its dated findings log. Record the evidence, correction, rejected approach and remaining limits; keep proposed techniques distinct from tested practice. Update affected prompts/assembly records, previews, tests and README descriptions together. Preserve historical validation reports.

# Release layout

Build directly to `dist/DesktopNeko.exe`; do not create release subfolders inside `dist`.
Keep only the current executable and its immediate predecessor, `dist/DesktopNeko-previous.exe`.
Preserve the verified current release before replacing it, and clean older outputs only after the new build passes its checks. Keep intermediate build files outside `dist`.
