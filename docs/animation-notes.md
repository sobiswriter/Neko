# Neko animation art

Created with the built-in ImageGen tool, using `assets/neko_idle.png` as the
character reference. The selected, cleaned atlas is `assets/neko-atlas.png`.
Original art is retained. This pass uses 64 drawings in eight rows, with timing
and directional variants defined in `animations.py`. No generated images are
needed from outside the project when running or building it.

The generator returned a 1254 × 1254 transparent sheet rather than the requested
1024 × 1024 canvas. The importer divides it proportionally, locates each main
connected silhouette to exclude neighboring-frame bleed, and uses a common scale
and ground anchor. There is still some variation between the generated drawings;
this is a compact expressive sprite set, not a manually polished animation film.

`docs/neko-preview.gif` renders the actual frame player on a warm preview canvas.
It is documentation only and is not bundled in the executable. Preview encoding
uses Pillow; the pet itself does not require Pillow for animation playback.

## Initial generation prompt

Create a production animation SPRITE ATLAS for the referenced white pixel-art desktop kitten. Reference image is character identity/style reference, not a background. One square 1024x1024 image, genuinely transparent background. EXACT regular 8 columns by 8 rows grid, every cell 128x128. Exactly ONE complete kitten per cell, 64 separate drawings total. NO labels, NO numbers, NO lines, NO background, NO ground/shadow, NO hearts/symbols/props. Keep kitten centered x=64 in every cell, paws baseline y=112, about 80 pixels tall, within cell with 16 pixels minimum margin. Consistent same character, same volume/head size/black pixel outline/offwhite coat/gray shadows/pink ears and nose/large shiny dark eyes/right curled tail. Clean deliberate pixel-art, hard crisp edges, simple readable shapes, tiny sprite intended to be shown ~88 pixels tall. Do NOT merely translate/rotate/resize the whole drawing. Animate eyes, ears, paws, head, spine and tail separately with genuine anatomical action. Left-to-right frames in each row are successive frames of ONE animation, smooth action anticipation and recovery; each row loops or ends back near starting pose. Every row use same silhouette and palette as reference. ROW 1: seated neutral idle, slow blink and subtle independent tail-tip curl, eyes close in frames 3-4 then reopen. ROW 2: curious looking, seated kitten turns head slightly toward left then right, ears rotate, eyes track, body planted. ROW 3: typing buddy, kitten seated and looking down, alternately lifting left and right front paws as though gently tapping an invisible keyboard, no keyboard object. ROW 4: grooming, kitten raises one front paw to mouth, licks it, rubs cheek and lowers paw. ROW 5: full-body cat stretch, kitten lowers forequarters and extends forepaws forward while back arches upward, then returns seated. ROW 6: sleepy yawn, kitten seated, eyelids lower then mouth opens for a tiny yawn then closes, body relaxes. ROW 7: happy head-pat response, eyes smiling closed, ears relax, kitten leans head forward and kneads paws softly then returns. ROW 8: asleep curled into a compact ball, closed eyes and head on forepaws, subtle belly breathing and ear twitch, tail tucked. Across all 64 frames keep face style and same cat identity. EXACT eight equal rows and eight equal columns; no missing/extra cells.

## Cleanup prompt

Clean and repair this animation sprite atlas, preserving the 8x8 grid, all 64 cat poses and white pixel kitten identity. Critical corrections: remove ALL stray RED pixels/red halos and all ghosted gray outlines/shadow trails around sprites. Outlines must be clean solid dark charcoal, no red edge artifacts, no drop shadow. Genuine transparent empty background, no ground line, no checkerboard painted into image. Each of the 64 complete kittens fits within its own equally sized cell with clear transparent padding on ALL four sides, including the stretch poses in row5 which must NOT touch adjacent cells. EXACT equal 8 rows and 8 columns square image. Align every frame at same center and shared paws baseline per row, maintain constant head size for each sequence, no jitter. Retain expression and real limb animation across frames. Sequence rows top-bottom: seated blinking idle; looking left and right; front paws typing; grooming paw then cheek; full body stretch and return; sleepy yawn and return; happy closed-eye kneading then return; curled sleeping. Make all cells equally sized, all sprites same scale, clean pixel-art pixels with limited palette offwhite/light gray/charcoal/pink only. Pink confined to inner ears, nose and tongue, absolutely NO red outside the cat. No text or added symbols.
