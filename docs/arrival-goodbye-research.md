# A little visitor: entrance and goodbye research

2026-10-23 · Research and proposed design, not implemented or animation-validated.

## What needs to change

Neko should seem to have noticed the desktop, chosen to join you, and chosen to leave. The charm should come from her attention and physical decisions, with enough time to read her face at desktop size.

I reviewed the current clip/controller code, the [used pose catalog](neko-tail-life-source-frames.png), [lifecycle notes and scene preview](tail-lifecycle-notes.md), [first-visible-tick correction](startup-thought-validation.md), [recent gallop lessons](run-timer-sleep-fix.md), and [startup performance evidence](startup-performance-validation.md).

Verified from current code and the catalog:

- Arrival lasts 1.9s. Its first three airborne drawings occupy 700ms while the window travels down from the monitor top. The next drawings already include contact, compression and recovery; those ingredients exist, but the initial action has little visible intention or changing airborne silhouette.
- Goodbye lasts 2.15s. The first two sad drawings take 1.0s, followed by a 200ms crouch and a hop. This makes sadness the longest acting beat. Whether that feels guilt-inducing is an artistic interpretation, not a measured user finding.
- Arrival moves the actual window. Departure instead applies `-96*p + 208*p*p` inside the fixed sprite canvas and does not move the window. Its disappearance therefore comes from local canvas cropping, rather than reaching a monitor boundary. Extending the same offset cannot supply a convincing physical exit.
- The current `arrive`/`depart` controllers own playback and bypass ordinary custom movies. Existing transition, saved-position and reduced-motion behavior must survive a redesign.

## What the research suggests

