# Petting selection catalog

![All twelve active pet reactions at their actual playback speed](neko-pet-catalog.gif)

Exactly twelve reactions are active. All twelve have been rebuilt into dedicated
16–28 source pose slots, with drawn physical recovery followed by canonical idle.
See [current per-reaction timing and verification](petting-revision-validation.md).

1. Head pats
2. Cheek nuzzle
3. Kneading
4. Chin scritches
5. Playful roll — replaces Tiny blep
6. Paw offer — remade
7. Ear rubs
8. Big front stretch
9. Happy back arch
10. Three tiny happy hops
11. Cozy side flop, snooze, wink and wake
12. Both-shoulder peek, yawn and sleepy deadpan

Seated hello, shy head dip, nose wiggle, tail curl, and old paw wave have been
removed from the active set. The old malformed paw offer is also excluded.
The obsolete six-frame sheet and its previews have been deleted.

The GIF starts with 0.8 seconds of actual idle, then uses production SpriteAtlas
and Clip timing at 20 FPS. Each gesture finishes at its own deadline and returns
to normal idle blinking. The nine-second catalog includes the complete longest
reaction plus idle afterward. Kneading makes four finite alternating pairs; side
flop has a separate forepaw-supported get-up after its sleepy wink. No extra petting loaf was added.

All twelve reactions use one seated-reference calibration through the full sequence.
Their final drawn neutral head positions also match the actual idle; extra transparent
canvas space accommodates the gestures without shrinking the kitten.
The preview returns to actual idle after each reaction to expose size jumps.
Postures still change naturally: a flop lowers her head and a stretch extends her body.
See [size matching and palm interaction](pet-scale-and-cursor.md).

[Inspect every imported runtime pose](neko-pet-frames.png), or the smaller
[first six](neko-pet-frames-a.png) and [last six](neko-pet-frames-b.png) sheets.
