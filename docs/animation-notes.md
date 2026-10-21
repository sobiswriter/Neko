# Neko animation art

Current petting art and final prompts are documented in [petting-notes.md](petting-notes.md).
The notes below record earlier sheets. Their wave and paw-offer rows are retired,
and historical preview GIFs containing those reactions have been removed.

Generated with the built-in ImageGen tool using assets/neko_idle.png as the
character reference. Four separate 4 x 4 sheets replace the earlier 8 x 8 atlas.
Smaller action groups made it easier to keep paws, tails and head proportions
consistent. No API key or art service is needed to run the companion.

| Sheet | Four rows, top to bottom |
| --- | --- |
| neko-idle-v3.png | blink, tail swish, ear flick, sniff |
| neko-pets-v3.png | head pat, cheek nuzzle, paw greeting, kneading |
| neko-activity-v3.png | typing, grooming, yawn, sleep |
| neko-movement-v3.png | walk, seated stretch, look around, loaf |

The four base sheets contain 64 drawings in sixteen action sequences. The
transition and extra affection sheets described below bring the total to 96. The frame player adds
directional looks and a blink variant. Timing holds and loops live in animations.py.
Walking mirrors the same drawings when heading right. The loader samples each
sheet at 512 x 512 and finds the main connected silhouette. The frame player now
normalizes seated drawings to 82 pixels tall, with an aspect-preserving width cap.
This fixes smaller pet drawings shrinking during a click. Low sleeping/loaf poses
share a 92-pixel width; walking keeps its natural proportions within 104 x 82.
Every frame uses a 112 x 100 transparent canvas with the same ground anchor.
Most gestures retain 5–6 second slots, with one gentle action and a relaxed rest.
No limbs or image pixels were repaired programmatically.

The sheets were inspected at desktop size and the old atlas was removed from
the build. Generated drawings still have small frame-to-frame shape changes;
these are not hand-drawn in-betweens. More frames alone would not fix that.
docs/neko-preview.gif shows the actual frame player with all sixteen sequences.
Pillow is used only to serialize this documentation preview, not by the app.

## Generation prompts

### idle

Production pixel-art kitten sprite sheet using the reference ONLY for the kitten's identity. Pure transparent background, no ground, shadows, outlines outside the character, labels or props. EXACT 4 columns x 4 rows, 16 fully separate sprites in equal cells. Each row is a four-frame animation, read left to right. Each cat is full body with 20% empty padding within its cell, same center and feet baseline. Clean crisp small pixel art with white coat, charcoal outline, pale gray shading, pink inner ears and nose, shiny dark eyes, ONE long tail. Same kitten size and proportions in every cell. ANATOMY IS CRITICAL: exactly four limbs total, only TWO front legs/paws; hind legs tucked under the seated haunches. If a front paw lifts, REMOVE that paw from the ground; NEVER leave its old copy behind. No extra paws, arms, legs, tails, ghost trails, red edge speckles or disconnected parts. Favor very simple subtle poses over complex anatomy. Rows: 1 seated slow blink, open eyes / half closed / closed / open; paws and body stay planted. 2 seated TAIL SWISH: body identical, the single tail visibly changes tip position from right / curved up / curling toward body / right again, never splits, tail attaches to rump throughout. 3 EAR TWITCH: same sitting body and paws; one ear upright / tilts sideways / tilts back / upright, small eye changes. 4 SNIFF: same sitting body, kitten tilts nose up a little, sniffs twice, returns to neutral. All 16 sprites anatomically clean. No walking, waving or extra poses.

### pets

Production pixel-art kitten sprite sheet using the reference ONLY for the kitten's identity. Pure transparent background, no ground, shadows, outlines outside the character, labels or props. EXACT 4 columns x 4 rows, 16 fully separate sprites in equal cells. Each row is a four-frame animation, read left to right. Each cat is full body with 20% empty padding within its cell, same center and feet baseline. Clean crisp small pixel art with white coat, charcoal outline, pale gray shading, pink inner ears and nose, shiny dark eyes, ONE long tail. Same kitten size and proportions in every cell. ANATOMY IS CRITICAL: exactly four limbs total, only TWO front legs/paws; hind legs tucked under the seated haunches. If a front paw lifts, REMOVE that paw from the ground; NEVER leave its old copy behind. No extra paws, arms, legs, tails, ghost trails, red edge speckles or disconnected parts. Favor very simple subtle poses over complex anatomy. Rows: 1 HEAD PAT reaction: sitting, closes eyes happily and lowers chin a little then returns, both front paws remain planted. 2 CHEEK NUZZLE: seated, tilts head slightly to one side / eyes close / cheek leans gently / head returns; body and both planted front paws identical throughout. 3 PAW GREETING: seated front-facing, left front paw remains planted while the RIGHT FRONT PAW lifts to chest / lifts near cheek / returns toward chest / rests on ground; never draw an additional right paw below the raised one. Only TWO front paws in each frame. 4 CONTENTED KNEADING: seated, exactly two front paws, alternate raising ONE paw just slightly and placing it back, tiny motion, never duplicate paws. No rolling, no standing, no limbs crossing the face. One tail attached to rump in every frame.