| Evidence | Application to Neko |
| --- | --- |
| Animation Mentor describes anticipation as both physical preparation and preparation for a new idea. A glance or a crouch can tell us what a character is about to do. [Anticipation, Chris Hurtt](https://www.animationmentor.com/blog/anticipation-the-12-basic-principles-of-animation/) | Give her a visible look toward the landing or exit before travel. A crouch must build the energy of the actual jump. |
| Its overlap tutorial recommends establishing the main body action before offsetting appendages, and checking that overlap does not make the character float. [Overlap and follow-through](https://www.animationmentor.com/blog/tutorial-animate-overlap-and-follow-through/) | Land the body first; let ears and tail catch up in small, diminishing movements. Avoid a second large body bounce just to make her lively. |
| Its secondary-action discussion distinguishes expressive acting from mechanically trailing appendages. [Secondary action, Kevin Koch](https://www.animationmentor.com/blog/secondary-action-the-12-basic-principles-of-animation/) | A final look back communicates attachment; a trailing tail communicates momentum. Give each its own readable beat. |
| A controlled study of seven cats landing from different heights found substantial forelimb loading and describes forelimbs making initial contact. [Wang et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6857581/), [abstract](https://pubmed.ncbi.nlm.nih.gov/31737447/) | Stage forepaw contact, yielding shoulders/elbows, then hindquarter settling. This is a mechanics reference, not a prescription for every stylized landing. |
| Experiments found more eye narrowing in response to human slow blinking and greater willingness to approach after a slow-blink interaction. [Humphrey et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7536207/) | A softly drawn slow blink is a plausible friendly goodbye. It does not scientifically establish that a cat is saying “I love you”; that meaning in our scene is artistic interpretation. |

These sources support the movement and communication choices. The stories, timing and appeal below are design proposals, not research results.

## Directions considered

| Direction | Entrance / exit | Decision |
| --- | --- | --- |
| **Curious little visitor** | Peek from the top, commit to a soft landing, acknowledge you / affectionate glance, gather, hop out, tail last | Recommended. Uses the desktop boundary as part of her world and gives the pair a relationship. |
| Eager little show-off | Confident dive, tiny controlled landing adjustment, proud head tilt / jaunty sideways bound | Possible later variant. More energetic, but close to the cursor game's existing excitement. |
| Sleepy neighbour | Drowsy arrival and tiny stretch / warm, heavy-lidded farewell | Good mood variant later. A sleepy performance on every startup would misrepresent an otherwise alert kitten. |

Parachutes, portals, sparkles and floating hearts would require props/effects and make the character's acting less central. Repeated pleading, falling panic and a comic crash would undermine the comfortable companion feeling. These are deliberate scope choices, not technical impossibilities.

## Recommended entrance: “Oh! There you are.”

Proposed total: **about 1.9–2.1s from first visible animation paint**. Show the first pose promptly; this animation must not add another loading stage to the measured 2.14s packaged startup.

| Beat | Target duration | Visible acting and physical support |
| --- | --- | --- |
| Peek | 300ms | A paw and curious face lean into view at the monitor's top edge. Eyes look toward the landing. The edge pose must show credible forepaw support, with the remaining body above the edge—not a detached floating face. |
| Decide | 200ms | Small head tilt, ears come forward, forepaw grip releases. This leads directly into descent without teleporting the torso. |
| Drop | 550–650ms | Start gathered, open the forelegs toward contact, keep hind legs tucked until needed. Tail trails the torso. Confident concentration, with a readable brief eye squeeze before contact rather than a frozen wide-eyed falling pose. |
| Catch the weight | 200ms | Forepaws arrive first; elbows/shoulders yield as hind paws find support. The face remains above the floor. Body volume is preserved through drawn joint changes. |
| Recover | 250ms | Hindquarters settle, spine rises and forepaws return into the seated support. Only a tiny body overshoot; tail catches up afterwards. |
| Recognize you | 400–500ms | Look out toward the viewer, small contented eye squeeze, then reopen into the actual canonical idle. The smile reads after landing, when she is stable. |

The emotional payoff is a tiny “I meant to do that” look after an impressively soft landing. A bigger bounce would steal attention from it.

The top-edge peek is the highest-risk new pose. Prototype its support, occlusion and retained-size silhouette before commissioning the full sequence. If it reads like dangling distress or needs anatomy distortion, use a clear head-leading look into the scene during the first descent poses; keep the rest of the story. This fallback remains a proposal.

## Recommended exit: “See you in a bit.”

Proposed total: **about 1.6–1.9s**. Closing remains prompt and dependable.

| Beat | Target duration | Visible acting and physical support |
| --- | --- | --- |
| Acknowledge | 400–500ms | From a compatible supported sit, one small head tilt and a soft slow blink, with reopening. No second-long sad stare. |
| Choose the way out | 250ms | Eyes lead a small turn toward the exit, then shoulders follow. Tail tip curls. Keep all support changes connected. |
| Gather | 250ms | Shift weight through planted forepaws into bent hind legs. Tail counterbalances; the push comes from the hindquarters. |
| Little hop | 700–900ms | A shallow up-and-forward arc becomes a downward exit through the chosen monitor's bottom edge. Move the actual window; retain the full sprite inside its canvas until the monitor edge occludes it. |
| Tail goodbye | 150–250ms within the final travel | Her attached tail is naturally the last visible part to cross the edge. No detached tail effect, reverse pop-back or additional farewell delay. |

The final tail movement is a physical continuation of the same hop. It should feel like she has gone somewhere, rather than the application cropping her off. Near a side edge, mirror the lateral component inward. Travel duration can adapt within its budget to the distance from the saved position; first preview both a kitten near the bottom and one high on the monitor. If a very long drop reads as a dangerous fall, revise the exit route before approving it rather than speeding a long path unnaturally.

A lifted-paw farewell could become a later alternate, with the other three limbs visibly supporting her. First make this one complete pair work. A different face pasted on the same hop is not a second animation.

## Production and runtime contract

- **Artwork budget:** prototype the top peek, forepaw landing/compression and exit's turned crouch first. Tentatively allow 20 entrance source slots and 16 exit slots, including calibration/recovery drawings. These are planning ceilings to review, not a demand to retain bad or redundant frames. No artwork generation is authorized by this research document.
- **Identity:** retain the 192×144 fixed canvas, about 62px head/82px seated reference, original palette and true alpha. Calibrate a batch once. Keep four accounted-for limbs, two ears and one attached tail; naturally occluded limbs stay hidden. No per-pose resizing or lettering over the eyes.
- **Motion ownership:** world movement belongs to the window trajectory; drawn limb movement and tiny settle offsets belong to the sprite. Do not apply the same jump arc twice. Clip at the selected monitor's actual geometry, including a neighbour above or below it. Do not introduce a screen-sized overlay, floor graphic, pointer capture or focus change.
- **Persistence:** retain the landing/resting origin independently from temporary animation coordinates. Saving during either transition must use that origin. The new exit needs this protection too; currently only arrival has a dedicated saved target.
- **First paint:** retain the existing first-animation-tick clock rule; preferably establish it for both lifecycle clips. Greeting text follows the entrance recovery. No new dialogue is necessary for the performance to work.
- **Competing activity:** games, care reactions and normal idles must not take over during lifecycle playback. Reset ordinary deadlines only after arrival reaches canonical idle. Show-from-tray keeps its current immediate behavior; do not replay a full startup on every visibility change.
- **Closing from other states:** do not snap a held, stretched or sleeping kitten into the new seated first frame. Reuse a short compatible supported recovery where available; if that would exceed the close budget or has no verified bridge, close immediately. A sleeping kitten need not be woken to perform a goodbye. Repeated quit must not restart or queue the sequence.
- **Interruptions:** hide/fullscreen hiding, reduced motion, monitor removal and quit during arrival must restore the saved origin and cancel transient state. Hidden/reduced-motion exits stay immediate. OS shutdown must not wait for the full performance. No new settings are needed.
- **Startup cost:** keep build-time baking. Regenerate the packed atlas whenever art/import registration changes; compare it with source import. Do not move source-sheet analysis back to launch for these sequences.

## Ordered implementation proposal

1. **Geometry and key-pose trial.** Prototype edge support, landing and exit crouch at native size; make a simple monitor-scene trajectory trial from high/low resting positions. Acceptance: coherent support, no canvas cropping before screen-edge occlusion, a comfortable exit within the close budget. Highest-risk decisions precede full art.
2. **Complete entrance.** Author connected drawings through actual idle; add trajectory and first-visible timing without changing accepted pet/run/carry clips. Acceptance: contact matches the landing position, face reads on light/dark desktops, no head/scale pop at idle. Review full-speed and half-speed preview before proceeding.
3. **Complete exit.** Author the blink/turn/gather/hop; add real travel, origin persistence and interruption handling. Acceptance: tail-last edge crossing, no local rectangle erasure, no saved-coordinate drift and a bounded close from arbitrary states.
4. **Focused release verification.** Check source/packed equality, unaffected frames/timing, lifecycle phase boundaries, delayed first paint, edge clipping, input/focus, hide/motion/fullscreen/monitor-change/quit paths and package resources. Observe real Windows painting, not a second timer driving the animation. Re-measure startup separately from animation completion. Preserve the verified executable and follow the flat current/previous release layout.

Likely files: `animations.py`, `main.py`, lifecycle assets, `test_animations.py`, `test_main.py`, packaging tests and build-time bake, preview tools, prompt/assembly records and README. `behavior.py` changes only if the existing lifecycle states cannot express the agreed behavior; no new general animation framework is proposed.

## Evidence boundaries

This research inspected current source and the existing pose catalog and consulted primary animation teaching and original feline studies. It did not generate new drawings, modify playback, run new native animation tests or replace the executable. Suggested timings, art budgets, emotional readability and edge choreography require prototype validation. Physical multi-monitor/mixed-DPI behavior remains unverified. Historical validation reports and unfinished work are preserved.
