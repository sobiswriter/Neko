# Desktop Neko 🐾

A little company for your Windows desktop. Neko stretches, settles down, notices
your cursor, and naps when you step away. No chores or attention meter.
Soft sounds are optional and off until you enable them.

![Neko's petting animations](docs/neko-pet-catalog.gif)

## Living with Neko

- **Catch the Cursor.** Right-click Neko or use her tray menu → **Play · Catch the Cursor**.
  The nook's **Play** tab has the same control and **Automatic cursor games**, enabled
  by default, with **90 seconds** between opportunities (adjustable from 30–600 seconds).
  The cooldown arms play; she waits for a fresh approach into the invisible reachable area
  beside her, outside her petting space. A stationary cursor cannot trigger it at expiry.
  Naps, carrying, care, menus, typing and fullscreen take priority; Quiet company pauses it.
  A fresh side approach during an idle gesture waits for that gesture to finish.
  She notices the arrow, gives a real **3… 2… 1… Here I come!**, then runs and pounces.
  There are no guide lines, game clock or floating buttons. Her forepaw touching the arrow
  wins one of three celebrations: happy hops, a proud hug or champion paws.
  Playful eye squeezes, a new eight-pose walk, sparse chase thoughts and three different
  sulks give her more life. Each chase lasts up to 45 seconds; four continuous seconds
  outside her reachable band ends it, with a little protest first.
  After a loss she curls up, a little disappointed. A pet comforts her through a drawn get-up;
  if left unattended, she can settle for her configured nap instead of sulking forever.
  Moving her preserves that mood and never counts as a nap.
  **End game** lives in her ordinary menu/nook; petting, holding, hide and fullscreen can cancel neutrally.
  Gentle motion off uses a stationary paw target. The real pointer is never moved,
  hidden or captured. **Games played** and **Neko wins** are saved locally in her menu and nook.
  Abandoned countdowns do not count as games.
  [Preview and verification](docs/cursor-play-v2-validation.md) · [approved design](docs/cursor-play-v2-plan.md).
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
  Petting now runs about 15% faster, keeping every pose and complete recovery;
  the shortest 50ms poses retain their original duration.
- **Pick her up.** Dragging starts a lift immediately; a stationary click-hold starts
  after 250ms. She dangles with little paw/tail movements, going from excited to
  calm after three seconds, mildly unimpressed after ten, then sleepy after twenty.
  A little yawn happens once before her sleepy loop. Release at any point—even
  mid-lift or mid-yawn—and she settles at the chosen location and returns to idle.
  Re-grabbing follows the visible pose back into the hold and preserves her expression.
  Holding never counts as petting; quick clicks still do. Real naps stay asleep
  while carried, with a due timed wake waiting for supported placement. Reduced
  motion uses a still held pose and immediate placement. Position is remembered.
  See the [complete pickup preview and verification](docs/pickup-validation.md).
- **A little helping hand.** Hovering shows an open palm; holding uses a closed hand
  for dragging. A pet click plays a short palm stroke without moving the actual pointer.
  Leaving, hiding, entering fullscreen or reduced motion stops the stroke.
- **Come close.** She can notice a nearby cursor while keeping her place.
  Cursor chasing belongs to Catch the Cursor; ordinary idle following has been removed.
- **Keep working.** Tail swishes, ear flicks, sniffing, loafing, grooming, stretches,
  yawns and sleepy peeks share an atlas of 839 entries, including 212 game source slots and 98 current/historical lifecycle entries, with eight-frame transitions into
  sleep and back to sitting. Most gestures have 5–6 seconds on screen: one gentle
  motion followed by a relaxed rest, without repeated head-bobbing or stretching.
  Tail swishes make one lazy sweep and rest; typing uses a gentle repeating cycle.
  Normal rendering runs at 10 FPS; tail running, petting and carrying use 20 FPS; cursor games use a precise 50 FPS timer.
  Petting/carrying use a precise Qt timer so short connecting poses get screen time.
  Arrival/departure briefly use 30 FPS for smooth travel,
  while the new supported walk uses eight poses in a 960ms cycle.
  Every frame has a 192 × 144 transparent canvas, with extra horizontal room for
  rolls/deeper reaches and 32 transparent pixels above the original footprint for lifting.
  Idle remains about 82 pixels tall;
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
- **Hello and goodbye.** One graceful diagonal leap brings her into view, with
  reaching forelegs, planted front paws, a folding spine and gathered hindquarters.
  She recovers under support into a pleased tilt and smile, with no second bounce.
  The 1.98s entrance uses 19 selected poses and ends at her actual idle and saved position.
  **Let her go · quit** gives her lowered ears, soft sad eyes and a dipped head,
  then a drawn turn into a loaded crouch and one diagonal
  leap out, stretching then tucking/reaching with her attached tail following.
  High perches use a nearer side boundary; low departures head diagonally down.
  This 20-entry goodbye lasts 2.20s and moves the actual window, while preserving
  her resting position. Both clocks start on Qt's first animation tick so loading
  cannot spend the performance before it appears. Visible fullscreen launches also
  play the drop-in, silently; the fullscreen hiding preference still applies.
  They keep her saved desktop position, and do not accept pets or
  window reactions midway through. Reduced motion skips the jumps; quitting
  while hidden or fullscreen is immediate. Sleeping, held or other incompatible
  poses close immediately rather than snapping into a seated goodbye. Hide/Show
  remains immediate. [Preview and verification](docs/lifecycle-v2-validation.md).
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
- **Offline personality.** 346 short lines, including more personal questions and
  company addressed to you, shuffled separately for typing,
  windows, pets, cursor curiosity, waking, and idle thoughts. No repeat until that
  context's bag is exhausted. Ambient thoughts default to about 75 seconds apart.
  All automatic words—including idle, activity and optional AI comments—respect
  the full **Thoughts every** minimum (default 75 seconds) and never replace a visible bubble.
  Every spontaneous idle attempts its own local thought, including “Look at meeee!”
  and “Round.. around... around...” for tail chasing. Quiet/fullscreen rules still apply.
  Thoughts use cream 16px semibold text with a small dark shadow and a compact,
  rounded glass backdrop with a faint rim, a nearly clear tint and gentler frosting.
  The desktop behind it blurs while the lettering stays
  sharp; unsupported systems retain a light translucent tint. It stays click-through,
  takes no focus, fits short lines and wraps within 270px for 5.5–10 seconds.
  A tiny backdrop sample is softened inside the rounded edges when each thought
  appears; it stays still until the thought closes. The sample stays in memory,
  is cleared on hide and is never saved or uploaded. No new runtime dependency is used.
  See the [rounded blur fix and verification](docs/thought-rounded-clip-validation.md).
- **Little app rituals.** VLC gets a watch-buddy loaf and questions about what
  you're watching; audio file titles and Spotify get listening questions and tail
  swishes. Coding, drawing, writing, chat, games, folders and terminals each have
  their own lines and matching gestures. These are app hints, not content analysis.
  Typing, window/tab events, cursor curiosity and following share one minimum
  reaction gap: **60 seconds** by default, adjustable from **15–600 seconds** through
  **Neko's nook → Company → Activity reactions every**. Events during that gap
  are discarded, so they cannot pile up. Idle gestures keep their separate timing;
  deliberate pets and naps still work normally.

  To edit her offline voice, open [dialogue.py](dialogue.py). Its `LINES` dictionary
  contains all 346 phrases in 33 named groups (`typing`, `coding`, `pet`, `tail_chase`, etc.).
  Edit or add one phrase per line inside the existing triple-quoted groups; keep the
  section names/quotes and aim for at most 110 characters per phrase. Source launches
  use your edits on restart; the packaged executable needs rebuilding. Optional AI
  comments are generated separately and are not part of this file.
- **Soft mews & purrs.** Enable them in the nook's Settings tab; Listen previews a
  small mew. These original synthesized cues are up to a second long, with low
  volume encoded into the WAV files. A deliberate pet can purr or mew; she can
  chirp on arrival. Automatic cues have a 45-second pause and are suppressed during media apps,
  quiet company and fullscreen. Turning sounds off or hiding stops playback.
- **Right-click for her nook.** Quiet company, reduced motion, startup, optional
  AI, cursor-play timing, sleep delay and duration, chatter and idle gesture frequency, and lifetime
  pet/nap and played/won counts live in one small window. Double-click the tray
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
Neko runs with normal user permissions. Enabling startup clears only its executable's
`RUNASADMIN` compatibility flag, which otherwise prevents a normal logon launch;
other compatibility flags remain intact. The supplied root `neko_sleep.ico` is the
shared executable, application-window, nook and tray icon. See the
[startup/icon repair record](docs/startup-icon-validation.md).

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

Packaging prepares all 839 calibrated animation frames once with
`tools/bake_atlas.py`. The executable loads those finished frames directly,
avoiding source-sheet silhouette analysis on every launch. Source launches keep
the original importer; source artwork and custom asset overrides are retained.
See the [startup measurements and verification](docs/startup-performance-validation.md).

The current build is `dist\DesktopNeko.exe`; its immediate predecessor is
`dist\DesktopNeko-previous.exe`. Keep these two files directly in `dist`, without
release subfolders. Quit the existing Neko before launching the new build;
the single-instance lock prevents two kittens running together.
The latest build includes Catch the Cursor, pickup, slightly faster petting, frosted thoughts,
the supplied icon and startup repair; see [Catch verification](docs/catch-validation.md)
and the [startup/icon record](docs/startup-icon-validation.md). The
[quieter cursor-play v2](docs/cursor-play-v2-validation.md) and the
[reference-led diagonal entrance/goodbye](docs/lifecycle-v2-validation.md) are implemented.
Historical build paths
in older reports describe their original delivery locations.

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
contains historical chin scritches, blep and ear rubs; those pet rows are no longer imported.
`assets/neko-petting-a-v1.png` and `assets/neko-petting-b-v1.png` each contain
three rows of four drawings from an earlier petting pass; they too are historical.
`assets/neko-tailplay-v4.png` supplies the eleven-pose running cycle and five preparation/payoff poses.
`assets/neko-tailsettle-v1.png` adds eight entry/recovery poses, calibrated separately
and appended to the tail sequence without altering the accepted running artwork.
`assets/neko-lifecycle-arrive-v2.png`, `assets/neko-lifecycle-depart-v2.png` and
`assets/neko-lifecycle-bridge-v2.png` supply the current diagonal arrival/departure
and corrective bridges. `assets/neko-lifecycle-sad-v2.png` adds the sad expression
and supported turn into take-off. [Exact prompts and assembly](docs/lifecycle-v2-prompts.json).
Earlier arrival/farewell/lifecycle/visitor sheets remain historical imported banks.
`assets/neko-tailswish-v1.png` supplies the lazy swish.
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
Current petting uses twelve dedicated `assets/neko-pet-*-v1.png` sheets, with
16–28 source slots each and a separate canonical-idle handoff. The playful roll
replaces blep. Older pet sheets remain historical assets rather than active pet playback.
Nine `assets/neko-carry-*-v1.png` sheets add 100 source slots for lifting, held
expressions, facial bridges and entry from side/low/rolled postures. They share
measured head calibration and supported recovery; release can interrupt every phase.
The original six
transparent PNGs remain as fallbacks. Matching
GIFs in `assets/` still take precedence over the atlas for customization. Motion can
be disabled in the nook, holding a still frame without losing direct interaction.
Missing art has a small text-cat fallback.
`gen_gif.py` is the original optional animation experiment; it needs Pillow and
generates a bouncing ball, so it isn't part of the app or build.

## Animation authoring

Read [framemaster.md](framemaster.md) before planning or changing animations.
It records the successful method: physical storyboards, subtle expressions,
ImageGen prompt requirements, exact frame assembly, fixed scale and support
registration, complete idle transitions, runtime integration and visual/native
verification. It also records rejected approaches and known testing limits.

[AGENTS.md](AGENTS.md) directs future animation work to that guide. Add verified
discoveries to the relevant section and its dated findings log, with evidence and
remaining limits; keep proposed techniques separate from tested practice.

The [pickup revision](docs/pickup-validation.md) implements the excited → calm →
mildly unimpressed → sleepy hold, release from any phase and gentle placement.
Its [approved design](docs/pickup-animation-plan.md), [exact prompts/assembly](docs/pickup-prompts.json)
and [native measurements](docs/pickup-native.json) preserve the reasoning and evidence.
Run `tools/preview_pickup.py` with optional Pillow to reproduce the full mood preview
and source/release sheets. Progress and verification are in [tasks/todo.md](tasks/todo.md).

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
- `framemaster.md`: animation philosophy, production method, verification and discoveries.
- `AGENTS.md`: animation-specific instructions for future agents.

Built by Sobi, who kinda likes Nekos.
