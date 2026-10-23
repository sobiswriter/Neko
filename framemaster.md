# Frame Master: Neko animation authoring

This is the working reference for every agent making or changing Neko animations. Read it before storyboarding, generating artwork, changing frame registration or altering animation playback. Update it when new evidence improves the method. Keep verified practice separate from proposed designs.

**Required motion study:** before planning frames for any motion, read the [permanent motion-reference index](references/motion/README.md), inspect the relevant originals/video study, and record which mechanics will inform the gesture. The user's five 2026-10-23 attachments are preserved in the project; do not depend on Downloads. They are reference material, not runtime assets or instructions to execute.

Baseline: the expressive petting revision completed on **2026-10-22**, artwork/runtime commit `28c4620`. Its [verification report](docs/petting-revision-validation.md), [exact prompts and assembly record](docs/petting-revision-prompts.json), [expression study](docs/petting-expression-study.md) and [native measurements](docs/petting-revision-native.json) are the evidence behind this guide. Earlier reports describe earlier versions; their numbers are not automatically current.

The later [pickup revision](docs/pickup-validation.md) implements held expressions and interruptible release. Its [approved design](docs/pickup-animation-plan.md), [exact provenance](docs/pickup-prompts.json) and [native measurements](docs/pickup-native.json) extend the method below. Historical reports retain their original dimensions/counts; current production values include the pickup extension.

The first [Catch the Cursor release](docs/catch-validation.md) added 48 source slots for lateral hunting and disappointment/comfort. Its [prompts and assembly regions](docs/catch-prompts.json), [all imported slots](docs/neko-game-frames.png) and [native playback measurements](docs/catch-native.json) describe that release's 576 entries.

The approved [cursor-play v2 revision](docs/cursor-play-v2-validation.md) replaces hunting and walking, adds anticipation/countdown and six distinct outcomes, and connects losses to the retained curl through a drawn look-up. That release contained729 entries; its [exact provenance](docs/cursor-play-v2-prompts.json), [imported slots](docs/cursor-play-v2-frames.png) and [native timing](docs/cursor-play-v2-native.json) remain historical evidence.

The subsequent [gallop/timer/sleep correction](docs/run-timer-sleep-fix.md) added one12-slot gallop/turn bank. That release contained **741 entries**, including212 game source slots and the appended walk idle. [Run provenance](docs/run-timer-sleep-prompts.json), [light/dark frames](docs/gallop-fix-frames.png) and [short preview](docs/gallop-fix.gif). Per the user's credit/time limit, that verification was focused; full native play-through and broad regression were deliberately left to the user.

The [2026-10-23 visitor revision](docs/visitor-validation.md) implemented the first entrance/goodbye research. That historical atlas contained **786 entries**. All 741 previous imported frames and 63 unrelated clip definitions remained identical. [Exact three prompts and assembly](docs/visitor-prompts.json), [full-canvas light/dark frames](docs/visitor-frames.png), [actual-controller preview](docs/visitor-scene.gif), [native pose coverage](docs/visitor-native.json).

The user subsequently **rejected that revision's animation quality** as unimaginative. Its report remains valid evidence of technical checks, not approval of its acting. The [reference-led v2 plan](docs/lifecycle-motion-v2-plan.md) is now implemented as [single diagonal leaps](docs/lifecycle-v2-validation.md): 19 used entrance poses/1.98s and 20 exit entries/2.20s. Current atlas: **839 entries**, retaining all 786 prior frames and 63 unrelated clips exactly. [Prompts/assembly](docs/lifecycle-v2-prompts.json), [native-size scene](docs/lifecycle-v2-scene.gif), [face-hidden scene](docs/lifecycle-v2-silhouette.gif), [native paint coverage](docs/lifecycle-v2-native.json). Technical/visual author review does not substitute for the user's artistic approval.

Latest: the [drop-out correction](docs/dropout-fix-validation.md) fixes menu quit skipping goodbye during awake gestures or visible fullscreen use. Arrival/art remain unchanged; exit selects17 entries/2.20s with continuous extension/reach, omitting the midair tuck/re-extension. All839 atlas frames remain identical. [Current actual-controller preview](docs/dropout-fix-scene.gif), [bundled-bytecode menu probe](docs/dropout-fix-native.json), [selection/assembly addendum](docs/dropout-fix-selection.json). The v2 reports above retain their historical counts and evidence.

The subsequent [idle review and diagnostics](docs/idle-diagnostics-validation.md) changes thought scheduling, automatic invitation qualification and logs only. All839 frames and every clip, including protected tail chase/catch, remain unchanged. [Current ordered idle poses](docs/idle-review-frames.png), [native-size catalog](docs/idle-review-current.gif), [measured clip/endpoint audit](docs/idle-review-metrics.json). The [idle refresh proposal](docs/idle-refresh-plan.md) awaits the user's review before any art/playback change.

Latest: [sleeping goodbye](docs/sleep-goodbye-validation.md) follows the user's explicit wake → sad → single diagonal exit request. Reuse the full eight-entry2.34s wake, then the existing17-entry2.20s departure. A partial curl finishes before wake; a partial wake continues. No new artwork or clip edits. [Actual-controller preview](docs/sleep-goodbye-scene.gif).

## 1. The design philosophy

Neko is a small character performing an action, rather than a still image being moved around. A reaction needs a readable physical story:

**Notice/anticipate → transfer weight → act/contact → let the expression read → release → recover → resume ordinary idle.**

The accepted tail chase is our reference for connected pose composition and cadence. A quiet cheek rub should have its own slower rhythm, with equally careful connections. Do not change the accepted tail art or timing as an incidental consequence of another animation.

- Give each gesture its own silhouette, supporting paws, rhythm and expression sequence. A new smile on the same head bob does not make another distinct reaction.
- Keep physical volume and character identity stable. A stretch gets wider/lower because joints change position, not because the entire kitten shrinks to fit a box.
- Make anticipation and recovery actual drawings. Appending idle cannot conceal an unfinished get-up, unplanted paw or turning head.
- Let a meaningful action linger. Paw contact, sustained stretch pressure or a sleepy pause can hold; adding two seconds to every drawing makes movement sluggish without adding acting.
- Use one main emphasis at a time. Constant simultaneous paw, head, ear and tail movement makes subtle gestures noisy.
- Review native desktop size before approving enlarged art. An attractive source sheet can lose its expression or anatomy after import.
- Use references for mechanics and silhouette. Preserve Neko's identity, palette and camera; reference backgrounds, hands, watermarks and text are not sprite content.

### Whole-body mechanics before facial polish · 2026-10-23

Observed in the [saved video study](references/motion/2026-10-23/video-pose-study.png): extended forelegs meet the ground with the rear still high, then the front yields, the spine folds and the hindquarters settle before recovery. The [spine page](references/motion/2026-10-23/spine-flexion-study.jpg) illustrates the contrast between stretched/concave and gathered/convex forms. The two silhouette collections demonstrate clear action-specific outlines; they do not provide timed frame order. These are verified observations of the supplied references, not a tested Neko recipe or universal live-cat timing law.

Apply the following as the revised authoring/acceptance workflow; validate its results on the next prototype:

