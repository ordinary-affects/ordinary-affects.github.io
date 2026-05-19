"""Sync finished vignettes from the Obsidian vault into the Astro content dir."""
import re

_SLUG_DROP = re.compile(r"[^a-z0-9一-鿿]+")
_SENTENCE_END = re.compile(r"[.!?。！？]")


def slugify(title):
    """Lowercase kebab-case slug. Keeps CJK characters."""
    return _SLUG_DROP.sub("-", title.strip().lower()).strip("-")


def extract_teaser(body):
    """First sentence of the body, with a trailing ellipsis."""
    text = body.strip()
    match = _SENTENCE_END.search(text)
    first = text[: match.start()] if match else text
    return first.strip() + "…"
