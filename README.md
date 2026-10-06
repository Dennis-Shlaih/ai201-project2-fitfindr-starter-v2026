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

FitFindr helps users find thrifted clothing and build an outfit around a selected listing. A user describes an item they want, optionally including a size and maximum price, and the agent searches the listings data for matches. If a match is found, it uses the user's wardrobe to suggest outfits and creates a short fit-card caption for the selected item. If no listing matches, the agent stops and tells the user what parts of the search they can change.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the listings data for items matching the requested description and optionally filters by size and maximum price.
- **Inputs:** `description` (`str`), `size` (`str | None`), `max_price` (`float | None`, inclusive).
- **Returns:** Up to `config.SEARCH_RESULT_LIMIT` matching listing dictionaries, ordered from highest keyword-overlap score to lowest. Each dictionary contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list (`[]`) when no listings match the description and provided filters. Size matching is case-insensitive; a requested `M` can match `S/M`, but `L` must not match `XL`.

### `suggest_outfit`

- **What it does:** Uses the selected listing and the user's wardrobe to suggest one or two outfits that incorporate the new item.
- **Inputs:** `new_item` (`dict`), `wardrobe` (`dict` containing an `items` list).
- **Returns:** A non-empty string containing outfit suggestions. When the wardrobe has items, suggestions should name specific pieces from it; when it is empty, the response should give general styling advice.
- **When it has nothing:** Does not return an empty string; an empty wardrobe produces general styling advice instead.

### `create_fit_card`

- **What it does:** Uses the selected item and outfit suggestion to create a short social-media-style caption for the outfit.
- **Inputs:** `outfit` (`str`), `new_item` (`dict`).
- **Returns:** A 2–4 sentence string that describes the outfit's vibe and mentions the new item, its price, and its platform once each.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, returns a descriptive message instead of calling the model or raising an exception.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, `run_agent` stores
a message explaining that the user can change the description, size, or price
limit and returns without calling `suggest_outfit`. Otherwise, it stores the
first result in `session["selected_item"]` and continues through the outfit and
fit-card tools.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions extract an optional size
introduced by `size` or `in size` and an optional maximum price introduced by
phrases such as `under`, `below`, `up to`, or `max`. The remaining text is the
search description.

**What moves through the session:** The parsed description, size, and maximum
price go into `session["parsed"]`; results go into `session["search_results"]`;
the first result goes into `session["selected_item"]`; then the outfit
suggestion and caption go into `session["outfit_suggestion"]` and
`session["fit_card"]`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey there! As your stylist, I am so excited to style this Y2K butterfly baby tee for you. Because it's fitted and cropped with those lovely pastel pink and purple tones, the key to balancing the outfit is playing with proportions and contrasting the cute graphic with a bit of edge.

Here are two practical, effortlessly cool outfits using pieces straight from your wardrobe:

### Outfit 1: Off-Duty Streetwear (Y2K Meets Grunge)
* **New Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces:**
  * Baggy straight-leg jeans (dark wash)
  * Black cropped zip hoodie
  * Chunky white sneakers
  * Black crossbody bag

**The Vibe & Why It Works:**
This is the ultimate homage to 2000s off-duty style. The super-fitted, cropped silhouette of the baby tee creates a fantastic contrast against your high-waisted, dark wash baggy jeans. Throwing the black cropped zip hoodie on top (worn unzipped or casually slung over your shoulders) adds that effortless streetwear edge. Tie the look together with your chunky white sneakers and the black crossbody bag for a practical, ultra-comfortable city day-off look.

---

### Outfit 2: Vintage Retro-Chic (Smart-Casual Balance)
* **New Item:** Y2K Baby Tee — Butterfly Print
* **Wardrobe Pieces:**
  * Wide-leg khaki trousers
  * Vintage black denim jacket
  * Black combat boots
  * Brown leather belt

