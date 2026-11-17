# Idle refresh — approved plan and implementation · 2026-10-23

The user authorized implementation on2026-10-23, explicitly making resting idle the first priority, requiring adequate expressions as a permanent rule and requesting old/new comparisons. Tail chase/catch artwork, cadence, transitions, selection weights and rest remain protected throughout.

## What exists

[Current native-size catalog](idle-review-current.gif) · [Current frame sequences](idle-review-frames.png). These are rendered from the current production atlas, not proposed new artwork. The existing [idle report](idle-personality-validation.md) describes the earlier intent; [Frame Master](../framemaster.md) now sets the stronger reference/support/shape acceptance bar.

Resting idle is four entries: open hold2500ms, blink120/160ms, open hold2400ms, repeating. It has drawn eyelid changes but no distinct supported breathing/weight-shift acting. The remaining gestures have authored anticipation/action/recovery: swish9 selected entries; ears/sniff/stretch/groom/yawn/loaf/peek8 each; directional looks5 each. The importer substitutes canonical idle at first/last slots for the eight-pose stories. Those endpoints make identity consistent but cannot prove the adjoining turn/get-up is smooth. Normal behavior reserves six seconds per gesture/eight for loaf, while many drawings finish earlier and hold their endpoint. This quiet rest is useful; the new plan must not turn every pause into movement.

The review finds opportunities in connected support changes, torso/neck independence, slower readable acting at the main beat, and gentler head/ear changes into canonical rest. This is an author review, not proof every existing pose is defective. The prior frames remain the baseline until approved replacements beat them in native-size comparison.

## Reference comparison

The [saved video study](../references/motion/2026-10-23/video-pose-study.png) shows chest/pelvis changing phase around contact and settling. For quiet idles borrow weight transfer and delayed settling, not its leap, running tempo or second bound. The [spine study](../references/motion/2026-10-23/spine-flexion-study.jpg) supports a flexible stretch/gather, not a rigid bitmap squash. The silhouette collections inform clear seated, loaf, crouch and reach extremes; static images do not supply timing. Keep canonical white/pink/gray Neko, actual ground and head calibration. Expressions should remain visible across changing drawings and then reopen smoothly; do not stamp face glyphs or add decorative effects to hide stiff anatomy.

## Proposed performances

