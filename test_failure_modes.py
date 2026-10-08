"""
# Unit 4, Milestone 2 — Regression tests for failure modes
Regression tests for the three failure modes in the checklist (empty search,
empty wardrobe, model unavailable) plus the "over $N" price-parsing bug found
while triggering them.

    python test_failure_modes.py

No pytest, no fixtures — each test patches out the one boundary it needs
(agent.call_tool so it doesn't spawn the MCP server, tools.generate /
agent.suggest_outfit so it doesn't call the model) and restores it in a
finally. Run before a fix to see it fail, after to confirm it's fixed.
"""

import sys

import agent
import tools
from generate import ModelUnavailable

FAKE_LISTING = {
    "id": "1", "title": "Test Tee", "description": "a plain cotton tee",
    "category": "top", "style_tags": [], "size": "M", "condition": "good",
    "price": 10.0, "colors": ["blue"], "brand": None, "platform": "depop",
}


def _patch(module, name, value):
    original = getattr(module, name)
    setattr(module, name, value)
    return original


def test_price_over_is_not_read_as_a_ceiling():
    parsed = agent.parse_query("vintage graphic tee over $20")
    assert parsed["max_price"] is None, (
        f"'over $20' should not be read as a max_price ceiling, got {parsed['max_price']!r}"
    )
    under = agent.parse_query("vintage graphic tee under $20")
    assert under["max_price"] == 20.0, "the existing 'under $N' case must keep working"


def test_empty_search_stops_before_suggest_outfit():
    def _boom(*a, **k):
        raise AssertionError("suggest_outfit should not run when search_results is empty")

    orig_call_tool = _patch(agent, "call_tool", lambda name, args: [])
    orig_suggest = _patch(agent, "suggest_outfit", _boom)
    try:
        session = agent.run_agent("nothing matches this", wardrobe={"items": []})
        assert session["error"], "expected an error message on empty search"
        assert session["fit_card"] is None
        assert session["selected_item"] is None
    finally:
        agent.call_tool = orig_call_tool
        agent.suggest_outfit = orig_suggest


def test_empty_wardrobe_gets_advice_not_crash():
    orig_generate = _patch(tools, "generate", lambda prompt, **k: "general styling advice")
    try:
        advice = tools.suggest_outfit(FAKE_LISTING, {"items": []})
        assert advice and advice.strip(), "empty wardrobe should return non-empty advice"
    finally:
        tools.generate = orig_generate


def test_model_unavailable_is_handled_not_raised():
    def _boom(*a, **k):
        raise ModelUnavailable("The model rejected your API key.")

    orig_call_tool = _patch(agent, "call_tool", lambda name, args: [FAKE_LISTING])
    orig_suggest = _patch(agent, "suggest_outfit", _boom)
    try:
        session = agent.run_agent("a test tee", wardrobe={"items": []})
        assert session["error"], (
            "run_agent should catch ModelUnavailable and set session['error'], not raise"
        )
        assert session["fit_card"] is None
    finally:
        agent.call_tool = orig_call_tool
        agent.suggest_outfit = orig_suggest


TESTS = [
    test_price_over_is_not_read_as_a_ceiling,
    test_empty_search_stops_before_suggest_outfit,
    test_empty_wardrobe_gets_advice_not_crash,
    test_model_unavailable_is_handled_not_raised,
]


def main():
    failures = []
    for test in TESTS:
        try:
            test()
        except AssertionError as exc:
            failures.append(test.__name__)
            print(f"FAIL  {test.__name__}: {exc}")
        except Exception as exc:  # noqa: BLE001 — an uncaught exception IS the failure here
            failures.append(test.__name__)
            print(f"ERROR {test.__name__}: {type(exc).__name__}: {exc}")
        else:
            print(f"PASS  {test.__name__}")

    print()
    if failures:
        print(f"{len(failures)} of {len(TESTS)} failed: {', '.join(failures)}")
        return 1
    print(f"All {len(TESTS)} passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
