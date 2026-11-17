# Exact tiny smile from the user's screenshot · 2026-10-23

The user supplies [this frame](../references/simple-smile/2026-10-23/user-smile.png) as the exact desired smile. It is the previous release/soft-mouth pose. Use that mouth throughout the existing2.9s smile interval; do not substitute the larger filled held mouth or a newly invented curve.

[Before/after](simple-smile-compare.html) · [native-size normal-speed GIF](simple-smile-compare.gif) · [keys](simple-smile-frames.png) · [assembly/source identities](simple-smile-assembly.json) · [release identities](simple-smile-release.json).

## Minimal change

The existing authored donor4 equals the requested frame9 mouth. Copy it to held smile entries6/7/8; entries5/9 already have it. Mouth rectangle x83..94,y93..98 and alpha are preserved. The exact small expression stays for half the5.8s loop (2.9s), with existing happy blink/quiet holds. Eyes, ears, head, body, paws and tail retain every accepted pixel at the same time. No runtime code or timing changes; atlas remains908. All other looks and protected tails remain intact.

A built-in ImageGen draft was generated before the user's precise screenshot arrived. It is retained, with its prompt, in the [source record](../references/simple-smile/README.md), and is not used. Final art reuses the selected existing drawing. Historical reports/comparisons remain untouched.

## Focused checks

Two targeted source cases pass: the held mouth is pixel-identical to selected frame9, lasts2900ms and respects the existing neutral/shared neutral; seated contacts/head and permitted motion remain anchored. Frozen predecessor comparison verifies exactly three changed frames, all905 others identical, all65 clip definitions identical, and synchronized50ms samples identical outside the mouth across the whole loop. All ten used rest drawings remain one significant connected component. Keys were inspected at native size; synchronized normal-speed GIF supplied for human review.

The prior [native0..9 sequence](rest-smile-native.json) is retained, not rerun: timing and all runtime bytecode are unchanged. Both focused package checks pass: all908 baked frames match source; resource/source hashes and dependency safety match. The release record verifies all six frozen modules against final source, all nine active refresh sheets against bundled bytes, and unchanged main/behavior/animation bytecode against the verified predecessor. Preserve the verified immediate predecessor and rotate only after package checks.

No broad regression, repeated native timing/startup test, unrelated behavior replay or hardware/soak checks. The local-file browser restriction was not retried. Matching the selected mouth is verified; artistic appeal remains the user's judgement.
