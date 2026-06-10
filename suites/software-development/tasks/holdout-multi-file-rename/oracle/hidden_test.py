"""Hidden oracle tests. Never copied into the trial sandbox."""

import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TOTAL_FALLBACK = 15

try:
    from contacts import api, cli, models, reports, storage
    from contacts.api import create_client, get_client
    from contacts.cli import build_parser, main
    from contacts.models import Client
    from contacts.storage import dump_db, load_client, load_db, save_client
    IMPORT_ERROR = None
except Exception as exc:  # broken package still yields a score
    IMPORT_ERROR = exc


class HiddenTests(unittest.TestCase):
    def test_client_model_renamed_attribute(self):
        client = Client("h1", "Ada Lovelace")
        self.assertEqual(client.client_id, "h1")
        self.assertEqual(client.name, "Ada Lovelace")

    def test_storage_round_trip_new_names(self):
        client = Client("h2", "Grace Hopper")
        save_client(client)
        self.assertEqual(load_client("h2"), client)

    def test_api_dict_uses_client_id_key_only(self):
        record = create_client("h3", "Mary Somerville")
        self.assertEqual(record, {"client_id": "h3", "name": "Mary Somerville"})
        self.assertNotIn("customer_id", get_client("h3"))

    def test_cli_new_flag(self):
        args = build_parser().parse_args(["--client-id", "h4"])
        self.assertEqual(args.client_id, "h4")

    def test_old_names_alias_same_objects(self):
        self.assertIs(models.Customer, models.Client)
        self.assertIs(storage.save_customer, storage.save_client)
        self.assertIs(storage.load_customer, storage.load_client)
        self.assertIs(api.create_customer, api.create_client)
        self.assertIs(api.get_customer, api.get_client)

    def test_old_api_names_still_work(self):
        api.create_customer("h5", "Edith Clarke")
        self.assertEqual(
            api.get_customer("h5"), {"client_id": "h5", "name": "Edith Clarke"}
        )

    def test_load_client_unknown_id_raises_keyerror(self):
        with self.assertRaises(KeyError):
            load_client("h-missing")

    def test_cli_main_end_to_end(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["--client-id", "h6", "--name", "Mary Anning"])
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out.getvalue()), {"client_id": "h6", "name": "Mary Anning"}
        )

    # --- hardened requirements -------------------------------------------

    def test_dump_db_writes_client_id_key(self):
        save_client(Client("h7", "Katherine Johnson"))
        records = json.loads(dump_db())
        self.assertTrue(any(r.get("client_id") == "h7" for r in records))
        for record in records:
            self.assertIn("client_id", record)
            self.assertNotIn("customer_id", record)

    def test_load_db_accepts_legacy_customer_id_records(self):
        legacy = json.dumps([{"customer_id": "h8", "name": "Dorothy Vaughan"}])
        load_db(legacy)
        self.assertEqual(load_client("h8"), Client("h8", "Dorothy Vaughan"))

    def test_load_db_accepts_mixed_old_and_new_records(self):
        mixed = json.dumps(
            [
                {"customer_id": "h9", "name": "Annie Easley"},
                {"client_id": "h10", "name": "Margaret Hamilton"},
            ]
        )
        load_db(mixed)
        self.assertEqual(load_client("h9"), Client("h9", "Annie Easley"))
        self.assertEqual(load_client("h10"), Client("h10", "Margaret Hamilton"))

    def test_dump_then_load_round_trip(self):
        save_client(Client("h11", "Radia Perlman"))
        snapshot = dump_db()
        load_db(snapshot)
        self.assertEqual(load_client("h11"), Client("h11", "Radia Perlman"))

    def test_reports_module_renamed(self):
        save_client(Client("h12", "Hedy Lamarr"))
        self.assertEqual(
            reports.client_summary("h12"), "client h12: Hedy Lamarr"
        )

    def test_reports_old_alias_same_object(self):
        self.assertIs(reports.customer_summary, reports.client_summary)

    def test_cli_help_text_uses_client_wording(self):
        help_text = build_parser().format_help()
        self.assertIn("--client-id", help_text)
        self.assertNotIn("customer", help_text.lower())


def run_suite():
    if IMPORT_ERROR is not None:
        print(json.dumps({"passed": 0, "total": TOTAL_FALLBACK}))
        return
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HiddenTests)
    with open(os.devnull, "w") as devnull:
        result = unittest.TextTestRunner(verbosity=0, stream=devnull).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(json.dumps({"passed": passed, "total": total}))


if __name__ == "__main__":
    run_suite()
