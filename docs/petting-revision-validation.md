# Expressive petting revision — 2026-10-22

![All twelve reactions at production timing](neko-pet-catalog.gif)

[Approved plan](../tasks/plan.md) · [Expression/gesture study](petting-expression-study.md) · [Exact ImageGen prompts and assembly record](petting-revision-prompts.json) · [All runtime pose slots](neko-pet-frames.png) · [Native light/dark rendering](neko-petting-native.png) · [Native measurements and release hash](petting-revision-native.json) · [Half-speed preview](neko-pet-catalog-slow.gif)

## Behavior delivered

All twelve reactions have dedicated revised drawings, individual acting and complete recovery. Tiny blep is replaced by playful rolling in the same twelve-reaction rotation. Short connecting movements, expression/contact holds and supported releases provide the added time. Expressions combine eyelids, ear direction, mouth and supporting posture; a wink or excited squeeze is a brief accent rather than a permanent happy face.

| Reaction | Source slots | Duration including idle handoff | Story and specific visual review |
| --- | ---: | ---: | --- |
| Head pats | 16 | 2.80 s | Forehead invitation, gentle compression and smaller second dip; soft partial lids, pressure-softened ears and quiet mouth. Review forehead/head volume and gradual lid reopening. |
| Cheek nuzzle | 20 | 3.70 s | Cheek lean/press, small curved rub, contact-side eye softness/wink and gradual shoulder release. Recovery drawings ordered by decreasing tilt to remove an unwanted second lean. |
| Kneading | 24 | 5.80 s | Supported bent-foreleg stance, four finite left/right pressure pairs, quiet head and relaxed straight upper lids. The upright cycle was redrawn lower; transition poses causing a head dip/jump were excluded. Review both attached forelegs, alternating support, loop seam and seated recovery. |
| Chin scritches | 16 | 3.00 s | Chin presents upward, soft closed eyes during contact, small pressure shifts and gentle lowering of the connected neck. No large smile or long neck. |
| Playful roll | 24 | 5.80 s | Side to belly-up, small wriggle, opposite-side recovery and supported push-up. Curiosity and brief playful eye squeezes. Review four anatomical limbs with natural occlusion and continuously attached tail; this is separate from the sleepy flop. |
| Paw offer | 20 | 3.60 s | Transfer onto supporting foreleg, offer the other paw, small wrist beckon, wink, withdrawal and placement. Review empty space beneath the lifted foreleg and no duplicate grounded forepaw. |
| Ear rubs | 16 | 2.95 s | One-sided ear melt and closed eye, opposite eye partly open, gentle pressure and ear perk before centering. Select a near-neutral softened-lid anticipation drawing to avoid an oversized early tilted head. |
| Front stretch | 24 | 5.20 s | Farther forepaw steps, low chest/high hips, extra toe/reach effort and relaxed release. Excited eye squeeze becomes relaxed lids. Head-scale repair and a separately drawn eight-pose recovery replace shrinking late drawings; registration uses the neutral head/body reference of each source batch. A contaminated hold drawing is rejected in favor of the adjacent complete clean pose. |
| Back arch | 24 | 4.90 s | Supported stand, gradual rounded spine, effort squeeze, delayed tail lift, relaxed lids and unrolling into sitting. Review comfortable ears/fur and four-paw support, distinct from the reaching bow. |
| Three tiny hops | 28 | 5.00 s | Three separate crouch/takeoff/air/contact/compression passages; the second is slightly higher, the last smaller. Excited eyes at each apex, attentive eyes around landing, then supported sitting. |
| Side flop | 28 | 6.80 s | Ease onto side, brief closed-eye snooze with a small breath, one-eye wink/peek, waking, planted-forepaw rise and drowsy seated settling. Remains a pet state rather than entering the real nap state. |
| Shoulder peek | 28 | 6.40 s | Left glance, center, right glance, drowsy forward look, opening/closing yawn, closed-mouth half-lidded deadpan and gradual reopening. Review natural neck limits, planted paws and both glance directions. |

Counts are source slots, not promises that every neutral/held drawing is unique. There are 268 source slots plus twelve appended canonical-idle entries: 280 pet atlas entries and 427 total entries. The final source slot selects its generated neutral calibration drawing again to remove incidental endpoint size drift, before the separate actual-idle handoff. Complete body recovery precedes this seated neutral. The old unconditional penultimate canonical blink substitution is removed.

## Scale and desktop placement

The transparent drawing canvas is now 192 × 112. This adds horizontal motion room while retaining the approximately 62px seated head width, 82px seated body height and existing ground line. Each sequence retains fixed calibration throughout its motion; a wider stretch/tail cannot trigger whole-body shrinking.

