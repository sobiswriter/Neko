# Idle refresh · 2026-10-23

The user approved the [idle plan](idle-refresh-plan.md), prioritizing resting idle, requiring expressive acting permanently, protecting tail chase/catch and requesting old/new comparisons with focused verification. This release refreshes eleven quiet clips across ten sheets. It does not change the accepted tail chase/catch, sleep, care, carry, lifecycle or game artwork.

[Synchronized old/new comparisons](idle-refresh-compare.html) · [resting comparison](idle-refresh-idle-compare.gif) · [light keys](idle-refresh-keys.png) · [dark keys](idle-refresh-keys-dark.png) · [face-hidden priority keys](idle-refresh-silhouettes.png).

## Performance and expressions

The permanent requirement is recorded in [AGENTS.md](../AGENTS.md) and [Frame Master](../framemaster.md): expressions belong in the brief and connected drawings, with readable eye, ear, mouth and head acting at desktop size. Quiet holds and supported anatomy remain essential.

| Clip / total | Expression and drawn transition |
| --- | --- |
| Rest / 6.8s loop | Planted paws/haunch, small chest breath, relaxed ears, quiet tiny mouth, soft lids into closed arcs and reopening. Two2.2s open holds preserve stillness. The user rejected the initial1.55s blink as too slow: closing/closed/reopening are now150ms each,450ms total, with the duplicate closed drawing omitted. Larger ear/head tilts8/9 are excluded. |
| Loaf / 6s | Forepaws tuck sequentially as shoulders lower, ears soften and head settles; contented lids linger through two900ms supported loaf drawings before unfolding and rising. |
| Stretch / 5.35s | Foretoes plant, chest lowers, pelvis remains high, hind leg extends; effort eyes squeeze across450/400/500ms pressure poses, mouth stays small and ears angle with the head before a relaxed supported sit. |
| Groom / 4.5s | Eyes follow the lifted paw, little lick mouth, cheek/ear wipe with contented eye arcs across450/400/450ms; the supporting paw stays planted, then head and paw recover. |
| Yawn / 4.3s | Heavy lids, lifted chin and jaw opening through drawn stages; two450ms full-yawn drawings, gradual closure, soft ears, blink/reopen and level head. |
| Sleepy peek / 4.5s | Head and ears settle with heavy lids, then one eye peeks and the other follows through450ms accents; the mouth stays quiet, and the supported sit returns to attentive neutral. |
| Ear flick / 3.7s | One ear leads, head follows slightly, opposite ear settles;350ms main accent, quiet mouth, restrained lids and connected reopen. |
| Sniff / 4.15s | Eyes/ears notice, nose reaches, small nose/mouth response, curious head tilt450ms, then neck eases back through a contented blink. |
| Left/right look / 3.5s each | Eyes/ears lead the head turn, mouth remains small, shoulder follows;650ms interested pause, reverse entry angles and drawn frontal recovery. |
| Quiet tail / 4.2s | Supported body/head registration stays steady, one attached tail sweeps, soft lids and tiny mouth settle through a400ms accent and drawn reopening. |

Finite clips play once; their actual duration owns the behavior deadline. Naps and queued pet requests wait for supported recovery. The existing pickup bridge can still interrupt. Gesture words remain bound to their actual pose, while general thoughts retain their separate timer. No finer idle timer was added: normal playback remains100ms, protected tails50ms.

## Artwork and corrections

Built-in ImageGen produced ten sheets using the canonical character and saved motion/support references. [Exact prompts, original crops, scales, support registration and final orders/timings](idle-refresh-prompts.json) accompany the [retained raw originals](../references/idle-refresh/2026-10-23). Packed source sheets contain128 complete drawings on192×144 transparent cells; ten canonical aliases give138 new atlas entries. Retiring73 superseded idle entries gives904 total.

Review corrected the stretch's shrunken final recovery group (crown7px low) using one constant calibration for13–15 against neutral15. Earlier raw-resolution contact measurements were also normalized before runtime support registration. Reject per-pose refitting. Low loaf/stretch silhouette runs can include the haunch and falsely report head width: neutral landmarks plus native color/silhouette review determine scale. Directional looks exclude opposite-turn returns5/13 and partial returns6/14; accepted entry angles reverse into drawn neutrals7/15. Yawn reuses4 during jaw closure. Quiet swish uses head registration to avoid body drift. Gray RGB stored under zero alpha in the look original does not produce a matte; light/dark review preserves its alpha.

## Focused evidence

- [Comparison metrics](idle-refresh-metrics.json) independently load the verified predecessor's frozen animation code and packed atlas: all766 retained frames are pixel-identical, and all54 unrelated clip definitions are identical, including tail chase/catch. Eleven old/new GIFs share elapsed time, character scale and normal speed. Each finite comparison includes entry, full action, recovery and rest; repetition is for review only.
- Source animation checks cover new bank dimensions/counts, bounds, significant connected components and canonical endpoint support. The new drawn-neutral test caught the7px stretch recovery error before correction; all ten corrected neutral head/crown checks pass. Significant-component checks include every128 imported source drawing. These cannot prove attached anatomy is correct.
- [Native Windows painter evidence](idle-refresh-native.json) observes every used pose in all eleven clips under production100ms animation and500ms behavior timers. After the user's blink comment, only resting coverage was repeated: all ten selected drawings still paint, maximum gap125.05ms. Cursor/settings are scripted and temporary. This proves Qt paints, not unobscured physical visibility.
- Seven focused interaction checks pass: idle recovery/queued pet/due nap, ordinary grooming protection, unchanged tail weighting, gesture thought expiry, armed game invitation and sleeping menu goodbye. All35 behavior tests pass after isolating the configurable-sleep test from a newly protected in-progress yawn. The corrected test and blink regression pass. Earlier32 animation checks pass; only affected checks were repeated after corrections.
- All five executable checks pass across the initial run and one targeted goodbye recheck: resources/icon/manifest, all904 baked/source frames, native bootloader startup/second instance and bundled menu goodbye/journal retention. The latter exceeded its legacy30s wrapper; five individually bounded7s cases plus imports/retention I/O require a larger overall budget. The wrapper is now60s, and the same assertions pass in41.26s. No application deadline was relaxed. [Release identities](idle-refresh-release.json) match all six frozen runtime modules to source and all ten new bundled sheets to final PNGs. Current/previous layout remains flat; the verified predecessor is preserved before replacement. Build intermediates remain outside `dist`.

## Limits

No broad full-suite rerun, physical pointer/mixed-DPI/multi-monitor trial or long soak was added, per the user's request for necessary checks only. Artwork appeal and subtle attached anatomy remain subject to human review; technical checks are not artistic approval. The original slow-blink preview is superseded by the corrected450ms comparison. Historical validation reports remain intact.