### activity

Production pixel-art kitten animation sheet matching the reference's identity: tiny white kitten, charcoal pixel outline, pale gray shadows, pink ears/nose, big shiny dark eyes, ONE curled tail. Genuinely transparent background. EXACT equal 4 columns x 4 rows = 16 sprites, NO labels, props, ground, shadow, or neighboring overlap. Every cell has generous 20% empty padding. Same character size, identical head proportions, same center and feet baseline across each row. Each row is one four-frame sequence. ANATOMY: four legs TOTAL, never more. Exactly TWO front paws, never leave a front paw planted if that same paw is lifted. Hind legs are tucked into haunches in seated poses, without extra hanging feet. No duplicate limbs, no disconnected legs, no duplicated tails, no ghost outlines/red edge artifacts. Clean legible low-resolution pixel art, simple gentle movements; anatomy and consistency are more important than complexity. ROW1 typing: seated, exactly TWO front paws alternate lifting just slightly and returning to the ground, small controlled tap; lifted paw REPLACES its previous ground position, no extra hand sticking out of body. ROW2 grooming: front-left paw remains grounded, front-right paw lifts to mouth / licks once / rubs cheek / returns to the ground; exactly two front limbs. ROW3 yawning: seated paws completely stationary, mouth closed / half open / small round yawn with eyes closed / mouth closed, no paws near face. ROW4 curled sleeping: compact cat curled with head resting on its two forepaws and rear legs completely tucked out of sight, one tail wrapped around body, eyes closed in all four frames, tiny ear/belly changes. Count visible paws carefully and omit hidden limbs.

### movement

Production pixel-art kitten animation sheet matching the reference's identity: tiny white kitten, charcoal pixel outline, pale gray shadows, pink ears/nose, big shiny dark eyes, ONE curled tail. Genuinely transparent background. EXACT equal 4 columns x 4 rows = 16 sprites, NO labels, props, ground, shadow, or neighboring overlap. Every cell has generous 20% empty padding. Same character size, identical head proportions, same center and feet baseline across each row. Each row is one four-frame sequence. ANATOMY: four legs TOTAL, never more. Exactly TWO front paws, never leave a front paw planted if that same paw is lifted. Hind legs are tucked into haunches in seated poses, without extra hanging feet. No duplicate limbs, no disconnected legs, no duplicated tails, no ghost outlines/red edge artifacts. Clean legible low-resolution pixel art, simple gentle movements; anatomy and consistency are more important than complexity. ROW1 walking toward LEFT: gentle four-frame side-view walk cycle, feline quadruped, small head turn so same face visible. Exactly four legs; near foreleg, far foreleg, near hindleg, far hindleg, alternate contacts without any fifth foot. Tail follows softly. Keep cat body at constant elevation and size. ROW2 SEATED stretch: kitten remains sitting on its haunches in every frame, its TWO front legs stretch forward together a little / extend / relax / return planted; rear legs remain tucked, no third front paw. No standing or complex contortions. ROW3 looking around: seated paws stationary, head turned a little left / front / a little right / front; ears follow, same head volume. ROW4 loaf: all frames are the same compact cat-loaf posture with ALL four paws tucked underneath and not visible, head upright, gentle eyes-open / half-blink / closed-blink / eyes-open; ONE tail wraps at the side. No detached parts, no extra paws.

## Sleep and wake transition sheet

Created with the built-in ImageGen tool from the existing idle and activity sheets.
Project asset: assets/neko-transitions-v1.png. No external art paths are used at runtime.
It adds sixteen drawings: rows 1–2 curl down into sleep, rows 3–4 unfold and wake.
Sleep uses the final two curled drawings, so settling ends in the same pose that
starts the sleep loop. The transition bank uses one constant scale based on its
first seated drawing, preserving head size while its body lowers. All frames
retain the common 112 x 100 canvas and feet baseline.

Existing gestures play once and rest inside their 5–6 second behavior slots;
tail swishes, kneading, walking and paw taps use slower continuous cycles.
rendering runs at 10 FPS, with action lengths preserved and slower holds for blinks and sleep.
docs/neko-sleep-preview.gif shows the actual frame player. The preview simulates
a pet between sleep and waking; runtime now also supports an optional nap duration.

### Transition generation prompt