- **Separate connected masses.** Plan head, chest and pelvis, with a flexible spine between chest and pelvis. Their phase and spacing change through reach, support, compression and extension. Do not move them as one rigid torso with feet attached decoratively.
- **Make the extremes different.** Stretch, gather, loaded support and recovery need recognizably different silhouettes. Show spine flexion and changing limb spacing. Stable character volume does not mean a fixed outline or constant torso length.
- **Explain every contact.** State which paws support weight, which swing, when contact begins and when it releases. Once a paw plants, the body moves relative to it until release. Near/far legs remain distinct through depth/occlusion; visible paws must not multiply to preserve an old contact.
- **Allow orientation to change.** A stable camera forbids arbitrary zoom or view jumps; it does not forbid a drawn turn of the animal. Use a side-biased three-quarter view when it exposes the mechanics, then author the turn back to familiar idle. Do not rotate a rigid bitmap to substitute for a new body pose.
- **Let force lead overlap.** Chest and pelvis need their own weight changes before adding tail/ear lag. A tail flick cannot rescue a motionless spine. Mechanical follow-through and expressive secondary action have different jobs.
- **Do not trap the kitten in the idle box.** The 82px height is the seated calibration reference. Natural crouches, extended bodies, turns and airborne tucks change their extents through drawing. Keep physical head/body volume, not identical per-pose width/height. Measure full extremes at retained scale before deciding the fixed canvas.
- **Approve keys before filling a sheet.** First review a small set of action-defining poses and their support maps, then their connected motion at native size and normal speed. More in-betweens around weak extremes produce a smoother weak action. Generate connecting poses only after the key movement works.
- **Test the face-hidden performance.** Reach/contact/gather/push/recovery must read without eyes or mouth. Then add expression across moving poses so it remains visible without freezing the body. Technical bounds, components and pose-coverage tests are necessary but cannot approve appeal or replace the user's judgement.

For each future animation, the brief must link its chosen reference and describe a support/spine map. Do not transplant the photographed gallop's frame count into a vertical landing, or treat the video's final walking exit as an observed downward jump. New combinations of those mechanics must be labelled proposed until tested in Neko.

Choose mechanics appropriate to the gesture: a quiet blink can keep chest/pelvis supported and still. These examples do not require exaggerated spine movement in every idle. The map should explain stillness as well as motion, preserving one clear main action.

### Expressions belong to gestures

The [expression study](docs/petting-expression-study.md) separates reference-informed body-language observations from stylized acting choices. Glyphs such as `=_=`, `;)` and excited squeezed eyes are descriptions for artists, never text stamped over the face.

| Acting | Drawn treatment | Timing/gesture |
| --- | --- | --- |
| Relaxed | Partial straight upper lids over the existing eyes, tiny quiet mouth, soft ears | Pressure eases into supporting paws; slow reopen after contact. |
| Wink | One eye closes through intermediate lids while the other stays soft | Brief accent during cheek/paw contact, followed by a drawn reopen. |
| Excited | Short inward eye squeeze, attentive ears and connected body effort | Reach or hop apex; open eyes around landing. Avoid angry brows. |
| Sleepy | Heavy lids, small breath, slight supported head settling | Sleep precedes the peek; reopening precedes rising. |
| Yawn/deadpan | Jaw opens and closes, then level half-lids with closed mouth | A complete yawn followed by a readable quiet hold, not one open-mouth sprite. |

Keep eye/nose spacing, mouth placement, head volume and ear construction consistent. Eyes/ears can lead a head movement by a drawing; shoulders follow and the tail lags a larger movement. This is an acting guideline, not a reason to move every feature in every pose.

## 2. Plan the complete action before making art

Read the current code and relevant validation report, then write the storyboard in `tasks/plan.md` with tasks in `tasks/todo.md`. Preserve incomplete work already recorded there. Ask for review when the user requested a plan first; do not treat a proposed plan as implementation authorization.

For each action, record:

1. Trigger, starting state, finishing state, total timing target and whether it is finite or genuinely looping.
2. Ordered story beats with approximate times, expression changes and what the viewer should notice.
3. Support/occlusion map at difficult poses: which forepaw/hindpaw supports weight, which leg is hidden and where the attached tail travels.
4. Entry, every repeated-cycle seam, recovery and connection to the actual idle drawing.
5. Interruption rules: repeated pets, dragging, nap, hiding, reduced motion, fullscreen and quit. User-controlled holding additionally needs release from every phase.
6. Source-pose budget, canonical calibration drawing, likely bounds and highest-risk prototype.
7. Acceptance evidence: numerical checks, source/runtime visual review and real-window playback.

Prototype the difficult geometry first: belly-up roll occlusion, low kneading support, deepest stretch and highest hop. For pickup, first prove the tall silhouette and release at arbitrary phases. Source slots are a planning budget, not a quota; repeated clean holds and neutral drawings may be selected intentionally. Source slots, unique drawings, clip order entries and screen repaints are different quantities.

Before that geometry prototype, choose the reference and establish the key silhouettes, chest/pelvis/spine changes and support map. For high-travel lifecycle actions, prototype route and pose together: a technically clipped exit can still look like a rigid kitten being thrown across the monitor.

## 3. Canonical character and current production measurements

Use `assets/neko_idle.png` as the generation identity reference and the actual atlas idle as the runtime comparison. Preserve white fur, gray chest/underchin shading, charcoal stepped outlines, pink nose/inner ears, large dark eyes with small square highlights, compact body and large head. Keep hard pixel clusters; use nearest-neighbor scaling for review/import.

Current pet production values in [animations.py](animations.py):

| Item | Verified baseline |
| --- | --- |
| Transparent runtime canvas | 192 × 144 px for every atlas frame; original 192 × 112 area padded 32px above |
| Horizontal padding relative to old 112px footprint | 40 px on each side |
| Seated reference body height | About 82 px |
| Seated reference head width | 62 px; endpoint tests allow ±4 px |
| Ground reference | Import y=98, then 32px top padding: runtime y=130 |
| Near-idle final head center | Within 2 px of actual idle |
| Final crown position | About y=48, ±2 px after top padding; held crown y=16 |
| Pet/carry playback repaint interval | Precise Qt timer, 50 ms, nominal 20 FPS |
| Total atlas entries | 839: 786 retained entries plus 20 arrival, 16 original departure, four corrective bridge and eight sad-transition slots, plus five appended departure keys; other replacement aliases add no keys |

These are baseline measurements, not permission to force every posture into a seated shape. A lying kitten is lower and wider. Check continuity against appropriate anatomical landmarks throughout the action. If a new pose needs space, measure it at the retained character scale before changing the fixed canvas. Do not resize the desktop window on each pose.

## 4. Generate the drawings, preserve the evidence

Use built-in ImageGen for authored raster anatomy and expression changes, with `transparent_background: true` and the canonical reference. Extraction/render tools may crop, register, pack and resize existing drawings; they do not invent limbs or paint replacement facial acting.

The exact successful and rejected prompts are in [petting-revision-prompts.json](docs/petting-revision-prompts.json). Reuse its structure, then specify the new action pose by pose. The common prompt contract included:

> Fixed camera and physical head volume; exactly four anatomical legs (two forelegs, two hindlegs), one connected torso/neck, one head, two ears and one attached tail. Occluded legs stay hidden. A lifted paw replaces its grounded version. Four chronological columns, generous clear cell padding, every complete sprite inside its cell. True transparent alpha; no floor, shadow, haze, props, hands, hearts, motion marks, labels, numbers, grid or watermark.

Also specify the particular eye/lid/mouth/ear acting, weight-bearing joints and complete seated recovery. “Cute kitten animation” alone leaves too much room for unrelated poses or decorative motion. Request distinct action-defining extremes and connected breakdowns between them, with ease into/out of contact. Small changes belong between strong extremes; they must not restrict the whole performance to nearly identical silhouettes. Earlier revisions used 16–28 source slots depending on the story; choose future counts from the motion, not those historical sheet sizes.

Generated sheets can violate row count, equal spacing, size, anatomy and the requested expression. Inspect actual output rather than trusting the prompt. Reject/redraw unusable anatomy or expression. An adjacent complete drawing can replace a contaminated hold if the action remains coherent; record the substitution and recheck its timing. Never keep a bad frame merely to reach the planned count.

Record exact prompt text, reference identities, generated output identity, rejected drafts, chosen source indices, batch calibration and final asset names. The generation cache is not a runtime asset directory. Final consumable PNGs belong in `assets/`; tracked prompt/assembly records must explain how they were made. The one-off extraction/native-probe scripts from this revision live under ignored `build/` and are not prerequisites future agents can assume are available.

## 5. Extract and assemble complete silhouettes

The revision's extraction procedure was:

