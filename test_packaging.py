"""Opt-in checks for the real Windows executable; no API calls or startup changes."""

import os
from pathlib import Path
import subprocess
import time
import unittest


@unittest.skipUnless(os.environ.get("NEKO_TEST_EXE"), "Set NEKO_TEST_EXE to test a Windows build")
class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.exe = Path(os.environ["NEKO_TEST_EXE"]).resolve()
        self.assertTrue(self.exe.is_file())

    def test_bundle_has_art_and_ai_but_no_credentials_or_foreign_icu(self):
        from PyInstaller.archive.readers import CArchiveReader
        archive = CArchiveReader(str(self.exe))
        names = {name.replace("\\", "/") for name in archive.toc}
        self.assertIn("assets/neko_idle.png", names)
        for bank in ("idle", "pets", "activity", "movement"):
            self.assertIn(f"assets/neko-{bank}-v3.png", names)
        self.assertIn("assets/neko-transitions-v1.png", names)
        self.assertIn("assets/neko-affection-v1.png", names)
        self.assertNotIn("assets/neko-petting-v1.png", names)
        self.assertIn("assets/neko-petting-a-v1.png", names)
        self.assertIn("assets/neko-petting-b-v1.png", names)
        self.assertIn("assets/neko-tailplay-v4.png", names)
        self.assertNotIn("assets/neko-tailplay-v3.png", names)
        self.assertIn("assets/neko-arrival-v1.png", names)
        self.assertIn("assets/neko-farewell-v1.png", names)
        self.assertNotIn("assets/neko-tailplay-v2.png", names)
        self.assertIn("assets/neko-lifecycle-v2.png", names)
        self.assertIn("assets/neko-tailswish-v1.png", names)
        self.assertNotIn("assets/neko-tailplay-v1.png", names)
        self.assertNotIn("assets/neko-lifecycle-v1.png", names)
        self.assertNotIn("assets/neko-atlas.png", names)
        for kind in ("mew", "chirp", "purr"):
            self.assertIn(f"assets/sounds/{kind}.wav", names)
        self.assertTrue(any(name.endswith("winsound.pyd") for name in names))
        self.assertNotIn("config.json", names)
        self.assertNotIn("icuuc.dll", names)
        modules = archive.open_embedded_archive("PYZ.pyz").toc
        self.assertIn("llm_brain", modules)
        self.assertIn("google.genai", modules)
        self.assertIn("activity", modules)
        self.assertIn("animations", modules)
        self.assertIn("dialogue", modules)
        self.assertIn("app_context", modules)
        self.assertIn("cursors", modules)

    def test_native_startup_and_second_instance_exits(self):
        import win32gui
        import win32process
        from win32com.client import GetObject

        wmi = GetObject("winmgmts:")

        def owned_windows(process):
            children = wmi.ExecQuery(
                "SELECT ProcessId FROM Win32_Process WHERE ParentProcessId=%d" % process.pid)
            pids = {process.pid} | {int(child.ProcessId) for child in children}
            windows = {}

            def visit(hwnd, _):
                if win32process.GetWindowThreadProcessId(hwnd)[1] in pids:
                    windows[win32gui.GetWindowText(hwnd)] = hwnd

            win32gui.EnumWindows(visit, None)
            return windows

        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "windows"
        processes = []
        try:
            first = subprocess.Popen([str(self.exe)], env=env, creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(first)
            deadline = time.monotonic() + 20
            windows = []
            while time.monotonic() < deadline and "QTrayIconMessageWindow" not in windows:
                self.assertIsNone(first.poll(), "Packaged app exited; quit any running Neko first")
                windows = owned_windows(first)
                self.assertNotIn("Unhandled exception in script", windows)
                time.sleep(0.2)
            # The tray is created even when fullscreen mode correctly hides the pet.
            self.assertIn("QTrayIconMessageWindow", windows, "Packaged Qt UI did not initialize")
            second = subprocess.Popen([str(self.exe)], env=env, creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(second)
            self.assertEqual(second.wait(timeout=15), 0)
            self.assertIsNone(first.poll())
            windows = owned_windows(first)
            self.assertNotIn("Unhandled exception in script", windows)
            self.assertIn("Desktop Neko", windows)
            pet = windows["Desktop Neko"]
            if win32gui.IsWindowVisible(pet):
                self.assertTrue(win32gui.GetWindowLong(pet, -20) & 8, "Visible pet must be topmost")
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                    process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
