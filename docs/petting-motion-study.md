# Petting motion study

Implemented in the later [twelve-reaction rebuild](petting-rebuild-validation.md). The findings below record the old set and the proposal that guided that work.

Study of the current twelve reactions, using the accepted tail chase as the quality reference. This is a proposal for the upcoming QOL work; no runtime behavior or artwork was changed.

[Current pet playback](neko-pet-catalog.gif) · [All 48 runtime pet poses](neko-pet-frames.png) · [Accepted tail playback](neko-tail-reference-preview.gif)

## Findings

The petting set can reach the tail chase's quality through connected drawings, clearer weight changes and individually paced reactions. Increasing the repaint rate alone would continue displaying the same four poses for long stretches.

I inspected all 48 imported pet poses, including enlarged kneading, paw-offer, hop and flop sequences, and traced their atlas import, playback, selection and return to idle. I also evaluated the clip timelines programmatically against the actual runtime frames. There are no custom GIF overrides in the current assets.

| Current property | Petting | Tail chase |
| --- | --- | --- |
| Distinct runtime drawings per reaction | Four | Eighteen, including entry/recovery; eleven form the run cycle |
| Frame timing | Mostly 350–1,100 ms holds; hop includes 300 ms | Running poses change every 50 ms; entry/recovery use longer holds |
| Repaint interval | 100 ms / 10 FPS | 50 ms / 20 FPS |
| Overall structure | Eleven one-shots; kneading loops | Anticipation, five turns, deceleration, seated recovery |
| Exact shared idle drawing at both ends | None of the twelve | Yes |

The tail chase has 63 timed entries over 4.69 seconds. Repeating its eleven-pose cycle creates five readable turns. Its entry and recovery also explain how the kitten changes posture. That combination is the useful reference: coherent silhouettes, movement between key poses, and timing suited to the action.

The current pet set was deliberately built under a four-drawing constraint. Some clips reuse those drawings in reverse or return to their own first pose, which adds timed entries without adding intermediate anatomy. The new smoothness target calls for revisiting that earlier drawing budget.

### Timing and transitions

All twelve occupy a nominal 5.8-second pet state. For the eleven one-shots, the last drawing starts roughly 1.6–3.25 seconds in, then stays still for the remaining 2.55–4.2 seconds. Head pats, for example, change only three times and reach their last drawing at 1.7 seconds. Cheek nuzzle reaches its last drawing at 1.6 seconds. A relaxed pause is appropriate, but these long holds suppress the normal idle blink until the pet state ends.

These are ideal clip thresholds, not measured display deadlines: the repaint interval and 500 ms behavior tick can delay visible changes and state completion. A sleep deadline or another click can also interrupt a reaction.

All twelve starting and ending images differ pixel-for-pixel from canonical idle, despite their previous head-size calibration. The size correction should be retained; it does not by itself guarantee matching face shape, body posture or planted-paw positions at the handoff. Back arch starts standing, making its entry particularly important.

Every new click currently chooses the next reaction and resets the pose clock immediately. A click during a flop or airborne hop can therefore cut straight into another reaction's starting pose. Smooth single-click playback and smooth repeated petting need separate verification.

## Distinct direction for every reaction

Drawing budgets below are storyboard estimates, including entry/recovery. Shared idle can be reused. They are not quotas or approved replacement assets.

| Reaction | Current opportunity | Proposed motion and identity | Initial drawing budget |
| --- | --- | --- | --- |
| Head pats | Mostly a smile/blink; little sense of receiving a pat | Forehead rises toward the palm, head compresses slightly into a contented dip, then eases upright. A small vertical head movement with seated paws fixed. | 8 |
| Cheek nuzzle | Large alternating tilts with few connecting poses | Turn toward one cheek, lean sideways into the imagined hand, briefly press, then ease back. Emphasize lateral cheek contact rather than rocking both ways. | 10 |
| Kneading | Four-pose loop includes neutral/open-eye resets; weight transfer is weak | Lean shoulders forward, alternate left press/release and right press/release for two or three cycles, then tuck both paws back. Keep the hindquarters settled and the expression relaxed through the cycle. | 8-pose cycle plus entry/exit, about 12 total |
| Chin scritches | Similar smiling seated silhouette to head pats | Lift the nose and extend the neck gradually, half-close the eyes, add a tiny chin adjustment, then lower the head. Its defining movement is upward chin presentation. | 8 |
| Tiny blep | Small mouth change competes with the other closed-eye smiles | Curious pause with eyes open, tiny tongue appears, one blink, tongue retracts, then a small shy look. Keep the body quiet so the face carries this reaction. | 6–8 |
| Paw offer | The raised paw is small and close to the body; the reach is hard to follow | Shift weight onto the supporting forepaw, lift the same opposite paw, extend it slightly forward, hold, then withdraw and place it down. One offered paw, with a continuous shoulder-to-wrist connection. | 10 |
| Ear rubs | Both ears flatten in a similar happy-face sequence | Turn one ear toward the hand, soften that ear while tilting the head, make a small settling adjustment, then perk the ear and return. Keep it asymmetric and gentle. | 8–10 |
| Front stretch | Seated-to-bow changes cover too much distance in one step | Rise, walk the forepaws forward, lower the chest while keeping hips high, hold the extension, then retract and sit. The forepaw reach and long body line distinguish it. | 12 |
| Back arch | Standing entry and sparse spine changes can read as another generic stretch | Transition from sitting to a supported stand, round the spine gradually, lift the tail with a slight delay, then relax and sit. Keep four paw contacts through the arch and a comfortable expression. | 10–12 |
| Tiny hop | One airborne pose holds for 350 ms; takeoff and landing are under-described | Notice the pet, crouch, extend into takeoff, tuck at the apex, descend, contact the floor, compress, rebound slightly, then settle. Keep it a small joyful vertical hop. | 12 |
| Side flop | Descent has a useful progression, but recovery reverses those same drawings | Shift onto one hip, lower through the elbow and shoulder, rest on the side, then use a separate forepaw-supported push-up to sit again. Preserve the slow, trusting mood. | 14–16 |
| Shoulder peek | Sparse head turns; shoulder involvement is limited | Rotate ears/head toward the shoulder, let the shoulder follow a little, hold the backward glance, then unwind in the opposite order and blink toward the viewer. Paws remain planted. | 10–12 |

