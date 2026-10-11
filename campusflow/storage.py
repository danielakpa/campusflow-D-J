"""Saves tickets to JSON files and loads saved tickets back."""

import json
from pathlib import Path


def validate_ticket_data(tickets):
    """Check that every ticket has valid fields, types, and values."""

    # The saved data must be a list.
    if not isinstance(tickets, list):
        raise ValueError("Invalid ticket data: expected a JSON list.")

    errors = []

    # Define the fields and their expected Python types.
    required_fields = {
        "id": str,
        "title": str,
        "category": str,
        "urgency": str,
        "affected_users": int,
        "priority": str,
        "status": str,
    }

    # Check every ticket in the list.
    for index, ticket in enumerate(tickets):
        location = f"Ticket at position {index + 1}"

        if not isinstance(ticket, dict):
            errors.append(f"{location}: Expected a ticket object.")
            continue

        # Check required fields and their data types.
        for field, expected_type in required_fields.items():
            if field not in ticket:
                errors.append(f"{location}: Missing '{field}'.")
                continue

            value = ticket[field]

            # Reject True and False for integer fields.
            if expected_type is int:
                valid_type = type(value) is int
            else:
                valid_type = isinstance(value, expected_type)

            if not valid_type:
                errors.append(
                    f"{location}, '{field}': Expected "
                    f"{expected_type.__name__}, received "
                    f"{type(value).__name__}."
                )

        # assigned_to must be a string or None.
        if "assigned_to" not in ticket:
            errors.append(f"{location}: Missing 'assigned_to'.")
        elif (
            ticket["assigned_to"] is not None
            and not isinstance(ticket["assigned_to"], str)
        ):
            errors.append(
                f"{location}, 'assigned_to': "
                "Expected a string or null."
            )

        # Check that text fields are not empty.
        for field in ["id", "title", "category"]:
            value = ticket.get(field)

            if isinstance(value, str) and not value.strip():
                errors.append(f"{location}: '{field}' cannot be empty.")

        # Check allowed urgency values.
        urgency = ticket.get("urgency")
        if isinstance(urgency, str):
            if urgency not in ["low", "medium", "high"]:
                errors.append(f"{location}: Invalid urgency '{urgency}'.")

        # Check allowed priority values.
        priority = ticket.get("priority")
        if isinstance(priority, str):
            if priority not in ["low", "medium", "high", "critical"]:
                errors.append(f"{location}: Invalid priority '{priority}'.")

        # Check allowed ticket statuses.
        status = ticket.get("status")
        if isinstance(status, str):
            if status not in ["open", "in_progress", "resolved"]:
                errors.append(f"{location}: Invalid status '{status}'.")

        # The number of affected users must be positive.
        affected_users = ticket.get("affected_users")
        if type(affected_users) is int and affected_users <= 0:
            errors.append(
                f"{location}: 'affected_users' must be greater than zero."
            )

    # Report all detected problems together.
    if errors:
        raise ValueError(
            "Ticket data validation failed:\n- "
            + "\n- ".join(errors)
        )

    return True


def save_tickets(tickets, file_path):
    """Validate tickets and save them to a JSON file."""

    # Never save invalid ticket data.
    validate_ticket_data(tickets)

    path = Path(file_path)

    # Create the parent directory if it does not exist.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write the validated tickets as readable JSON.
    with path.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)

def repair_ticket_data(tickets):
    """Let a user correct invalid affected_users values interactively."""

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        affected_users = ticket.get("affected_users")

        # Skip values that are already valid positive integers.
        if type(affected_users) is int and affected_users > 0:
            continue

        print(f"\nTicket ID: {ticket.get('id', 'Unknown')}")
        print(f"Invalid affected_users value: {affected_users!r}")

        while True:
            answer = input(
                "Enter a positive whole number for affected users "
                "(or type 'skip' to cancel): "
            ).strip()

            if answer.lower() == "skip":
                print("Repair cancelled. The saved file was not changed.")
                return None

            try:
                corrected_value = int(answer)
            except ValueError:
                print("Error: Enter a valid whole number, such as 5.")
                continue

            if corrected_value <= 0:
                print("Error: The number must be greater than zero.")
                continue

            ticket["affected_users"] = corrected_value
            break

    # Confirm that all ticket data is valid before returning it.
    validate_ticket_data(tickets)

    return tickets

def load_tickets(file_path):
    """Load and validate tickets without modifying the saved file."""
    path = Path(file_path)

    # A missing file means there are no saved tickets yet.
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            content = file.read()

    except OSError:
        raise

    # An empty file starts with an empty ticket list.
    if not content.strip():
        return []

    try:
        tickets = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets: {path} contains invalid JSON."
        ) from error

    # Reject invalid data instead of asking questions during loading.
    validate_ticket_data(tickets)

    return tickets