1. Inspect the sheet's actual layout. Search source columns with horizontal overscan for the expected major high-alpha connected kitten silhouettes.
2. Sort silhouettes into their intended chronological row/column order; verify it visually against the storyboard.
3. Crop each complete silhouette's bounding rectangle, retaining ears, paws and tail. Check for neighboring-cell bleed and detached fragments inside that rectangle.
4. Pack the selected drawings in four columns of **384 × 384 px cells**, with a shared baseline 12 px above the cell bottom and adequate clear padding.
5. Use a single documented calibration for a source batch. Combine separately generated batches only after comparing neutral head/body landmarks.
6. Select the same generated neutral calibration drawing for source slot zero and the final source slot. Runtime substitutes actual idle at zero and appends actual idle after the final generated neutral; physical recovery must already be finished.

Bounding-box extraction is not a transparency cleanup guarantee: an unrelated fragment inside the bounding rectangle survives. The final stretch review found exactly this failure. The regression checks imported drawings for 8-connected components at alpha ≥128, ignores isolated 1–2 px specks and requires a single larger component. This catches detached pieces, not attached extra limbs or incorrect anatomy. Light/dark visual review remains essential, including faint alpha below that threshold.

### Actual assembly decisions worth preserving

These are revision-specific recipes, with full output identities in the JSON; they are examples of measured corrections rather than universal constants.

- **Roll:** from 28 generated slots, exclude zero-based `1, 3, 24, 26`, leaving 24. Inspect the turning/occluded legs and supported rise closely.
- **Knead:** generate transition `T0..T11` and cycle `C0..C11` separately. Register the cycle uniformly by `head_width(T0) / head_width(C0)`. Entry is `T0,T1,T2,T3,C0,C0`; run `C0..C11` as four finite left/right pairs; recovery is `T3,T2,T8,T9,T10,T0`. Transition `T4..T7` caused a head dip/jump and were excluded. The cycle was redrawn with bent elbows and yielded shoulders because the upright draft did not read as kneading.
- **Front stretch:** use the first 16 corrected main drawings and eight separately authored recovery drawings. That recovery batch used `scale_x = 153/229` from neutral head width and `scale_y = 214/355` from neutral seated height. These fixed batch values correct source mismatch; they are not per-pose fitting. Final neutral selects main `M0`.
- **Stretch fragment:** source slot 14 contained a detached 16-pixel line. Reject it and select the clean complete slot-13 hold again; do not paint/delete anatomy to disguise a bad drawing.
- **Nuzzle:** recovery order is `0..14,16,17,15,18,0`; decreasing head tilt removes an unwanted second lean after centering.
- **Ear rub:** anticipation slot 1 selects near-neutral softened-lid source drawing 14, avoiding an oversized early tilted head.

## 6. Import at one scale; anchor the physical support

### Cursor-play v2 evidence

The supplied gallop GIF has eight decoded frames (first0ms, remaining seven100ms). Its mechanics emphasize hind loading, leg gathering, spine extension and forepaw support. The replacement run selects eight drawings at90ms each, with drawn excited squeezed eyes across four consecutive poses (360ms), then four attentive open-eye support poses. This replaces the old70ms single-pose expression accent. Source flight poses3/4 have fixed5/8px lift offsets; contact poses remain at baseline130. Neutral calibration and all existing jump/paw-contact artwork remain unchanged. This recipe has light/dark strip, short runtime-timing preview and focused bounds/component checks, not a full new native gameplay validation.

The game importer retains one neutral calibration per batch: head62/body82, baseline130 in the 192×144 canvas. Do not reuse a seated-width heuristic as a head-width measurement for a lying pose: the haunch can join the longest alpha run. Review the actual face, support and silhouette together. The first loss-c batch visibly grew through later rows and was redrawn against the actual new curl; per-pose fitting was rejected.

Both ready drafts yielded fifteen drawings. Repeat the complete gathering crouch once (source11), then use the squeeze, reopen and final launch-ready drawing; this gives sixteen runtime slots without inventing anatomy. Its longest complete tail is 387px wide, requiring 448px packed cells/baseline436. Other v2 batches retain384/baseline372. Complete silhouette crops preserve original RGBA, including faint alpha; labels/matte are removed through ImageGen edits, not pixel painting.

The grasp victory's final tall sit was rejected. Its complete supported recovery uses source14→13→2→1→generated neutral0→actual idle; packed18/19 select source0. Hop/grasp batches have a measured constant +2px x registration. The walk's final source sit was 6px shorter than canonical: packed15 selects generated neutral0 after the completed supported sit/blink, before appended actual idle16; settle lasts720ms. Three hop arcs and a single hug bounce use explicit in-canvas offsets in `load_games`; proud-paw celebration remains grounded.

New lowered-face curls cannot cut straight to the retained outward-looking curl: the crown changes by about18px. The eight-slot common look-up bridge supplies small drawn ear/head changes before the retained curl and comfort. Seven used entries last120ms each. All three seams must be reviewed; appending a canonical endpoint alone is insufficient.

Count the notice and each numeral as independent controller phases. Start the phase clock after its actual thought label is presented, so backdrop preparation cannot shorten a beat. Native cue timestamps are stronger evidence than the first later polling observation of a phase. The warmed Windows probe measured each numeral near one second, all six outcome orders, all hunt/walk/countdown drawings, unchanged foreground and actual thought hit-through. This was DPR 1.0 on one monitor; mixed-DPI behavior remains unverified on physical hardware.

The current pet importer in `SpriteAtlas.load_pets` reads four columns and `PET_ROWS[name]` rows, overscans each cell vertically by one eighth, scales the cell to width 128 and finds its main sprite bounds. `pet_landmarks` measures the longest opaque head run in the upper three-fifths and extreme contact pixels in the bottom 14 rows. This heuristic suits the current drawings; validate it before applying it to a new hanging or turned pose.

For the first neutral source drawing:

```text
sx = 62 / reference_head_width
sy = 82 / reference_sprite_height
center_target = idle_head_center + ((reference_left + reference_right)/2 - reference_head_center) * sx
rear_target   = idle_head_center + (reference_right - reference_head_center) * sx
```

Apply those same `sx, sy` values throughout the sequence. Separate x/y calibration here is existing source normalization against measured canonical landmarks, not permission to squash individual poses. If a new batch needs extreme distortion to match, redraw it.

Default placement aligns the mean support contacts with `center_target`. Stretch/arch align their rear support with `rear_target`. Hops align the head axis with the actual idle head axis; roll uses a silhouette-center track calibrated against the reference head. These are action-specific anchors, not arbitrary recentering of every bounding box. The head-relative target prevents a different tail/haunch width from shifting the resting kitten sideways.

The hop's ground offsets are explicitly:

```text
0,0,0,0,3,8,11,6,0,0,0,4,10,13,7,0,0,0,2,6,8,4,0,0,0,0,0,0
```

There are three actual airborne passages separated by contact/compression. During petting the desktop window stays fixed; these arcs happen within its canvas. The importer currently clamps a sprite's left margin to 2 px where its full width fits. Do not rely on that clamp to conceal source drift or clipping.

### Idle handoff and timing

`Clip` stores bank, row, integer millisecond durations, pose order and loop flag. Finite actions clamp at their last entry; genuinely repeating states opt into loops. Match duration/order lengths and use the actual clip sum as the runtime deadline.

Source pose zero becomes the actual canonical idle. Keep the final generated neutral after the complete recovery, then append the canonical idle at index `rows * 4`. The importer does not automatically insert an unrelated penultimate idle blink. The current clip setup splits the old final hold into `150 ms` drawn neutral plus `old_final_hold - 150 ms` canonical idle, preserving total duration. New clips must have enough final hold for that split or use an explicitly reviewed alternative.

Connecting poses currently have at least 50 ms, commonly 100–250 ms; contact/expression holds can be 250–500 ms or longer where the story warrants it. These are observations and planning guidance. Judge rhythm in normal-speed playback, not by maximizing frame count.

