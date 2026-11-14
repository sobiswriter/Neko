"""Small local app hints; no document text, media capture, or process inventory."""

from pathlib import PureWindowsPath


APP_KINDS = {
    # Music players and streaming apps.
    "spotify.exe": "music", "music.ui.exe": "music", "foobar2000.exe": "music",
    "aimp.exe": "music", "itunes.exe": "music", "musicbee.exe": "music",
    "applemusic.exe": "music", "winamp.exe": "music", "tidal.exe": "music",
    "deezer.exe": "music", "amazon music.exe": "music", "youtube music.exe": "music",
    "youtube music desktop app.exe": "music", "audacious.exe": "music",
    "clementine.exe": "music", "strawberry.exe": "music", "dopamine.exe": "music",
    "musicolet.exe": "music", "cider.exe": "music", "plexamp.exe": "music",
    # Video players (audio files in these are detected from the title below).
    "vlc.exe": "video", "mpv.exe": "video", "mpc-hc64.exe": "video",
    "mpc-hc.exe": "video", "mpc-be64.exe": "video", "mpc-be.exe": "video",
    "potplayermini64.exe": "video", "potplayermini.exe": "video", "potplayer64.exe": "video",
    "kmplayer.exe": "video", "kmplayer64x.exe": "video", "gom.exe": "video",
    "smplayer.exe": "video", "video.ui.exe": "video", "wmplayer.exe": "video",
    "microsoft.media.player.exe": "video", "plex.exe": "video", "stremio.exe": "video",
    "kodi.exe": "video", "jellyfin media player.exe": "video", "netflix.exe": "video",
    # Code editors and IDEs.
    "code.exe": "coding", "code - insiders.exe": "coding", "vscodium.exe": "coding",
    "kiro.exe": "coding", "cursor.exe": "coding", "windsurf.exe": "coding",
    "zed.exe": "coding", "sublime_text.exe": "coding", "notepad++.exe": "coding",
    "devenv.exe": "coding", "pycharm64.exe": "coding", "pycharm.exe": "coding",
    "idea64.exe": "coding", "idea.exe": "coding", "webstorm64.exe": "coding",
    "rider64.exe": "coding", "clion64.exe": "coding", "goland64.exe": "coding",
    "phpstorm64.exe": "coding", "rustrover64.exe": "coding", "datagrip64.exe": "coding",
    "studio64.exe": "coding", "fleet.exe": "coding", "eclipse.exe": "coding",
    "nvim-qt.exe": "coding", "neovide.exe": "coding", "gvim.exe": "coding",
    "emacs.exe": "coding", "runemacs.exe": "coding", "lapce.exe": "coding",
    "godot.exe": "coding", "unity.exe": "coding", "unityhub.exe": "coding",
    "unrealeditor.exe": "coding", "github desktop.exe": "coding", "githubdesktop.exe": "coding",
    "postman.exe": "coding", "arduino ide.exe": "coding",
    # Drawing, design and media creation.
    "krita.exe": "drawing", "photoshop.exe": "drawing", "mspaint.exe": "drawing",
    "aseprite.exe": "drawing", "blender.exe": "drawing", "figma.exe": "drawing",
    "illustrator.exe": "drawing", "clipstudiopaint.exe": "drawing", "gimp.exe": "drawing",
    "gimp-2.10.exe": "drawing", "inkscape.exe": "drawing", "paintdotnet.exe": "drawing",
    "affinity photo 2.exe": "drawing", "affinity designer 2.exe": "drawing",
    "photo.exe": "drawing", "designer.exe": "drawing", "medibangpaintpro.exe": "drawing",
    "firealpaca.exe": "drawing", "sai.exe": "drawing", "sai2.exe": "drawing",
    "canva.exe": "drawing", "pixelorama.exe": "drawing",
    # Writing and notes.
    "winword.exe": "writing", "notepad.exe": "writing", "obsidian.exe": "writing",
    "notion.exe": "writing", "onenote.exe": "writing", "wordpad.exe": "writing",
    "typora.exe": "writing", "logseq.exe": "writing", "joplin.exe": "writing",
    "scrivener.exe": "writing", "soffice.bin": "writing", "swriter.exe": "writing",
    "evernote.exe": "writing", "anytype.exe": "writing", "standard notes.exe": "writing",
    # Chat.
    "discord.exe": "chat", "slack.exe": "chat", "telegram.exe": "chat",
    "whatsapp.exe": "chat", "ms-teams.exe": "chat", "teams.exe": "chat",
    "signal.exe": "chat", "element.exe": "chat", "zoom.exe": "chat",
    "messenger.exe": "chat", "skype.exe": "chat", "thunderbird.exe": "chat",
    "outlook.exe": "chat", "olk.exe": "chat", "vesktop.exe": "chat",
    # Game launchers.
    "steam.exe": "game", "epicgameslauncher.exe": "game", "battle.net.exe": "game",
    "gog galaxy.exe": "game", "galaxyclient.exe": "game", "riotclientux.exe": "game",
    "eadesktop.exe": "game", "ubisoftconnect.exe": "game", "xboxapp.exe": "game",
    "xboxpcapp.exe": "game", "minecraftlauncher.exe": "game", "playnite.desktopapp.exe": "game",
    # Files and terminals.
    "explorer.exe": "files", "totalcmd64.exe": "files", "files.exe": "files",
    "everything.exe": "files", "7zfm.exe": "files",
    "windowsterminal.exe": "terminal", "openconsole.exe": "terminal",
    "cmd.exe": "terminal", "powershell.exe": "terminal", "pwsh.exe": "terminal",
    "wezterm-gui.exe": "terminal", "alacritty.exe": "terminal", "mintty.exe": "terminal",
    "conemu64.exe": "terminal", "tabby.exe": "terminal", "warp.exe": "terminal",
    "hyper.exe": "terminal", "wsl.exe": "terminal", "putty.exe": "terminal",
}
AUDIO_EXTENSIONS = (".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", ".opus", ".wma", ".alac", ".aiff")
BROWSERS = ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "opera_gx.exe",
            "vivaldi.exe", "arc.exe", "zen.exe", "librewolf.exe", "floorp.exe", "waterfox.exe",
            "chromium.exe", "thorium.exe", "yandex.exe", "browser.exe")
