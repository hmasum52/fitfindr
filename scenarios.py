"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    # Criterion 3 — 5 different matching queries. Check selected_item["id"]
    # against the new_item id in the suggest_outfit trace step.
    {"name": "state: polo shirt", "query": "vintage polo shirt", "wardrobe": "example", "criterion": 3},
    {"name": "state: cargo pants", "query": "cargo pants under $30", "wardrobe": "example", "criterion": 3},
    {"name": "state: chelsea boots", "query": "suede chelsea boots", "wardrobe": "example", "criterion": 3},
    {"name": "state: cardigan", "query": "chunky knit cardigan", "wardrobe": "example", "criterion": 3},
    {"name": "state: linen blazer", "query": "linen blazer under $40", "wardrobe": "example", "criterion": 3},

    # Criterion 4 — 5 different items (distinct top results). Check each fit
    # card mentions its item's price and no two cards are identical.
    {"name": "fit card: flannel", "query": "oversized flannel shirt", "wardrobe": "example", "criterion": 4},
    {"name": "fit card: bomber", "query": "leather bomber jacket", "wardrobe": "example", "criterion": 4},
    {"name": "fit card: denim jacket", "query": "light wash denim jacket", "wardrobe": "example", "criterion": 4},
    {"name": "fit card: mary janes", "query": "platform mary janes", "wardrobe": "example", "criterion": 4},
    {"name": "fit card: tie-dye", "query": "tie-dye long sleeve", "wardrobe": "example", "criterion": 4},

    # Criterion 5 — every returned price must be <= the ceiling (read the
    # search_listings step in the trace). The $38 one sits on listings priced
    # exactly $38, so it checks the ceiling is inclusive.
    {"name": "ceiling: tee $20", "query": "vintage tee under $20", "wardrobe": "example", "criterion": 5},
    {"name": "ceiling: jacket $38", "query": "vintage jacket under $38", "wardrobe": "example", "criterion": 5},
    {"name": "ceiling: denim $30", "query": "denim under $30", "wardrobe": "example", "criterion": 5},
    {"name": "ceiling: streetwear $15", "query": "streetwear under $15", "wardrobe": "example", "criterion": 5},
    {"name": "ceiling: black $25", "query": "black under $25", "wardrobe": "example", "criterion": 5},
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
