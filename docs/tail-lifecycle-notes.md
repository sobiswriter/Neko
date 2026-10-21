# Tail, arrival and departure rebuild

![Runtime playback, enlarged without smoothing](neko-tail-life-preview.gif)

[Native-size playback](neko-tail-life-native.gif) · [untranslated source poses](neko-tail-life-source-frames.png) · [runtime poses including entry/exit clipping](neko-tail-life-frames.png)

## What changed

The built-in ImageGen tool generated three replacement sheets from the existing
`assets/neko-idle-v3.png` character reference:

- `assets/neko-lifecycle-v2.png`: eight landing poses and eight hop-down poses.
- `assets/neko-tailplay-v2.png`: eight tail-chase poses and eight seated tail-catch poses.
- `assets/neko-tailswish-v1.png`: eight poses for a small lazy swish.

The previous lifecycle and tail-play sheets are removed from the bundle. The
original swish row remains inside the shared idle sheet but is not imported.
There are 148 atlas entries. The twelve pet reactions remain unchanged.

Arrival uses a quick accelerating drop, forepaw contact, compression, recovery
and sitting. Departure uses a relaxed downward glance, crouch, push-off, a small
upward arc and accelerating fall; no sad face or guilt cue. Every source pose is
complete. Translation and viewport clipping happen during playback, independently
of the held pose, without moving the actual desktop window or saved position.

Arrival lasts 1.6 seconds and departure 1.8 seconds. The first 420ms of arrival
cover flight. Departure starts pushing off after 850ms and is fully out of view
by 1.6 seconds. Lifecycle repainting briefly runs at approximately 30 FPS;
ordinary animation stays at 10 FPS so cursor walking retains its existing speed.

The tail chase notices its tail, rises, completes one turn and settles. The
seated catch uses one forepaw at floor level: notice, reach, pin, slip, recover.
The lazy swish plays once and rests instead of wagging continuously. Swish frames
have explicit horizontal registration to keep the head anchored as the tail
widens the silhouette. All three actions start and finish with the actual idle
seated drawing; arrival also ends there and departure begins there.

## Interaction safeguards

The existing lifecycle timer handles greeting and cleanup independently of the
behavior tick. Petting and desktop activity cannot interrupt these transitions.
Repeated quit clicks do not restart them. Ordinary Hide/Show does not replay
arrival. Hiding during arrival cancels the pending greeting. Reduced motion skips
both jumps; switching it off during a transition finishes immediately. Hidden or
fullscreen quits remain immediate. The existing AI-worker shutdown is unchanged.

## Art review

The first tail-catch draft was rejected because the old planted paw and reaching
leg could read as a third foreleg. A targeted ImageGen correction replaced those
lower eight drawings. The accepted catch moves one existing foreleg, with the
other supporting foreleg retained; small seated haunch outlines are hindquarters,
not extra front legs. The tail passes under the reaching paw at floor level.

Source sheets were reviewed for one head/body, four anatomical limbs total,
visible versus occluded legs, one attached tail, head scale and clean silhouettes.
Runtime contact sheets expose every used drawing at desktop scale and enlarged;
[flight strips](neko-lifecycle-flight.png) expose the intermediate translated positions. Generated
art is visually assessed; automated tests cannot certify anatomical correctness.
No anatomy pixels were painted or patched programmatically.

See the [verification record](animation-rebuild-validation.md) for per-action
inspection results, native checks and the remaining cold-start validation limit.

The full prompt set, including the rejected draft's correction, is retained in
[animation-rebuild-prompts.md](animation-rebuild-prompts.md).

## Reproduce the previews

With optional Pillow installed:

```powershell
.venv\Scripts\python.exe tools\preview_animations.py
```

The script uses the production SpriteAtlas and Clip timing. Native-size and 2x
previews include the three tail actions and both lifecycle transitions. Idle and
activity catalogs are regenerated too. The GIF timebase alternates 30/30/40ms
frames, giving exactly 30 samples per second for lifecycle movement; other clips
are sampled at the app's 10 FPS. Preview loops restart after six/eight seconds;
the real startup/departure transitions run once.
