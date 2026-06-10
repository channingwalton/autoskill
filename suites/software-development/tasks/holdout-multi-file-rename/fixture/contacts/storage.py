"""In-memory persistence for customer records."""

_DB = {}


def save_customer(customer):
    """Store a customer, keyed by its id."""
    _DB[customer.customer_id] = customer


def load_customer(customer_id):
    """Return the stored customer, or raise KeyError if unknown."""
    if customer_id not in _DB:
        raise KeyError(f"unknown id {customer_id!r}")
    return _DB[customer_id]
