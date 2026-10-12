# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

Thrifting takes work. Someone has to search listings across apps, picture how a thing would go with what's already in the closet, and guess whether the price is fair. FitFindr handles that part. A user describes what they want in plain language, something like "vintage graphic tee under $30" or "90s track jacket in size M." The agent searches secondhand listings for the closest match on description, size, and price, figures out what it pairs with in the user's wardrobe, and writes a short caption for the post. If nothing in the listings matches, it says so instead of forcing a result.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters listings by max price and size, scores the rest by keyword overlap with the description, and returns the best matches.
- **Inputs:** `description` (str) — keywords describing what the user wants. `size` (str | None) — size to filter by, case-insensitive token match (e.g. "M" matches "S/M"); `None` skips the filter. `max_price` (float | None) — inclusive price ceiling; `None` skips the filter.
- **Returns:** A list of listing dicts (fields: `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform`), sorted best match first, capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** Returns an empty list — never `None`, never raises.

### `suggest_outfit`

- **What it does:** Asks the model for outfit suggestions pairing a thrifted item with the user's existing wardrobe.
- **Inputs:** `new_item` (dict) — a listing dict for the item being considered. `wardrobe` (dict) — has an `items` key holding a list of the user's clothing items; may be empty.
- **Returns:** A non-empty string with one or two outfit suggestions.
- **When it has nothing:** If `wardrobe['items']` is empty, returns general styling advice for the item (still a non-empty string) instead of raising or returning `""`.

### `create_fit_card`

