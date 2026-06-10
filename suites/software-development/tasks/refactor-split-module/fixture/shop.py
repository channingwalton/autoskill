"""Shop: pricing rules, baskets, and receipt formatting (amounts in pence)."""

# --- pricing ---------------------------------------------------------------

PRICES = {
    "apple": 60,
    "banana": 25,
    "milk": 130,
    "bread": 110,
    "cheese": 350,
}

BULK_THRESHOLD = 10
BULK_DISCOUNT_PERCENT = 10
VAT_PERCENT = 20


def unit_price(item):
    """Return the unit price of an item in pence."""
    try:
        return PRICES[item]
    except KeyError:
        raise KeyError(f"unknown item: {item!r}")


def line_price(item, quantity):
    """Price for a quantity of an item, with a bulk discount on 10 or more."""
    if quantity < 0:
        raise ValueError("quantity must not be negative")
    total = unit_price(item) * quantity
    if quantity >= BULK_THRESHOLD:
        total -= total * BULK_DISCOUNT_PERCENT // 100
    return total


def add_vat(amount_pence):
    """Return the amount with VAT added (integer pence, rounded down)."""
    return amount_pence + amount_pence * VAT_PERCENT // 100


# --- basket ----------------------------------------------------------------


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


# --- report ----------------------------------------------------------------


def format_pence(pence):
    """Format integer pence as pounds, e.g. 130 -> '£1.30'."""
    return f"£{pence // 100}.{pence % 100:02d}"


def format_line(item, quantity, price_pence):
    """Format one receipt line."""
    return f"{quantity:>3} x {item:<12}{format_pence(price_pence):>8}"


def format_receipt(basket):
    """Render a basket as a printable receipt."""
    lines = ["RECEIPT"]
    for item, qty, price in basket.lines():
        lines.append(format_line(item, qty, price))
    lines.append("SUBTOTAL " + format_pence(basket.subtotal()))
    lines.append("TOTAL    " + format_pence(basket.total_with_vat()))
    return "\n".join(lines)
