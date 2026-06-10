"""Parse page-range specs like "1-5", "3", or "1-3,7" into lists of ints."""


def parse_range(spec):
    """Parse a range spec into a sorted list of unique page numbers.

    Examples:
        "3"      -> [3]
        "1-3"    -> [1, 2, 3]
        "1-3,7"  -> [1, 2, 3, 7]

    Contract:
        - Ranges are inclusive at both ends: "1-3" contains 3, and "4-4"
          is the single page [4].
        - Whitespace may appear anywhere and is ignored:
          " 1 - 3 , 7 " parses the same as "1-3,7".
        - Empty parts are ignored: "1,,3" -> [1, 3], "1-3," -> [1, 2, 3],
          and "" -> [].
        - Page numbers are non-negative; 0 is a valid page. Any negative
          number anywhere in the spec raises ValueError.
        - A reversed range such as "5-3" raises ValueError, and the error
          message must contain the offending part (e.g. the text "5-3").
        - Duplicate pages collapse: "1-3,2,3" -> [1, 2, 3].
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
