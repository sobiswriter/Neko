# Desktop Neko 🐾

A little company for your Windows desktop. Neko stretches, settles down, notices
your cursor, and naps when you step away. No chores, guilt, or attention meter.
Soft sounds are optional and off until you enable them.

![Neko's petting animations](docs/neko-pet-catalog.gif)

## Living with Neko

- **Click to pet.** Twelve individually paced reactions with 16–28 source pose slots: head pats, cheek nuzzles,
  kneading, chin scritches, a playful roll, offering a paw, relaxed ear rubs,
  a front stretch, back arch, tiny hop, side flop, and shoulder peek.
  Each has drawn anticipation/action/recovery and uses the actual idle drawing
  at both ends, with a complete drawn recovery before the final idle. The old four-frame pet rows are
  excluded from playback. Each plays once and returns to normal idle blinking;
  kneading makes four alternating paw pairs first. The hop has three little jumps;
  shoulder peek looks both ways, yawns and holds a sleepy face; side flop snoozes,
  winks and wakes before getting up. Contact gestures linger with soft lids and
  small ear/paw movements. All twelve appear before the
  rotation repeats. Repeated clicks count immediately and coalesce into one
  next reaction, which waits for the current landing/get-up to finish.
  If she's asleep, a pet plays her waking sequence instead.
- **Drag to move.** She looks around while held and blinks when set down. Dragging
  never counts as petting. Position is remembered, including on another monitor.
- **A little helping hand.** Hovering shows an open palm; holding uses a closed hand
  for dragging. A pet click plays a short palm stroke without moving the actual pointer.
  Leaving, hiding, entering fullscreen or reduced motion stops the stroke.
- **Come close.** She sniffs at a moving cursor and sometimes takes a small walk
  left or right toward it, keeping the same height. Each walk can last 6.5 seconds, travels at most about 220 pixels,
  and keeps a gap from the arrow. Mouse following is optional, with a 25-second rest.
- **Keep working.** Tail swishes, ear flicks, sniffing, loafing, grooming, stretches,
  yawns and sleepy peeks share an atlas of 427 entries, including eight-frame transitions into
  sleep and back to sitting. Most gestures have 5–6 seconds on screen: one gentle
  motion followed by a relaxed rest, without repeated head-bobbing or stretching.
  Tail swishes make one lazy sweep and rest; typing uses a gentle repeating cycle.
  Normal rendering runs at 10 FPS; tail running and petting use 20 FPS.
  Petting uses a precise Qt timer so its short connecting poses get screen time.
  Arrival/departure briefly use 30 FPS for smooth travel,
  keeping walking speed unchanged.
  Every frame has a 192 × 112 transparent canvas, with extra horizontal room for
  rolls and deeper reaches. Idle remains about 82 pixels tall;
  pet sequences use a 62px-wide seated head reference and 82px-tall reference body.
  Each retains one calibration throughout its poses, with ground contacts used
  for registration. Crouching and lying down preserve their natural posture;
  no whole-body refitting happens per frame. The hops follow three small in-canvas arcs.
  Walking, loafing and sleep preserve their natural posture and proportions.
  Grooming, stretching, loafing, sniffing, ear flicks, yawning, sleepy peeks and
  directional looks now have drawn anticipation and recovery: paw lick and ear wipe,
  a stretch/paw shake, tuck into loaf, tiny nose twitches and contented blinks.
  The accepted lazy swish gains a blink before sitting still again.
- **A little tail trouble.** She runs low with closed eyes and a trailing tail through five quick
  turns, following the supplied GIF's eleven 50ms poses. The catch game takes two turns, then a small pounce and a
  two-paw catch before the tip slips away. An eager head tilt and crouch lead into play;
  a half-sit and contented blink bring her back to sitting. Chase lasts 4.69 seconds,
  catch 3.68 seconds. Each gets three times an ordinary idle's selection weight,
  with no consecutive repeats and the same rest between gestures.
  These do not change the twelve pet reactions.
- **Hello and goodbye.** Starting the app plays a drop-in, landing crouch and
  sit-up before her greeting. She enters from her monitor's top edge and lands at
  her saved position. **Let her go · quit** gives her a little sad look and lowered
  ears, then the existing crouch and graceful hop. These eight-drawing
  transitions last 1.9 and 2.15 seconds, use continuous travel between poses,
  and start the arrival clock on Qt's first animation tick so a slow launch
  cannot spend the fall before it appears. Visible fullscreen launches also
  play the drop-in, silently; the fullscreen hiding preference still applies.
  They keep her saved desktop position, and do not accept pets or
  window reactions midway through. Reduced motion skips the jumps; quitting
  while hidden or fullscreen is immediate. Hide/Show remains immediate.
- **Type together.** A typing burst gets a few little paw taps and a local thought
  such as “whatcha typing?”, at most once every 30 seconds.
- **Open, close, or move windows.** Native events earn a look, blink and contextual
  line, with an eight-second visual cooldown. Foreground app selections and title
  changes also hint at internal tab/document changes. Events wait briefly for an
  ongoing animation instead of disappearing immediately.
- **Step away.** She yawns and naps after a configurable period without input.
  The default is three minutes; choose 1–3600 seconds. Type a number and press Enter
  or leave the field to save it. **Nap duration** independently chooses how long
  she stays asleep: 1–3600 seconds, or 0 (**Until petted**, the default).
  The nap clock starts when she finishes curling down; changes apply to the current nap.
  Typing, app switches and dragging let her sleep. A pet wakes her early,
  and timed naps use the same gentle waking transition. After waking she stays
  awake for at least the inactivity delay before another nap.
  Ignoring her never creates chores or penalties.
- **Offline personality.** 298 short lines, including more personal questions and
  company addressed to you, shuffled separately for typing,
  windows, pets, cursor curiosity, waking, and idle thoughts. No repeat until that
  context's bag is exhausted. Ambient thoughts default to about 75 seconds apart.
  All automatic words share an 8–30 second pause and never replace a visible bubble.
  Every spontaneous idle attempts its own local thought, including “Look at meeee!”
  and “Round.. around... around...” for tail chasing. Quiet/fullscreen rules still apply.
  Thoughts use cream 16px semibold text with a small dark shadow around the letters,
  transparent margins and no background or border. They wrap within 270px and
  remain for 5.5–10 seconds of reading time.
- **Little app rituals.** VLC gets a watch-buddy loaf and questions about what
  you're watching; audio file titles and Spotify get listening questions and tail
  swishes. Coding, drawing, writing, chat, games, folders and terminals each have
  their own lines and matching gestures. These are app hints, not content analysis.
- **Soft mews & purrs.** Enable them in the nook's Settings tab; Listen previews a
  small mew. These original synthesized cues are up to a second long, with low
  volume encoded into the WAV files. A deliberate pet can purr or mew; she can
  chirp on arrival. Automatic cues have a 45-second pause and are suppressed during media apps,
  quiet company and fullscreen. Turning sounds off or hiding stops playback.
- **Right-click for her nook.** Quiet company, reduced motion, startup, optional
  AI, mouse following, sleep delay and duration, chatter and idle gesture frequency, and lifetime
  pet/nap counts live in one small window. Double-click the tray
  icon to find her again.
  Menus and the nook open beside her, with no periodic re-pinning over the controls.

Quiet company stops unprompted words and sounds while keeping deliberate pet reactions.
Hide really hides her: no surprise appearances, bubbles, or animation. Native
topmost positioning keeps her above normal windows without stealing focus.
**Tuck away during fullscreen apps** is a separate, opt-in choice in the nook.
Fullscreen activity always suppresses automatic words and typing/window reactions,
even when she remains visible. Exclusive-fullscreen games and other topmost overlays
can still cover desktop windows. Only one copy runs at a time.

Typing and window reactions work locally and can be switched off. Keyboard
detection requests only raw-input headers: key identities, text and passwords are
never read, reconstructed, saved, or sent anywhere. Window reactions use native
events plus a local, temporary hash of the foreground window title to notice
changes, plus the foreground executable's name for app-specific reactions. Titles
are used briefly for local media hints, then discarded; neither titles nor app
history are stored or transmitted in offline mode. Optional AI has
its own title-sharing toggle below. Apps expose different accessibility events:
internal tabs are hints, not universal exact tracking. Background tabs are not
tracked. See [Microsoft's event reference](https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants).

## Run from source

Windows 10/11, Python 3.11 or newer. Tested with Python 3.13 and Qt 6.12.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\pythonw.exe main.py
```

Preferences and lifetime counts use per-user Windows settings
(`HKEY_CURRENT_USER\Software\DesktopNeko\Neko`). Startup is opt-in from the nook;
existing startup registrations from the old version remain in place until changed.
Turning startup off also removes the old `DesktopNeko.lnk` shortcut. Keep the
executable/source folder in a stable location if using startup.

## Optional AI observations

The pet works offline. AI is off by default. To enable it:

1. Set `GEMINI_API_KEY` in the environment **before launching Neko**, or copy
   `config.example.json` to `config.json` and fill in your own key.
2. Open the nook and enable **AI observations**.

For a packaged executable, `config.json` belongs beside the executable. Keys are
never included in a build. If a key was committed in an older revision, rotate it:
ignoring the file now does not remove it from Git history.

When an unprompted comment is due, AI sends the **current window title** to Google
Gemini, at most once every ten minutes. Other comments remain offline. Window
titles may contain private names or document titles. No screenshots,
microphone, files, or conversation history are collected. Quiet mode and hiding
prevent new requests. An already-sent request cannot be retracted, but its reply
is discarded after hiding, petting, entering fullscreen, or changing AI/quiet mode.

The default model is `gemini-3.5-flash-lite`; set `GEMINI_MODEL` to override it.
Requests use a 12-second HTTP timeout without retries. Missing keys, network
failures, or empty responses fall back to local dialogue without error bubbles.
The nook shows connection status. No real API calls are made by the tests.

SDK configuration follows the [Google Gen AI SDK](https://github.com/googleapis/python-genai).
Model availability is listed in [Google's model lifecycle documentation](https://ai.google.dev/gemini-api/docs/deprecations).

## Build a Windows executable

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean main.spec
```

The result is `dist\DesktopNeko.exe`. Assets are bundled; local configuration is
deliberately excluded. Build on Windows. A source launch and the executable use
the same preferences and instance lock. The build isolates its DLL search path
so unrelated tools cannot supply conflicting Windows libraries.

The startup/thought correction build is `dist\updated\DesktopNeko.exe` while the
previous executable is running. Quit the existing Neko from her tray menu before
launching it; the single-instance lock prevents two kittens running together.

The newer twelve-reaction petting build is `dist\petting-qol\DesktopNeko.exe`.
Use that build for the new petting animations; quit the existing Neko first.

## Check the behavior

```powershell
.venv\Scripts\python.exe -m unittest discover -v
```

Tests cover animation timing, frame importing, header-only keyboard detection,
window events, quiet timing, naps, curiosity, clicks versus dragging, fullscreen
preferences, pinning flags, persistence, stale AI replies and API failure handling.
Qt tests default to offscreen rendering with temporary settings.
For native Windows widgets, set `$env:QT_QPA_PLATFORM = 'windows'` before running.
Tests do not change Windows startup or use your API key.

After building, quit any running Neko and check the actual executable as well:

```powershell
$env:NEKO_TEST_EXE = 'dist\DesktopNeko.exe'
.venv\Scripts\python.exe -m unittest test_packaging -v
Remove-Item Env:NEKO_TEST_EXE
```

These opt-in checks verify bundle contents, native Qt startup, and rejection of
a second instance. They respect foreground fullscreen apps and stop only the
processes they launch.

## Character assets

The base idle, pets, activity and movement v3 sheets each contain four sequences of four drawings.
`assets/neko-transitions-v1.png` adds sixteen sleep/wake drawings with a constant
character scale through the change in posture. `assets/neko-affection-v1.png`
supplies the retained chin scritches, blep and ear rubs.
`assets/neko-petting-a-v1.png` and `assets/neko-petting-b-v1.png` each contain
three rows of four drawings, for five new reactions and the remade paw offer.
`assets/neko-tailplay-v4.png` supplies the eleven-pose running cycle and five preparation/payoff poses.
`assets/neko-tailsettle-v1.png` adds eight entry/recovery poses, calibrated separately
and appended to the tail sequence without altering the accepted running artwork.
`assets/neko-arrival-v1.png` supplies the graceful landing; the first two drawings in
`assets/neko-farewell-v1.png` introduce sadness before the retained hop in
`assets/neko-lifecycle-v2.png`. `assets/neko-tailswish-v1.png` supplies the lazy swish.
`assets/neko-idleplay-a-v1.png`, `assets/neko-idleplay-b-v1.png` and
`assets/neko-idleplay-c-v1.png` provide the new idle stories. Replaced idle/activity/
movement rows and the rejected swish candidates are not imported. New idle stories
share measured head calibration throughout each sequence and return to canonical idle.
The retired wave, old paw-offer and original tail-swish rows are never loaded into the atlas. Frame
durations and directional variants live in `animations.py`. Frames are imported
once at a consistent scale and anchored at their feet. Generated-sheet bleed from
neighboring cells is excluded when locating each silhouette.

The [generation prompts and art notes](docs/animation-notes.md) document the built-in
ImageGen workflow; [tail and lifecycle notes](docs/tail-lifecycle-notes.md) include
the rebuilt motion, [revision prompts](docs/playful-motion-prompts.md), and frame-by-frame QA.
Run `tools/preview_animations.py` with optional Pillow installed to regenerate the runtime catalogs.
See [idle personality and readability verification](docs/idle-personality-validation.md),
the [generation prompts](docs/idle-personality-prompts.md) and the
[native before/after bubble preview](docs/neko-thought-readability.png).
The later [startup and transparent-thought correction](docs/startup-thought-validation.md)
supersedes that bubble styling; see the [current text-only preview](docs/neko-thought-transparent.png).
The [expressive petting revision and per-reaction verification](docs/petting-revision-validation.md)
records current timings, expression choices, native rendering and safe repeated-click handoffs.
See the [expression/gesture study](docs/petting-expression-study.md) for the acting references.
The original six
transparent PNGs remain as fallbacks. Matching
GIFs in `assets/` still take precedence over the atlas for customization. Motion can
be disabled in the nook, holding a still frame without losing direct interaction.
Missing art has a small text-cat fallback.
`gen_gif.py` is the original optional animation experiment; it needs Pillow and
generates a bouncing ball, so it isn't part of the app or build.

## Project map

- `behavior.py`: timing, temporary poses, naps, and pet reactions; no Qt or network.
- `main.py`: desktop integration, rendering, preferences, nook, and tray.
- `animations.py`: sprite atlas loading, frame timing and directional clips.
- `cursors.py`: small palm-stroke cursor frames with a stationary hotspot.
- `activity.py`: local keyboard headers, Windows events and foreground executable name.
- `app_context.py`: local app categories and media title hints.
- `dialogue.py`: offline lines and per-context shuffle bags.
- `tools/make_sounds.py`: reproducible, original synthesized WAV cues; standard library only.
- `llm_brain.py`: optional title-only Gemini worker.
- `test_*.py`: standard-library unittest suite, with Qt's event helpers.
- `Plan.txt`: interaction rules for keeping future changes quiet and minimal.

Built by Sobi, who kinda likes Nekos.
