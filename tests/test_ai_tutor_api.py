"""API contract tests for the `/ask` endpoint (mocked tutor behavior)."""

import unittest
from unittest.mock import patch

from ai_tutor.api import app


class AskEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_ask_requires_question(self):
        response = self.client.post("/ask", json={"foo": "bar"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Field 'question' is required")

    @patch("ai_tutor.api.tutor.ask_freeform", return_value="Solved")
    def test_ask_accepts_question_only(self, mock_ask):
        response = self.client.post("/ask", json={"question": "3/4 + 1/2"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["explanation"], "Solved")
        mock_ask.assert_called_once_with("3/4 + 1/2", "", None)


if __name__ == "__main__":
    unittest.main()
