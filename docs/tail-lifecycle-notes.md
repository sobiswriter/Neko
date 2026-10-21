# Tail games, arrival and departure

![Actual new animation playback](neko-tail-life-preview.gif)

Two new sheets were generated with the built-in ImageGen tool, using
`assets/neko-pets-v3.png` for kitten identity. Each is four columns by four rows.
Rows 1–2 and 3–4 are separate eight-drawing sequences.

- `assets/neko-tailplay-v1.png`: clockwise tail chase, then seated tail catch.
- `assets/neko-lifecycle-v1.png`: drop-in landing, then wistful hop-out.

Tail chase changes facing direction through front, profile and back views;
it completes one turn, then rests. Tail catch remains seated: the tail slides
forward, she tries to trap its tip between her forepaws, and it escapes.
These join the idle pool, leaving the twelve approved pet reactions unchanged.
Each eight-drawing group uses one consistent scale and a 112×100 output canvas.

Starting the executable calls `show_neko(greet=True)`: a 2.2-second arrival
sequence finishes its landing and sit-up before the greeting. Launching an
already-running second copy still exits through the single-instance lock.
Ordinary Hide/Show does not replay startup. Normal startup speech follows the
existing quiet/fullscreen rules and optional sound toggle.

**Let her go · quit** runs a 2.1-second wistful pause, crouch and downward leap.
Departure uses a parented single-shot timer to finish cleanup even without a
behavior tick. Repeated quit clicks, petting, and activity cannot restart or
replace it. The jump is drawn inside her existing window rather than moving
the saved desktop position. The final departure frame is fully transparent.
The app hides and closes its input hooks/tray after the animation; an optional
AI worker still receives the existing interruption request and finishes safely.

Reduced motion skips the jumps. Disabling motion midway finishes the lifecycle
transition immediately. Hidden/fullscreen quits are immediate. Hiding during
arrival cancels it and its greeting, without revealing the hidden kitten later.
The soft pause contains no guilt message or obligation.

The atlas has 144 loaded drawings. `neko-tail-life-frames.png` exposes all eight
rendered frames of each new clip, including intentional arrival/departure clipping.
The existing connected-silhouette importer handles row bleed; no anatomy pixels
were painted or repaired programmatically. Generated frames can retain small
outline and proportion differences, so visual inspection accompanies tests.

## Research and motion decisions

Cornell's [What to Expect When Adopting a Feline Friend](https://www.vet.cornell.edu/sites/default/files/WhatToExpect_Updated_2022.pdf)
lists tail chasing, pouncing and leaping among kitten play behaviors. This
informed the choice of two short playful actions rather than continuous spinning.

Chris Hurtt's [Animation Mentor explanation of anticipation](https://www.animationmentor.com/blog/anticipation-the-12-basic-principles-of-animation/)
describes preparation such as a crouch before a jump. The departure includes
that preparation, while arrival includes contact, a landing crouch and recovery
before speech. These are motion-design choices inspired by those principles.

## Generation prompts

+Initial tail sheet

