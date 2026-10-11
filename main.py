"""Main entry point for the CampusFlow helpdesk application."""

from pathlib import Path

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_staff,
    get_unresolved_queue,
    update_status,
)
from campusflow.reports import generate_report
from campusflow.storage import load_tickets, save_tickets


# Store tickets in the data folder inside the project.
DATA_FILE = Path(__file__).parent / "data" / "tickets.json"


def display_ticket(ticket):
    """Display the important information about one ticket."""

    print("-" * 40)
    print(f"Ticket ID:      {ticket['id']}")
    print(f"Title:          {ticket['title']}")
    print(f"Category:       {ticket['category']}")
    print(f"Urgency:        {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority:       {ticket['priority']}")
    print(f"Status:         {ticket['status']}")
    print(f"Assigned to:    {ticket['assigned_to'] or 'Not assigned'}")
    print("-" * 40)

def create_new_ticket(tickets):
    """Create a ticket and keep asking until each input is valid."""

    # Ask for the title.
    while True:
        title = input("\nEnter ticket title: ").strip()

        if title:
            break

        print("Error: Ticket title cannot be empty. Please try again.")

    # Let the user select a category.
    category_options = {
        "1": "Network",
        "2": "Hardware",
        "3": "Software",
        "4": "Other",
    }

    while True:
        print("\nChoose a category:")
        print("1. Network")
        print("2. Hardware")
        print("3. Software")
        print("4. Other")

        category_choice = input("Enter your choice (1-4): ").strip()

        if category_choice in category_options:
            category = category_options[category_choice]

            # If the user selects Other, ask for a custom category.
            if category == "Other":
                while True:
                    custom_category = input(
                        "Enter your category: "
                    ).strip()

                    if custom_category:
                        category = custom_category
                        break

                    print(
                        "Error: Category cannot be empty. "
                        "Please try again."
                    )

            break

        print(
            "Error: Invalid category. "
            "Please choose an option from 1 to 4."
        )

    # Let the user select a valid urgency.
    urgency_options = {
        "1": "low",
        "2": "medium",
        "3": "high",
    }

    while True:
        print("\nChoose urgency:")
        print("1. Low")
        print("2. Medium")
        print("3. High")

        urgency_choice = input("Enter your choice (1-3): ").strip()

        if urgency_choice in urgency_options:
            urgency = urgency_options[urgency_choice]
            break

        print("Error: Invalid urgency. Please choose an option from 1 to 3.")

    # Keep asking until the user enters a positive whole number.
    while True:
        affected_users_input = input(
            "\nEnter the number of affected users: "
        ).strip()

        try:
            affected_users = int(affected_users_input)

            if affected_users > 0:
                break

            print("Error: The number of affected users must be greater than zero.")

        except ValueError:
            print("Error: Please enter a valid whole number, such as 5.")

    # Create the ticket after all inputs are valid.
    try:
        ticket = create_ticket(
            tickets,
            title,
            category,
            urgency,
            affected_users,
        )

        save_tickets(tickets, DATA_FILE)

        print(f"\nTicket {ticket['id']} created successfully!")
        display_ticket(ticket)

    except ValueError as error:
        print(f"\nError creating ticket: {error}")


def list_tickets(tickets):
    """Display all tickets."""

    if not tickets:
        print("\nNo tickets found.")
        return

    print("\nALL TICKETS")

    for ticket in tickets:
        display_ticket(ticket)