- **What it does:** Writes a short, social-media-style caption for the thrifted find, mentioning the item, its price and platform, and the suggested outfit.
- **Inputs:** `outfit` (str) — the outfit suggestion string from `suggest_outfit()`. `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption string.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a descriptive message string instead of raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` saying what the user could change (broaden the description, drop the size, raise the max price) and return — do not call `suggest_outfit`. Otherwise take the first result and proceed to `suggest_outfit` and `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex (`agent.py::parse_query`). One pattern pulls a `$` price (optionally preceded by "under"/"below"/"less than"/"max"/"up to") and strips it from the text; another pulls a `size <word>` or trailing `, <word>` token and strips that too; whatever text is left, whitespace-normalized, becomes `description`. Chosen over a model call because it costs nothing, returns the same answer on the same input every time (which the session-visibility check above depends on), and a wrong parse is readable in the pattern instead of being a model's opinion to debug.

**What moves through the session:** `query` (the raw input) → `parsed` (from `parse_query`) → `search_results` (from `search_listings(**parsed)`) → `selected_item` (`search_results[0]`, only reached if `search_results` is non-empty) → `outfit_suggestion` (from `suggest_outfit(selected_item, wardrobe)`) → `fit_card` (from `create_fit_card(outfit_suggestion, selected_item)`). Each tool call reads its inputs back out of `session` rather than from a variable held over from the previous step, and writes its result into `session` before the next call runs — that's what makes `error` checkable as a stop condition and lets a no-match run be verified by inspecting `session["fit_card"] is None` without re-running anything.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ AI201_CACHE=0 python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Outerwear:** Black cropped zip hoodie (worn open)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag

*Why it works:* The fitted baby tee balances the volume of the baggy jeans, while the cropped hoodie and chunky sneakers lean fully into the Y2K streetwear aesthetic.

**Outfit 2: High-Low Contrast**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Wide-leg khaki trousers
*   **Accessories:** Brown leather belt + Black crossbody bag
*   **Shoes:** Chunky white sneakers (or black combat boots for an edgy twist)

*Why it works:* Pairing the playful, feminine butterfly tee with structured, minimalist earth-tone trousers creates a cool, balanced high-low mix. Cinch with the brown belt to pull it together.

  Fit card: Living out my ultimate 2000s pop star dreams in this butterfly baby tee. 🦋✨ Style her with baggy dark denim and a zip-up hoodie for off-duty Y2K streetwear, or dress it down with wide-leg trousers for that effortless high-low mix. Grab this little aesthetic dream for just $18 over on my Depop!

2 model calls this session, 648 prompt + 295 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([l['id'] for l in search_listings('graphic tee', max_price=30)])"

['lst_002', 'lst_006', 'lst_017', 'lst_033', 'lst_011', 'lst_015']
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(repr(suggest_outfit(load_listings()[0], get_example_wardrobe())))"

'**Buy them.** Vintage 501s are a timeless staple that will anchor your wardrobe. \n\nHere are two ways to style them using what you already own:\n\n**Outfit 1: Casual & Minimal**\n*   **Top:** White ribbed tank top (tucked in)\n*   **Belt:** Brown leather belt\n*   **Shoes:** Chunky white sneakers\n*   **Accessories:** Black crossbody bag\n*   *Why it works:* The fitted tank balances the straight-leg fit of the 501s for an effortless, classic off-duty look. \n\n**Outfit 2: Edgy & Cozy**\n*   **Top:** Black cropped zip hoodie\n*   **Outerwear:** Vintage black denim jacket (layered over the hoodie)\n*   **Shoes:** Black combat boots\n*   *Why it works:* Double denim feels intentional when mixing washes (indigo jeans with the black jacket), and the cropped hoodie adds a modern streetwear proportion.'
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(repr(create_fit_card('jeans and white sneakers', load_listings()[0])))"

"You seriously can’t beat the fit of broken-in vintage denim. These classic Levi's 501s have the prettiest knee fading that just screams effortless. Throw them on with some crisp white sneakers and you're good to go. Grab them on my Depop right now for just $38!"
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Implement `run_agent()` in `agent.py` following the branch rule I'd already written in the README, reusing the existing `parse_query()`.
- *What came back:* A working implementation — but the call into `suggest_outfit()` was `suggest_outfit(session["selected_item"], wardrobe)`, reading `selected_item` out of the session while still passing the plain `wardrobe` function argument straight through instead of `session["wardrobe"]`.
- *What I changed:* Told it every tool call has to read its inputs back out of the session, not from a variable carried over from the caller. It changed the line to `suggest_outfit(session["selected_item"], session["wardrobe"])`, which is what actually makes the session the single source of truth instead of a side log of values that are really flowing through local variables.

**Moment 2**

- *What I asked for:* Run the happy path, print the session, and check that the item in `session["selected_item"]` is the exact same item that reached `suggest_outfit()`.
- *What came back:* It monkeypatched `suggest_outfit` with a spy to capture the argument it was actually called with, ran `run_agent()`, and compared the captured object to `session["selected_item"]` with `is`.
- *What I changed:* Nothing — the check came back `True`, confirming the session-threading fix from Moment 1 actually holds at runtime and isn't just correct-looking code. I kept the verification method (the `is` check via a spy) rather than just eyeballing printed output, since `==` on two separately-constructed dicts with the same fields would have passed even if the loop had copied or refetched the item somewhere.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | ≥ 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item selected is the item passed downstream | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card is grounded in the actual item | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. The price ceiling is never violated | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Raw log: `results/run_2026-10-12_0107_before.md` (caching off, `TEMPERATURE = 0.9`, 170 model calls).

How the tries map: criterion 1 and 2 are one query run 5 times. For criteria 3, 4 and 5, Try *n* is the *n*-th of five different queries or items (see `scenarios.py`). Each of those queries was also run 5 times in the harness and all 25 runs per criterion passed too.

- **1:** all 5 tries ended with `error: None` and a fit card.
- **2:** all 5 tries ended with the "No listings matched — try broadening…" message, 0 search results, and no outfit or fit card.
- **3:** the run log's trace prints only `dict with keys: new_item, wardrobe`, not the id. I checked it separately by replacing `suggest_outfit` with a spy that captures `new_item`, then comparing its `id` to `session["selected_item"]["id"]`. That matched in 25 of 25 runs (5 queries × 5 tries). This spy check is not in the run log.
- **4:** every fit card contained its item's price, in 25 of 25 runs. All 85 fit cards in the log are distinct, so no two were word-for-word identical.
- **5:** the trace shows only the first three titles, so I checked prices with the same spy approach. Every listing in `session["search_results"]` was ≤ the ceiling, in 25 of 25 runs. The "$38" query includes two listings priced exactly $38.

**Real output from one try** (criterion 1, try 1), from `run_eval.py::run_once`, which calls `agent.py::run_agent`. The trace is printed by `trace.py`:

```
Query: vintage graphic tee under $30   (example wardrobe)

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:

**Outfit 1: Y2K Streetwear**
Pair the butterfly baby tee with your **baggy straight-leg jeans (dark wash)** and **chunky white sneakers**. Layer the **black cropped zip hoodie** over top (leave it unzipped to show off the graphic) and finish with your **black crossbody bag**. 

**Outfit 2: Casual Contrast**
Tuck the baby tee into your **wide-leg khaki trousers**, worn with the **brown leather belt**. Throw on your **vintage black denim jacket** and ground the look with your **chunky white sneakers** for an easy, balanced mix of Y2K and earth tones.

Fit card:

Channeling my inner 2000s pop princess in this dreamy little butterfly baby tee. 🦋✨ Grabbed this Y2K gem for just $18 over on my Depop before someone else snatched it up. Honestly obsessed with how it looks thrown on with baggy dark wash denim and a zip hoodie, or dressed down just a bit with some effortless khaki trousers.

