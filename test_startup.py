"""Neko-only startup compatibility repair. All registry writes are mocked."""
from pathlib import Path
import unittest
from unittest.mock import patch
import winreg
from main import clear_startup_elevation


class StartupTests(unittest.TestCase):
    def test_removes_only_elevation_for_exact_executable(self):
        with patch("main.winreg.OpenKey") as opened, \
                patch("main.winreg.QueryValueEx", return_value=("~ RUNASADMIN", winreg.REG_SZ)), \
                patch("main.winreg.DeleteValue") as delete, patch("main.winreg.SetValueEx") as write:
            clear_startup_elevation("dist/DesktopNeko.exe")
        delete.assert_called_once_with(opened.return_value.__enter__.return_value,
                                       str(Path("dist/DesktopNeko.exe").resolve()))
        write.assert_not_called()

    def test_preserves_other_compatibility_flags(self):
        with patch("main.winreg.OpenKey"), \
                patch("main.winreg.QueryValueEx", return_value=("~ HIGHDPIAWARE RUNASADMIN WIN8RTM", winreg.REG_SZ)), \
                patch("main.winreg.DeleteValue") as delete, patch("main.winreg.SetValueEx") as write:
            clear_startup_elevation("dist/DesktopNeko.exe")
        self.assertEqual(write.call_args.args[-2:], (winreg.REG_SZ, "~ HIGHDPIAWARE WIN8RTM"))
        delete.assert_not_called()

    def test_missing_or_non_elevated_entry_is_unchanged(self):
        with patch("main.winreg.OpenKey", side_effect=FileNotFoundError):
            clear_startup_elevation("dist/DesktopNeko.exe")
        with patch("main.winreg.OpenKey"), \
                patch("main.winreg.QueryValueEx", return_value=("~ HIGHDPIAWARE", winreg.REG_SZ)), \
                patch("main.winreg.DeleteValue") as delete, patch("main.winreg.SetValueEx") as write:
            clear_startup_elevation("dist/DesktopNeko.exe")
        delete.assert_not_called()
        write.assert_not_called()

    def test_errors_surface_without_overwriting_data(self):
        with patch("main.winreg.OpenKey", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                clear_startup_elevation("dist/DesktopNeko.exe")
        with patch("main.winreg.OpenKey"), \
                patch("main.winreg.QueryValueEx", return_value=(b"unexpected", winreg.REG_BINARY)), \
                patch("main.winreg.DeleteValue") as delete, patch("main.winreg.SetValueEx") as write:
            with self.assertRaises(OSError):
                clear_startup_elevation("dist/DesktopNeko.exe")
        delete.assert_not_called()
        write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