Use case: stylized-concept. Production transparent PIXEL-ART sprite sheet for the existing tiny white desktop kitten. Reference supplies EXACT character identity only: white fur, charcoal crisp pixel outline, pale gray shading, pink nose/ears, shiny dark eyes, one attached tail. EXACT FOUR EQUAL COLUMNS and FOUR EQUAL ROWS,16 complete separate sprites with generous 20% clear padding INSIDE each cell. No labels, text, floor, shadows, hearts, props, motion trails or human hands. True transparent alpha. Fixed camera and physical character scale, identical head volume across all drawings, complete bodies never touch cell boundaries. Anatomy: four limbs TOTAL, exactly two forelegs, one tail always attached at rump. Occluded limbs stay hidden; lifted paws replace their grounded versions. No extra feet, floating hands, duplicate tails, detached parts or ghost outlines. Simple clean readable kitten poses rather than elaborate overlapping limbs. Rows1+2 form ONE EIGHT-FRAME TAIL CHASING sequence read left-to-right top-to-bottom. A kitten playfully trots clockwise in a TIGHT circle trying to catch its own tail. Real changing three-dimensional facing direction, not merely tilting its head: frame1 standing three-quarter front looking at tail; frame2 turns45degrees toward right, short running steps; frame3 right-facing profile trotting nose following tail; frame4 rear-right three-quarter, hindquarters visible head glances toward single tail; frame5 full BACK view running, two ears and back of head visible, one tailcurvesaside; frame6 rear-left three-quarter continuing same rotation; frame7 LEFT-facing profile trotting; frame8 front-left three-quarter almost returned to start. Body stays near cell center; four leg silhouettes readable with far legs hidden when overlapped; NO human torso/arms. The same tail follows the circular turn and remains attached, never a second cat or loose object. A smooth consistent clockwise progression. Rows3+4 form a DIFFERENT EIGHT-FRAME SEATED TAIL-CATCH sequence: frame9 neutral front-facing seated with tail curled to viewer-right; frame10 looks down toward own tail tip; frame11 tail tip slides forward near right side; frame12 front-right foreleg bends and reaches toward tail at ground level, that paw's old planted position disappears, other front leg grounded; frame13 same paw gently pins tailtip, leaning slightly sideways with happy eyes, only one reaching paw; frame14 tail slips away from beneath paw, kitten looks surprised; frame15 lifted forepaw returns toward its original ground position, tail curls back; frame16 neutral sitting with two front paws planted. She stays seated throughout, NO spinning, NO belly roll. Distinct full-body/foreleg and tail drawings, not eight near-identical blinks. Crisp minimal pixel art matching reference, correct anatomy and consistent head size above all.

Lifecycle sheet

Use case: stylized-concept. Production transparent PIXEL-ART sprite sheet for the existing tiny white desktop kitten. Reference supplies EXACT character identity only: white fur, charcoal crisp pixel outline, pale gray shading, pink nose/ears, shiny dark eyes, one attached tail. EXACT FOUR EQUAL COLUMNS and FOUR EQUAL ROWS,16 complete separate sprites with generous 20% clear padding INSIDE each cell. No labels, text, floor, shadows, hearts, props, motion trails or human hands. True transparent alpha. Fixed camera and physical character scale, identical head volume across all drawings, complete bodies never touch cell boundaries. Anatomy: four limbs TOTAL, exactly two forelegs, one tail always attached at rump. Occluded limbs stay hidden; lifted paws replace their grounded versions. No extra feet, floating hands, duplicate tails, detached parts or ghost outlines. Simple clean readable kitten poses rather than elaborate overlapping limbs. Rows1+2 form an EIGHT-FRAME ARRIVAL / LANDING sequence: frame1 kitten airborne front-facing, body slightly elongated downward, forepaws pointing down close together; frame2 airborne a little more tucked, hind legs behind body; frame3 forepaws extend toward landing; frame4 forepaws first touch ground with hindquarters still a little raised; frame5 complete gentle landing crouch, all legs correctly connected, head low; frame6 rises halfway from crouch; frame7 sits almost upright, ears perk; frame8 neutral upright sitting with two front paws planted and friendly open eyes, matching original kitten. Rows3+4 form EIGHT-FRAME GOODBYE JUMP sequence: frame9 seated with mildly wistful face, soft droopy eyelids and lowered ears, NO tears; frame10 head dips gently, same seated body; frame11 bends into a pre-jump crouch; frame12 extends body and forelegs into a small forward-downward leap; frame13 airborne with forepaws close together pointing down, hindlegs tucked behind; frame14 same complete kitten body slightly more tucked midair; frame15 descending front-facing, forepaws extend down; frame16 airborne descending with body elongated a little and tail following. Each sprite is COMPLETE and centered at consistent baseline in its cell; software will move the drawings vertically for falling/jumping, so DO NOT crop any body or paint disappearance/fade/shadow. No splash, no particle effects, no transparent missing body portions. Keep head size fixed during crouch and leap, avoid stretched faces or growing heads. Gentle cute natural kitten weight and posture. Four limbs total, only TWO forelegs in front, no duplicate planted paws when airborne.

