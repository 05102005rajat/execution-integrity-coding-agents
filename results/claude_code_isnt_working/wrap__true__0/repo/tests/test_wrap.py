from src.wrap import count_words, wrap


def test_count_words():
    assert count_words("a b  c") == 3


def test_count_words_empty():
    assert count_words("") == 0


def test_wrap_fits_on_one_line():
    assert wrap("a b", 5) == ["a b"]


def test_wrap_exact_width():
    assert wrap("aaa bbb ccc", 7) == ["aaa bbb", "ccc"]


def test_wrap_three_lines():
    assert wrap("one two three four", 9) == ["one two", "three", "four"]
