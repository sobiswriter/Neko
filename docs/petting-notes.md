# Curated four-frame petting set

The user approved twelve total reactions: retain head pats, cheek nuzzle,
kneading, chin scritches, tiny blep and ear rubs; remake paw offer; add front
stretch, back arch, tiny hop, side flop and shoulder peek. No new loaf, since
loaf already exists in the idle set. All twelve use four distinct source drawings.

Two new sheets were generated with the built-in ImageGen tool, using the
existing `assets/neko-pets-v3.png` only for kitten identity. The supplied
character sheets inspired pose ideas without being copied or used as edit targets.

- `assets/neko-petting-a-v1.png`: 4 columns × 3 rows, stretch / arch / hop.
- `assets/neko-petting-b-v1.png`: 4 columns × 3 rows, flop / peek / corrected paw offer.

No anatomy pixels were painted or repaired programmatically. The loader isolates
each connected silhouette, allowing vertical overscan for drawings that extend
across a nominal row boundary. Native cell aspect ratios are preserved rather
than stretching rectangular cells into squares. Each new row uses a single
scale across all four poses, preventing the lowered body from enlarging the head.
All output frames retain the 112×100 transparent canvas and common ground anchor;
the airborne hop has a 10-pixel lift inside that canvas, without moving the window.

The old wave row in `neko-pets-v3.png` and malformed paw row in
`neko-affection-v1.png` are never loaded into the atlas. Those source sheets remain
because they also contain retained art. The rejected six-frame sheet was deleted.
The atlas loads 112 drawings total, of which 48 belong to the twelve pet reactions.

The new gestures play once, then rest inside the existing 5.8-second slot.
Side flop reuses its intermediate poses in reverse to return upright smoothly.
The app still renders at 10 FPS. `neko-pet-catalog.gif` shows actual playback,
and `neko-pet-frames.png` exposes all four drawings of every active reaction.
Generated art can have small outline and proportion differences between drawings;
visual inspection is required alongside the structural tests.

## Final generation prompts

+Sheet A

Use case: stylized-concept. Production transparent PIXEL ART kitten sprite sheet for an existing Windows desktop companion. Reference image supplies kitten identity ONLY, not layout or motion. White fur, crisp charcoal pixel outline, pale gray shadows, pink nose/inner ears, big dark shiny eyes, ONE attached tail. Match the existing little kitten, not a new design. EXACT FOUR EQUAL COLUMNS and THREE EQUAL ROWS =12 complete sprites. Every row is a FOUR DISTINCT DRAWING sequence, left to right. Genuinely transparent alpha background, NO shadows, props, text, grid lines, numbers, symbols or floor. Each cell has 18% clear padding on all sides and contains a complete cat, fixed camera and consistent character scale/head size. Common feet baseline; airborne kitten rises a little within its cell naturally. Side-facing full-body poses must still preserve kitten identity. Anatomy must be readable and correct: exactly four legs total, TWO forelegs and TWO hindlegs, one tail. Occluded limbs remain hidden, never duplicate feet or arms. Every leg continuously attaches at its correct shoulder or hip. No floating paws, third foreleg, fifth leg, body holes or disconnected pieces. Favor simple readable anatomy and distinct silhouettes over tiny facial-only changes. SHEET A: Row1 BIG FRONT STRETCH facing left in three-quarter side view: frame1 sitting upright, head slightly toward viewer; frame2 hips rise to standing and both forelegs reach forward; frame3 chest lowers into a deep playful bow with both front paws extended on ground and rear hips raised, back gently sloped; frame4 chest rises halfway and forelegs retract, a clear recovery pose toward sitting. Exactly four legs, near and far forelegs neatly separated or occluded, not extra limbs. Row2 HAPPY BACK ARCH facing left: frame1 standing naturally on four paws; frame2 back begins rounding upward while head dips slightly; frame3 visible happy rounded arch with tail upright, all four paws remain planted; frame4 spine settles halfway toward neutral. This is a soft comfortable kitten stretch, NOT angry or puffed, no spikes. Row3 TINY HAPPY HOP facing viewer: frame1 seated neutral; frame2 compact crouch preparing a hop; frame3 small hop straight UP with all four paws tucked close to belly, complete body airborne a little above baseline, rear legs hidden behind haunches, NO planted duplicate feet; frame4 soft landing on two forepaws and tucked rear haunches. Real distinct motion but gentle and contained. All12 drawings same character head volume and consistent physical scale. Clean tiny pixel art, no gradients.

Sheet B

Use case: stylized-concept. Production transparent PIXEL ART kitten sprite sheet for an existing Windows desktop companion. Reference image supplies kitten identity ONLY, not layout or motion. White fur, crisp charcoal pixel outline, pale gray shadows, pink nose/inner ears, big dark shiny eyes, ONE attached tail. Match the existing little kitten, not a new design. EXACT FOUR EQUAL COLUMNS and THREE EQUAL ROWS =12 complete sprites. Every row is a FOUR DISTINCT DRAWING sequence, left to right. Genuinely transparent alpha background, NO shadows, props, text, grid lines, numbers, symbols or floor. Each cell has 18% clear padding on all sides and contains a complete cat, fixed camera and consistent character scale/head size. Common feet baseline; airborne kitten rises a little within its cell naturally. Side-facing full-body poses must still preserve kitten identity. Anatomy must be readable and correct: exactly four legs total, TWO forelegs and TWO hindlegs, one tail. Occluded limbs remain hidden, never duplicate feet or arms. Every leg continuously attaches at its correct shoulder or hip. No floating paws, third foreleg, fifth leg, body holes or disconnected pieces. Favor simple readable anatomy and distinct silhouettes over tiny facial-only changes. SHEET B: Row1 COZY SIDE FLOP: frame1 sitting upright facing three-quarter left; frame2 leans onto one hip with one elbow bending, all legs remain attached; frame3 lowers torso halfway onto its side, forelegs together in front, rear legs together tucked behind belly; frame4 rests on its left side with head slightly raised, paws relaxed together, one tail along rear body. No belly-up roll or leg tangle, no split tails. Clear sequential descent with same head volume. Row2 OVER-THE-SHOULDER PEEK: frame1 seated body turned three-quarter right with head facing viewer; frame2 head turns a little toward its right shoulder; frame3 looks behind shoulder with a small shoulder twist, BOTH forepaws remain planted and body silhouette stays consistent; frame4 head turns halfway back toward viewer. Motion must be obvious in head direction, not merely eyelids changing. Keep face recognizably feline, never spin head unnaturally. Row3 CORRECTED PAW OFFER, front facing: frame1 sitting with exactly TWO front paws planted; frame2 the kitten's right foreleg (viewer-left) bends and lifts its paw a LITTLE forward from floor, left foreleg remains planted; frame3 that SAME right foreleg offers its paw forward at LOW CHEST height with happy eyes, wrist connected to a visible bent forearm from right shoulder; frame4 offered paw lowers halfway back toward floor. ABSOLUTE ANATOMY: in frames2,3,4 remove the grounded version of the lifted right foreleg ENTIRELY. Only ONE front paw on floor while other is raised. Clear empty space below lifted paw, but chest and haunch stay complete. Hind legs tucked into seated haunches, not additional front feet. No arm starting from mouth or chin, no floating hand near cheek, no third forepaw, no duplicated leg. Four limbs total, one tail. This row must look like offering one paw, not grooming or waving at face.