def assign_ticket_to_staff(tickets):
    """Show tickets by priority and let the administrator assign staff."""

    if not tickets:
        print("\nThere are no tickets to assign.")
        return

    # Arrange tickets from highest to lowest priority.
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    sorted_tickets = sorted(
        tickets,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )

    print("\n========== ASSIGN STAFF ==========")
    print("Tickets are arranged from highest to lowest priority.")

    # Display all tickets so the administrator can choose quickly.
    for ticket in sorted_tickets:
        print(
            f"\nID: {ticket['id']} | "
            f"Priority: {ticket['priority'].upper()} | "
            f"Status: {ticket['status']}"
        )
        print(f"Title: {ticket['title']}")
        print(f"Category: {ticket['category']}")
        print(f"Affected users: {ticket['affected_users']}")
        print(f"Assigned to: {ticket['assigned_to'] or 'Not assigned'}")

    # Keep asking until the administrator selects a valid ticket.
    while True:
        ticket_id = input(
            "\nEnter ticket ID to assign staff (or 0 to cancel): "
        ).strip()

        # Allow the administrator to cancel.
        if ticket_id == "0":
            print("Staff assignment cancelled.")
            return

        # Convert the input to uppercase so t001 and T001 both work.
        ticket_id = ticket_id.upper()

        # Find the selected ticket without considering letter case.
        # Find the selected ticket without considering letter case.
        selected_ticket = next(
            (
                ticket
                for ticket in tickets
                if ticket["id"].upper() == ticket_id
            ),
            None,
        )

        # If the ID does not exist, display available tickets again.
        if selected_ticket is None:
            print(
                "\nError: Ticket ID not found. "
                "Please select an available ticket."
            )

            print("\nAVAILABLE TICKETS")

            for ticket in sorted_tickets:
                print(
                    f"\nID: {ticket['id']} | "
                    f"Priority: {ticket['priority'].upper()} | "
                    f"Status: {ticket['status']}"
                )
                print(f"Title: {ticket['title']}")
                print(f"Affected users: {ticket['affected_users']}")
                print(
                    f"Assigned to: "
                    f"{ticket['assigned_to'] or 'Not assigned'}"
                )

            continue

        # Resolved tickets cannot be assigned until reopened.
        if selected_ticket["status"] == "resolved":
            print(
                "Error: This ticket is resolved. "
                "Reopen it before assigning staff."
            )
            continue

        # A valid, assignable ticket has been selected.
        break

    # Keep asking until a staff name is entered.
    while True:
        staff_name = input(
            "Enter the staff member's name (or 0 to cancel): "
        ).strip()

        if staff_name == "0":
            print("Staff assignment cancelled.")
            return

        if staff_name:
            break

        print("Error: Staff name cannot be empty. Please try again.")

    # Assign the staff member and save the changes.
    try:
        ticket = assign_staff(
            tickets,
            selected_ticket["id"],
            staff_name,
        )

        save_tickets(tickets, DATA_FILE)

        print(
            f"\nTicket {ticket['id']} successfully assigned "
            f"to {ticket['assigned_to']}."
        )

    except ValueError as error:
        print(f"Error: {error}")


