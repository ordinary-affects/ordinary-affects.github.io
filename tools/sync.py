"""Sync finished vignettes from the Obsidian vault into the Astro content dir."""
import os
import re
from datetime import datetime

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


def _mtime_iso(path):
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts).replace(microsecond=0).isoformat()


def sync(src_dir, dest_dir):
    """Mirror finished vignettes from src_dir into dest_dir. Returns a summary."""
    os.makedirs(dest_dir, exist_ok=True)
    written = set()
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(".md"):
            continue
        src_path = os.path.join(src_dir, name)
        with open(src_path, encoding="utf-8") as f:
            raw = f.read()
        out = normalize(raw, _mtime_iso(src_path))
        if out is None:
            continue
        filename = slugify(name[:-3]) + ".md"
        with open(os.path.join(dest_dir, filename), "w", encoding="utf-8") as f:
            f.write(out)
        written.add(filename)
    removed = 0
    for name in os.listdir(dest_dir):
        if name.endswith(".md") and name not in written:
            os.remove(os.path.join(dest_dir, name))
            removed += 1
    return {"written": len(written), "removed": removed}


def publish(repo_dir):
    """Stage, commit, and push the synced content. Skips if nothing changed."""
    import subprocess

    def git(*args):
        subprocess.run(["git", "-C", repo_dir, *args], check=True)

    content = os.path.join("src", "content", "vignettes")
    git("add", content)
    status = subprocess.run(
        ["git", "-C", repo_dir, "status", "--porcelain", content],
        capture_output=True, text=True).stdout
    if not status.strip():
        print("vignette-publish: nothing changed")
        return
    git("commit", "-m", f"vignettes: sync {datetime.now():%Y-%m-%d %H:%M}")
    git("push")


if __name__ == "__main__":
    src = os.environ["VIGNETTES_SRC"]
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(repo, "src", "content", "vignettes")
    result = sync(src, dest)
    print(f"vignette-publish: {result['written']} written, {result['removed']} removed")
    publish(repo)
