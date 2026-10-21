# Playfulness revision: exact ImageGen prompts


## Direct attached GIF correction

The attached `dm4uz3-sakamoto.gif` has eleven frames, each 50ms. All eleven were extracted into a contact sheet as a motion reference; no source pixels enter the runtime art. Built-in ImageGen generated `assets/neko-tailplay-v4.png` from that contact sheet and the existing idle character sheet, with transparent background. This supersedes the earlier tucked-tail cycle.

```text
Use case: stylized-concept. Create a production transparent PIXEL ART sprite sheet for existing WHITE kitten desktop pet. Image1 is CHARACTER IDENTITY ONLY: white fur, charcoal pixel outline, gray shading, pink ears/nose, constant large round head, small normal kitten ears and compact feline proportions. Image2 is the EXACT MOTION STORYBOARD: 11 consecutive frames of a real tail-chasing animation. Adapt those 11 poses faithfully to the white kitten. Do not copy black fur, red scarf, long pointy ears, room/floor, labels or background. True transparent alpha.

EXACT 4 equal columns x4 equal rows, 16 separate complete sprites, row-major reading order. Constant physical head/body scale, generous clear padding inside EVERY cell. Each sprite fully contained, no cell-edge clipping. Crisp stepped pixel edges. No labels/shadows/ground/effects.

CRITICAL MOTION: TOP ELEVEN drawings reproduce the FIRST ELEVEN consecutive reference frames, in order. The kitten is RUNNING IN A TIGHT CIRCLE after her own tail. Body LOW and stretched HORIZONTALLY, curved like a broad C, hips leaning into the turn. Head leads the body around the circle with eyes SQUEEZED CLOSED in playful determination. Forelegs paddle/scramble, hindlegs push under rump, alternating paw contacts with small bounds. Tail is LONG and TRAILS OUTSIDE the turning body in a wide curved arc, tip escaping away from the nose. Keep clear negative space between tail and torso. Do not put tail under chin/in mouth or wrap it around chest. Do not animate an upright seated mannequin turning on a pedestal. Whole torso changes direction naturally; no face on back of head. The reference pose at each angle is more important than making cute front portraits.

Frame mapping, match the corresponding numbered reference cell:
1 head/front paws toward LOWER RIGHT, curved body extends UPPER LEFT, trailing tail curls wide around LOWER LEFT. One foreleg reaching.
2 head points DOWN, hips upper right; long tail sweeps across upper left, tip far left. Other foreleg reaching.
3 same down/front orientation with next RUNNING FOOT CONTACT (not an identical drawing).
4 head LEFT and a little down, hips right, body bent strongly toward left; long tail sweeps outside at top.
5 head LEFT, body extends right and lower, near foreleg reaching LEFT, tail curves from right rump upward ending high near center.
6 same left orientation next running stride, forepaw replaces old position, different hindpaw contact.
7 head points UP and LEFT, back of head visible, body lower right, tail long on outer RIGHT of turn.
8 head UP and away, back of skull only, body below/left, long tail sweeps RIGHT outside.
9 head UP and RIGHT, near cheek barely visible, body below/left, tail sweeps lower right.
10 head RIGHT and slightly down, body left/lower, long tail curls outside along BOTTOM.
11 almost matches frame1: head LOWER RIGHT, body UPPER LEFT, tail trailing wide around lower-left, opposite foot contact so 11->1 is a seamless RUNNING cycle.

LAST FIVE drawings:
12 neutral front-facing seated white kitten, EXACT identity image, one curled tail and two planted forepaws.
13 drops to LOW CURVED crouch noticing tail, eyes eager, rear hips slightly raised, all four legs coherent, one long tail behind.
14 low short pounce to own trailing tail, both forepaws reach together replacing planted paws, hindlegs tuck behind. Four legs TOTAL.
15 belly low, both forepaws hold own single tailtip on floor, head low, closed happy eyes, hindfeet hidden tucked. No third foreleg, no raised human arms.
16 normal neutral seated EXACTLY same as frame12.

ANATOMY: one head/torso, FOUR anatomical legs TOTAL, only TWO forelegs, one continuous tail ATTACHED AT RUMP. Far legs occluded where appropriate. Every moving paw REPLACES its original location. No extra limbs, duplicate feet, detached parts, second tails or changing skull size. Broad low running silhouettes like the reference, not old upright turning poses. Reference motion silhouette and footfall are the core request.
```


Character reference: `assets/neko-idle-v3.png`. Pose references: the user's two attached images and [tail-chasing GIF](https://media.tenor.com/Gxa1JfN3334AAAAM/dm4uz3-sakamoto.gif), opened through the supplied Google share link. Pose references supply motion only; the existing white kitten supplies identity. All calls used built-in ImageGen with transparent background. Corrections reference the corresponding generated sheet. All four farewell candidates are retained in the source sheet; only the first two are used.

## playful-tail

