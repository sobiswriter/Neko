"""Small local app hints; no document text, media capture, or process inventory."""

from pathlib import PureWindowsPath


APP_KINDS = {
    "spotify.exe": "music", "music.ui.exe": "music", "foobar2000.exe": "music",
    "aimp.exe": "music", "itunes.exe": "music", "musicbee.exe": "music",
    "vlc.exe": "video", "mpv.exe": "video", "mpc-hc64.exe": "video",
    "mpc-hc.exe": "video", "potplayermini64.exe": "video",
    "code.exe": "coding", "devenv.exe": "coding", "pycharm64.exe": "coding",
    "idea64.exe": "coding", "godot.exe": "coding", "unity.exe": "coding",
    "krita.exe": "drawing", "photoshop.exe": "drawing", "mspaint.exe": "drawing",
    "aseprite.exe": "drawing", "blender.exe": "drawing", "figma.exe": "drawing",
    "winword.exe": "writing", "notepad.exe": "writing", "obsidian.exe": "writing",
    "notion.exe": "writing", "onenote.exe": "writing",
    "discord.exe": "chat", "slack.exe": "chat", "telegram.exe": "chat",
    "whatsapp.exe": "chat", "ms-teams.exe": "chat",
    "steam.exe": "game", "epicgameslauncher.exe": "game",
    "explorer.exe": "files", "windowsterminal.exe": "terminal",
    "cmd.exe": "terminal", "powershell.exe": "terminal", "pwsh.exe": "terminal",
}
AUDIO_EXTENSIONS = (".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", ".opus")


def app_kind(executable, title=""):
    name = PureWindowsPath(executable).name.casefold()
    title = title.casefold()
    kind = APP_KINDS.get(name)
    if name in ("vlc.exe", "mpv.exe", "mpc-hc.exe", "mpc-hc64.exe"):
        if any(extension in title for extension in AUDIO_EXTENSIONS):
            return "music"
    # shortcut: app/title hints do not prove playback; use media-session APIs for exact playback state.
    if name in ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"):
        if "spotify" in title or "youtube music" in title or "soundcloud" in title:
            return "music"
        if " - youtube" in title or " | netflix" in title or " - netflix" in title:
            return "video"
    return kind
