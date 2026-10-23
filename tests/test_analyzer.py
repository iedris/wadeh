import io
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import analyzer


class AnalyzerTests(unittest.TestCase):
    def test_empty_document_does_not_create_client(self):
        with patch.object(analyzer, "Groq") as factory:
            with self.assertRaisesRegex(analyzer.AnalysisError, "empty"):
                analyzer.ask_ai(" \n ")
            factory.assert_not_called()

    def test_missing_key(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(analyzer, "load_dotenv"):
            with self.assertRaisesRegex(analyzer.AnalysisError, "GROQ_API_KEY"):
                analyzer.ask_ai("A document")

    def test_request_and_response(self):
        client = MagicMock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" Explanation "))]
        )
        with patch.dict(os.environ, {"GROQ_API_KEY": "test", "GROQ_MODEL": "env-model"}), \
             patch.object(analyzer, "load_dotenv"), \
             patch.object(analyzer, "Groq") as factory:
            factory.return_value.__enter__.return_value = client
            self.assertEqual(analyzer.ask_ai(" document ", model="override"), "Explanation")
            request = client.chat.completions.create.call_args.kwargs
            self.assertEqual(request["model"], "override")
            self.assertEqual(request["messages"][1], {"role": "user", "content": "document"})
            client.chat.completions.create.return_value.choices = []
            with self.assertRaisesRegex(analyzer.AnalysisError, "no explanation"):
                analyzer.ask_ai("document")

    def test_interactive_multiline(self):
        with patch.object(analyzer.sys, "stdin") as stdin, \
             patch("builtins.input", side_effect=["First", "", "Second", "", ""]), \
             patch.object(analyzer.sys, "stderr", io.StringIO()):
            stdin.isatty.return_value = True
            self.assertEqual(analyzer.read_document(None), "First\n\nSecond")

    def test_missing_file(self):
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(analyzer.AnalysisError, "Cannot read"):
                analyzer.read_document(Path("missing.txt"))

    def test_cli_failure_status(self):
        with patch.object(analyzer, "read_document", return_value=""), \
             patch.object(analyzer.sys, "stderr", io.StringIO()) as stderr:
            self.assertEqual(analyzer.main([]), 1)
            self.assertIn("empty", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
