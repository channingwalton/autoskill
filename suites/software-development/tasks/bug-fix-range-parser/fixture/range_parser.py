"""Parse page-range specs like "1-5", "3", or "1-3,7" into lists of ints."""


def parse_range(spec):
    """Parse a range spec into a sorted list of unique page numbers.

    Examples:
        "3"      -> [3]
        "1-3"    -> [1, 2, 3]
        "1-3,7"  -> [1, 2, 3, 7]
    """
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            pages.update(range(int(lo), int(hi)))
        else:
            pages.add(int(part))
    return sorted(pages)