**The Vibe & Why It Works:**
If you want to lean a little more into the "vintage" and "cottagecore" style tags of the top while keeping it grounded for everyday wear, this combination is a winner. Tucking the baby tee into your wide-leg khaki trousers (accentuated with the brown leather belt to pull in some earth tones) creates a polished, high-waisted silhouette. Layer the slightly cropped vintage black denim jacket on top to add texture, and finish the outfit with your black combat boots. The mix of the sweet butterfly graphic with the utilitarian trousers and boots gives it a really cool, curated high-low fashion feel.

Which one are you wearing first?

  Fit card: Obsessed with this Y2K Baby Tee — Butterfly Print I just scored for only $18.00 on depop! It gives major off-duty streetwear vibes when you style the sweet pastel graphic with baggy denim and chunky sneakers. Honestly can't wait to wear this all summer long.
```

**The three tools, tested one at a time**

**`search_listings`**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

**`suggest_outfit`**

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import load_listings, get_example_wardrobe; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hello! I am so excited to style these Vintage Levi's 501s for you—a medium-wash straight-leg is truly the ultimate wardrobe workhorse.

Here are two practical, effortlessly cool outfit combinations utilizing pieces straight from your existing closet:

### Outfit 1: The Off-Duty Streetwear Look
* **The Look:** Cool, casual, and balanced between fitted and oversized.
* **Pieces to pair with your new Levi's:**
  * **White ribbed tank top** (Tops)
  * **Black cropped zip hoodie** (Tops — worn open or half-zipped)
  * **Chunky white sneakers** (Shoes)
  * **Black crossbody bag** (Accessories)

**Why it works:**
The slim-to-straight fit of the 501s creates a great silhouette when balanced with a fitted base like your white ribbed tank. Layering the black cropped zip hoodie on top adds depth and leans into that effortless streetwear vibe. Finishing the fit with your chunky white sneakers and the black crossbody bag ties the black-and-white accents together while keeping the outfit ultra-comfortable for a day of running errands or grabbing coffee.

---

### Outfit 2: The Vintage Denim-on-Denim Edge
* **The Look:** Classic, textured, and slightly grungy with a deliberate nod to vintage styling.
* **Pieces to pair with your new Levi's:**
  * **White ribbed tank top** (Tops)
  * **Vintage black denim jacket** (Outerwear)
  * **Brown leather belt** (Accessories)
  * **Black combat boots** (Shoes)
  * **Black crossbody bag** (Accessories)

**Why it works:**
Denim-on-denim is timeless, but pairing a medium-wash blue jean with a vintage black denim jacket keeps it modern and intentional (avoiding the "Canadian tuxedo" trap by mixing your washes). Tucking the white ribbed tank in and cinching the 501s with your brown leather belt adds a polished structure to the waist. Finally, grounding the outfit with your black combat boots and crossbody bag gives the classic denim pieces a tougher, downtown-cool edge.
```

**`create_fit_card`**

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Obsessed with how these Vintage Levi's 501 Jeans in medium wash fit, so I just dropped them on depop for $38.00. I styled them with crisp white sneakers for that effortlessly cool, 90s-off-duty model vibe. Seriously the easiest everyday uniform you could ask for.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I used copilot to help correct the three tools from
  the specifications in `tools.py`.
- *What came back:* It identified that my code had invalid syntax at
  `return response.strip() and def create_fit_card(...)`, then drafted the
  search, outfit-suggestion, and fit-card implementations.
- *What I changed:* I reviewed the implementation against the listing and
  wardrobe data shapes, kept the inclusive price filter and token-based size
  matching, and made empty model responses raise an explicit error instead of
  silently returning an empty string.

**Moment 2**

- *What I asked for:* I used copilot to help connect the three tools into the required planning loop in `agent.py`, including the empty-search branch and session state.
- *What came back:* It explained how run_agent should parse the query, call search_listings, stop when the result is empty, store the selected listing in session["selected_item"], and pass that same item to the next tools.
- *What I changed:* I implemented the loop in the code, kept the starter structure and variable names, and tested both the matching and no-match paths. I verified that the empty path stops before generating an outfit or fit card and that the selected listing is preserved through the later tool calls.

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

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