```text
Use case: stylized-concept. Production transparent PIXEL ART sprite sheet for existing tiny white desktop kitten. Image1 CHARACTER IDENTITY: match EXACT white fur, charcoal stepped pixel outline, gray shading, pink ears/nose, big dark eyes, compact short kitten body and constant head size. Image2 POSE/MOTION ONLY: crouched body curved toward own tail, nose following tip, whole-body playful turning. DO NOT copy its black fur, giant ears, scarf, camera or background. Actual transparent alpha. EXACT 4 equal columns x4 equal rows,16 COMPLETE isolated sprites, 20% empty padding per cell, no labels/text/grid/ground/shadow/effects. Same camera, fixed physical size, constant HEAD volume in every drawing. ONE head/torso/tail, only FOUR anatomical legs total, only TWO forelegs. Occluded legs stay hidden. Each new paw position replaces the old position. Tail visibly attaches at pelvis/rump, never shoulder/chest.

TOP TWO ROWS: frames1-8 form ONE SEAMLESS clockwise full-body stepping circle. NO sitting in these eight. Playfully CURVED LOW C-SHAPED BODY with nose bent toward own tail at every angle, like motion reference. One long attached tail curls ahead of nose, kitten follows it. Compact planted stepping or small hopping steps, never rotating a stiff seated paper doll.
1 front-right three-quarter, crouched low with hips slightly high, nose looking back toward own tail;
2 right profile, shoulders turned, near foreleg stepping, far leg hidden behind, single tail arcing forward from rump toward nose;
3 rear-right three-quarter, bent body continues turn, near hindleg steps;
4 full back view, back of head TWO ears, NO face on back, shoulders/hips curved and one attached tail to side;
5 rear-left three-quarter, a tiny glimpse of left cheek, same turn direction;
6 left profile, head looks back around flank toward own tail, compact stepping legs;
7 front-left three-quarter, head follows tailtip, distinct alternating foot contact;
8 front-right three-quarter again, nearly IDENTICAL silhouette/camera to frame1 but opposite foot contact, so 8->1 continues fluidly. No frame at a different size.

BOTTOM TWO ROWS: frames9-16 are preparation and payoff, same kitten/head scale.
9 neutral front-facing seated, EXACT reference identity.
10 looks back at single tailtip, drops shoulders into playful crouch, rear hips a little raised, forepaws planted.
11 three-quarter right LOW pounce preparation, spine curved toward own tail, two bent forelegs, hind legs planted behind.
12 small forward-side pounce toward own tailtip: both forepaws reach together replacing old planted positions, rear legs tucked behind. Exactly four legs TOTAL, no third front foot. SINGLE tail still attached curling beside forepaws.
13 settled low on belly/haunches with TWO forepaws holding own tailtip on floor, head lowered toward tip, ears attentive, gentle satisfied eyes; rear feet hidden/tucked.
14 tail slips free to side; nose follows it, both forepaws still grounded, one continuous tail.
15 sits back on haunches, small playful head tilt/bright eyes, two forepaws together, no extra arms.
16 neutral seated EXACT same silhouette as frame9 and identity reference.
Anatomy and connected silhouette are critical: no extra paws, duplicated planted limbs, disconnected parts, body holes, stretched heads, second tails, rabbit ears, rolling or humanoid arm gestures. All sprites fully inside their equal cells.
```

## graceful-arrival

```text
Use case: stylized-concept. Production transparent PIXEL ART EIGHT-FRAME graceful kitten fall/landing sprite sheet. Image1 supplies EXACT existing white kitten identity: white fur, charcoal pixel outline, gray shading, pink nose/ears, dark shiny eyes, large constant head volume and compact kitten body. Image2 is MOTION REFERENCE ONLY: graceful forepaws-first landing with a long trailing up-curved tail and hindquarters behind, NOT a seated cat sliding down. Do not copy blue palette/pink backdrop/ground. EXACT FOUR equal columns x TWO equal rows, eight complete isolated sprites, read left to right top to bottom, generous 20% empty margins. True transparent alpha, no floor/shadows/text/labels/props/effects. Same camera and fixed physical character/head size. Complete bodies in every cell: software moves entire window from above monitor, do NOT crop sprites or change their vertical location arbitrarily. Forepaws have a common ground baseline when grounded.

Frame1 airborne falling from above, front-left three-quarter view, spine slightly diagonal/horizontal, two forelegs reaching DOWN beneath chest, two hindlegs tucked close behind, tail curves UP from rump. A true four-legged cat in free fall, not sitting in air.
Frame2 forelegs extend gracefully toward landing, head attentive and eyes bright, rear legs still tucked behind pelvis, same head volume/body orientation.
Frame3 both forepaws just meet ground, forelegs extended, hindquarters and tail still raised behind, same three-quarter-left orientation like motion reference. Only TWO forepaws and TWO hind paws.
Frame4 hind paws settle, foreleg elbows bend absorbing impact, head and chest lower gently, tail follows momentum.
Frame5 soft deep landing crouch, head SAME SIZE not squashed, knees folded, TWO forepaws planted with rear feet tucked behind, cheerful closed eyes. No extra old leg copies under bent legs.
Frame6 springs lightly out of crouch into half-sit, chest rises and ears perk, playful small smile, tail gives one jaunty curl. A little bounce in body posture, not a second big jump.
Frame7 upright nearly seated, turns face toward viewer with bright curious eyes and relaxed happy ears, two paws planted, same proportions as reference.
Frame8 normal neutral upright front-facing sit EXACTLY matching reference identity/size, two forepaws planted, haunches tucked, one curled tail.
ONE head/torso, FOUR anatomical limbs TOTAL, exactly TWO forelegs, one long tail ATTACHED AT RUMP. Hidden legs stay hidden. No duplicate feet, floating paws, torso holes, extra tails, changing skull size or wide stretched faces. Prioritize readable natural cat landing and affectionate playful recovery, no stars/hearts/particles.
```