# Site names as browsers show them in a page title ("Page - Site - Browser").
# Each hint is matched as a separate " - site", " | site" or "site - " title segment, not
# any mention, so a search *about* Spotify does not count as listening to it.
BROWSER_SITES = (
    ("music", ("youtube music", "spotify", "soundcloud", "apple music",
               "deezer", "tidal", "bandcamp", "pandora", "amazon music", "last.fm")),
    ("video", ("youtube", "netflix", "twitch", "prime video", "disney+", "crunchyroll", "vimeo",
               "max", "hulu", "jiocinema", "hotstar", "jiohotstar", "plex", "apple tv", "dailymotion")),
    ("coding", ("github", "gitlab", "stack overflow", "codepen", "codesandbox", "replit",
                "leetcode", "google colab", "colab", "jupyterlab", "stackblitz", "vercel", "bitbucket")),
    ("drawing", ("figma", "canva", "photopea", "excalidraw", "miro")),
    ("writing", ("google docs", "notion", "overleaf", "medium", "word", "google keep", "dropbox paper")),
    ("chat", ("discord", "whatsapp", "slack", "messenger", "telegram", "gmail", "outlook",
              "microsoft teams", "teams", "instagram")),
    ("game", ("itch.io", "chess.com", "lichess.org", "poki", "crazygames")),
)


def _segments(title):
    """Split a browser title into the separate pieces sites use for their names."""
    for mark in (" — ", " – ", " | ", " · ", " - "):
        title = title.replace(mark, "\n")
    return {part.strip() for part in title.split("\n") if part.strip()}


def browser_kind(title):
    segments = _segments(title)
    for kind, sites in BROWSER_SITES:
        if any(site in segments for site in sites):
            return kind
    if title.startswith("spotify") or title.startswith("netflix"):
        return "music" if title.startswith("spotify") else "video"
    return None


def app_kind(executable, title=""):
    name = PureWindowsPath(executable).name.casefold()
    title = title.casefold()
    kind = APP_KINDS.get(name)
    if kind == "video" and any(extension in title for extension in AUDIO_EXTENSIONS):
        return "music"
    # shortcut: app/title hints do not prove playback; use media-session APIs for exact playback state.
    if name in BROWSERS:
        return browser_kind(title)
    return kind
