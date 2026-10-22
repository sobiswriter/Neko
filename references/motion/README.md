# Neko motion reference library

Read this index before planning or drawing **any** Neko motion. Select the relevant references, watch their action in context, and state what physical mechanics the new gesture will borrow. This library informs movement, not Neko's character design or runtime assets.

## User-supplied study set · 2026-10-23

The user supplied these after rejecting the visitor entrance/goodbye as insufficiently imaginative. All five originals are copied byte-for-byte into the project, with original paths, byte counts and SHA256 identities in [the manifest](2026-10-23/manifest.json). Downloads is not a future dependency.

| Saved reference | What to study | Limits |
| --- | --- | --- |
| [Walking, fast walking and running](2026-10-23/gaits-walk-fast-run.jpg) | Changes in stride, leg gathering and whole-body posture; distinguish near/far legs. | An illustrated comparison, not a timed gait cycle. Labels alone do not establish an exact footfall order or speed. |
| [Silhouettes on white](2026-10-23/pose-silhouettes-white.jpg) | Crouch, extension, airborne separation and negative spaces between limbs, belly and tail. | Static pose collection, not chronological frames. Stock markings remain in the original; do not turn it into a sprite sheet. |
| [Silhouettes on cream](2026-10-23/pose-silhouettes-cream.jpg) | Distinct lines of action for sitting, reaching, arching, stretching, gathering and running. | Preserve Neko's identity; do not adopt the thin body, yellow eyes or pointed design. |
| [Spine flexibility study](2026-10-23/spine-flexion-study.jpg) | Chest/pelvis separation; stretched versus gathered spine; leg placement tied to changing body shape; folding and unfolding of connected masses. | A photographed teaching page. Its running sequence is not a landing recipe, and “on ones” is not a requirement to use its frame count or production rate. Authorship is not verified from the supplied image alone. |
| [Original motion video](2026-10-23/motion-reference.mp4) | Dynamic reach → fore-contact → folding body → hindquarter settling → recovery, then another bound and a departure through walking strides. | Stylized animation, not live-cat biomechanics. The download's bedroom-decor filename does not describe its actual content. Audio was not part of the motion analysis. |

[Video contact sheet in screen coordinates](2026-10-23/video-contact-sheet.jpg) · [Pose study](2026-10-23/video-pose-study.png) · [Review metadata](2026-10-23/video-review.json).

The video is approximately 4.18s, 714×1134, with a 30fps video stream. All 125 video frames were decoded for inspection. The full-scene contact sheet samples the sequence at 12fps; its timestamp labels are approximate sample times. The pose study selects source frames at the times recorded in review metadata, crops the bright character plus padding, translates it into a comparison cell, and applies the **same 0.65 scale** to every crop. It removes world travel to make the body changes easier to compare; it must not be mistaken for a trajectory reference. Partial silhouettes at the beginning/end are already clipped in the source video. Crops are study derivatives, not extracted game assets. The unmodified original remains the authoritative reference.

## Observed video beats

- **About 0.3–0.5s:** the cat enters on an extended diagonal, with forelegs reaching ahead of the falling body and rear/tail trailing.
- **About 0.6–0.8s:** front support arrives while the pelvis remains high; the forequarters yield, spine changes curvature, hind legs come under the body and the outline gathers. This is the strongest contrast with the near-rigid Neko descent.
- **About 0.9–1.1s:** the body rises from compression and the tail continues changing after the main landing.
- **About 1.4–2.2s:** a second short bound repeats the stretch/contact/gather/recover relationship. This is not a somersault or a reason to add an unobserved flip.
- **About 3.5–4.1s:** the departure has changing planted/swinging legs, head/body direction and a trailing tail as the cat crosses the right boundary. Do not describe this part as a demonstrated downward jump.

## How to use the library

1. Review the full scene, then isolate the relevant physical beats. Still silhouettes help design extremes but cannot supply missing timing.
2. Make a motion brief: intention, chest/pelvis positions, spine curve, supporting/swinging legs, contact points, tail phase and expression at each key pose.
3. First judge a small set of full-body keys without facial acting. If action cannot be read from the silhouette, more smiles or more in-betweens will not solve it.
4. Keep head identity and body volume, while allowing natural changes in torso length/curvature and joint positions. The seated height is a calibration reference, not a cage for every pose.
5. Author the hard poses and connecting turns before a full sheet; approve movement at desktop size and normal speed before adding a polished expression pass.
6. Keep tested runtime facts, reference observations and proposed acting separate. A passing component/timing test is not the user's approval of the animation.

See [Frame Master](../../framemaster.md) for production constraints and [the revised lifecycle plan](../../docs/lifecycle-motion-v2-plan.md) for the first application. Do not copy reference backgrounds, captions, watermarks or sound into the pet.
