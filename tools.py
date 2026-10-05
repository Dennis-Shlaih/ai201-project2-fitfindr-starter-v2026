"""
The three standalone tools used by the FitFindr planning loop.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


def _tokens(text: str) -> set[str]:
    """Return lowercase alphanumeric tokens without merging size labels."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _list_text(values: list[str] | None) -> str:
    """Format optional lists for model prompts."""
    return ", ".join(str(value) for value in (values or []) if value is not None)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search listings by keyword overlap, with optional size and price filters.

    Returns matching listing dictionaries, best match first, limited by
    config.SEARCH_RESULT_LIMIT. Returns an empty list if nothing matches.
    """
    query_tokens = _tokens(description)
    if not query_tokens:
        return []

    requested_size = _tokens(size) if size is not None else set()
    matches: list[tuple[int, dict]] = []

    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue

        if requested_size and not requested_size.issubset(_tokens(listing["size"])):
            continue

        searchable_text = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                " ".join(listing["style_tags"]),
            ]
        )
        score = len(query_tokens & _tokens(searchable_text))
        if score:
            matches.append((score, listing))

    matches.sort(key=lambda match: match[0], reverse=True)
    return [
        listing
        for _, listing in matches[: config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Suggest outfits using the new listing and, when available, wardrobe pieces.

    An empty wardrobe produces general styling advice rather than an empty
    result. Raises RuntimeError if the model returns no usable text.
    """
    wardrobe_items = wardrobe.get("items", []) or []
    item_description = "\n".join(
        [
            f"Name: {new_item.get('title') or 'Unknown item'}",
            f"Category: {new_item.get('category') or 'Unknown'}",
            f"Colors: {_list_text(new_item.get('colors'))}",
            f"Style tags: {_list_text(new_item.get('style_tags'))}",
            f"Description: {new_item.get('description') or ''}",
        ]
    )

    if wardrobe_items:
        wardrobe_description = "\n".join(
            "- "
            + " | ".join(
                [
                    str(item.get("name") or "Unknown item"),
                    f"category: {item.get('category') or 'unknown'}",
                    f"colors: {_list_text(item.get('colors'))}",
                    f"styles: {_list_text(item.get('style_tags'))}",
                    f"notes: {item.get('notes') or ''}",
                ]
            )
            for item in wardrobe_items
        )
        wardrobe_instruction = (
            "Suggest one or two practical outfits using the new item and "
            "specific pieces from the user's existing wardrobe. Name the "
            "wardrobe pieces you recommend."
        )
        wardrobe_section = f"\nUser's wardrobe:\n{wardrobe_description}\n"
    else:
        wardrobe_instruction = (
            "Suggest one or two practical ways to style the new item using "
            "general fashion advice. The user has an empty wardrobe, so do "
            "not pretend they already own specific pieces."
        )
        wardrobe_section = "\nThe user's wardrobe is empty.\n"

    prompt = f"""
You are a helpful fashion stylist.

{wardrobe_instruction}

New item:
{item_description}
{wardrobe_section}
Explain the outfit combinations and their overall style or vibe.
"""
    response = generate(prompt).strip()
    if not response:
        raise RuntimeError("The model returned an empty outfit suggestion.")
    return response


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short social-media-style caption for the outfit and thrifted item.

    Returns a descriptive message when outfit is empty or whitespace.
    Raises RuntimeError if the model returns no usable caption.
    """
    if not outfit or not outfit.strip():
        return (
            "No outfit suggestion was provided, so a fit card could not be "
            "created."
        )

    item_title = new_item.get("title") or "this item"
    item_price = new_item.get("price")
    price_text = (
        f"${item_price:.2f}"
        if isinstance(item_price, (int, float))
        else f"${item_price}" if item_price is not None else "unknown price"
    )
    platform = new_item.get("platform") or "unknown platform"

    prompt = f"""
Write a short social-media-style fit card caption for this outfit.

New item: {item_title}
Price: {price_text}
Platform: {platform}

Outfit suggestion:
{outfit}

Requirements:
- Write 2 to 4 sentences.
- Mention the new item's title, price, and platform exactly once each.
- Describe the specific vibe of the outfit.
- Make it sound like a real person posting about a thrift find, not a product listing.
- Do not use hashtags.
"""
    response = generate(prompt).strip()
    if not response:
        raise RuntimeError("The model returned an empty fit card.")
    return response
