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


_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")


def parse_frontmatter(text):
    """Return (meta dict, body). Assumes flat 'key: value' frontmatter."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, parts[2].lstrip("\n")


def flatten_wikilinks(body):
    """Replace [[X]] and [[X|Y]] with plain text (Y if present, else X)."""
    return _WIKILINK.sub(lambda m: m.group(1).split("|")[-1], body)


def _is_draft(value):
    return str(value).strip().lower() in ("true", "yes", "1")


def _yaml_quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize(raw_text, mtime_iso):
    """Build the Astro-side file text, or None if the vignette is a draft."""
    meta, body = parse_frontmatter(raw_text)
    if _is_draft(meta.get("draft", "")):
        return None
    title = meta.get("title", "").strip()
    body = flatten_wikilinks(body).strip()
    return (
        "---\n"
        f"title: {_yaml_quote(title)}\n"
        f"updated: {_yaml_quote(mtime_iso)}\n"
        f"teaser: {_yaml_quote(extract_teaser(body))}\n"
        "---\n\n"
        f"{body}\n"
    )