def change_ticket_status(tickets):
    """Let the administrator select a ticket and update its status."""

    if not tickets:
        print("\nThere are no tickets available to update.")
        return

    # Arrange tickets by priority to make selection easier.
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    sorted_tickets = sorted(
        tickets,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )

    # Display tickets in priority order.
    print("\n========== UPDATE TICKET STATUS ==========")

    for ticket in sorted_tickets:
        print(
            f"\nID: {ticket['id']} | "
            f"Priority: {ticket['priority'].upper()} | "
            f"Status: {ticket['status']}"
        )
        print(f"Title: {ticket['title']}")
        print(f"Affected users: {ticket['affected_users']}")
        print(f"Assigned to: {ticket['assigned_to'] or 'Not assigned'}")

    # Keep asking until the administrator selects a valid ticket.
    while True:
        ticket_id = input(
            "\nEnter ticket ID to update (or 0 to cancel): "
        ).strip()

        if ticket_id == "0":
            print("Status update cancelled.")
            return

        # Allow lowercase or uppercase ticket IDs.
        ticket_id = ticket_id.upper()

        # Find the ticket without considering letter case.
        selected_ticket = next(
            (
                ticket
                for ticket in tickets
                if ticket["id"].upper() == ticket_id
            ),
            None,
        )

        # If the ticket does not exist, display available tickets again.
        if selected_ticket is None:
            print(
                "\nError: Ticket ID not found. "
                "Please select an available ticket."
            )

            print("\nAVAILABLE TICKETS")

            for ticket in sorted_tickets:
                print(
                    f"\nID: {ticket['id']} | "
                    f"Priority: {ticket['priority'].upper()} | "
                    f"Status: {ticket['status']}"
                )
                print(f"Title: {ticket['title']}")
                print(f"Affected users: {ticket['affected_users']}")
                print(
                    f"Assigned to: "
                    f"{ticket['assigned_to'] or 'Not assigned'}"
                )

            continue

        # A valid ticket has been selected.
        break



       # Show status options based on the ticket's current status.
    if selected_ticket["status"] == "resolved":
        status_options = {
            "1": "open",
        }

    elif selected_ticket["status"] == "in_progress":
        status_options = {
            "1": "resolved",
        }

    else:
        status_options = {}

    # Do not offer status changes for unassigned open tickets.
    if selected_ticket["status"] == "open":
        if not selected_ticket["assigned_to"]:
            print("\nThis ticket has not been assigned to staff yet.")
            print("Assign a staff member first to start working on it.")
            return

        # An open ticket that already has an assignee can be started.
        status_options = {
            "1": "in_progress",
        }

    # Display the available status choices.
    while True:
        print("\nChoose the new status:")

        for number, status in status_options.items():
            print(f"{number}. {status.replace('_', ' ').title()}")

        print("0. Cancel")

        status_choice = input("Enter your choice: ").strip()

        if status_choice == "0":
            print("Status update cancelled.")
            return

        if status_choice not in status_options:
            print("Error: Invalid choice. Please try again.")
            continue

        new_status = status_options[status_choice]

        # Apply the status change and enforce workflow rules.
        try:
            ticket = update_status(
                tickets,
                selected_ticket["id"],
                new_status,
            )

            # Save only after the status update succeeds.
            save_tickets(tickets, DATA_FILE)

            print(
                f"\nTicket {ticket['id']} status updated successfully "
                f"to {ticket['status']}."
            )
            return

        except ValueError as error:
            print(f"\nError: {error}")
            print("Please choose a valid status for this ticket.")

def show_unresolved_queue(tickets):
    """Display unresolved tickets in priority order."""

    queue = get_unresolved_queue(tickets)

    if not queue:
        print("\nThere are no unresolved tickets.")
        return

    print("\nUNRESOLVED TICKET QUEUE")
    print("Tickets are ordered by priority.")

    for ticket in queue:
        display_ticket(ticket)


def show_reports(tickets):
    """Display ticket totals, status counts, and priority counts."""

    report = generate_report(tickets)

    print("\nCAMPUSFLOW REPORT")
    print("=" * 30)

    print(f"Total tickets: {report['total']}")

    print("\nTickets by status:")

    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")

    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")

    print("=" * 30)


def show_menu():
    """Display the main menu."""

    print("\n========== CAMPUSFLOW ==========")
    print("1. Create a ticket")
    print("2. List all tickets")
    print("3. Assign staff")
    print("4. Update ticket status")
    print("5. View unresolved queue")
    print("6. View reports")
    print("7. Exit")
    print("================================")


def main():
    """Load saved tickets and run the application menu."""

    try:
        tickets = load_tickets(DATA_FILE)
    except (ValueError, OSError) as error:
        # Stop if saved data cannot be loaded.
        # This prevents malformed data from being overwritten.
        print(f"Could not load tickets: {error}")
        print("Please check the saved data before restarting CampusFlow.")
        return

    print("Welcome to CampusFlow!")

    while True:
        show_menu()
        choice = input("Choose an option (1-7): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)

            elif choice == "2":
                list_tickets(tickets)

            elif choice == "3":
                assign_ticket_to_staff(tickets)

            elif choice == "4":
                change_ticket_status(tickets)

            elif choice == "5":
                show_unresolved_queue(tickets)

            elif choice == "6":
                show_reports(tickets)

            elif choice == "7":
                print("Thank you for using CampusFlow!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 7.")

        except ValueError as error:
            # Display validation and workflow errors without crashing.
            print(f"\nError: {error}")

        except OSError as error:
            # Display file-saving errors.
            print(f"\nFile error: {error}")


if __name__ == "__main__":
    main()