"""The shopping basket."""

from pricing import add_vat, line_price, unit_price


class Basket:
    """A shopping basket: items with quantities, in insertion order."""

    def __init__(self):
        self._items = {}

    def add(self, item, quantity=1):
        """Add a quantity of an item; quantities accumulate."""
        unit_price(item)  # validates the item exists
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self._items[item] = self._items.get(item, 0) + quantity

    def remove(self, item):
        """Remove an item entirely from the basket."""
        self._items.pop(item, None)

    def quantity(self, item):
        """Return the quantity of an item currently in the basket."""
        return self._items.get(item, 0)

    def lines(self):
        """Return (item, quantity, line_price_pence) per item, insertion order."""
        return [
            (item, qty, line_price(item, qty))
            for item, qty in self._items.items()
        ]

    def subtotal(self):
        """Total of all lines, before VAT."""
        return sum(price for _, _, price in self.lines())

    def total_with_vat(self):
        """Total of all lines, including VAT."""
        return add_vat(self.subtotal())
