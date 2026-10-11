"""Generates reports about ticket totals, statuses, and priorities."""


def generate_report(tickets):
    """Count tickets by status and priority."""

    # Start every status count at zero.
    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }

    # Start every priority count at zero.
    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    # Examine each ticket and count its status and priority.
    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1

    # Collect the results into one dictionary.
    report = {
        "total": len(tickets),
        "by_status": status_counts,
        "by_priority": priority_counts,
    }

    return report