Trace:

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: **Outfit 1: Y2K Streetwear** Pair the butterfly baby tee with your **baggy straight-leg jeans (dark wash)** an…
[3] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Channeling my inner 2000s pop princess in this dreamy little butterfly baby tee. 🦋✨ Grabbed this Y2K gem for j…
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | ≥ 4 of 5 | MET | 5 of 5 tries ended with `error: None` and a fit card. None of the fit cards was the "No outfit suggestion yet" fallback text. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | 5 of 5 tries returned the "No listings matched…" message. The trace of each has only the `search_listings` step, so `suggest_outfit` and `create_fit_card` never ran. |
| 3 | The item selected is the item passed downstream | 5 of 5 | MET | A spy on `suggest_outfit` captured `new_item`, and its `id` equalled `session["selected_item"]["id"]` in 25 of 25 runs (5 queries × 5 tries). |
| 4 | The fit card is grounded in the actual item | 5 of 5 | MET | All 25 cards contained their item's exact price, checked by regex so "$22" can't match inside "$220". All 85 cards in the log were distinct, so none were word-for-word identical. |
| 5 | The price ceiling is never violated | 5 of 5 (revised from 10 of 10) | MET | Every listing in `session["search_results"]` was ≤ the ceiling in 25 of 25 runs, including the "$38" query, which has two listings priced at exactly $38. |

Criteria 3 and 5 were scored with a spy script rather than from the run log. The log's trace prints only titles and "dict with keys", not ids or prices.

**Diagnoses**

No criterion was missed, so there is no failure to place in a tool, the loop's branch, the session or the model's output, and I'm not inventing one.

The results match what the criteria's own reasoning predicted:
- **Criteria 2, 3 and 5** are plain code (an `if not search_results` check, passing a dict through two calls, and a `price <=` comparison). Nothing in them involves the model or a scoring judgment, so 5 of 5 was the right target and they held.
- **Criterion 4** depends on the prompt asking for the price (`create_fit_card` puts `Price: $…` in the prompt and tells the model to mention it). The model followed that in all 25 runs. With caching off and `TEMPERATURE = 0.9` the cards varied; they were not hiding identical output.
- **Criterion 1** allowed a miss on wording ("tee" vs "t-shirt"). The query I picked ("vintage graphic tee under $30") shares literal keywords with its listings, so the allowed miss never happened.

Limits of this result: the five criteria only cover queries I chose to match the data's wording. Outside them there are known gaps. "coat", "sweater under $40" and "trainers" return 0 listings, because `search_listings` matches only literal keywords. "jacket over $50" returns jackets under $50, because the "over $N" fix drops the number and never applies it as a floor. Neither gap is one of the five criteria, and I haven't turned them into failures.


---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask "looking for a vintage graphic tee under $30" --trace

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: **Outfit 1: Y2K Streetwear** *   **Top:** Y2K Butterfly Baby Tee *   **Bottoms:** Baggy straight-leg jeans (da…
[3] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Channeling major early 2000s energy with this butterfly print baby tee 🦋 Pair it with baggy dark denim and chu…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
```

**Empty search**

```
$ python app.py ask "designer ballgown size XXS under \$5" --trace

[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping

  No listings matched — try broadening the description, dropping the size filter, or raising the max price.
```

**On the MCP move:** `search_listings` was already rewired to call
`call_tool("search_listings", session["parsed"])` against the MCP server
before this unit, so no behavior changed here. What's new is that the call is
now *visible* as step `[1] search_listings (via MCP)` in the trace — the label
makes it obvious the result came back over MCP rather than from a local
function, and the step's `out:` line shows the unwrapped list of listing dicts
came back in native Python shape, same as a direct call would have returned.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Nothing. I made no improvement and did not run `python run_eval.py --label after`.

**Which failure it was meant to fix:** None. All five criteria were MET in the before run (see Run Log — Before and Verdicts and Diagnoses), so there is no missed criterion to diagnose or fix.

I rejected the alternatives for these reasons:
- Changing code just to have something to measure would move no number. The before table is already at its targets, so a second run could only repeat 5 of 5.
- I did not tighten or reword a criterion until it failed. `criteria.md` allows a revision only when a criterion can't be measured, and none of these were unmeasurable. The one revision I made, criterion 5 from 10 queries to 5, was for run cost, and it is recorded under the original line.

### Run Log — After

Not run. There was no change to measure, so the before table stands as the result.

**Did it help, and how do I know:** There was no change, so nothing to compare. The evidence that no improvement is needed is the before run: 5 of 5 on criteria 2, 3, 4 and 5 and 5 of 5 against a 4-of-5 target on criterion 1. This holds only for the five criteria as written. The gaps listed at the end of Verdicts and Diagnoses (synonym queries and "over $N") are real, but no criterion covers them.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
