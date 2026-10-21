# Idle and activity animation catalog

![Current idle animations](neko-idle-catalog.gif)

The main catalog includes the default sitting loop and all nine ambient moods.
Looking around has two directional variants, producing eleven numbered entries.

1. Sitting / slow blink — default resting loop
2. Tail swish
3. Ear flick
4. Sniffing — also responds to a nearby moving cursor
5. Seated stretch
6. Grooming
7. Yawning — also used when getting sleepy
8. Loaf
9. Sleepy peek — uses the sitting/blink drawings with different timing
10. Looking around, left-leading
11. Looking around, right-leading — same four drawings, different playback order

All use the actual runtime SpriteAtlas and Clip timing at 10 FPS. Ambient moods
are shown for their six-second slot, then return to the default sitting loop;
loaf has its eight-second slot. The catalog repeats every eight seconds and omits
the random wait between gestures so they can be compared side by side.

[Inspect the individual idle drawings](neko-idle-catalog-frames.png).

## Other non-petting sequences

![Related activity and sleep animations](neko-activity-catalog.gif)

12. Typing paw taps — typing, writing and coding reactions
13. Cursor walk — left-facing art; the app mirrors it to walk right
14. Falling asleep — eight transition drawings
15. Sleeping — two-drawing breathing loop
16. Waking up — eight transition drawings

These are displayed separately because their triggers differ from ambient idle
moods. Loops are shown continuously for inspection; transition clips finish and
hold their final drawing. The walking preview shows its leg cycle without moving
the window. The app still walks horizontally only.

[Inspect the activity and sleep drawings](neko-activity-catalog-frames.png).

The catalog covers every current non-petting clip. No runtime art, timing,
behavior, settings or executable was changed to create it.
