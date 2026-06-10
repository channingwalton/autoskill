"""In-memory persistence for client records."""

_DB = {}


def save_client(client):
    """Store a client, keyed by its id."""
    _DB[client.client_id] = client


def load_client(client_id):
    """Return the stored client, or raise KeyError if unknown."""
    if client_id not in _DB:
        raise KeyError(f"unknown id {client_id!r}")
    return _DB[client_id]


# Deprecated aliases.
save_customer = save_client
load_customer = load_client
