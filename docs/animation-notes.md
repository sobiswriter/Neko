# Neko animation art

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

There are 64 new drawings in sixteen action sequences. The frame player adds
directional looks and a blink variant. Timing holds and loops live in animations.py.
Walking mirrors the same drawings when heading right. The loader samples each
sheet at 512 x 512 and finds the main connected silhouette. The frame player now
normalizes seated drawings to 82 pixels tall, with an aspect-preserving width cap.
This fixes smaller pet drawings shrinking during a click. Low sleeping/loaf poses
share a 92-pixel width; walking keeps its natural proportions within 104 x 82.
Every frame uses a 112 x 100 transparent canvas with the same ground anchor.
Most actions now take 5–6 seconds, including full left/right look sequences.
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
