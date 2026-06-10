"""Domain model for the contacts package."""


class Client:
    """A client record."""

    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name

    def __eq__(self, other):
        return (
            isinstance(other, Client)
            and self.client_id == other.client_id
            and self.name == other.name
        )

    def __repr__(self):
        return f"Client({self.client_id!r}, {self.name!r})"


# Deprecated alias.
Customer = Client
