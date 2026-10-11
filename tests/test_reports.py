"""Tests ticket reports and ticket counts."""

import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import assign_staff, update_status
from campusflow.reports import generate_report


class TestReports(unittest.TestCase):
    """Tests ticket totals, statuses, and priorities."""

    def setUp(self):
        """Create example tickets before each test."""

        self.tickets = []

        # This ticket will have critical priority.
        create_ticket(
            self.tickets,
            "Campus Wi-Fi problem",
            "Network",
            "high",
            15,
        )

        # This ticket will have medium priority.
        create_ticket(
            self.tickets,
            "Broken projector",
            "Hardware",
            "medium",
            4,
        )

        # This ticket will have low priority.
        create_ticket(
            self.tickets,
            "Software problem",
            "Software",
            "low",
            1,
        )

        # Resolve the first ticket.
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")

    def test_total_ticket_count(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["total"], 3)

    def test_status_counts(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_status"],
            {
                "open": 2,
                "in_progress": 0,
                "resolved": 1,
            },
        )

    def test_priority_counts(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_priority"],
            {
                "critical": 1,
                "high": 0,
                "medium": 1,
                "low": 1,
            },
        )

    def test_empty_ticket_report(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)

        self.assertEqual(
            report["by_status"],
            {
                "open": 0,
                "in_progress": 0,
                "resolved": 0,
            },
        )

        self.assertEqual(
            report["by_priority"],
            {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()