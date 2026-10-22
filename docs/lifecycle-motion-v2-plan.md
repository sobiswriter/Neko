# Lifecycle motion v2 — body mechanics before expressions

2026-10-23 · Revised plan following the user's critique and supplied motion references. Subsequently authorized and implemented: [delivery and evidence](lifecycle-v2-validation.md).

Latest user direction: **one graceful leap for each action, with diagonal entry and exit**. Arrival may enter through the side along its diagonal rather than appearing directly above home. Landing compression recovers under support; it must not become a second airborne bounce. Departure has one push-off and one arc.

Final expression direction: “Let her go” should make her sad before she gracefully takes her exit pose. Replace the cheerful last-look acting with gradually lowered ears, soft heavy eyes and dipped head, a slow subdued blink/reopen, then supported turn/steps into the crouch. Give the expression700ms to read and draw the transition through the body; keep one leap afterwards. Final departure budget2.20s/20 selected entries supersedes the earlier1.5–1.9s target below.

## What the previous pass missed

The delivered visitor build is a technical baseline: clocks, native pose coverage, boundary clipping, saved origin and packed resources were verified. The user rejected its animation quality. These are different judgements; passing 115 tests and painting every pose did not establish convincing weight or imagination.

The body silhouettes in the delivered entrance and exit stayed too similar across major beats, especially in flight. Front-biased views hid useful spine and chest/pelvis changes; much of the apparent movement came from moving the window. The smile and blink were drawn, but the physical performance needed a stronger redesign. The next pass must be recognizable with the face hidden.

All supplied material is now in [the permanent reference library](../references/motion/README.md). The actual 4.18s video, rather than its misleading filename, is the principal movement reference. The spine page and silhouette sheets provide complementary shape studies. Detailed observations and source timestamps are in that index.

## Change to the production method

Before a full sheet, prepare approximately eight **key poses per action**, with a simple support map for each. Use a side-biased three-quarter view during the mechanics, with an authored turn into Neko's familiar front-facing idle. This is a camera/pose choice for these actions, not a redesign of her face.

Each pose brief must identify: head, chest and pelvis; concave/convex/neutral spine; which feet carry weight and which are swinging; planted contact positions; tail phase; and the next force/weight change. A broad torso outline with four decorative feet is not a solution. Judge the keys in silhouette at native size, then judge their transitions at normal speed. Add connecting drawings according to the actual gaps in the movement, not to fill a fixed four-by-five sheet. Only then polish expressions.

## New drop-in: reach, fold, settle into composure

Drop the current prolonged crouch floating near the top. Start with the kitten already committing to a small diagonal entry, as in the reference. The landing is the event, rather than a seated face waiting for a window to move.

| Key | Physical action | What makes it read |
| --- | --- | --- |
| A1 · Enter | Forequarters lead down the diagonal; rear legs and tail trail. | A clear extended line of action, different from a sit or crouch. No bitmap elongation. |
| A2 · Reach | Forelegs reach toward the landing as chest and pelvis remain separated. | Long/short limb spacing and negative space change; head stays recognizable. |
| A3 · First support | Forepaws plant; elbows start yielding; rear is still high. | Paw contacts remain fixed while the body continues toward them. |
| A4 · Fold | Shoulders lower; back rounds; pelvis follows through. | Distinct chest/pelvis phase delay, not a whole-sprite downscale. This is the video’s roughly 0.6–0.8s lesson. |
| A5 · Gather | Hind feet arrive beneath the mass, completing a compact supported landing. | All four legs accounted for, a readable folded spine and no extra paw silhouettes. |
| A6 · Release | Supported joint extension lifts the chest out of compression; tail still catches up. | Paws retain support. No second airborne hop or bounce. |
| A7 · Compose | Hindquarters settle into a sit; forepaws step/plant into their final positions; head turns toward the viewer. | A drawn support change and turn, not a cut to canonical idle. |
| A8 · Attitude | A small pleased head lift and eye squeeze, then reopen to actual idle. | A brief “yes, I meant to do that” finish after the body earns it. |

Expression progression: attentive reach → a brief effort squeeze through the changing contact/compression drawings → pleased recovery. The squeeze spans multiple moving poses rather than freezing one sprite. Ears and tail respond to the main movement with a short delay; they do not all reverse at the same instant.

Working timing target: approximately 1.7–2.1s from first visible paint. Most time belongs to the physical action; the final face beat is around 250–350ms. Entry height and fall timing must be tried together on an actual monitor, rather than attaching a fixed extreme pose to any arbitrary travel curve. Keep one world trajectory and no double-applied body arc.

## New drop-out: look back, wind up, push and unfold

