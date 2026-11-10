from src.lru import LRUCache


def test_put_get():
    c = LRUCache(2)
    c.put("a", 1)
    assert c.get("a") == 1


def test_missing_returns_none():
    c = LRUCache(2)
    assert c.get("zzz") is None


def test_evicts_oldest_without_gets():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") is None
    assert c.get("c") == 3


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None


def test_update_existing_key():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("a", 9)
    assert c.get("a") == 9
    assert len(c) == 1


def test_zero_capacity_stores_nothing():
    c = LRUCache(0)
    c.put("a", 1)
    assert c.get("a") is None
    assert len(c) == 0


def test_negative_capacity_rejected():
    import pytest
    with pytest.raises(ValueError):
        LRUCache(-1)
