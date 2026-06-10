import unittest

from contacts.api import create_client, get_client
from contacts.cli import build_parser
from contacts.models import Client
from contacts.storage import load_client, save_client


class TestContacts(unittest.TestCase):
    def test_client_model(self):
        client = Client("c1", "Ada Lovelace")
        self.assertEqual(client.client_id, "c1")
        self.assertEqual(client.name, "Ada Lovelace")

    def test_storage_round_trip(self):
        client = Client("c2", "Grace Hopper")
        save_client(client)
        self.assertEqual(load_client("c2"), client)

    def test_api_uses_client_id_key(self):
        create_client("c3", "Mary Somerville")
        self.assertEqual(
            get_client("c3"), {"client_id": "c3", "name": "Mary Somerville"}
        )

    def test_cli_flag(self):
        args = build_parser().parse_args(["--client-id", "c4", "--name", "Edith Clarke"])
        self.assertEqual(args.client_id, "c4")


if __name__ == "__main__":
    unittest.main()
