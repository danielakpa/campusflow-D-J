"""Saves tickets to JSON files and loads saved tickets back."""

import json
from pathlib import Path


def save_tickets(tickets, file_path):
    """Save tickets to a JSON file."""

    # Convert the file path into a Path object.
    path = Path(file_path)

    # Create the parent directory if it does not exist.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write the tickets as readable JSON.
    with path.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4)


def load_tickets(file_path):
    """Load tickets from JSON or return an empty list if missing."""

    path = Path(file_path)

    # A missing file means the application has no saved tickets yet.
    if not path.exists():
        return []

    try:
        # Open the file and convert its JSON into Python data.
        with path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)

    except json.JSONDecodeError as error:
        # Do not silently replace a malformed file with empty data.
        raise ValueError(
            f"Cannot load tickets: {path} contains invalid JSON."
        ) from error

    # Make sure the top-level JSON value is a list.
    if not isinstance(tickets, list):
        raise ValueError("Invalid ticket data: expected a JSON list.")

    # Return the loaded tickets.
    return tickets