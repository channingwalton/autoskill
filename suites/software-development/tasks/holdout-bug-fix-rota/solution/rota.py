"""Build a weekday rota, assigning people to days in fair rotation."""


def build_rota(people, days, unavailable=None):
    """Assign one person to each day, rotating fairly through ``people``.

    The rotation pointer starts at the first person. For each day the next
    available person is assigned, scanning forward from the pointer and
    wrapping around, and the pointer then moves to the person *after* the
    one who was assigned. A person is skipped on any day listed for them in
    ``unavailable`` (a mapping of name -> collection of days).

    Returns a dict mapping each day to the assigned person.
    Raises ValueError if nobody is available on a given day.
    """
    if unavailable is None:
        unavailable = {}
    rota = {}
    pointer = 0
    for day in days:
        assigned = None
        for offset in range(len(people)):
            idx = (pointer + offset) % len(people)
            person = people[idx]
            if day in unavailable.get(person, ()):
                continue
            assigned = person
            pointer = (idx + 1) % len(people)
            break
        if assigned is None:
            raise ValueError(f"no one is available on {day}")
        rota[day] = assigned
    return rota
