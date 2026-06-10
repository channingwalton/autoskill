"""In-memory persistence for customer records, with JSON import/export."""

import json

from contacts.models import Customer

_DB = {}


def save_customer(customer):
    """Store a customer, keyed by its id."""
    _DB[customer.customer_id] = customer


def load_customer(customer_id):
    """Return the stored customer, or raise KeyError if unknown."""
    if customer_id not in _DB:
        raise KeyError(f"unknown id {customer_id!r}")
    return _DB[customer_id]


def dump_db():
    """Serialise every stored record to a JSON array of plain dicts."""
    return json.dumps(
        [
            {"customer_id": customer.customer_id, "name": customer.name}
            for customer in _DB.values()
        ]
    )


def load_db(text):
    """Load records from JSON produced by ``dump_db`` into the store."""
    for record in json.loads(text):
        save_customer(Customer(record["customer_id"], record["name"]))
