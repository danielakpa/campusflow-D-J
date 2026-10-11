"""Tests for JSON storage and ticket data validation."""

import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import (
    load_tickets,
    save_tickets,
    validate_ticket_data,
)


class TestTicketDataValidation(unittest.TestCase):
    """Tests validation of ticket fields and values."""

    def setUp(self):
        """Create a valid ticket for testing."""

        self.ticket = {
            "id": "T001",
            "title": "Slow internet speed",
            "category": "Other",
            "urgency": "medium",
            "affected_users": 3,
            "priority": "medium",
            "status": "in_progress",
            "assigned_to": "janai",
        }

    def test_accept_valid_ticket(self):
        self.assertTrue(validate_ticket_data([self.ticket]))

    def test_accept_custom_category(self):
        ticket = self.ticket.copy()
        ticket["category"] = "Electricity"

        self.assertTrue(validate_ticket_data([ticket]))

    def test_reject_non_list_data(self):
        with self.assertRaises(ValueError):
            validate_ticket_data(self.ticket)

    def test_reject_non_dictionary_ticket(self):
        with self.assertRaises(ValueError):
            validate_ticket_data(["not a ticket"])

    def test_reject_missing_field(self):
        ticket = self.ticket.copy()
        del ticket["title"]

        with self.assertRaisesRegex(ValueError, "Missing 'title'"):
            validate_ticket_data([ticket])

    def test_reject_wrong_data_types(self):
        # Each field must contain its expected data type.
        invalid_values = {
            "id": 404,
            "title": 123,
            "category": 45,
            "urgency": True,
            "affected_users": "boy",
            "priority": 20,
            "status": 10,
            "assigned_to": 200,
        }

        for field, invalid_value in invalid_values.items():
            with self.subTest(field=field):
                ticket = self.ticket.copy()
                ticket[field] = invalid_value

                with self.assertRaises(ValueError):
                    validate_ticket_data([ticket])

    def test_reject_boolean_as_affected_users(self):
        ticket = self.ticket.copy()
        ticket["affected_users"] = True

        with self.assertRaises(ValueError):
            validate_ticket_data([ticket])

    def test_reject_zero_affected_users(self):
        ticket = self.ticket.copy()
        ticket["affected_users"] = 0

        with self.assertRaises(ValueError):
            validate_ticket_data([ticket])

    def test_reject_invalid_status(self):
        ticket = self.ticket.copy()
        ticket["status"] = "sleeping"

        with self.assertRaisesRegex(ValueError, "Invalid status"):
            validate_ticket_data([ticket])

    def test_reject_invalid_urgency(self):
        ticket = self.ticket.copy()
        ticket["urgency"] = "urgent"

        with self.assertRaisesRegex(ValueError, "Invalid urgency"):
            validate_ticket_data([ticket])

    def test_reject_invalid_priority(self):
        ticket = self.ticket.copy()
        ticket["priority"] = "extreme"

        with self.assertRaisesRegex(ValueError, "Invalid priority"):
            validate_ticket_data([ticket])

    def test_reject_empty_title(self):
        ticket = self.ticket.copy()
        ticket["title"] = "   "

        with self.assertRaises(ValueError):
            validate_ticket_data([ticket])


class TestJSONStorage(unittest.TestCase):
    """Tests loading, saving, and handling corrupted JSON files."""

    def setUp(self):
        """Create a temporary directory for storage tests."""

        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

        self.ticket = {
            "id": "T001",
            "title": "Slow internet speed",
            "category": "Other",
            "urgency": "medium",
            "affected_users": 3,
            "priority": "medium",
            "status": "in_progress",
            "assigned_to": "janai",
        }

    def tearDown(self):
        """Remove temporary test files."""

        self.temp_directory.cleanup()

    def test_save_and_load_valid_tickets(self):
        save_tickets([self.ticket], self.file_path)

        loaded_tickets = load_tickets(self.file_path)

        self.assertEqual(loaded_tickets, [self.ticket])

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.file_path), [])

    def test_invalid_json_is_detected(self):
        self.file_path.write_text(
            '{"affected_users": boy}',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.file_path)

    def test_wrong_field_type_is_detected_when_loading(self):
        corrupted_ticket = self.ticket.copy()
        corrupted_ticket["affected_users"] = "boy"

        self.file_path.write_text(
            json.dumps([corrupted_ticket]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "affected_users",
        ):
            load_tickets(self.file_path)

    def test_corrupted_file_is_not_modified_when_loading_fails(self):
        corrupted_content = '{"affected_users": boy}'

        self.file_path.write_text(
            corrupted_content,
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            corrupted_content,
        )

    def test_invalid_data_is_not_saved(self):
        # Start with a valid file.
        save_tickets([self.ticket], self.file_path)

        original_content = self.file_path.read_text(encoding="utf-8")

        # Attempt to save a ticket containing an invalid value.
        corrupted_ticket = self.ticket.copy()
        corrupted_ticket["affected_users"] = "boy"

        with self.assertRaises(ValueError):
            save_tickets([corrupted_ticket], self.file_path)

        # The existing file must remain unchanged.
        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            original_content,
        )


if __name__ == "__main__":
    unittest.main()