Tail correction

Targeted correction of this existing four-column by four-row pixel kitten sheet. Preserve kitten identity, style, transparent background, exact4x4 grid and consistent head size. Top8 drawings are one clockwise tail-chasing circle. Fix frame6 (row2,col2): it MUST be a BACK-LEFT three-quarter view, back of head and shoulders visible, only a small left-facing glimpse of cheek/nose, kitten's tail attached to its RUMP curving toward viewer-left, completing progression front→right→back→left→front. Not a repeated right-facing view. Ensure tail in all top8 drawings connects at rump/back of pelvis, never at shoulder/chest. Lower8 drawings are seated tail-catching. Fix rows3+4 to avoid duplicated forepaws: EXACTLY TWO front legs in ALL frames. Use simple ground-level paw movement, NEVER raise a hand at face/chest. Frame9 neutral seated two front paws planted. Frame10 looks down at tailtip. Frame11 single tail curves forward near right forepaw. Frame12 right foreleg slides its paw along floor toward tailtip, replacing its old paw location; other foreleg stays planted, no third foot. Frame13 same right paw pins tailtip on floor, eyes happy, other paw planted, hindlegs tucked. Frame14 tailtip slips free and both forepaws are planted close together, surprised round mouth, NO paw near chest/face. Frame15 right paw slides back toward neutral, left remains planted. Frame16 neutral sitting. Tail stays one connected long feline tail at rump in ALL16 frames. Tail-catching kitten remains seated, no roll or spin. No duplicated grounded leg below reaching forepaw, no holes in body, no detached pieces, no extra limbs or tails. Four limbs total. Keep lower8 drawings distinct through the reaching leg and tail motion, not just blinks. True transparent alpha no props no text no backdrop.

Final seated catch correction

Edit ONLY LOWER TWO ROWS (frames9–16) of this exact4x4 transparent pixel kitten sheet; preserve TOP8 drawings unchanged. The lower kitten MUST have EXACTLY TWO simple forelegs and TWO forepaws on the floor throughout. Remove all third paws, arms, raised hands and duplicated vertical grounded legs. Use the neutral seated anatomy from bottom-right frame for all lower8 drawings. Animate a FLOOR-LEVEL attempt to trap its own tail between BOTH planted forepaws: frame9 neutral sitting pawsapart tailcurlright; frame10 head looksdown and tailtip starts moving forward; frame11 tailtip slides horizontally in FRONT of both paws; frame12 kitten leans forward slightly and BOTH forepaws slide inward toward tailtip along floor; frame13 BOTH forepaws are close together pinching the tailtip BETWEEN THEM, closed happy eyes, exactly TWO front legs that CONNECT from shoulders to those two moved paws, no other grounded front feet; frame14 tail slides out to right while both forepaws remain together on floor, surprised expression, NO raised paw at chest; frame15 both forepaws slide apart toward original positions with head looking after escapingtail; frame16 neutral sitting with two planted forepaws and one tail curledright. When paws slide inward, replace original front leg locations with the two angled forelegs leading to their new paw positions; do not leave vertical old leg copies behind. Tail is ONE continuous attached tail originating at rump and curls forward around side into front. Rear legs remain hidden behind seated body; no third front paw. Complete chest and belly, no holes, no detached pieces. All8 must have clearly distinct head/torso/tail/forepaw positions but minimalist readable anatomy. Same kitten identity, whitefur charcoalpixeloutline pinkears darkeyes, fixedheadsize, exactequal4x4 grid, puretransparentbackground, no text props shadows. No paw reaches sideways; BOTH move toward each other at floor level, visibly an attempt to trap the tail.