Current reaction totals/source slots after the requested speed adjustment: head pats 2.432s/16, nuzzle 3.214s/20, knead 5.173s/24, chin 2.606s/16, roll 5.039s/24, paw offer 3.125s/20, ear rub 2.562s/16, stretch 4.516s/24, arch 4.253s/24, three hops 4.342s/28, side flop 5.910s/28 and shoulder peek 5.561s/28. Pet durations are divided by 1.15 and rounded to integer milliseconds, with a 50ms floor so no drawing becomes shorter than one nominal repaint. All orders, artwork and complete recoveries remain unchanged; other clips retain their timings. See the [speed verification](docs/petting-speed-validation.md).

### Single diagonal lifecycle leaps · 2026-10-23

**Current correction:** source v2 menu quit only admitted IDLE/ARRIVING and rejected every fullscreen flag, so ordinary awake gestures and a deliberately visible fullscreen pet could close without any goodbye. Queue a finite clip's authored recovery, suppress competing interactions, then start the seated sad departure once. Sleeping quit now plays the complete wake first, at the actual clip sum rather than the behavior model's2.6s fallback. A partial curl must reach its supported sleep endpoint before waking; a partial wake must not restart. Do not snap sleep directly to seated sadness. Motion-off, hiding or monitor change can still close promptly; carry/game quit stays immediate. Respect actual visibility/fullscreen-hiding preference instead of rejecting a visible fullscreen pet. Test the **menu QAction**, including the executable's bundled code/assets; direct `start_transition` coverage alone cannot validate the entry path.

Use departure order0/1/2/16/17/18/19/20/4/5/6/7/8/11/13/14/15. Flight durations90/90/100/120/140/200/260ms total1000ms after the unchanged1200ms expression/load/push. Remove9/10's midair fold and12's steep-to-shallow reversal to keep one continuous reaching leap. Retain the single world arc; no second push or grounded contact after launch. Source pixels/calibration and the arrival order/timing are unchanged. Exact selection addendum and preview are linked in the latest report.

The current [v2 report](docs/lifecycle-v2-validation.md) supersedes the visitor acting below. The user explicitly requires **one graceful leap per action**. Arrival starts already reaching along a down-right diagonal from the first upper/left monitor boundary. World travel ends at first fore-contact (500ms); the subsequent folding, hindquarter settling and supported rise never launch another hop. Departure gathers and pushes, then follows one arc: a single 18px rise followed by a descending diagonal through the bottom or nearer side. Pick the route before playback and mirror the animal with its direction; preserve the canonical first idle without mirroring its asymmetrical placement.

The final user steering requires sadness on “Let her go.” A separate eight-slot sheet draws neutral → softened ears/eyes → sad dipped head → heavy blink → reopened turn → planted steps → lowered shoulders → loaded crouch. Sad1/2 replace depart1/2; sad3..7 append as depart16..20. The old cheerful blink and redundant half-crouch3 are omitted from the active order. The first700ms lets sadness read; all eight expression/turn entries stay grounded for1000ms, then load/push200ms and one flight1000ms. Keep front-facing0/1/2/16 unmirrored in either direction; mirror from the drawn turn17 onward to avoid flipping the sad face/placement before she turns. One direct painter regression checks both sides of this seam. Sadness is authored expression, not a text glyph or a frozen pre-jump overlay.

Two 12-pose key studies established extended reach versus convex gather before the full 20/16-slot sources. In these reviewed drawings, bottommost leading foretoes provide a usable contact anchor: align arrive1..11 to x130, with constant sampled ground132. Arrival4..8 keeps that toe within one pixel while shoulders yield and pelvis follows. This heuristic is **specific to these raised-tail poses**, not a universal paw detector. Do not apply it to a low trailing tail. Departure3..5 uses authored hind-toe offsets (-9,0,+19), with the window stationary through the planted push. Source6 is already airborne; world flight therefore starts there, even though the generation prompt had requested final toe contact.

Complete original RGBA crops use 512px cells/baseline500 to retain the longest extremes. Sample at128, then calibrate one batch reference to head62/height85 and place at ground132. The two-pixel transparent edge compensation produces the measured canonical visible height/crown/ground; it is not a new general seated-height target. Arrival12..19 uses its own neutral16 for the drawn turn/recovery. Do not fit each pose independently. The final arrival19 and first departure0 use actual idle only after/before their compatible drawn transitions.

Bounding crops retained neighbouring-row paw fragments in departure8/11/12/15. Reject those active drawings: a separately generated four-slot bridge supplies three complete replacements; final15 repeats clean14 as a follow-through hold. Exact original regions and substitutions remain in provenance. All 53 new imported entries pass the significant-component check, but attached anatomy and appeal still require visual review. [Light/dark full-canvas sheet](docs/lifecycle-v2-frames.png), [invariant measurements](docs/lifecycle-v2-invariants.json).

### Retained tail and historical lifecycle recipes

The [2026-10-23 entrance/goodbye research](docs/arrival-goodbye-research.md) was subsequently approved and implemented in the [visitor revision](docs/visitor-validation.md). The old lifecycle recipes below are historical. The new pair uses real window travel and selected-monitor clipping for both directions; the full departure sprite stays intact inside its fixed canvas. Preserve the resting origin independently of temporary travel, including save, hide, motion-off, monitor change and final cleanup.

Native review accepted a low supported curious lean instead of a hanging edge grip; the latter was not generated or claimed as tested. The first arrival sheet's seated recovery shrank to 67px versus the canonical 83px bounds. Reject that endpoint; a separately generated/calibrated eight-slot recovery replaces arrive14..19 with recover1..6, followed by actual idle20. Do not repair head/body drift through per-pose fitting or an abrupt canonical substitution. The near-neutral recovery now passes crown/head-size/baseline checks. Three real native scenes paint all 20 entrance and 16 goodbye poses; a higher exit retains the same bounded 1.8s clip. Subjective motion quality and physical mixed-DPI remain human checks.

The [tail/lifecycle notes](docs/tail-lifecycle-notes.md) and [exact revision prompts](docs/playful-motion-prompts.md) preserve that earlier motion study; their old canvas/atlas totals are historical. The accepted construction is still relevant:

- The supplied running GIF informed **eleven 50ms poses**, making a 550ms turn: low stretched body, squeezed eyes, alternating scrambling paws and a long tail trailing outside the turn. It replaced a rejected slow tucked-tail cycle. Chase repeats the turn five times; catch uses two turns before its pounce/two-paw payoff. Final totals are 4.69s chase and 3.68s catch.
- `neko-tailplay-v4.png` contains the accepted run/payoff. `neko-tailsettle-v1.png` adds eight separately calibrated entry/recovery drawings, appended as indices 16–23 rather than modifying the accepted run. Eager tilt/crouch/run-ready prepares play; deceleration/half-sit/contented blink returns to actual idle. Catch connects its low pounce into half-sit. Inspect the run seam and these physical-height changes independently.
- Arrival combines `neko-arrival-v1.png` landing art with real window travel from the target monitor's top edge to the saved resting position. The first three pose durations total 700ms; accelerating travel uses `drop_progress`. Complete airborne/contact/compression/rebound/sit drawings make the 1.9s story. A pose-only sheet cannot verify that desktop trajectory; use the monitor-scene preview and native window.
- Departure introduces the first two `neko-farewell-v1.png` sad drawings for 650ms and 350ms, then the retained 200ms crouch and accepted `neko-lifecycle-v2.png` hop/arc. Its 2.15s total gives the emotion time to read without replacing the graceful motion.
- A later startup correction starts arrival timing on the first Qt animation tick so loading cannot consume the fall before the window appears. See [startup verification](docs/startup-thought-validation.md). Preserve the landing target through hiding, reduced motion, monitor changes and quit.

## 7. Carry artwork changes through the runtime

### Prepare release frames at build time

