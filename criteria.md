# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

4 of 5, not 5 of 5, because `search_listings` scores by plain keyword overlap
between the query's words and each listing's title/description/style_tags. A
query that's a real match in meaning can still share zero literal keywords
with the listing it should hit — "tee" vs. "t-shirt", "jacket" vs. "coat" —
so an occasional miss on wording, not on logic, is expected even for queries
picked to match.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

5 of 5 because this path never reaches the model or any scoring heuristic —
it's a single deterministic check (`if not session["search_results"]`) on
whatever `search_listings` returned. Unlike criterion 1, there's no
keyword-overlap judgment call in play, so there's no reason it should ever
vary across identical conditions.

---

## 3. The item selected is the item passed downstream

For 5 different matching queries, the `id` field of
`session["selected_item"]` matches the `id` field of the item object actually
received by `suggest_outfit` as `new_item` — 5 of 5 tries.

**Why this target:**

This is the one failure mode that won't look like itself — if the wrong item
(or a stale/copied one) reaches `suggest_outfit`, the outfit and fit card
still come back looking like normal output, just about the wrong thing.
Comparing ids catches a mismatch that reading the final fit card alone
wouldn't. It's 5 of 5 because passing a dict reference through two function
calls is plain code, not a model call — nothing here should vary.

---

## 4. The fit card is grounded in the actual item, not generic

For 5 different items, each fit card mentions that item's price at least
once, in 5 of 5 tries, and no two of the 5 cards are word-for-word identical.

**Why this target:**

The price-mention part is deterministic enough to hold at 5/5 — it's an
instruction in the prompt I control, not something the model has to infer.
The non-identical part is there because `TEMPERATURE = 0.9` is supposed to
produce real variation; if five different items came back with the same
caption, that's the cache or the temperature setting silently doing nothing,
not an acceptable range of model output.

---

## 5. The price ceiling is never violated

For 10 queries that specify a max_price, every listing in every returned
result list has `price <= max_price` — 10 of 10 tries, across all returned
listings, not just the first.

**Why this target:**

This is enforced by a plain comparison in `search_listings`, before any
scoring or model call happens. There's no reasonable path where correct code
lets even one listing through over the ceiling, so 10/10 is the honest
target, not an easy one — a miss here means the filter itself is broken, not
that the data was ambiguous.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
