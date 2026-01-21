import pytest
from .utils import chain_fixtures

def test_chain_fixtures():
    def f1(x):
        return x + 1
    def f2(x):
        return x * 2
    chained = chain_fixtures(f1, f2)
    assert chained(3) == 8