`main.spec` runs `tools/bake_atlas.py` on every build. It packs the original importer's complete frames into a lossless PNG plus their ordered keys; the executable reads these without redoing silhouette analysis. Keep the source importer as the authoring and damaged-resource fallback. Any importer/art change must regenerate the packed atlas and pass exact equality for every frame. Clip timing, canvas registration and source artwork stay unchanged. Existing previews remain valid only while this equality holds; do not use a stale packed sheet for authoring. See [startup evidence](docs/startup-performance-validation.md).

### Cursor-game drawings and contact

Verified in [Catch QA](docs/catch-validation.md): extract complete significant connected silhouettes before packing; nominal source-row cuts admitted preceding-row paws in a hunt drawing. Store exact crop regions in provenance. Source bounding crops retain original alpha; a generated transparency edit is not proof that every fringe was removed. Inspect the final native light/dark output and test significant imported components.

Game source cells use the existing 128px nearest-neighbor sampling step before connected-silhouette extraction. Each bank keeps fixed neutral-head/height calibration (62px/82px), 192×144 canvas and ground130. Airborne poses remain registered in that canvas; the controller supplies the world arc once. The actual painter's y−1 offset must also be included in collision coordinates. The reviewed high-reach point is hunt19 (49,80); landing contact is hunt21 (59,124). Contact additionally needs the current pose's authored forepaw region and visible alpha, mirrored with the drawing. Never count head/tail/transparent padding or interpolate a fictitious pointer trail.

The game runs a precise 20ms timer so its 40–80ms connecting poses can be observed; ordinary pet/carry/tail timings remain intact. Reuse the accepted three-hop clip unchanged for a game victory without entering a counted pet state. A disappointed curl is an explicit mood, distinct from a nap; hide/carry preserve it and a deliberate pet owns its get-up. Preserve the original resting position during pursuit/flight and return home after recovery; an actual user drag can choose a new resting origin.

Native scripted cursor observations validate real Qt playback and drawing coverage, not human enjoyment or physical multi-monitor/DPI behavior. Keep those limits explicit.

Read callers before changing a shared function. An animation change can reach:

| Surface | Current responsibility / what to check |
| --- | --- |
| `behavior.py` | State selection, deadlines, nap rules, twelve-reaction shuffle bag and bounded pending pet. |
| `animations.py` | Imported banks/row counts, calibration, frame order, durations, loops and canonical endpoints. |
| `main.py` | State-to-clip mapping, repaint cadence, real clip deadline, input, cursor, saving/clamping and lifecycle. |
| `assets/`, `main.spec` | Final bundled artwork and resource presence. Retiring an action includes its selection/mapping and required assets. |
| `test_behavior.py`, `test_animations.py`, `test_main.py`, `test_packaging.py` | Behavior, rendered pose invariants, native integration and actual bundle checks. |
| `tools/preview_animations.py`, `docs/`, README | Accurate sampling, full playback, contact sheets, prompt provenance and current descriptions. |

`Companion.pet()` counts clicks immediately and coalesces at most one pending reaction. `finish_pet()` starts that pending reaction at the completed action's safe end, without counting it twice. `main.refresh_asset()` replaces the provisional behavior duration with the actual clip sum at every pet start, including queued starts. A longer clip must not be truncated by an old generic duration. Nap waits for active pet completion; a tiny snooze inside flop stays a pet state rather than starting a real nap. Hide/reduced motion clear pending pets.

Current timer classes differ intentionally: petting/carrying use precise 50 ms; accepted tail motion uses 50 ms coarse; arrival/departure briefly use 33 ms; ordinary idle uses 100 ms. Source-pose timing and Qt repaint interval are separate. Custom GIF assets still override ordinary atlas playback where supported; carrying/lifecycle own their authored drawings and do not play a competing custom movie. Inspect customization paths when changing behavior.

### Desktop and presentation compatibility

- The 192 × 144 widget is fixed during playback. Keep original visible placement through the saved-position convention: load `saved - QPoint(40,32)`, save `(arrival_target or current_position) + QPoint(40,32)`. The expanded canvas is clamped to available screen space; edges can therefore nudge a placement. Lift/descent artwork stays inside that canvas, so its transient offset never enters preferences.
- Keep the tray icon's central 112 × 112 crop (`x=40,y=32`) so transparent padding does not make her icon tiny. Preserve shadow/heart/text and mouse-follow reference positions when adding canvas space. Legacy catalogs omit the empty top padding to keep their earlier layout.
  For following, use the original footprint's `QRect.center()` after removing top padding; `width // 2` differs by one pixel from Qt's integer rectangle center and changed the tested walking stop point.
- Transparent side padding must pass through to desktop clicks; the visible kitten remains interactive. Added space is not an invisible click-blocking panel.
- Arrival leans into view at its selected monitor top before accelerating to the saved landing target. Both lifecycle clocks start on the first animation tick. Save the resting origin through either flight; departure now uses a warm blink and real window trajectory, not its historical sad pause/local crop.
- The user's later readability request supersedes background-free thoughts: semibold glyphs sit on compact rounded glass, with click-through/no-focus behavior. A local per-thought sample is softened at 3px and painted inside the 20px rounded path; text adapts to light/dark content. It is static while visible and the sample clears on hide, with no file/network output. Native accent blur was rejected after actual outside-corner pixels exposed square spill despite a valid window mask. See [clipping verification](docs/thought-rounded-clip-validation.md). Sprite artwork still requires true transparency. Cursor artwork retains a fixed hotspot; the pet stroke never moves the actual pointer.
- Carrying does not count as petting, preserves real naps and defers a due timed wake until supported placement. An already waking kitten finishes upright on placement rather than replaying a partial wake. Held drowsiness remains distinct from the real nap lifecycle.

### Interruptible pickup method

The pickup revision uses four expression sets over compatible held body phases, authored entry families and one shared landing. See its linked report/provenance for exact timings and source identities.

1. Prototype the retained-scale hanging silhouette first. The roughly 100px hanging body required 32px top padding for a readable lift; head/body were not shrunk. All 427 earlier drawings compare exactly after removing that padding, and all 32 earlier clip definitions are unchanged.
2. Generate the common held loop, then edit expressions against it. Reject geometry drift: the original sleepy generation shortened the torso and introduced detached fragments. Its face-only repair retained the accepted loop body. Reject visible background haze too; the rolled entry required a fresh clean redraw after a failed alpha repair.
3. Calibrate each bank once. Sample cells to width 128 before connected bounds, then use a 62px head span. For hanging drawings, measure only the upper 40% to exclude a high tail. Side/low/rolled entry families calibrate from their final upright held drawing; track their full silhouettes relative to that reference head instead of trying to measure a tilted/occluded starting head as seated.
4. Preserve the actual currently visible frame at recognition. Align the appropriate drawn entry family and fade its placement offset to zero. Do not insert idle before lifting from a stretch/flop/roll. Normal entry is eight 50ms slots; awake side entries also reopen the eyes through drawn bridges.
5. Release owns the next visible response. Capture the current frame, close/reopen the face through authored drawings where needed, then use the 700ms supported landing. For real sleep, reverse the closed-eye side entry into the curled nap pose. Early release reverses visited entry drawings and uses the starting gesture's existing recovery.
6. Re-grab reverses the visited release and must also finish any unvisited lift. A test reproduced a 22px jump when that remaining lift was omitted. Preserve active expression time through release/retracing so re-grab cannot skip a mood bridge or reopen a yawn abruptly. Keep the unvisited lift separate from the remaining placement path; when released again during retracing, retain its frozen expression elapsed time rather than deriving it from a transient path clock.
7. Use existing `Clip` timing for dynamic paths as well as atlas clips. Keep drawing selection/phase separate from behavior ownership: `HELD`/`SETTING_DOWN` suppress competing actions, while real nap state/counts are retained separately. Keep all path storage bounded; long holds reuse loops rather than accumulating frames.
8. Load carry banks as a complete set. Missing/corrupt sheets must preserve ordinary dragging/fallback instead of exposing a half-loaded pose family that crashes on release. Validate with a damaged-bank regression and bundled-asset hashes.
9. Keep every state renderable even without a live input payload. The all-states smoke check creates held states directly; it exposed a missing-context assumption in the renderer. An absent carry context now selects safe idle and can be cancelled. Keep that regression alongside the live-grab tests.

