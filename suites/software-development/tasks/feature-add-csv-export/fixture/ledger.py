"""A small in-memory ledger of transactions."""

import datetime


class Ledger:
    """Records transactions; each has a date, an amount, and a description."""

    def __init__(self):
        self._transactions = []

    def add(self, date, amount, description):
        """Record a transaction.

        date must be a datetime.date; amount is in pounds; description is free text.
        """
        if not isinstance(date, datetime.date):
            raise TypeError("date must be a datetime.date")
        self._transactions.append((date, float(amount), str(description)))

    def transactions(self):
        """Return all transactions in insertion order as (date, amount, description)."""
        return list(self._transactions)

    def balance(self):
        """Return the sum of all transaction amounts."""
        return sum(amount for _, amount, _ in self._transactions)
