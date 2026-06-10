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
        part = "".join(part.split())  # whitespace may appear anywhere
        if not part:
            continue
        if part.startswith("-"):
            raise ValueError(f"negative page number in part: {part!r}")
        if "-" in part:
            lo_text, hi_text = part.split("-", 1)
            if hi_text.startswith("-"):
                raise ValueError(f"negative page number in part: {part!r}")
            lo, hi = int(lo_text), int(hi_text)
            if lo > hi:
                raise ValueError(f"reversed range: {part!r}")
            pages.update(range(lo, hi + 1))
        else:
            pages.add(int(part))
    return sorted(pages)
