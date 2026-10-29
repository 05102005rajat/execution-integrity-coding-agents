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
