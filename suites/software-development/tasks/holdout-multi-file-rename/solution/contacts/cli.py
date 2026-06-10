"""Command-line interface for the contacts package."""

import argparse
import json

from contacts.api import create_client, get_client


def build_parser():
    parser = argparse.ArgumentParser(prog="contacts")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--name")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.name:
        record = create_client(args.client_id, args.name)
    else:
        record = get_client(args.client_id)
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
