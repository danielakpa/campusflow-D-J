from campusflow.tickets import create_ticket

# Start with an empty collection.
tickets = []

# Create a ticket.
ticket = create_ticket(
    tickets,
    "Campus Wi-Fi is not working",
    "network",
    "high",
    15
)

# Display the created ticket.
print(ticket)