The current mood targets are excited 0–3s, calm 3–10s, mildly unimpressed 10–20s and sleepy 20s onward. Two four-drawing facial bridges and a one-time 650ms yawn prevent abrupt face switches. Loops have a 2.4s period; sleepy uses eight closed-eye drawings rather than repeating its yawn. Short click versus 250ms stationary hold versus immediate distance-triggered drag are separately tested.

## 8. Verification: drawings, sampling, real playback, release

### Behavior evidence alongside motion review · 2026-10-23

An action's thought is not a generic idle thought. Dispatch gesture-specific lines while the matching clip is active, cap their visible lifetime to the remaining action, and do not consume the general-thought timer. A due general thought remains due if another bubble blocks it; acknowledge its interval after actual display. A new gesture or sleep/care/visibility restriction can still suppress speech rather than replacing readable text. Diagnose those decisions in the local journal instead of assuming no words means no animation.

For automatic play, observe the outside approach before cooldown expiry, but require the stable entry itself at/after the deadline. Discard stale qualification during sleep/care/typing/visibility blocks and preserve one pending intent. Test already-inside-at-expiry as well as first-entry-after-expiry. The Nook Journal can observe automatic play live; editing other Nook tabs pauses auto invitations. Model acceptance, actual game creation, countdown labels, outcomes and rendered words are distinct events and should be recorded distinctly. Wait reasons log on change, not every100ms poll.

These are verified scheduling/diagnostic practices, not new approved idle artwork. Existing idle entries/recoveries are real drawings; canonical first/last aliases alone do not certify adjoining pose continuity. The current ordered review must follow first-use clip order (lazy swish0..6,8,7), preserve the full144px canvas and keep protected tail art/timings/weights intact. Proposed resting breath, richer support changes and new in-betweens remain in the plan until approved and tested.

### A. Establish failure and protect unrelated work

For logic/calibration changes, first add the smallest meaningful regression demonstrating the defect. Do not write tests that merely restate an array. Example: count three separated airborne passages from rendered ground bounds, rather than only asserting that an offset tuple exists.

Before shared atlas/canvas work, snapshot unrelated clip definitions and rendered frames. The last revision compared all 147 non-pet frames pixel-for-pixel after cropping the new padding (`40,0,112,112`) and verified unchanged clip definitions. This protected the accepted tail art/cadence. A reversed calibration-sign mutation was also rejected by head-alignment checks; mutation stayed in memory, not in production files.

The pickup comparison retains each QImage object while copying `constBits()` into bytes; do not hash a buffer exposed by a temporary image whose owner has already been released. That correction produced a clean comparison of all 427 earlier frames after cropping `(0,32,192,112)` and all 32 original clip definitions.

### B. Review every selected drawing and connection

- Before facial polish, compare the full-body extremes with the selected motion reference. Hide facial features and verify that line of action, spine shape, contact and weight changes explain the action. Mark a technically valid but weak performance for redraw; do not count pose coverage as artistic acceptance.
- One connected head/neck/torso; two forelegs and two hindlegs accounted for, allowing natural occlusion; no extra grounded paw beneath a lifted leg; one attached tail, two coherent ears.
- Review entry, action, maximum reach/turn, each loop seam, complete release and actual-idle handoff. Compare adjacent frames and slow playback, not only attractive keyframes.
- Check head volume, eye/nose/mouth drift, expressions at native size and scale/alignment at both endpoints.
- Check clear boundaries, genuine alpha, faint haze, detached islands and neighboring sheet fragments on light and dark backgrounds. Numeric component tests cannot certify attached anatomy.
- Check physical support and believable joint travel. Kneading alternates pressure with a quiet head; roll rises through planted support; hops have landing compression between arcs.

### C. Preview the runtime output

Use `SpriteAtlas` and actual `Clip` timing through [tools/preview_animations.py](tools/preview_animations.py), not a separately approximated timing list. Pillow is an optional preview dependency, not a new runtime dependency.

```powershell
.venv\Scripts\python.exe -m unittest test_behavior test_animations test_main -v
.venv\Scripts\python.exe tools/preview_animations.py
```

The current pet catalog includes 0.8s ordinary idle first, the full longest reaction, then at least 0.8s ordinary idle. Duration is derived from the maximum clip length plus that allowance (currently 9s normal, 18s half speed). Verify decoded GIF durations and that every used pose is sampled. Round the elapsed time after subtracting the intro (`round(elapsed - 0.8, 3)`): floating-point subtraction previously skipped short poses. Native 192 × 112 images and contact sheets must retain aspect ratio; the old square-thumbnail resize would squash the expanded canvas.

### D. Observe the actual Windows event loop

An offscreen screenshot or generated GIF is not proof of native timing. Let a test-owned visible window warm up, start each action, record every expected pose entry and paint interval through the real Qt event loop, and capture light/dark native rendering. A synthetic polling loop can distort timing; starting before the window is visible can miss initial entries in the probe.

The v2 probe observes `current_frame` calls from actual Qt painting while production's own animation timer advances the controller. Calling `animate()` from a second 20ms probe timer would double the repaint rate and is rejected as timing evidence. Group paint intervals within each staged scene; an intentional idle gap between scenes is not a dropped game frame. After displaying the notice, use a fresh monotonic timestamp for a staged outcome: passing the pre-label time back into the controller correctly triggers its backwards-clock cancellation.

Exercise repeated clicks through the longest clip, nap during a reaction, hide/show, reduced motion, actual drag versus pet, saved-origin roundtrip and corner clamping. Verify transparent-margin hit testing and tray framing after footprint changes. For interruptible actions add systematic release/cancel checks at every phase and timing boundary.

### E. Build and inspect the actual deliverable

After source/art checks pass, preserve the current verified release as `dist/DesktopNeko-previous.exe`, then build directly to `dist/DesktopNeko.exe` and test that exact executable. Keep only these two files in `dist`, with no release subfolders. Never overwrite a user's running build or kill unrelated app processes to make a test pass.

```powershell
.venv\Scripts\python.exe -m unittest discover -v
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --distpath dist main.spec
$env:NEKO_TEST_EXE = 'dist\DesktopNeko.exe'
.venv\Scripts\python.exe -m unittest test_packaging -v
Remove-Item Env:NEKO_TEST_EXE
```

The native packaging smoke check needs the existing Neko closed because the shared single-instance lock is intentional. Tests stop only their own process trees. Check bundle resource presence and hashes against final PNGs, native startup/tray/topmost behavior, second-instance rejection and exclusion of credentials/unrelated DLLs. Record the executable hash and actual source/art commit; do not claim an older executable contains new art.

For pickup, run `tools/preview_pickup.py` as well: it uses the real controller paths, asserts all held/bridge/yawn pose coverage, decodes the 27s GIF duration and exports every source slot plus seven complete release stories. The ordinary pet catalogs still describe the earlier nine-second pet timeline. Review native re-grab and arbitrary-release cases separately from an uninterrupted loop.

### Evidence and honest limits

The baseline native run observed all 280 pet entries; median paint intervals were 49.85–50.03ms at DPR 1.0. Full discovery ran 149 tests: 147 passed, two opt-in package checks skipped. After final fragment rejection, three focused render checks and the corrected stretch's 25-entry native playback passed; both final packaged checks passed. This is not a claim that the entire suite was rerun after that last selection edit.

The later pickup revision ran full discovery again: 171 tests, 169 passed and two opt-in package checks skipped, followed by both final packaged checks passing. Its 100 carry source slots, 86 release samples, 14 native releases, four native re-grabs and stretch/flop/roll/nap entry paths were checked. Median native paint interval was 49.973ms at DPR 1.0. See the [current report](docs/pickup-validation.md) for exact cases, source/build identities and the 27s/54s previews.

