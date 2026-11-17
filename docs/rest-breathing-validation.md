# New resting breath and happy blink · 2026-10-23

The user rejected the prior eye-only correction as an overcorrection and explicitly requested new frames with subtle breathing, happy blinks and brisk movement, without up/down displacement or size changes. This supersedes the eye-only constraint; the original left/right looks and lazy tail remain restored.

[Previous/new comparison](rest-breathing-compare.html) · [native-size GIF](rest-breathing-compare.gif) · [eight pose drawings](rest-breathing-frames.png) · [exact prompt/assembly](rest-breathing-prompts.json) · [native paint sequence](rest-breathing-native.json) · [unchanged-frame/clip evidence](rest-breathing-metrics.json).

## Authored action

Built-in ImageGen produced a new eight-drawing sheet from the canonical identity and the earlier expressive resting study. The saved source is [rest-raw.png](../references/rest-breathing/2026-10-23/rest-raw.png). The support/spine brief retains planted forepaws/haunches and stable head/pelvis, with a small locally drawn chest/shoulder response. This applies the saved motion library's separation of connected masses to quiet supported rest, without borrowing its travel or gait tempo.

The performance is settle900ms → inhale220ms → full chest300ms → half-close100ms → happy eye arcs100ms → reopen100ms → exhale220ms → drawn recovery260ms → quiet shared neutral1800ms. Total4s; the actual blink remains300ms. Eyes soften and close into happy arcs, the mouth develops a tiny pleased smile and eases back, ears stay relaxed, and the head remains supported and steady. Crest2 reuses phase1's open eyes so the breath hold does not accidentally prolong eyelid closure.

Every active moving pose contains the newly drawn chest and expression regions. The shared neutral at entry/exit preserves transitions with other gestures. Chest shading/contours change during inhale and exhale;24 chest pixels change by more than20 RGB levels between inhale and crest, so this is not merely an eye animation or compression noise. No generated old whole-body resting sequence is reused.

Assembly uses one head calibration and nose registration, then imports the reviewed expression regions plus the internal chest/shoulder window x78..107,y104..116 onto stable support anchors. The larger proposed outer-torso window showed up to4px variation relative to the canonical torso and was rejected; the final local window keeps the entire alpha silhouette unchanged. One transparent neck-edge pixel at the first proposed window's top-right was excluded by narrowing that region. Source artwork supplies all facial/chest pixels; the assembly tool does not invent anatomy or apply whole-body scaling/bobbing. Exact crop rectangles and substitutions remain in provenance.

## Focused evidence

- Four source checks pass: all resting alpha values and all pixels outside the reviewed eye/mouth/chest regions remain identical; chest phases differ; blink timing/loop boundaries are correct; atlas count and drawn-neutral head/crown sizes remain valid. This deliberately replaces the previous eye-only pixel restriction with an anchored local-motion contract authorized by the user.
- The native Qt observer paints the complete0→1→2→3→4→5→6→7→8→0 sequence at the unchanged100ms timer, including both blink transitions. Maximum paint gap124.09ms. Settings/cursor are scripted and temporary.
- Frozen-code/packed-atlas comparison to the verified previous release confirms all878 unrelated frames and all64 other clip definitions are identical, including restored looks/quiet tail and protected tail chase/catch. Current atlas887 entries; only resting source rows/timing change.
- All three final package checks pass: resources/source hashes, all887 baked/source frames, and real startup/second-instance handling. [Release identities](rest-breathing-release.json) also match all six frozen runtime modules to final source and confirm unchanged main/behavior bytecode. The verified immediate predecessor is preserved before replacement and rotated after checks; intermediate files stay outside the flat current/previous release directory.

## Limits

No broad regression suite, unrelated interaction/game/goodbye replay or physical mixed-DPI/multi-monitor/long-soak testing was repeated. Technical anchor/paint checks do not establish subjective naturalness. Breathing is intentionally local and small; it is not a moving or scaling whole-body bitmap. Earlier eye-only and rejected full-body reports/previews remain historical evidence.