Replace the nearly upright crouch and suspended flight with a compact cat preparing a proper leap. Affection should appear in a quick look back while she is doing something, not as a long goodbye pose disconnected from the exit.

| Key | Physical action | What makes it read |
| --- | --- | --- |
| D1 · Decide | Head looks toward the way out; shoulders begin the turn. | Eyes/head lead, torso follows through authored turn poses. |
| D2 · Last look | A short over-shoulder look back/soft blink while feet settle into support. | The friendly beat belongs to the turn; no pleading expression. |
| D3 · Wind up | Rear lowers, spine rounds and weight shifts onto the planted hind feet. | A tiny deliberate hindquarter adjustment; paw contacts explain where the push will come from. |
| D4 · Push | Hind legs extend from their planted contacts; forelegs lift first. | Energy visibly releases from the crouch; feet do not slide backwards as the window moves. |
| D5 · Stretch | Body opens into a long, clear diagonal airborne shape. | Chest/pelvis separation and opened limb spacing, using the silhouette/spine references. |
| D6 · Gather | Spine folds and hind legs tuck under the body as the arc turns downward. | A strong contrast to D5; tail follows rather than being the only moving part. |
| D7 · Reach out | Forelegs lead the descent beyond the chosen monitor edge; pelvis follows. | The body keeps articulating right through the boundary. No local rectangular crop. |
| D8 · Follow through | The attached tail sweeps after the departing body. | A consequence of the body's motion; no detached tail effect or arbitrary late flick. |

Working timing target: approximately 1.5–1.9s. A short effort expression can span push/gather poses; reopen before the final reach. The intended read is a springy, self-directed little departure.

The reference's final exit is a walk to the right, not a filmed drop-out. The proposed leap combines its changing departure silhouette with its earlier bound and the supplied spine mechanics. This combination is a new acting choice that needs testing; it is not a motion sequence already validated by the reference.

Prototype near-bottom **and high** resting positions before fixing the route. For a high perch, test an inward diagonal toward a nearer side boundary as well as the bottom route; select the route with credible pacing within the close budget. Do not preserve a bottom-only rule by firing her across an entire monitor in a fraction of a second. Near-edge direction must keep the anticipation readable before she crosses the boundary. Route choice is a prototype decision, not a shipped feature or an invitation to add settings.

## Non-negotiable checks before full production

1. **Silhouette gate:** without eyes or mouth, a viewer can distinguish reach, contact, folded compression, extension and recovery. Review at actual desktop size. Similar silhouettes under different window positions fail this gate.
2. **Weight gate:** first contact changes the next pose; feet that support the body stay planted; chest and pelvis do not move as a rigid block. Review slow and normal-speed playback, including side-by-side extreme poses.
3. **Identity gate:** preserve head construction, physical volume, palette and four accounted-for limbs. Torso/spine deformation is allowed and required where appropriate. No arbitrary per-frame fitting or anatomy changes to meet a bounding box.
4. **Space gate:** fit the full stretched/tucked extremes at retained character scale before choosing the source-cell or runtime canvas. The present 192×144 is a starting constraint, not permission to clip or shrink the hardest pose. Any proven need to change the fixed canvas requires corresponding input/origin/tray/packing checks; do not resize it during playback.
5. **Performance gate:** prototype normal-speed movement before adding the facial polish. Technical tests alone cannot approve appeal; a short visible motion checkpoint is required before building all connecting frames.

## Implementation order once requested

- Build and review the sixteen key poses and their support maps, with two short normal-speed rough sequences. Use original Neko identity references and only the relevant motion-study images/frames.
- Resolve the first-contact anchor, spine folding, drawn camera turn and high-perch exit route. Redraw weak extremes before making the full sheets. A prompt describing “more flexible” without these decisions is insufficient.
- Author the connecting poses; then add the effort/affection acting, ears and tail overlap. Record selected/rejected drawings, exact prompts, frame order and timing.
- Integrate with the existing first-visible clocks, real world movement, per-monitor clipping and persistent resting origin. Keep reduced motion, hide/fullscreen, sleep/carry, repeated quit and OS shutdown safe and prompt.
- Verify retained frames and unrelated clips, source/packed equality, planted contacts and connection to actual idle. Record native paint coverage and startup timing; keep build-time baking. Update previews, README, Frame Master findings and release identities together, with the flat current/previous executable layout.

The initial planning revision archived the references without changing runtime. Its subsequent implementation uses 19 entrance entries/1.98s and 20 exit entries/2.20s, with one diagonal leap each. Exact selected/rejected artwork, registration corrections, native evidence and remaining limits are in [the delivery report](lifecycle-v2-validation.md). Proposed mechanisms above are not blanket approval for future artwork.
