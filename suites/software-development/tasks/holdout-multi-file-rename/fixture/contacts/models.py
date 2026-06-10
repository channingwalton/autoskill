"""Domain model for the contacts package."""


class Customer:
    """A customer record."""

    def __init__(self, customer_id, name):
        self.customer_id = customer_id
        self.name = name

    def __eq__(self, other):
        return (
            isinstance(other, Customer)
            and self.customer_id == other.customer_id
            and self.name == other.name
        )

    def __repr__(self):
        return f"Customer({self.customer_id!r}, {self.name!r})"