Use case: stylized-concept. Asset type: production pixel-art sprite sheet for an existing tiny Windows desktop kitten. Input image 1 is the exact white kitten character/style reference; image 2 supplies its curled sleeping posture. Create ONE transparent sprite sheet, EXACTLY FOUR equal columns and FOUR equal rows (16 fully separate sprites), no labels, grid lines, shadows, props or symbols. Read cells left-to-right, top-to-bottom. Rows 1+2 are a continuous EIGHT-FRAME FALLING-ASLEEP animation: frame1 sitting upright eyes open; 2 eyelids droop and head nods; 3 elbows gently bend lowering chest; 4 forepaws extend and chest lowers halfway; 5 belly rests down, hindquarters settle; 6 tail wraps around body and nose lowers toward forepaws; 7 head rests on paws with eyes shut, tail tucked; 8 same compact fully curled asleep posture. Rows 3+4 are a continuous EIGHT-FRAME WAKING animation: frame9 exactly the same curled sleeping pose as frame8; 10 eyes half-open with head still down; 11 head lifts a little; 12 forelegs begin unfolding; 13 chest slowly rises from ground; 14 seated haunches with forelegs extending; 15 seated with a small head/shoulder stretch; 16 neutral upright sitting eyes open matching frame1. CRITICAL CHARACTER CONSISTENCY: same head size and volume in ALL sixteen frames, no enlarging the head as body curls. Match the existing simple white pixel kitten, charcoal outline, pale gray shadows, pink nose and inner ears, shiny dark eyes, one attached tail. Keep common feet/ground baseline and centered body in each equal cell, 20% clear padding on all sides, complete sprites never touch neighboring cells. Keep camera and scale FIXED; the curled cat should naturally be shorter but NOT a differently sized animal. ANATOMY: only FOUR limbs TOTAL, exactly TWO forelegs. As forepaws lift or tuck, remove their previous positions; do NOT draw duplicate paws or extra arms. Rear legs tuck behind the body and are not additional front feet. No ghost trails, disconnected pieces, red edge specks or duplicated tails. Favor very simple readable intermediate poses with gentle movement over elaborate contortions. Clean crisp low-resolution pixel art matching the reference, not a new art style. Actual transparent background.

## Extra petting reactions

Generated with the built-in ImageGen tool using assets/neko-pets-v3.png as the
character reference. Saved in the project as assets/neko-affection-v1.png.
Four rows add chin scritches, a tiny blep, a paw offer, and relaxed ear rubs.
Each row is four drawings; this brings the collection to 96 drawings total.
These are one-shot gestures with a relaxed rest within the existing 5.8-second
petting slot, at 10 FPS rendering. They use the existing 112 x 100 canvas,
82-pixel seated size and common baseline. No frame pixels were repaired by code.
The eight pet responses use a shuffled bag, avoiding a repeat across bag boundaries.
docs/neko-affection-preview.gif renders the actual player with the four new clips.

### Extra petting generation prompt

Use case: stylized-concept. Asset type: production transparent PIXEL-ART animation sprite sheet for the existing white desktop kitten. Reference image supplies EXACT character identity, palette, head size and simple anatomy. Create EXACTLY FOUR EQUAL COLUMNS by FOUR EQUAL ROWS, 16 separate complete kitten sprites, no labels, lines, ground, shadows, symbols, hands or props. Each row is a FOUR-FRAME petting response read left to right. Same seated body size, fixed camera, fixed head volume, common feet baseline and center per cell, at least 18 percent clear padding on all sides. Crisp charcoal pixel outline, white coat, pale gray shadows, pink ear interiors and nose, big shiny dark eyes, ONE attached tail. Row1 CHIN SCRITCH: neutral seated / lifts chin a little, eyes soften / chin happily tipped upward, eyes closed / returns to neutral. Row2 TINY BLEP: neutral seated / happy half-closed eyes and a tiny pink tongue peeks from mouth / eyes smiling closed with tiny tongue still visible / tongue disappears and neutral returns. Tongue must be just a tiny pink pixel mark, no huge mouth or teeth. Row3 OFFERING ONE PAW: neutral seated with exactly two planted forepaws / lifts front-left paw slightly forward toward viewer / gently offers that same paw at chest level, soft happy eyes / returns that paw to ground. CRITICAL: the lifted paw REPLACES its original ground position. Never leave a duplicate paw below it. Other front paw stays grounded, hind legs remain tucked, no extra arm. Row4 EAR RUB: neutral seated / both ears relax a little outward while eyes half-close / ears comfortably splay sideways, eyes smiling closed / ears return upright with eyes open. Keep the head upright and both front paws planted; no whole-body spinning or excessive head rotation. All poses anatomically simple: FOUR LIMBS TOTAL, TWO front paws only, ONE tail attached to rump. No extra paws, arms, dangling legs, duplicated tails, ghosts, red speckles or disconnected parts. Every row ends in a neutral posture matching its starting posture. Match the reference's cute minimalist pixel kitten, not a new style. Genuine transparent background.
