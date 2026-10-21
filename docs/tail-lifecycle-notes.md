# Playful tail games, arrival and goodbye

![Runtime poses](neko-tail-life-preview.gif)

[Monitor-scene arrival and farewell](neko-lifecycle-scene.gif) · [Native-size playback](neko-tail-life-native.gif) · [All used source poses](neko-tail-life-source-frames.png)

The attached GIF correction replaces the earlier slow tucked-tail cycle. Its eleven 50ms poses guide low, stretched running with squeezed-shut eyes, alternating scrambling paws and a long tail trailing outside the turn. One 550ms turn now repeats five times for chase and twice before the catch/pounce. Chase lasts 4.69 seconds; catch lasts 3.68 seconds, both inside the six-second idle slot. The lazy swish and twelve pet reactions remain as previously calibrated. [Tail-only playback](neko-tail-reference-preview.gif) preserves exact 50ms frame timing.

Eight new transition drawings add an eager head tilt, a crouch and a run-ready pose, then a deceleration pose, half-sit and contented closed-eye tilt before returning to canonical idle. Both clips share the entry and seated recovery; catch goes from its low pounce/crouch directly into the half-sit. The new source sheet is calibrated independently and appended as indices 16–23 in the tail bank, keeping the accepted running frames unchanged. Idle endpoints use the actual idle drawing.

Each tail game has three times the selection weight of an ordinary spontaneous idle. The last selected idle is excluded before weighting, so consecutive identical idles remain impossible. Other idles, sleep timing, six-second slots and the configured gap between gestures are preserved. A seeded 3,000-selection simulation checks that tail games make up 30–45% of choices and every other idle still appears.

Arrival lasts 1.9 seconds. Her actual 112px desktop window moves from just above the target monitor to the saved landing position over 700ms, with accelerating travel. Complete airborne/forepaw-contact poses lead into compression, a cheerful rebound and the canonical idle drawing. Ink is clipped to the target monitor's top edge, including when another monitor sits above it. The monitor-scene preview uses the production trajectory and atlas; the pose catalog alone does not show desktop window travel.

Departure lasts 2.15 seconds. A sad look with lowered ears appears immediately for 650ms; a second downcast pose holds 350ms. The retained crouch follows for 200ms, then the previously accepted hop drawings and upward/downward arc. There is no new dialogue. Only the first two farewell candidates are imported.

The current atlas has 195 entries after the [idle-personality update](idle-personality-validation.md). neko-tailplay-v4.png, neko-tailsettle-v1.png, neko-arrival-v1.png and neko-farewell-v1.png provide the tail/lifecycle art. neko-lifecycle-v2.png remains for its accepted departure poses; its old arrival rows are not loaded. Retired tailplay sheets are removed from the bundle. Shared idle endpoints prevent a face change at rest.

Generated poses slightly cross nominal row boundaries. Arrival and tail cells use padded sampling regions, connected-silhouette bounds and constant width-based source sampling, so paws are retained without changing scale between rows. Whole sequences share a scale and ground anchor; frames are never individually fitted to their bounding boxes. No anatomy pixels were painted or patched programmatically.

Every used new pose was inspected at enlarged and desktop size for one connected body/head, four anatomical limbs total (with occlusion), one attached tail, complete paws and consistent proportions. Two turn views and oversized arrival tails were corrected through ImageGen. Runtime review caught and corrected row-boundary paw clipping. Numerical tests cover silhouettes, timing, turns and state transitions; they cannot certify anatomy.

Position saves always use the landing target during flight. Hiding, motion-off, fullscreen, quitting and monitor removal restore that target before proceeding. Greeting happens after landing, unless interrupted. Petting and window reactions cannot interrupt lifecycle states; repeat quit does not restart farewell. Reduced motion and hidden/fullscreen quit remain immediate. Palm feedback and idle/pet head calibration remain unchanged.

See [exact prompts](playful-motion-prompts.md), [verification](playful-motion-validation.md) and the earlier [rebuild record](animation-rebuild-validation.md).

This addition has its own [transition prompt](tail-transitions-prompts.md), [verification record](tail-transitions-validation.md) and [other-idle ideas](idle-personality-ideas.md).

Rebuild previews with .venv\Scripts\python.exe tools\preview_animations.py (optional Pillow). These use production atlas/timing, 30 samples/second for lifecycle, 20 FPS for tail running and 10 FPS for other actions. GIF loops are documentation replay; startup/departure run once.
