"""Creates tickets, validates ticket information, and calculates priority."""


def calculate_priority(urgency, affected_users):
    """Calculate a ticket's priority using the CampusFlow rules."""

    # Critical: high urgency and at least 10 affected users.
    if urgency == "high" and affected_users >= 10:
        return "critical"

    # High: high urgency or at least 10 affected users.
    if urgency == "high" or affected_users >= 10:
        return "high"

    # Medium: medium urgency or at least 3 affected users.
    if urgency == "medium" or affected_users >= 3:
        return "medium"

    # All other valid tickets have low priority.
    return "low"


def validate_ticket(title, category, urgency, affected_users):
    """Validate ticket details and standardize category and urgency."""

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title cannot be empty.")

    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    category = category.strip().lower()

    # Standard categories are accepted directly.
    valid_categories = ["Network", "Hardware", "Software", "Other"]

    # Remove unnecessary spaces and standardize the category.
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category cannot be empty.")

    category = category.strip()

    # Standard categories should use consistent capitalization.
    for valid_category in valid_categories:
        if category.lower() == valid_category.lower():
            category = valid_category
            break

    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    urgency = urgency.strip().lower()

    if urgency not in ["low", "medium", "high"]:
        raise ValueError("Urgency must be low, medium, or high.")

    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a whole number.")

    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero.")

    return title.strip(), category.title(), urgency


def generate_ticket_id(tickets):
    """Generate an ID greater than every existing valid ticket ID."""

    highest_number = 0

    # Examine the IDs already stored in the ticket collection.
    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        # Accept IDs such as T001, T002, and T125.
        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            number = int(ticket_id[1:])

            # Remember the largest ticket number found so far.
            if number > highest_number:
                highest_number = number

    # Generate the next ID after the highest existing number.
    return f"T{highest_number + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate details, calculate priority, and add a new ticket."""

    title, category, urgency = validate_ticket(
        title,
        category,
        urgency,
        affected_users,
    )

    # Generate an ID based on existing IDs, not the number of tickets.
    ticket_id = generate_ticket_id(tickets)

    priority = calculate_priority(urgency, affected_users)

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    # Store the new ticket in the collection.
    tickets.append(ticket)

    return ticket