Source contact coordinates are calibrated relative to the actual idle head center. This removes rest-position shifts caused by differences in the generated tail/haunch width. A new regression reproduced misalignment in five reactions, including a six-pixel back-arch shift, before the shared registration correction. Last drawn neutral head positions now match idle within two pixels; their head widths and crown height retain the existing scale checks.

Grounded reactions register support contacts; stretches/arch use rear support, hops use the head axis with three deliberate small lift arcs, and roll uses a calibrated silhouette-center track. The window remains stationary during petting. Existing saved positions retain the original 112px sprite-origin convention through a 40px horizontal offset, so ordinary saved visible positions round-trip across versions. Monitor clamping still reserves the expanded drawing area at screen edges. Tray icon extraction crops out the extra transparent padding.

## Art and preview review

Built-in ImageGen generated/edited the artwork. The exact prompts, generated source identities, rejected passages and final frame selections are recorded in the linked JSON. Extraction/packing tools select complete connected silhouettes and register/resize existing drawings; they do not paint replacement anatomy or expressions.

Reviewed every selected source pose and imported runtime pose, including adjacent handoffs and the kneading cycle seam. Review checks covered one head, connected torso/neck, two anatomical forelegs and two hindlegs with sensible occlusion, one attached tail, intact paws/ears, facial continuity and transparent margins. No extra limbs or detached parts were observed in the accepted passages. This is a visual assessment, not an automated guarantee.

The catalog uses actual Clip timing at 20 FPS, with 0.8 seconds of idle first and enough time after the longest reaction for live idle. Its duration is derived from clip length (currently nine seconds), preventing truncation of flop/peek recovery. Contact sheets preserve pixel aspect and native size. Native Qt captures are shown on light/dark backgrounds. Normal-speed and slowed/ordered-frame previews expose timing, support changes and the return to idle.

## Verification record

- Initial regressions reproduced the retired blep/short-story durations and a queued reaction starting before the new long flop could finish.
- Focused checks pass for approved duration budgets, finite clips, complete pose order, real idle endpoints, head scale/alignment, clear canvas edges, three airborne arcs with contacts between them, four kneading pairs, quiet cycle head position and drawn recovery.
- An isolated in-memory mutation reversed the new support/head calibration sign; the head-alignment regression rejected it in eight reaction subtests. Production files were unchanged.
- All 147 non-pet runtime drawings compare pixel-for-pixel with the baseline after removing the new transparent horizontal padding. Every non-pet clip definition/cadence is unchanged, including the accepted tail games.
- Full discovery: 149 tests run, 147 passed and two opt-in packaging checks skipped. This includes long-pet/queued-nap behavior, saved-origin compatibility, dragging, hiding, reduced motion, startup/drop, speech transparency and the accepted tail behavior.
- Final native Windows event-loop playback observed all 280 pet pose entries across all twelve reactions, at median paint intervals of 49.85–50.03 ms on the available display (DPR 1.0). The window did not move; a queued pet waited through the long flop, counts remained correct, and the saved visible origin round-tripped.
- Native hit-testing confirmed both transparent side margins pass through to the desktop while the kitten remains clickable. All four real screen-corner clamp checks passed. Tray framing retains the original icon footprint.
- Final light/dark review caught a detached 16-pixel line beside stretch pose 14. A new connected-fragment regression reproduced it. That drawing was rejected and its slot selects the adjacent clean held stretch pose; no anatomy pixels were painted or deleted. The new all-pet fragment check and existing all-pose clipping/head-alignment checks then passed (three checks). The corrected stretch was replayed natively: all 25 entries observed and its light/dark capture refreshed.
- Final catalogs decode to nine seconds at production speed and eighteen seconds at half speed. Every used pose is covered by the 50 ms sampler; all complete actions have idle afterward. Contact sheets retain pixel aspect.
- PyInstaller build passed. Both packaged checks passed against the final executable: native startup/tray/topmost window, clean second-instance rejection, required artwork/modules and no bundled credentials/foreign ICU. All twelve packaged pet sheets hash-match the final working-tree PNGs, including the corrected stretch. Test-owned executable processes were stopped afterward.

The new executable is `dist/expressive-petting/DesktopNeko.exe`. Earlier builds remain separate. Quit an older Neko before launching it, because the single-instance lock intentionally prevents duplicate companions.

## Limits

Native checks use the available Windows display. Physical mixed-DPI/multi-monitor hardware and long-session resource behavior have not been exercised. Anatomy/expression authenticity still depends on visual review; numerical timing/boundary checks cannot establish it alone.
