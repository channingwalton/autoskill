#!/usr/bin/env bash
# Oracle: run hidden tests against the trial work dir. Prints {"passed": n, "total": m}.
set -u
WORK="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT
cp -R "$WORK/." "$SCRATCH/"
cp "$HERE/hidden_test.py" "$SCRATCH/__hidden_oracle.py"
cd "$SCRATCH"
exec python3 __hidden_oracle.py
