"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


def parse_query(query: str) -> tuple[str, str | None, float | None]:
    """Extract a search description, optional size, and optional price ceiling.

    Recognizes sizes introduced by ``size`` (optionally ``in size``), and
    prices introduced by ``under``, ``below``, ``less than``, ``up to``,
    ``at most``, or ``max``. Unrecognized text remains part of the description.
    """
    description = query.strip()
    size: str | None = None
    max_price: float | None = None

    price_match = re.search(
        r"\b(?:under|below|less\s+than|up\s+to|at\s+most|max(?:imum)?"
        r"(?:\s+price)?(?:\s+of)?)\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
        description,
        flags=re.IGNORECASE,
    )
    if price_match:
        max_price = float(price_match.group(1))
        description = (
            description[:price_match.start()] + description[price_match.end():]
        )

    size_match = re.search(
        r"\b(?:in\s+)?size\s+"
        r"(?:(US|UK)\s*)?"
        r"(one\s+size|[A-Z]\d{1,2}\s+[A-Z]\d{1,2}|"
        r"[A-Z0-9]+(?:\s*/\s*[A-Z0-9]+)?)\b",
        description,
        flags=re.IGNORECASE,
    )
    if size_match:
        size = " ".join(
            part for part in (size_match.group(1), size_match.group(2)) if part
        )
        size = re.sub(r"\s*/\s*", "/", size).upper()
        description = (
            description[:size_match.start()] + description[size_match.end():]
        )

    description = re.sub(
        r"^\s*(?:looking\s+for|searching\s+for|find\s+me)\s+",
        "",
        description,
        flags=re.IGNORECASE,
    )
    description = re.sub(
        r"^\s*(?:a|an|the)\s+", "", description, flags=re.IGNORECASE
    )
    description = re.sub(r"\s+", " ", description).strip(" \t\n,;:")

    return description, size, max_price


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    count = 0

    # 1. Parse the user's query.
    count += 1
    trace.check_iterations(count)
    description, size, max_price = parse_query(query)
    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # 2. Search for listings.
    count += 1
    trace.check_iterations(count)
    search_results = search_listings(
        session["parsed"]["description"],
        session["parsed"]["size"],
        session["parsed"]["max_price"],
    )
    session["search_results"] = search_results

    # 3. Branch: stop if there are no matching listings.
    count += 1
    trace.check_iterations(count)
    if not session["search_results"]:
        session["error"] = (
            "No listings matched your search. Try changing the description, "
            "size, or maximum price."
        )
        return session

    # 4. Select the first result and store it in session state.
    count += 1
    trace.check_iterations(count)
    session["selected_item"] = session["search_results"][0]

    # 5. Use the selected item from session to suggest an outfit.
    count += 1
    trace.check_iterations(count)
    outfit_suggestion = suggest_outfit(
        session["selected_item"],
        session["wardrobe"],
    )
    session["outfit_suggestion"] = outfit_suggestion

    # 6. Use the outfit suggestion and selected item from session
    #    to create the final fit card.
    count += 1
    trace.check_iterations(count)
    fit_card = create_fit_card(
        session["outfit_suggestion"],
        session["selected_item"],
    )
    session["fit_card"] = fit_card

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
