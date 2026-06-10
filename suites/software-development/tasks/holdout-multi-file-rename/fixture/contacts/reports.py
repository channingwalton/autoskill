"""Plain-text reporting over stored customer records."""

from contacts.storage import load_customer


def customer_summary(customer_id):
    """Return a one-line description like ``customer c1: Ada Lovelace``."""
    customer = load_customer(customer_id)
    return f"customer {customer.customer_id}: {customer.name}"
