from src.slugify import slugify, truncate


def test_slugify_simple():
    assert slugify("Hello World") == "hello-world"


def test_slugify_extra_spaces():
    assert slugify("  a   b  ") == "a-b"


def test_slugify_punctuation():
    assert slugify("C++ rocks!") == "c-rocks"


def test_truncate_short():
    assert truncate("abc", 5) == "abc"


def test_truncate_long():
    assert truncate("abcdefghij", 8) == "abcde..."


def test_slugify_accents():
    assert slugify("Café Münster") == "cafe-munster"


def test_truncate_tiny_n():
    assert truncate("abcdef", 2) == ".."
    assert truncate("abcdef", 3) == "..."
    assert truncate("abcdef", 0) == ""