## sad-farewell

```text
Use case: stylized-concept. Production transparent PIXEL ART FOUR-FRAME gentle sad goodbye facial/body-preparation sheet for existing kitten. Image1 exact kitten identity and neutral seated proportions. Image2 existing hop-down identity/pose continuity reference; do not redraw jumping here. Create EXACT FOUR EQUAL columns x ONE row, four COMPLETE isolated seated kittens, generous clear padding, transparent alpha, no text/grid/ground/shadows/props/symbols. Pixel-art white fur, charcoal outline, gray shade, pink ears/nose, shiny dark eyes, one attached curled tail. Keep same body/head size and seated outline across all four, same feet baseline, TWO forepaws planted, hindlegs tucked. No duplicate legs, raised hands, tears, giant eyes or missing parts.

1 immediately a little SAD: inner eye corners/eyebrows subtly raised, eyelids soft and lowered, mouth a tiny downturned curve, ears gently lower outward. Head still upright. The emotion must be visibly wistful rather than the normal blank face. Keep the face cute and restrained.
2 head dips slightly with downcast soft eyes, ears a little lower, shoulders gently sink, two paws still planted. One curled tail rests quietly at side. Sad but not crying.
3 one brief slow eyes-closed blink, head still a little dipped, mild sadness, steady body, same size.
4 looks down toward where she will hop, a quiet resigned expression, ears still relaxed. Same seated anatomy and compact short kitten body so it can connect to the existing crouch/jump art.
No tears, text, guilt message, waving, hearts or melodrama. One head, one connected torso, four anatomical limbs total with only two forepaws visible, one tail attached at rump. Constant head size, no stretching.
```

## tail-turn-correction

```text
Use case: precise-object-edit. Production animation correction to this exact transparent 4x4 white kitten sprite sheet. Preserve character, grid, transparent alpha, physical head size and all other drawings. Correct ONLY TWO drawings in the top eight-frame turn: frame3 = row1,column3 MUST be REAR-RIGHT THREE-QUARTER, back of skull/neck and curved spine visible, only a tiny cheek glimpse, not another right-profile front face. Frame5 = row2,column1 MUST be REAR-LEFT THREE-QUARTER, back of skull and left shoulder visible, only a small left cheek glimpse, not front-facing. These connect right profile(frame2) -> rear-right(frame3) -> full back(frame4) -> rear-left(frame5) -> left profile(frame6). The kitten remains crouched low, body curves toward its own tail, paws stepping with changing contacts, one tail attached at pelvis curling around flank toward nose. NO sitting in top8, NO stationary paper doll spin. Nose follows tail tip while torso turns. Four anatomical legs total, only TWO front legs; far legs remain occluded where appropriate; no extra feet or disconnected tail. Keep all other14 sprites unchanged including bottom8 crouch/pounce/recovery frames. Do not enlarge or stretch head, add a face on the back, or move tail attachment onto shoulder.
```

## arrival-tail-correction

```text
Use case: precise-object-edit. Correct this transparent 4-column x2-row EIGHT-FRAME white kitten landing sprite sheet. Preserve EXACT existing head, body, legs, expressions and motion poses in ALL eight cells. Change ONLY the single tail in the FIRST FIVE drawings. It currently sticks far upward like a giant flagpole and makes those frames much taller than the seated kitten. Recurve that same tail into a COMPACT graceful BACKWARD-UPWARD CURL from the rump, with its highest point no more than about10% of a head-height above the ear tips. Shorten its vertical reach by curling it sideways/back toward the rump, do NOT shrink kitten/head or amputate tail. Keep tail length visually feline and tail visibly attached to pelvis, one continuous tail, not a separate object. Frames1-3 airborne/reaching, frame4 contact and frame5 compressed landing keep exactly their current four-leg anatomy and body/head sizes. Do not redraw forelegs, add feet, change face, change frame grid/spacing, crop bodies or put shadows/background. Preserve last three drawings unchanged. Pure transparent alpha. This is a tail-only fit correction; the body motion and physical character scale must remain identical.
```