| Priority/action | Proposed action and transitions | Support/scale/acting | Initial pose budget and time |
| --- | --- | --- | --- |
| 1 · Resting idle | Supported quiet sit, small chest breath, asymmetric slow blink/reopen; occasional tiny ear response, then real stillness. | Paws/haunch stay planted; head volume/crown stable. Chest breath has a small drawn shape change, no whole-body scaling. Avoid constant rocking or moving all parts together. | 6–10 distinct drawings; roughly5–8s sparse loop with long rests. |
| 1 · Loaf | Notice comfort → shoulder weight lowers → forepaws tuck sequentially → complete loaf/slow blink → one paw unfolds → chest rises → supported sit. | Rear remains supported; forepaws disappear by occlusion, never multiply. Spine/shoulders change before tail settles. Exact last drawn get-up precedes idle. | 10–14 drawings; about5–7s, most hold at supported loaf. |
| 1 · Stretch | Shift weight forward → plant/reach forepaws → lower chest with hips high → extend one hind leg → gather under pelvis → raise chest and sit. | Anchor foretoes through pressure; hind extension follows pelvis. Separate chest/pelvis; preserve physical head/body volume outside the seated box. Effort squeeze across pressure/release, then relaxed eyes. | 12–16 drawings; about4–5.5s. Prototype lowest/longest shape first. |
| 2 · Groom | Look at one paw → transfer weight onto the other → lift/lick → same paw wipes cheek/ear → lower and plant → satisfied blink/reopen. | One lifted forepaw replaces its grounded version. Other forepaw and haunch support weight; torso leans slightly to counterbalance. No instant paw-side swap. | 10–14 drawings; about4–5s, lick/wipe readable. |
| 2 · Yawn | Heavy eyelids → small inhale/head lift → jaw opens through clear stages → full yawn → close jaw → soft blink/reopen → level head. | Seated support stays stable; mouth is drawn, head does not grow as jaw opens. Keep a tiny chest response; no exaggerated full-body stretch here. | 10–12 drawings; about3.5–4.5s. |
| 2 · Sleepy peek | Head settles → eyelids nearly close → one eye cautiously opens → ear leads a small curious look → both eyes reopen → slow return. | Supported sit/haunch throughout; do not cut from a deep loaf to a tall sit. Distinguish a sleepy peek gesture from the real sleep state. | 8–12 drawings; about3.5–4.5s. |
| 3 · Sniff | Ears notice → nose/head reaches → small nose/whisker response → curious tilt → neck eases back → blink/reopen. | Paws stay planted; neck/shoulders follow the head in smaller delayed motion. No torso shrink/recenter. | 8–10 drawings; about3–4s. |
| 3 · Ear flick | One ear notices → ear flick with slight head follow → opposite ear settles → tiny blink → rest. | Most of the supported body stays still. Independent ears and a restrained head response, not repeated whole-head bobs. | 8–10 drawings; about2.5–3.5s. |
| 3 · Left/right look | Eyes/ears lead → drawn head turn → small shoulder follow → interested pause → reverse through intermediate angles → front rest. | Same camera/volume; allow narrower perspective. Actual intermediate turn drawings, not horizontal bitmap movement. Preserve the two directions. | About8 drawings each with shared neutral;3–4s. |
| 3 · Lazy tail swish | Keep a planted, relaxed body; tail base initiates a soft sweep, tip catches up, then eases to rest. Blink between sweeps, not at every extreme. | One attached tail, unchanged seated/head registration. This is the quiet swish only; tail chase/catch are excluded. | 8–12 drawings;3–4.5s finite gesture. |

These are proposed budgets, not required sheet sizes or approved acting. Judge small sets of neutral/extreme/support/recovery keys before filling in-betweens. Resting idle, loaf and stretch provide the highest-value first checkpoint; complete them before expanding the remaining actions.

## Integration and acceptance

1. Show native-size color and face-hidden keys, plus entry/action/recovery at normal speed. Keep old/new comparisons. Reject weak support, volume drift, extra paws, rigid torso and insufficiently distinct extremes before expressions.
2. Use one batch calibration and measured support anchors. Review penultimate→neutral and repeat seams, not merely the substituted canonical endpoint. Full canvas/alpha/component checks complement visual anatomy review.
3. Prototype timing with the actual controller. Align each finite gesture's behavior deadline with its complete clip, then retain intentional quiet rest. No abrupt default6s cutoff or unnecessary replay. Tail chase/catch timings and weights remain exactly unchanged.
   Ordinary idle playback currently samples at100ms. Keep proposed key durations readable on that clock and verify native coverage; adding shorter source frames alone will not make them visible. Any proposed finer timer must be limited to the affected idle performance and measured for idle CPU cost, preserving the accepted50ms tail clock and long quiet holds.
4. Attach gesture thoughts only to their actual gesture and general idle thoughts to their separate timer. Never emit stale gesture lines after returning to idle. Keep quiet/sleep/fullscreen and readable single-bubble rules; logs must explain suppression/deferment.
5. Exercise pet/pickup interruption from the difficult poses using existing carry families/recoveries; nap/wake, hide/reduced motion, queued goodbye and game start wait for compatible support. Do not rebuild sleep/carry/game art as part of this scope.
6. Verify source/baked equality, preserved tail bytes/clips and unrelated behavior, native pose coverage, contact/head landmarks, transparent margins and flat current/previous release. Update source prompts/selections, previews, README and Frame Master findings with each verified slice.

Implemented after the user's approval: [validation and final timings](idle-refresh-validation.md), [synchronized old/new comparisons](idle-refresh-compare.html). Proposed budgets above remain design history. Rest uses a6.8s loop with a450ms blink after the user rejected the initial slow blink. Tail chase/catch remain unchanged.
