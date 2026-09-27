"""Training plan data: 29 weeks from beginner to half marathon."""
from dataclasses import dataclass
from datetime import date, timedelta

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
REST = "Rest"
STR = "Strength 20–30 min"
WALK = "Easy walk 30 min or rest"


@dataclass
class Session:
    id: str        # e.g. "w3d5"
    week: int      # 1-based
    day: int       # 0 = Monday
    text: str
    kind: str      # run | long | str | rest | race
    phase: int


def _kind(text: str) -> str:
    if text.startswith("Half marathon"):
        return "race"
    if text in (REST, WALK) or text.startswith("Rest,"):
        return "rest"
    if text == STR:
        return "str"
    if text.startswith("Long run"):
        return "long"
    return "run"


def _build():
    weeks = []  # list of (phase, focus, [7 texts])

    p1 = [
        ("Run 1 min / walk 2 min, ×8", "Learning the rhythm"),
        ("Run 2 min / walk 2 min, ×6", "Longer running bits"),
        ("Run 3 min / walk 2 min, ×5", "Getting comfortable"),
        ("Run 4 min / walk 1.5 min, ×4", "Shorter walk breaks"),
        ("Run 5 min / walk 1 min, ×4", "20 minutes of running"),
        ("Run 8 min / walk 1 min, ×3", "Longer blocks"),
        ("Run 12 min / walk 1 min, ×2", "Almost continuous"),
        ("Run 20 min continuous", "First non-stop runs"),
        ("Run 25–30 min continuous", "You can run 5 km"),
    ]
    for r, f in p1:
        weeks.append((1, f, [REST, r, STR, r, REST, r, WALK]))

    p2 = [(4, 4, 5, ""), (4, 4, 6, ""), (5, 4, 6, ""), (5, 5, 7, ""),
          (4, 4, 5, "Recovery week"), (5, 5, 8, ""), (6, 5, 9, ""), (6, 5, 10, "First 10 km")]
    for a, b, c, f in p2:
        weeks.append((2, f or f"Long run {c} km",
                      [REST, f"Easy run {a} km", STR, f"Easy run {b} km", REST, f"Long run {c} km", WALK]))

    p3 = [
        (6, "Easy 5 km + strides", 4, 10, ""), (6, "Easy 6 km + strides", 4, 11, ""),
        (6, "6 km incl. 2 km tempo", 4, 12, ""), (5, "Easy 5 km", 3, 8, "Recovery week"),
        (7, "6 km incl. 3 km tempo", 4, 13, ""), (7, "Easy 7 km + strides", 5, 14, ""),
        (7, "7 km incl. 4 km tempo", 5, 16, ""), (5, "Easy 5 km", 4, 10, "Recovery week"),
        (8, "7 km incl. 4 km tempo", 5, 17, ""), (8, "8 km incl. 5 km tempo", 5, 18, "Peak week"),
        (6, "6 km incl. 3 km tempo", 4, 12, "Taper: less volume"),
    ]
    for a, b, c, d, f in p3:
        weeks.append((3, f or f"Long run {d} km",
                      [REST, f"Easy run {a} km", STR, b, f"Easy run {c} km", f"Long run {d} km", REST]))
    weeks.append((3, "Race week", [REST, "Easy run 5 km", "Easy run 3 km + strides", REST,
                                   "Easy jog 2 km (optional)", "Rest, lay out kit, eat normally",
                                   "Half marathon race, 21.1 km"]))
    return weeks


WEEKS = _build()  # [(phase, focus, [texts])]
SESSIONS = [
    Session(f"w{w}d{d}", w, d, t, _kind(t), ph)
    for w, (ph, _, texts) in enumerate(WEEKS, start=1)
    for d, t in enumerate(texts)
]
TOTAL_WEEKS = len(WEEKS)

PHASES = {
    1: ("Phase 1: Run-walk to 5 km", "Weeks 1–9. Three sessions a week, measured in minutes."),
    2: ("Phase 2: 5 km to 10 km", "Weeks 10–17. Three runs a week, measured in kilometres."),
    3: ("Phase 3: 10 km to half marathon", "Weeks 18–29. Four runs a week, with one quality session."),
}


def in_break(d: date, breaks) -> bool:
    """breaks: list of (break_start, resume_date); days from break_start up to the day before resume."""
    return any(b0 <= d < b1 for b0, b1 in breaks)


def schedule(start: date, breaks=()) -> dict:
    """Map session id -> date, laying sessions on consecutive days and skipping break days."""
    out, d = {}, start
    for s in SESSIONS:
        while in_break(d, breaks):
            d += timedelta(days=1)
        out[s.id] = d
        d += timedelta(days=1)
    return out


def by_date(start: date, breaks=()) -> dict:
    sched = schedule(start, breaks)
    lookup = {s.id: s for s in SESSIONS}
    return {d: lookup[sid] for sid, d in sched.items()}


def race_day(start: date, breaks=()) -> date:
    return schedule(start, breaks)[SESSIONS[-1].id]


def months_in_plan(start: date, breaks=()):
    """List of (year, month) the plan touches."""
    end = race_day(start, breaks)
    y, m, out = start.year, start.month, []
    while (y, m) <= (end.year, end.month):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out
