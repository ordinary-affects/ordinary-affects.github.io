from sync import slugify, extract_teaser
from sync import parse_frontmatter, flatten_wikilinks, normalize


def test_slugify_basic():
    assert slugify("Dog Days") == "dog-days"


def test_slugify_punctuation_and_case():
    assert slugify("  First Impressions!  ") == "first-impressions"


def test_slugify_keeps_cjk():
    assert slugify("下降") == "下降"


def test_extract_teaser_first_sentence():
    body = "It's been years now since we've been watching. Something surges."
    assert extract_teaser(body) == "It's been years now since we've been watching…"


def test_extract_teaser_chinese():
    assert extract_teaser("雨停了。我睡着了。") == "雨停了…"


def test_extract_teaser_no_terminator():
    assert extract_teaser("a quiet fragment") == "a quiet fragment…"


def test_parse_frontmatter():
    text = "---\ntitle: Dog Days\ntype: vignette\n---\n\nThe body.\n"
    meta, body = parse_frontmatter(text)
    assert meta["title"] == "Dog Days"
    assert meta["type"] == "vignette"
    assert body.strip() == "The body."


def test_parse_frontmatter_none():
    meta, body = parse_frontmatter("just a body")
    assert meta == {}
    assert body == "just a body"


def test_flatten_wikilinks():
    assert flatten_wikilinks("see [[Other Note]] and [[A|B]]") == "see Other Note and B"


def test_normalize_builds_clean_frontmatter():
    raw = "---\ntitle: Dog Days\ndate: 2026-05-19\ntype: vignette\n---\n\nIt's a scene. More.\n"
    out = normalize(raw, "2026-05-19T10:00:00")
    assert 'title: "Dog Days"' in out
    assert 'updated: "2026-05-19T10:00:00"' in out
    assert 'teaser: "It\'s a scene…"' in out
    assert "type: vignette" not in out
    assert out.strip().endswith("It's a scene. More.")


def test_normalize_skips_draft():
    raw = "---\ntitle: Half Thought\ndraft: true\n---\n\nUnfinished.\n"
    assert normalize(raw, "2026-05-19T10:00:00") is None
