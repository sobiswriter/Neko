import os
import unittest
from unittest.mock import MagicMock, patch

from llm_brain import AIBrainWorker, load_api_key


class BrainTests(unittest.TestCase):
    def test_environment_key_takes_precedence(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": " test-key "}):
            self.assertEqual(load_api_key(), "test-key")

    def test_bad_config_is_not_a_crash(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}), \
                patch("pathlib.Path.read_text", return_value='{"GEMINI_API_KEY": 123}'):
            self.assertEqual(load_api_key(), "")

    def test_missing_key_returns_a_silent_failure(self):
        worker = AIBrainWorker("private window title")
        results = []
        worker.finished_thinking.connect(lambda *args: results.append(args))
        with patch("llm_brain.load_api_key", return_value=""):
            worker.run()
        self.assertEqual(results, [("", False)])

    def test_request_is_title_only_bounded_and_times_out(self):
        worker = AIBrainWorker("a" * 1000)
        results = []
        worker.finished_thinking.connect(lambda *args: results.append(args))
        client = MagicMock()
        client.models.generate_content.return_value.text = "  a little   company.  "
        with patch("llm_brain.load_api_key", return_value="test-key"), \
                patch("google.genai.Client") as factory:
            factory.return_value.__enter__.return_value = client
            worker.run()
        self.assertEqual(results, [("a little company.", True)])
        request = client.models.generate_content.call_args.kwargs
        self.assertIsInstance(request["contents"], str)
        self.assertNotIn("private window", request["contents"])
        self.assertEqual(len(worker.active_window_title), 240)
        self.assertEqual(factory.call_args.kwargs["http_options"].timeout, 12000)

    def test_network_error_does_not_become_dialogue(self):
        worker = AIBrainWorker("private title")
        results = []
        worker.finished_thinking.connect(lambda *args: results.append(args))
        with patch("llm_brain.load_api_key", return_value="test-key"), \
                patch("google.genai.Client", side_effect=RuntimeError("private error")):
            worker.run()
        self.assertEqual(results, [("", False)])


if __name__ == "__main__":
    unittest.main()
