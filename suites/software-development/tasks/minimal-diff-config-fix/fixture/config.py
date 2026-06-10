r"""Minimal line-oriented config parser.

Shared module -- under change control. Keep edits small and focused.

Format:
    key = value          # trailing comment
Blank lines (including whitespace-only lines) and lines whose first
non-blank character is '#' are skipped; whitespace around keys and
values is trimmed.

Values may be double-quoted. Inside a double-quoted value, spaces and
'#' characters are preserved ('#' may even be the first character of
the value) and type coercion is suppressed. A backslash immediately
before a double quote escapes it: \" yields a literal quote and the
backslash is dropped; no other escape sequences are recognised. A
trailing '#' comment may follow the closing quote.
"""


def parse(text):
    """Parse config text into a dict of coerced values."""
    result = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = _strip_comment(line)
        if "=" not in line:
            raise ValueError("line %d: expected key = value" % lineno)
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("line %d: empty key" % lineno)
        result[key] = _coerce(value)
    return result


def _strip_comment(line):
    # A '#' outside quotes starts a trailing comment.
    idx = line.find("#")
    if idx >= 0:
        return line[:idx]
    return line


def _coerce(value):
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
