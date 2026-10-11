"""Tests for ticket creation, validation, and priority calculation."""

import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    validate_ticket,
)


class TestPriorityCalculation(unittest.TestCase):
    """Tests for calculating ticket priority."""

    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_high_priority_from_urgency(self):
        self.assertEqual(calculate_priority("high", 5), "high")

    def test_high_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("medium", 2), "medium")

    def test_medium_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestTicketValidation(unittest.TestCase):
    """Tests for validating ticket information."""

    def test_reject_empty_title(self):
        with self.assertRaises(ValueError):
            validate_ticket("   ", "Network", "high", 5)

    def test_accept_custom_category(self):
        """Allow a user-defined category."""
        title, category, urgency = validate_ticket(
            "Internet is down",
            "Food",
            "high",
            5,
        )

        self.assertEqual(category, "Food")

    def test_reject_empty_category(self):
        """Reject a category containing only whitespace."""
        with self.assertRaises(ValueError):
            validate_ticket(
                "Internet is down",
                "   ",
                "high",
                5,
            )

    def test_reject_invalid_urgency(self):
        with self.assertRaises(ValueError):
            validate_ticket(
                "Internet is down",
                "Network",
                "urgent",
                5,
            )

    def test_reject_zero_affected_users(self):
        with self.assertRaises(ValueError):
            validate_ticket(
                "Internet is down",
                "Network",
                "high",
                0,
            )

    def test_reject_boolean_affected_users(self):
        with self.assertRaises(ValueError):
            validate_ticket(
                "Internet is down",
                "Network",
                "high",
                True,
            )

    def test_standardize_category_and_urgency(self):
        title, category, urgency = validate_ticket(
            "  Internet is down  ",
            " network ",
            " HIGH ",
            5,
        )

        self.assertEqual(title, "Internet is down")
        self.assertEqual(category, "Network")
        self.assertEqual(urgency, "high")


class TestTicketCreation(unittest.TestCase):
    """Tests for creating tickets."""

    def test_create_ticket_with_correct_details(self):
        tickets = []

        ticket = create_ticket(
            tickets,
            "Internet is down",
            "Network",
            "high",
            5,
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Internet is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 5)
        self.assertEqual(ticket["priority"], "high")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_ticket_is_added_to_collection(self):
        tickets = []

        ticket = create_ticket(
            tickets,
            "Computer is broken",
            "Hardware",
            "medium",
            2,
        )

        self.assertEqual(len(tickets), 1)
        self.assertIn(ticket, tickets)

    def test_ticket_ids_increase(self):
        tickets = []

        first_ticket = create_ticket(
            tickets,
            "First problem",
            "Network",
            "low",
            1,
        )

        second_ticket = create_ticket(
            tickets,
            "Second problem",
            "Software",
            "medium",
            3,
        )

        self.assertEqual(first_ticket["id"], "T001")
        self.assertEqual(second_ticket["id"], "T002")

    def test_ticket_id_uses_highest_existing_number(self):
        tickets = [
            {"id": "T001"},
            {"id": "T002"},
            {"id": "T004"},
        ]

        ticket = create_ticket(
            tickets,
            "New network problem",
            "Network",
            "high",
            5,
        )

        self.assertEqual(ticket["id"], "T005")

    def test_ticket_id_starts_at_one_for_empty_collection(self):
        tickets = []

        ticket = create_ticket(
            tickets,
            "New network problem",
            "Network",
            "high",
            5,
        )

        self.assertEqual(ticket["id"], "T001")


if __name__ == "__main__":
    unittest.main()