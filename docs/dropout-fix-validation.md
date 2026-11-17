# Drop-out menu correction · 2026-10-23

The user reported that drop-out did not work in the executable and reiterated one graceful leap, while approving the rest. This correction preserves the entrance, artwork and unrelated behavior. [Current scene](dropout-fix-scene.gif) · [Face-hidden scene](dropout-fix-silhouette.gif) · [Full-canvas frames](dropout-fix-frames.png) · [Selection addendum](dropout-fix-selection.json).

## Reproduced cause

The previous release matches its recorded SHA256 `ee17613928266a91472253a5929d18e0ff9e2f8c0dddb46bb4a2ece82209f253`. Its main/animation bytecode and bundled assets reproduce the missing goodbye through the real Qt “Let her go · quit” QAction. Idle paints the whole goodbye; an awake tail gesture and a visible fullscreen pet each close in about7ms with **zero goodbye paints**. This is a quit eligibility bug present in the executable, not missing artwork or a stale atlas.

Two conditions caused it: only IDLE/ARRIVING were allowed, and every fullscreen flag skipped animation even when the user had disabled fullscreen hiding. A new permanent [bundled menu probe](../tools/probe_bundled_goodbye.py) covers both paths. It extracts the trusted local executable's main/animation bytecode and assets into temporary storage, executes them under the installed Python/Qt runtime, invokes the actual QAction and observes production-timer paint events. This specifically tests frozen code/resources/menu ownership, separate from the bootloader's native startup/instance test. Windows Computer Use did not expose the pet's tool window as a target, so no manual-pointer interaction with the release menu is claimed.

## Correction

An awake finite gesture finishes its existing drawn recovery, then enters the sad goodbye once. Competing pets, games, idle/sleep ticks, reopen and repeated quit cannot replace/restart that pending close. Motion-off, hiding, monitor change and explicit fullscreen-hiding changes can still finish promptly. Sleeping, held/waking and active-game closes retain their immediate behavior. A pet deliberately visible over fullscreen now plays goodbye.

Sadness, supported turn, hind loading and push remain. Flight now selects6→7→8→11→13→14→15: a continuous extension into a descending reach. The former9/10 midair tuck/re-extension and12's steep-to-shallow reversal are omitted. There is one push-off and one world apex, with no second contact/launch. Seven flight durations total1000ms after the unchanged1200ms expression/preparation. Goodbye is17 selected entries/2.20s; arrival remains19/1.98s. No new drawings, pixel edits, dependencies, preferences or runtime atlas preprocessing were added.

## Verification

- Three reproductions fail before the fix: awake-menu quit, visible-fullscreen quit and the continuous flight order. They pass after correction.
- **123 focused source checks pass**, plus **two additional pending-close interruption checks** after the final guard:125 source checks across these runs. Existing single-apex, diagonal travel, contact, origin persistence, reduced-motion, clipping, sad expression/direction and baked/source equality checks remain.
- **Five exact-executable checks pass**: bundled resources/icon/manifest, pixel-identical baked frames, actual bootloader UI startup/second-instance handling and the new bundled menu-action probe.
- [Invariant record](dropout-fix-invariants.json): all839 frames compare pixel-identically with the replaced executable. Arrival is unchanged. Both new actual-controller previews decode to3000ms; previous previews/provenance remain historical.
- [Windows bundled-menu records](dropout-fix-native.json) cover idle, near-complete awake gesture and visible fullscreen, observing selected goodbye poses and final cleanup/home restoration. Temporary settings and disabled test activity hooks isolate user input/preferences.

[Release identities](dropout-fix-release.json) record the flat `dist/DesktopNeko.exe` and verified immediate predecessor. The prior executable was preserved before building, then rotated only after the new package passed. Build intermediates remain outside dist.

## Remaining limits

A goodbye requested during a long awake gesture waits for that gesture's remaining recovery before the2.20s departure; it never starts a new gesture. No physical mixed-DPI/multi-monitor trial, reboot/logon test, long soak or broad gameplay rerun was added. The Windows bytecode probe uses installed Qt/Python; the separate executable test covers bootloader startup, not an external physical menu click. CPU load can still skip short time-based intermediate frames. Artistic smoothness remains for the user's judgement.
