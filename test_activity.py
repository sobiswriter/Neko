import ctypes
import time
import unittest
from unittest.mock import patch
from ctypes import wintypes

from activity import ActivityMonitor, RawInputHeader


class ActivityTests(unittest.TestCase):
    def test_keyboard_events_are_bounded_and_expire(self):
        monitor = ActivityMonitor()
        monitor.keyboard.extend([1, 2, 9, 10])
        self.assertEqual(monitor.consume(10), (2, None))
        for n in range(1000):
            monitor.keyboard.append(n)
        self.assertEqual(len(monitor.keyboard), 120)

    def test_only_header_is_requested_not_key_payload(self):
        monitor = ActivityMonitor()
        msg = wintypes.MSG()
        msg.message = 0x00FF
        msg.lParam = 123

        def copy_header(handle, command, output, size, header_size):
            self.assertEqual(command, 0x10000005)
            self.assertEqual(header_size, ctypes.sizeof(RawInputHeader))
            ctypes.cast(output, ctypes.POINTER(RawInputHeader)).contents.kind = 1
            return header_size

        with patch("activity.USER32.GetRawInputData", side_effect=copy_header):
            self.assertEqual(monitor.nativeEventFilter(b"windows_generic_MSG", ctypes.addressof(msg)),
                             (False, 0))
        self.assertEqual(monitor.consume(time.monotonic())[0], 1)

    def test_disabling_reactivity_discards_pending_signals(self):
        monitor = ActivityMonitor()
        monitor.keyboard.append(time.monotonic())
        monitor.window_event = "open"
        monitor.enabled = False
        self.assertEqual(monitor.consume(time.monotonic()), (0, None))

    def test_closing_known_window_emits_one_event(self):
        monitor = ActivityMonitor()
        monitor.windows.add(123)
        monitor.on_window_event(None, 0x8001, 123, 0, 0, 0, 0)
        self.assertEqual(monitor.consume(time.monotonic())[1], "close")
        self.assertIsNone(monitor.consume(time.monotonic())[1])

    def test_title_changes_need_no_window_text(self):
        monitor = ActivityMonitor()
        with patch("activity.win32gui.IsWindowVisible", return_value=True), \
                patch("activity.win32gui.GetAncestor", return_value=123), \
                patch("activity.win32gui.GetWindowLong", return_value=0), \
                patch("activity.win32gui.GetClassName", return_value="Chrome_WidgetWin_1"), \
                patch("activity.win32gui.GetForegroundWindow", return_value=123), \
                patch("activity.win32gui.GetWindowText", side_effect=AssertionError("must not read text")):
            monitor.on_window_event(None, 0x800C, 123, 0, 0, 0, 0)
        self.assertEqual(monitor.consume(time.monotonic())[1], "change")
