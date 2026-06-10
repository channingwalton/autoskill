"""Dict-based API over the storage layer."""

from contacts.models import Client
from contacts.storage import load_client, save_client


def create_client(client_id, name):
    """Create and store a client, returning it as a dict."""
    client = Client(client_id, name)
    save_client(client)
    return _to_dict(client)


def get_client(client_id):
    """Return a stored client as a dict."""
    return _to_dict(load_client(client_id))


def _to_dict(client):
    return {"client_id": client.client_id, "name": client.name}


# Deprecated aliases.
create_customer = create_client
get_customer = get_client
