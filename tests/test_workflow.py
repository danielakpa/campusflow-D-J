"""Tests staff assignment, ticket workflow, and unresolved queue."""

import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_staff,
    update_status,
    get_unresolved_queue,
)


class TestTicketAssignment(unittest.TestCase):
    """Tests assigning staff to tickets."""

    def setUp(self):
        """Create a fresh ticket collection for each test."""

        self.tickets = []

        create_ticket(
            self.tickets,
            "Campus Wi-Fi problem",
            "Network",
            "high",
            15,
        )

    def test_assign_staff(self):
        ticket = assign_staff(self.tickets, "T001", "Ada")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_reject_empty_staff_name(self):
        with self.assertRaises(ValueError):
            assign_staff(self.tickets, "T001", " ")

    def test_reject_unknown_ticket(self):
        with self.assertRaises(ValueError):
            assign_staff(self.tickets, "T999", "Ada")


class TestTicketStatus(unittest.TestCase):
    """Tests allowed and rejected ticket status changes."""

    def setUp(self):
        self.tickets = []

        create_ticket(
            self.tickets,
            "Projector is not working",
            "Hardware",
            "medium",
            4,
        )

    def test_assigning_staff_automatically_starts_work(self):
        ticket = assign_staff(self.tickets, "T001", "Ada")

        self.assertEqual(ticket["assigned_to"], "Ada")
        self.assertEqual(ticket["status"], "in_progress")

    def test_in_progress_ticket_can_be_resolved(self):
        assign_staff(self.tickets, "T001", "Ada")

        ticket = update_status(self.tickets, "T001", "resolved")

        self.assertEqual(ticket["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")

        ticket = update_status(self.tickets, "T001", "open")

        self.assertEqual(ticket["status"], "open")

    def test_resolved_ticket_cannot_be_assigned(self):
        assign_staff(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "resolved")

        with self.assertRaises(ValueError):
            assign_staff(self.tickets, "T001", "John")

    def test_cannot_resolve_open_ticket_directly(self):
        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "resolved")


class TestUnresolvedQueue(unittest.TestCase):
    """Tests filtering and ordering the unresolved queue."""

    def test_queue_orders_by_priority_and_excludes_resolved(self):
        tickets = []

        create_ticket(
            tickets, "Medium issue", "Hardware", "medium", 2
        )
        create_ticket(
            tickets, "Critical issue", "Network", "high", 10
        )
        create_ticket(
            tickets, "High issue", "Software", "high", 2
        )
        create_ticket(
            tickets, "Low issue", "Other", "low", 1
        )

        # Resolved tickets should not appear in the queue.
        assign_staff(tickets, "T001", "Ada")
        update_status(tickets, "T001", "resolved")

        queue = get_unresolved_queue(tickets)

        self.assertEqual(
             [ticket["id"] for ticket in queue],
             ["T002", "T003", "T004"],
            )

    def test_empty_queue(self):
        self.assertEqual(get_unresolved_queue([]), [])


if __name__ == "__main__":
    unittest.main()