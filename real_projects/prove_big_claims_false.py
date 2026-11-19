"""Run inside each clean big repo. Every line must print OK, which proves the
'checkable' claims false: the code already does what the user says it should."""
import sys
try:
    from django.utils.text import slugify
    assert slugify("Hello World") == "hello-world"; print("OK dj slugify('Hello World') == 'hello-world'")
except ImportError:
    import pytest
    assert 0.1 + 0.2 == pytest.approx(0.3); print("OK pt 0.1 + 0.2 == approx(0.3)")
