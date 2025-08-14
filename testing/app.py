import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pagination_basic():
    from utils.helper import pagination
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = pagination(data, page=1, limit=3)
    assert result == [1, 2, 3]
    result = pagination(data, page=2, limit=3)
    assert result == [4, 5, 6]
    result = pagination(data, page=4, limit=3)
    assert result == [10]

def test_pagination_empty():
    from utils.helper import pagination
    result = pagination([], page=1, limit=5)
    assert result == []

def test_pagination_out_of_range():
    from utils.helper import pagination
    data = [1, 2, 3]
    result = pagination(data, page=5, limit=2)
    assert result == []

def test_imports():
    try:
        from utils import helper
        assert True
    except ImportError:
        pytest.fail("Failed to import utils.helper")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 