import io
import unittest
from unittest.mock import patch

from app import app
from analyzer import AnalysisError


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Explain my document", response.data)
        for asset in ("style.css", "app.js"):
            with self.client.get(f"/static/{asset}") as asset_response:
                self.assertEqual(asset_response.status_code, 200)

    @patch("app.ask_ai", return_value="<script>alert('test')</script>")
    def test_text_analysis_escapes_output(self, analyze):
        response = self.client.post("/", data={"document": "Notice"})
        self.assertEqual(response.status_code, 200)
        analyze.assert_called_once_with("Notice")
        self.assertIn(b"&lt;script&gt;", response.data)
        self.assertNotIn(b"<script>alert", response.data)

    @patch("app.ask_ai", return_value="Explanation")
    def test_upload(self, analyze):
        response = self.client.post("/", data={"file": (io.BytesIO(b"\xef\xbb\xbfNotice"), "notice.txt")})
        self.assertEqual(response.status_code, 200)
        analyze.assert_called_once_with("Notice")

    @patch("app.ask_ai")
    def test_invalid_inputs_do_not_call_api(self, analyze):
        for data in (
            {"file": (io.BytesIO(b"pdf"), "notice.pdf")},
            {"file": (io.BytesIO(b"\xff"), "notice.txt")},
            {"document": "x" * 50001},
            {"document": "Text", "file": (io.BytesIO(b"File"), "notice.txt")},
        ):
            with self.subTest(data_type=list(data)):
                self.assertEqual(self.client.post("/", data=data).status_code, 400)
        analyze.assert_not_called()

    @patch("app.ask_ai", side_effect=AnalysisError("Try again later"))
    def test_api_failure_preserves_input(self, analyze):
        response = self.client.post("/", data={"document": "My notice"})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"My notice", response.data)
        self.assertIn(b"Try again later", response.data)

    def test_request_limit(self):
        response = self.client.post("/", data={"document": "x" * (1024 * 1024)})
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
