"""A small in-memory ledger of transactions."""

import csv
import datetime
import io


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

    def to_csv(self):
        """Return the ledger as a CSV string with a header row.

        Dates are ISO formatted, amounts have exactly two decimal places, and
        descriptions are escaped per standard CSV conventions.
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(["date", "amount", "description"])
        for date, amount, description in self._transactions:
            writer.writerow([date.isoformat(), f"{amount:.2f}", description])
        return buffer.getvalue()
