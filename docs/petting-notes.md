# Six-frame petting additions

Generated and revised with the built-in ImageGen tool, using the existing
`assets/neko-pets-v3.png` for character identity. Final asset:
`assets/neko-petting-v1.png`, a transparent 6-column by 4-row sheet.
The first row replaces the malformed paw greeting with a seated hello, keeping
both forepaws planted. Three additional rows add a shy head dip, nose wiggles,
and a contented tail curl. The other seven reactions retain their original art.
Eleven reactions rotate without repeats until the bag is exhausted.

Each sequence has six drawings with holds of 350, 400, 450, 650, 450, 700 ms.
It runs once in three seconds, resting in its final pose until the existing
5.8-second interaction ends. The common 112×100 canvas, ground baseline,
82-pixel seated height and 10 FPS renderer are unchanged. The old four-frame
greeting remains in its original source sheet but is no longer played.
`neko-petting-preview.gif` renders the actual frame player, rather than a mockup.
No frame anatomy was painted or repaired programmatically.

The first generated greeting retained a duplicate forepaw; a targeted revision
removed too much of the body. Both versions were rejected. The final revision
uses a complete seated body with only head and ear motion for the greeting.
Subtle generated shape changes remain; these are drawn frames, not interpolated motion.

## Prompt history

+Use case: stylized-concept. Production transparent pixel-art animation sprite sheet matching reference white desktop kitten exactly. Reference is identity/style only. EXACT SIX EQUAL COLUMNS and FOUR EQUAL ROWS (24 complete separate sprites) on transparent background. Each ROW is one SIX FRAME sequence read left to right. No text labels lines props hands hearts shadows or ground. Each equal cell has same centered kitten, same feet baseline, fixed head size and seated body scale, generous empty 18% padding. White fur, charcoal crisp pixel outline, pale gray shading, pink ears/nose, large dark shiny eyes, one attached tail. Row1 corrected PAW GREETING: neutral sitting; front-right paw bends off ground slightly; same front-right paw raised halfway; same paw held at chest height smiling; paw lowers halfway; returns to planted neutral. CRITICAL exactly TWO front limbs in EVERY frame: the lifted right foreleg replaces its grounded position, no extra paw under the raised arm; left foreleg remains planted; rear haunches tucked behind body with NO additional front feet. Count limbs carefully. Row2 SHY HEAD DIP: both forepaws planted unchanged, head level / chin dips slightly / eyes soften / shy eyes closed chin lowered / head gently rises / neutral. Row3 NOSE WIGGLE: both paws planted, head stable, neutral / nose lifts tiny amount / small gentle sniff eyes half close / tiny nose twitch / nose relaxes / neutral. Row4 CONTENTED TAIL CURL: both paws planted identical, neutral tail curving at right / single tail tip bends inward slightly / curls nearer side / curls gently around side of body eyes happily closed / unwraps halfway / neutral. Tail never crosses front legs, no second tail. Genuine six distinct subtle in-between drawings per row, not duplicate poses. ANATOMY OVER COMPLEXITY: FOUR legs maximum, ONLY TWO forelegs, hind legs tucked behind body; no floating limbs, extra arms, ghost traces, detached pixels, duplicated parts. Fixed camera, consistent cat proportions, crisp minimal pixel style of reference, not polished vector art. Each row begins and ends neutral. True transparent alpha.

### Targeted revision

Precise object edit of this 6 columns x4 rows sprite sheet. KEEP grid EXACTLY 6x4 and keep rows2,3,4 unchanged. Fix ONLY the first row paw-greeting anatomy: in columns2,3,4,5 one forepaw is raised, but its old grounded front leg remains, creating a THIRD forelimb. DELETE the vertical grounded foreleg directly underneath the raised paw in those four frames. There must be ONE planted front leg at viewer-left and ONE raised bent front leg at viewer-right, with CLEAR EMPTY TRANSPARENT SPACE underneath that lifted front paw, between planted leg and tucked right haunch. Draw only one planted forepaw, one lifted forepaw. No third paw or detached hand. The seated rear haunch at far right remains a simple rounded body mass, NO extra vertical foot or dangling leg there. Raised limb attaches at shoulder at side of chest, never at chin or mouth. In col2 lift slightly, col3 halfway, col4 chest height (not face), col5 lowering. Col1 and6 neutral two forepaws planted unchanged. Keep rows2–4 and character identity, pose scale, simple crisp pixel art, white body charcoal outlines pink ears one tail, exact baseline and transparency. Actual transparent background alpha, no backdrop shadows labels or props.

### Targeted revision

Edit ONLY top row of this 6-column by 4-row transparent pixel kitten sheet. Keep lower three rows exactly unchanged. Top row must be a simple SIX-FRAME SEATED HELLO, no raised paws at all. Use the complete anatomically correct neutral seated body from top-left cell for ALL SIX top-row cells: TWO front legs planted on ground, same complete white chest and rounded haunch, one attached tail at right. No holes in body. No paw near face or floating hand. Replace ALL raised-paw poses with this complete neutral seated body. Animate ONLY the face/head and ears: col1 neutral eyes open head level; col2 head tilts very slightly left eyes soften; col3 head tilt a little more eyes half close; col4 friendly smiling closed eyes with tiny ear relaxation; col5 head straightens eyes half open; col6 neutral matching col1. Fixed head volume, feet baseline, body and tail unchanged. Simple gentle hello response to petting. Avoid extra arms by keeping both front paws planted and visible in all six frames. No extra limbs, detached pieces, duplicate paws, body holes, ghost trails. Preserve transparent background alpha, exact6x4 equal grid, white coat charcoal crisp pixel outline pink ears dark eyes, reference proportions. No text no props no background.
