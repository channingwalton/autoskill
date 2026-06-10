"""In-memory persistence for client records, with JSON import/export."""

import json

from contacts.models import Client

_DB = {}


def save_client(client):
    """Store a client, keyed by its id."""
    _DB[client.client_id] = client


def load_client(client_id):
    """Return the stored client, or raise KeyError if unknown."""
    if client_id not in _DB:
        raise KeyError(f"unknown id {client_id!r}")
    return _DB[client_id]


def dump_db():
    """Serialise every stored record to a JSON array of plain dicts."""
    return json.dumps(
        [
            {"client_id": client.client_id, "name": client.name}
            for client in _DB.values()
        ]
    )


def load_db(text):
    """Load records from JSON produced by ``dump_db`` into the store.

    Records written by older releases use a ``customer_id`` key; they are
    still accepted.
    """
    for record in json.loads(text):
        if "client_id" in record:
            client_id = record["client_id"]
        else:
            client_id = record["customer_id"]
        save_client(Client(client_id, record["name"]))


# Deprecated aliases.
save_customer = save_client
load_customer = load_client
