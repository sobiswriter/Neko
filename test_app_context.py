import unittest
from unittest.mock import MagicMock, patch
import win32api

from activity import foreground_executable
from app_context import app_kind


class AppContextTests(unittest.TestCase):
    def test_known_apps_use_executable_names_without_needing_document_text(self):
        for executable, expected in ((r"C:\Program Files\VideoLAN\VLC\vlc.exe", "video"),
                                     ("Spotify.EXE", "music"), ("Code.exe", "coding"),
                                     ("krita.exe", "drawing"), ("WINWORD.EXE", "writing"),
                                     ("Discord.exe", "chat"), ("steam.exe", "game"),
                                     ("explorer.exe", "files"), ("pwsh.exe", "terminal")):
            self.assertEqual(app_kind(executable), expected)

    def test_audio_files_in_a_video_player_get_listening_lines(self):
        self.assertEqual(app_kind("vlc.exe", "little song.FLAC - VLC media player"), "music")
        self.assertEqual(app_kind("vlc.exe", "movie.mkv - VLC media player"), "video")

    def test_browser_media_is_only_a_hint_and_unknown_apps_stay_generic(self):
        self.assertEqual(app_kind("firefox.exe", "playlist - YouTube Music"), "music")
        self.assertEqual(app_kind("msedge.exe", "a film - YouTube - Microsoft Edge"), "video")
        self.assertIsNone(app_kind("not-a-browser.exe", "YouTube Spotify"))
        self.assertIsNone(app_kind("chrome.exe", "private document"))

    def test_process_handle_is_closed_and_only_the_executable_name_is_returned(self):
        handle = MagicMock()
        handle.__int__.return_value = 123
        def query(process, flags, buffer, size):
            self.assertEqual(process, 123)
            buffer.value = r"C:\Users\someone\Apps\vlc.exe"
            return True
        with patch("activity.win32process.GetWindowThreadProcessId", return_value=(1, 2)), \
                patch("activity.win32api.OpenProcess", return_value=handle) as opened, \
                patch("activity.KERNEL32.QueryFullProcessImageNameW", side_effect=query):
            self.assertEqual(foreground_executable(100), "vlc.exe")
        opened.assert_called_once_with(0x1000, False, 2)
        handle.Close.assert_called_once()

    def test_inaccessible_apps_leave_context_unknown(self):
        with patch("activity.win32process.GetWindowThreadProcessId", side_effect=win32api.error(5, "test", "denied")):
            self.assertEqual(foreground_executable(100), "")
