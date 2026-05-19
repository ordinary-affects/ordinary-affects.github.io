from sync import slugify, extract_teaser


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
