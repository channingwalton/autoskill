"""Plain-text reporting over stored client records."""

from contacts.storage import load_client


def client_summary(client_id):
    """Return a one-line description like ``client c1: Ada Lovelace``."""
    client = load_client(client_id)
    return f"client {client.client_id}: {client.name}"


# Deprecated alias.
customer_summary = client_summary