Physical mixed-DPI/multiple-monitor hardware and long-session resource behavior were not exercised. Automated geometry checks and our visual review cannot promise the absence of every possible anatomy defect. Report what was observed and what remains untested.

## 9. Keep this guide alive

Before finishing any animation change:

1. Update the relevant method section when a verified discovery changes the process. Do not leave an obsolete recipe as the apparent current instruction.
2. Add a dated finding below: symptom, cause, evidence, chosen correction, rejected approach, regression/visual check and remaining limit. Link tracked code/art/QA records.
3. Record exact prompts and assembly selections in that revision's provenance file. Update current counts, timings, README and preview tools when affected; preserve old reports as historical evidence.
4. Mark proposals as proposals. Promote a proposed technique to verified practice only after source/runtime review and recorded evidence.

Do not relax an anatomy, scale, timing or clipping check merely to accept a new sheet. Investigate the source and the shared import/registration first. A future discovery can supersede a measured constant, but must carry the measurements and compatibility reasoning that justify it.

### Findings log

| Date | Finding and correction | Evidence / remaining limit |
| --- | --- | --- |
| 2026-10-23 | Sleeping quit was explicitly excluded and closed in7–11ms without any paint. User now requires wake → sad → drop. Reuse the existing wake and pending-recovery path, finish partial curling before wake and preserve partial wake progress; reject immediate sleeping close and a snap to seated sadness. | Three regressions fail before correction;164 source checks pass afterwards. [Assembly, preview, package/native evidence and limits](docs/sleep-goodbye-validation.md). All839 frames/65 clips retained; no new art or gait change. Physical mixed-DPI/long soak remain untested. |
| 2026-10-23 | Idle review confirms existing anticipation/recovery and canonical endpoint substitutions; more convincing support/neck/chest transitions are proposed, not implemented. Shared chatter cooldown hid gesture thoughts and advancing an undisplayed general thought lost it. Outside-zone history was discarded before cooldown, losing first valid approach; Nook controls also blocked observation. Separate channels/acknowledge display, retain pre-deadline outside history with post-deadline entry, allow live Journal monitoring and record bounded local action/decision events. | [Plan](docs/idle-refresh-plan.md), [validation](docs/idle-diagnostics-validation.md), [native countdown/journal evidence](docs/idle-diagnostics-native.json). All839 frames and all clips unchanged; tail chase/catch protected. Existing-bubble/quiet/sleep/care still defer or suppress words. No new art is approved by these tests. |
| 2026-10-23 | User reported missing drop-out in the exe. Bundled main/animation bytecode with bundled assets reproduces immediate7ms closes and zero goodbye paints from awake gesture and visible-fullscreen cases; idle works. Queue the finite recovery and allow deliberately visible fullscreen goodbye. Remove flight tuck/re-extension and steep reversal for one continuous leap. | Three pre-fix regressions fail; source and bundled-menu checks cover recovery→sadness→one leap, interruption, home restoration and unchanged frames. [Current report](docs/dropout-fix-validation.md), [probe](tools/probe_bundled_goodbye.py), [selection](docs/dropout-fix-selection.json). The probe runs frozen bytecode/assets under the installed Qt/Python runtime, separate from the bootloader's native startup check; physical mixed-DPI/soak remain unverified. |
| 2026-10-23 | Final user direction requires sadness before the goodbye pose. Add eight authored neutral/ear-drop/heavy-eye/blink/turn/crouch drawings; replace the cheerful blink, allow700ms for sadness and connect grounded steps into one load/push. Mirror only after the front-facing expression, avoiding a premature face/placement flip. | [Selected sad sheet and exact prompt](docs/lifecycle-v2-prompts.json); expression-order/read-time and actual-painter direction regressions pass. Final departure20 entries/2.20s. A native run concurrent with packaging work missed one70ms arrival drawing; quiet native coverage is recorded separately. Time-based animation can skip intermediate drawings under load; artistic smoothness remains a user judgement. |
| 2026-10-23 | Rigid flight was replaced with side-biased stretch, planted fore-contact, folding spine, gathered support and a drawn turn; the user then required single diagonal leaps. Trace arrival backwards to its first upper/left boundary, stop world travel at contact, and use one departure arc toward bottom/nearer side. Anchor the foretoe rather than recentering changing silhouettes. Reject neighbouring paw fragments through complete redraws/one clean final hold. | 120 focused checks plus one final front-seam regression; all 786 earlier frames/63 other clips identical; all53 new entries pass components/bounds. Native Windows paints all19 arrival/20 exit entries at low/high positions, preserves focus/home. [Report](docs/lifecycle-v2-validation.md), [prompts](docs/lifecycle-v2-prompts.json), [face-hidden preview](docs/lifecycle-v2-silhouette.gif). No extra hop, per-pose fitting or anatomy painting. Physical mixed-DPI/long soak and user's aesthetic judgement remain open. |
| 2026-10-23 | User rejected the visitor acting despite passed technical checks. Supplied video shows reach → fore-contact with pelvis high → folding spine/hindquarter settling → recovery; supplied spine/silhouette sheets expose the missing range of whole-body shapes. Require reference selection, chest/pelvis/support maps and a face-hidden key-pose review before full sheets. Clarify that fixed identity/camera does not mean fixed silhouette or frozen orientation. | Five originals saved byte-identically with hashes in [the reference library](references/motion/README.md); full video decoded, timestamped scene/pose studies inspected. [Revised entrance/exit plan](docs/lifecycle-motion-v2-plan.md). Observations are reference evidence; the new workflow/acting is proposed and has not yet been validated in Neko. Existing reports/releases remain historical. |
| 2026-10-23 | The first visitor recovery shrank to 67px and would pop to 83px idle. Redraw a separately calibrated supported recovery; keep the generated neutral before actual idle. Replace local departure erasure with actual window travel and monitor-edge clipping; retain origin through saves/cleanup and skip incompatible starting poses. | 115 focused checks; all 741 prior frames/63 unrelated clips identical; all 45 visitor entries pass component checks. Native event-loop painting covers 20 arrival/16 departure poses, both low and high exits, with home restored and foreground unchanged. [Validation and remaining limits](docs/visitor-validation.md). |
| 2026-10-23 | Lifecycle source review distinguishes actual arrival travel from departure's in-canvas offset. A full second of the current 2.15s exit is two sad poses. A future edge exit needs world travel and saved-origin protection rather than a larger local offset. | [Source inspection, research and proposed storyboards](docs/arrival-goodbye-research.md); existing pose catalog reviewed. No new animation/runtime validation or implementation. Keep proposed peek/landing/exit techniques separate from tested recipes. |
| 2026-10-22 | Launch rebuilt every calibrated sprite before showing Neko. Profiling found silhouette extraction dominated; move the unchanged importer to packaging and load lossless finished frames. Retain source fallback rather than weakening calibration or discarding animation frames. | All 741 frames compare pixel-identically; source atlas 5.49s versus packed load 0.27s in the same process. [Executable startup timings, package checks and limits](docs/startup-performance-validation.md). Source authoring still uses the full importer. |
| 2026-10-22 | A70ms run expression disappeared in motion; redraw the gallop against the user's eight-frame mechanics reference and keep acting across four poses (360ms), instead of freezing one pose longer. Add fixed flight lift only to airborne drawings. Idle gestures also discarded qualified invitations; defer launch until their supported finish. A persistent loss curl bypassed the nap state machine; complete its existing silent get-up/home path, then honor the due nap without counting a pet. |72 focused checks pass (71 timer/game/behavior plus care override), including reproductions that failed before correction. Twelve imported slots/741 atlas entries; [preview, provenance and limits](docs/run-timer-sleep-fix.md). Extended play, full suite and native animation QA intentionally deferred at the user's request. |
| 2026-10-22 | Cursor-play v2 needed connected playful run/walk and six outcomes. Reject label/matte drafts, a proportion-drifting loss-c and an over-tall grasp recovery. Use complete silhouette crops, one repeated ready hold, whole-batch registration and a drawn curl look-up; retain the real neutral before walk idle. Countdown clocks begin after label presentation. | 729 atlas entries; all 200 game source slots pass bounds/components; 552 retained frames/41 unaffected clips compare unchanged. Native full pose coverage, actual one-second cues, hit-through and no focus theft in [v2 QA](docs/cursor-play-v2-validation.md). No physical mixed-DPI/multi-monitor trial or guarantee of subjective fun; prompts and rejected selections remain recorded. |
| 2026-10-22 | A second probe timer calling `animate()` doubled the observed native paint rate; gaps between independent scenes also polluted the maximum. Observe actual `current_frame` calls under production's own timer and group intervals by scene. A staged outcome needs a fresh timestamp after the notice label, otherwise backwards-clock cancellation is correct. | Every used hunt/countdown/walk/outcome pose is actually painted; median 20.004ms, within-scene maximum 71.12ms at DPR 1.0. [Native record](docs/cursor-play-v2-native.json). Reject polling-only frame coverage as display evidence; other hardware remains untested. |
| 2026-10-22 | A bare zero-delay deferred play callback could enter the desktop tick after its widget was deleted during QA teardown. Supply the widget as the Qt single-shot context so its lifetime owns the callback. | The same 20 controller/desktop checks now pass without the teardown traceback. No artwork, clip timing or proposed v2 behavior changes. [Startup/icon maintenance record](docs/startup-icon-validation.md). |
| 2026-10-22 | Nominal hunt source cells included the previous row's seated paws, reducing one imported run pose to a fragment. Extract complete significant silhouettes, pack fixed cells, sample to 128px before import and add bounds/component checks. Collision must include the painter's y−1 offset and mirror actual paw-alpha regions. | All 48 game slots pass bounds/significant-component checks; stationary high/low/distant contacts and both mirrored directions pass. All 528 earlier frames/42 clips compare unchanged. Native jump/loss/curl/comfort/three-hop entry coverage recorded in [Catch QA](docs/catch-validation.md). Source alpha fringe and attached anatomy still require visual review; physical mixed-DPI and human tuning remain unverified. |
| 2026-10-22 | Independent typing/window/cursor/follow cooldowns allowed frequent alternating reactions; idle thoughts also bypassed the full configured speech interval. Use one configurable activity minimum (60s default, 15–600s) and the full automatic speech minimum, discarding activity events during cooldown. | 38 behavior/dialogue and 12 desktop checks pass, covering shared boundaries, preferences, quiet/AI guards and no event backlog. Idle animation cadence and deliberate pet replies remain independent. [Report](docs/activity-reaction-validation.md). |
| 2026-10-22 | Native blur escaped the rounded window even though Qt/Win32 regions excluded the corners; the earlier mask-only test missed it. Replace private accent blur with a softly blurred per-thought background sample clipped in the painter, and test actual outside pixels. Reuse also exposed a stale fixed-height constraint; reset before remeasurement. | All 36 outside-corner samples across initial/resized/restored display are unchanged; seven focused source checks pass. The background sample is local/static until the thought closes and clears on hide. [Current report](docs/thought-rounded-clip-validation.md). |
| 2026-10-22 | User requested rounder glass and less frosting. Match 20px corners across mask/paint/style and blend the whole overlay at 88% opacity. | Five focused source checks and native corner/click-through/focus checks pass; background stripe contrast increased 4→13, retaining more clear detail. This softens the composed effect, not Windows' fixed blur radius; glyphs share the overlay opacity. |
| 2026-10-22 | User preferred almost see-through glass over the dark frosted tint. Replace alpha-110 dark fill with a subtle alpha-10–32 highlight/shade gradient and a faint rim; retain native blur and sharp glyph shadow. | Five focused source checks, native light/dark preview with the real glyph shadow, click-through and unchanged foreground pass; stripe contrast 70→4 at DPR 1.0. Same native-policy/fallback limits apply. |
| 2026-10-22 | Requested subtle blur behind thoughts. Documented Desktop Acrylic became opaque for the unfocused tooltip despite successful API returns. The accent blur path preserves underlying colors and softens detail without taking focus; explicit rounded painting supplies a tint fallback. | Native test-owned light/dark capture, click-through, unchanged foreground and stripe contrast 70→3 at DPR 1.0; five focused source checks and both exact-package checks pass. The private accent policy may change; Windows 10/mixed-DPI were not exercised. [Report](docs/thought-backdrop-validation.md). |
| 2026-10-22 | User found petting slightly slow. Divide pet-only durations by 1.15, retain a 50ms minimum and every pose/recovery. Update the queued-flop regression to sample relative to the clip deadline rather than the obsolete six-second timestamp. | All twelve sequences retain every drawing at nominal 20 FPS; all non-pet clip timings unchanged; refreshed eight-second catalog, 41 focused source checks and both packaged checks pass. See [speed verification](docs/petting-speed-validation.md). Full discovery/native animation timing were not repeated. |
| 2026-10-22 | Tail/haunch-based registration shifted five pet endpoints, including a 6px arch shift. Reference support targets to the canonical head axis. | Endpoint checks now within 2px; reversed-sign mutation fails. See [revision report](docs/petting-revision-validation.md). |
| 2026-10-22 | Uneven generated layout and separately drawn knead/stretch batches caused pose drift. Extract complete silhouettes, compare neutral landmarks, use fixed batch calibration and redraw unsuitable mechanics. | Exact selections/ratios in [assembly record](docs/petting-revision-prompts.json); heuristics still need checking for new postures. |
| 2026-10-22 | A detached 16px line survived bounding-box cropping beside stretch pose 14. Reject the drawing, select a clean neighboring hold and add a connected-fragment regression. | Final light/dark review, focused checks and native stretch replay passed. Connected extra limbs still require visual review. |
| 2026-10-22 | Short previews and floating intro subtraction could hide recovery or skip connecting poses. Derive preview length from longest clip, round intro-adjusted time and assert pose coverage/decoded duration. | Current catalogs cover every used entry and decode to 9s/18s. Preview sampling alone does not prove native playback. |
| 2026-10-22 | Retained-scale hanging required 32px more space above idle. Pad the fixed canvas, preserve saved/tray/visual origins and leave existing pixels alone. | All427 previous frames and32 clips unchanged; native saved-origin and top/side click-through checks pass. See [pickup verification](docs/pickup-validation.md). |
| 2026-10-22 | A newly generated sleepy body shortened and fragmented; rolled entry acquired a gray halo that survived an alpha edit. Reject these drafts; repair sleepy acting against the accepted body and redraw roll cleanly. | Exact accepted/rejected outputs in [pickup provenance](docs/pickup-prompts.json); all 100 imported carry slots reviewed and pass fragment/scale/bounds checks. |
| 2026-10-22 | Re-grabbing an early release omitted the rest of the lift, causing a reproduced 22px crown jump. Retrace release, append unvisited lift and pause the expression clock during return. | Early-regrab and mood-boundary regressions pass; arbitrary native release paths are recorded separately. |
| 2026-10-22 | A hash probe exposed a buffer from a temporary QImage, invalidating the measurement. Retain the image object before copying its bytes. | Recomputed against commit `199392b`: all 427 earlier drawings compare exactly. Production drawing was unaffected. |
| 2026-10-22 | The all-states smoke check constructed a held state without its grab payload, exposing an unsafe render assumption. Fall back safely and allow cancellation when context is absent. | Both the direct missing-context regression and the original all-poses render check pass; keep live-input tests too. |
| 2026-10-22 | Integer half-width arithmetic shifted the mouse-follow anchor by one pixel after padding, changing the horizontal walk stop by a two-pixel step. Use the adjusted original footprint's Qt rectangle center. | The existing above/below-cursor and directly-above walking regressions pass with their original expected stop values. |
