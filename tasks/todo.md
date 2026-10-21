# Animation rebuild checklist

- [x] Read current art, playback, callers, tests and packaging references; record scope and acceptance criteria.
- [x] Generate replacement art and inspect every source frame; reject and redraw the tail-catch draft.
- [x] Implement and test lifecycle translation and pose endpoints.
- [x] Implement and test tail motion and rest transitions, including a fixed head anchor during swishes.
- [x] Inspect all runtime frames plus native-size/enlarged playback previews; correct defects.
- [x] Run regression suite, build executable and verify packaging, native Qt rendering and second-instance launch. Cold packaged startup deferred because the user's existing copy is running.
- [x] Update prompts, animation catalogs and final validation notes.