The important distinctions are physical: forehead dip versus chin lift; lateral cheek press versus one-ear tilt; alternating paw pressure versus a single offered paw; forward extension versus a rounded spine; quick vertical energy versus a slow sideways release. Facial details should reinforce those actions rather than substitute for them.

## Motion rules for the rework

- Use the same canonical idle at entry and final recovery, with drawn transitions for sitting-to-standing and sitting-to-lying changes. Retain the 112 × 112 transparent canvas and established head scale.
- Position planted paws and the torso deliberately. The importer currently centers cropped silhouettes, so a changing tail or extended paw can influence placement; a fixed canvas alone does not establish a stable body anchor.
- Start by matching the tail's 50 ms repaint interval for pet playback, while assigning pose holds to each action. Test roughly 80–150 ms connecting poses and longer expressive holds; tune the final timing against that repaint cadence. Calm scritches should remain calm.
- Spend drawings where movement changes direction, contact or weight. Hop needs ascent, descent and compression; flop needs a separate recovery. Similar consecutive smiles do little for either.
- Let settled reactions return to the normal blink/rest once their recovery completes. Treat the current 5.8 seconds as an interaction budget to review, rather than stretching every gesture to fill it with a still frame. Kneading can use a limited repeating cycle.
- Review repeated-click behavior explicitly. A reasonable pilot is to acknowledge every click immediately with the existing palm stroke, preserve landing/get-up during vulnerable poses, and retain at most one pending reaction. This is a proposed interaction change to evaluate, not an implemented queue.
- Keep anticipation short enough that a pet feels immediate. The current nine-frame palm stroke lasts 630 ms; the kitten should visibly respond while it is happening.
- Preserve reduced motion, sleep/wake behavior, dragging separation, shuffled twelve-reaction coverage, quiet controls and the accepted tail animation.

## Anatomy and visual acceptance

Review every proposed pose at actual desktop size and enlarged, then every neighboring pair in motion. A kitten has four anatomical legs and one attached tail; occluded legs should stay hidden rather than being drawn as extra visible feet. Automated frame counts cannot certify this.

The highest-risk passages are alternating kneading forepaws, lifting the offered paw without retaining its grounded duplicate, tucked hop legs, landing contact, and the flop's overlapping legs during recovery. Track each limb through those passages. Check tail attachment, shoulder/hip origins, continuous limb connections, head volume, face direction and clean outline changes as well as total limb count.

Use stationary ground-contact guides to catch paw sliding. Check ears, tail, paws and shadows for clipping throughout the 112 px canvas. Compare idle → reaction → idle and reaction → repeated pet at normal speed, half speed and by stepping poses. Include light and dark desktop surfaces. A pose can be anatomically valid and still be a poor transition to the next drawing.

## Implementation sequence to propose

1. **Storyboard and pilot cheek nuzzle plus tiny hop.** They cover subtle contact and full-body weight changes. Put canonical idle at both ends and establish acceptable timing and anatomy before commissioning the remaining set.
2. **Rebuild by motion family.** Face/contact reactions, paw reactions, then standing/airborne/lying reactions. Review the twelve together for repetition, not just each in isolation.
3. **Integrate complete sequences.** Update `CLIPS`, pet sheet import/head calibration, pet repaint cadence and completion behavior together. Address repeated-click handoffs against the chosen policy. Preserve the tail cycle unchanged.
4. **Verify and package after visual acceptance.** Update tests and previews to cover every used drawing, rather than retaining four-frame assumptions. Check all reactions, entry/recovery and interruptions before building the executable.

The main implementation touchpoints are `animations.py` (clip timing, sheet import, `PET_HEADS` and anchoring), `behavior.py` (pet duration/selection), `main.py` (render cadence, pet restarts, palm/heart timing), the preview helper, animation/behavior/desktop tests and packaging asset assertions. Some current tests explicitly require four drawings or assume the atlas contains 195 entries; these must follow the new approved assets while preserving the scale, clipping and selection checks. Additional pose rows must receive the same sequence calibration rather than falling into another import path.

## Scope of this study

This assessment used the current source, actual atlas images and existing playback catalogs. No artwork was generated, no runtime files or settings were changed, and no executable was rebuilt. Suggested timings, drawing budgets and repeated-click policy still require a pilot; the study does not claim a new set has passed anatomy or native playback verification.

Six focused baseline tests passed: current head scale, unclipped pet poses, the existing four-drawing sequences, twelve-reaction rotation coverage, non-consecutive selection, and desktop state-to-clip selection. These establish existing behavior to preserve; they do not measure perceived smoothness or certify anatomy.
