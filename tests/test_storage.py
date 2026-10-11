"""Tests saving and loading tickets."""

import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import save_tickets, load_tickets


class TestTicketStorage(unittest.TestCase):
    """Tests JSON persistence."""

    def setUp(self):
        # Create a temporary directory for each test.
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi problem",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

    def tearDown(self):
        # Remove the temporary directory after each test.
        self.temp_directory.cleanup()

    def test_save_and_load_tickets(self):
        save_tickets(self.tickets, self.file_path)

        loaded_tickets = load_tickets(self.file_path)

        self.assertEqual(loaded_tickets, self.tickets)

    def test_missing_file_returns_empty_list(self):
        loaded_tickets = load_tickets(self.file_path)

        self.assertEqual(loaded_tickets, [])

    def test_malformed_json_raises_error(self):
        self.file_path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_json_must_contain_a_list(self):
        self.file_path.write_text(
            json.dumps({"id": "T001"}),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)


if __name__ == "__main__":
    unittest.main()