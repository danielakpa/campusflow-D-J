"""Handles staff assignment, ticket status changes, and the unresolved queue."""


def find_ticket(tickets, ticket_id):
    """Find a ticket by its ID or raise an error if it does not exist."""

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    # Do not allow operations on a ticket that does not exist.
    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_staff(tickets, ticket_id, staff_name):
    """Assign a staff member to a ticket."""

    # A staff member's name must be valid text.
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    # Find the ticket before trying to change it.
    ticket = find_ticket(tickets, ticket_id)

    # Resolved tickets must be reopened before they can be modified.
    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before modifying it.")

    # Remove unnecessary spaces around the staff member's name.
    ticket["assigned_to"] = staff_name.strip()

    # Automatically start the ticket when staff is assigned.
    ticket["status"] = "in_progress"

    # Return the updated ticket.
    return ticket


def update_status(tickets, ticket_id, new_status):
    """Change a ticket's status while enforcing workflow rules."""

    valid_statuses = ["open", "in_progress", "resolved"]

    # Standardize the status text.
    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in valid_statuses:
        raise ValueError(
            "Status must be open, in_progress, or resolved."
        )

    # Find the ticket we want to update.
    ticket = find_ticket(tickets, ticket_id)

    current_status = ticket["status"]

    # Do not allow a ticket to move to its existing status.
    if current_status == new_status:
        raise ValueError("The ticket already has this status.")

    # A resolved ticket can only be reopened to open.
    if current_status == "resolved":
        if new_status == "open":
            ticket["status"] = "open"
            return ticket

        raise ValueError("Reopen the ticket before changing its status.")

    # A ticket must have assigned staff before work can begin.
    if new_status == "in_progress":
        if not ticket["assigned_to"]:
            raise ValueError(
                "Assign a staff member before starting the ticket."
            )

        if current_status != "open":
            raise ValueError("Only open tickets can start work.")

    # Only an in-progress ticket can be resolved.
    if new_status == "resolved":
        if current_status != "in_progress":
            raise ValueError(
                "Only in-progress tickets can be resolved."
            )

    # Save the approved status change.
    ticket["status"] = new_status

    return ticket


def get_unresolved_queue(tickets):
    """Return open and in-progress tickets in priority order."""

    # Higher-priority tickets must appear first.
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    # Resolved tickets no longer belong in the work queue.
    unresolved_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] in ["open", "in_progress"]
    ]

    # Sort by priority first, then by numeric ticket ID.
    unresolved_tickets.sort(
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        )
    )

    return unresolved_tickets