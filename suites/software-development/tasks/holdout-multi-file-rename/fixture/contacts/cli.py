"""Command-line interface for the contacts package."""

import argparse
import json

from contacts.api import create_customer, get_customer


def build_parser():
    parser = argparse.ArgumentParser(
        prog="contacts",
        description="Look up and create customer records.",
    )
    parser.add_argument(
        "--customer-id",
        required=True,
        help="id of the customer to look up or create",
    )
    parser.add_argument(
        "--name",
        help="if given, create a customer with this name",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.name:
        record = create_customer(args.customer_id, args.name)
    else:
        record = get_customer(args.customer_id)
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
