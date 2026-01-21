"""
utils.py: Utilities for creating chained fixtures for agentic flow testing.
"""

from typing import Callable, Any, List
import pytest

def chain_fixtures(*fixtures: List[Callable]) -> Callable:
    """
    Chains multiple pytest fixtures or callables, passing the output of one as input to the next.
    Returns a function that executes the chain.
    """
    def chained(initial_input: Any = None):
        result = initial_input
        for fixture in fixtures:
            result = fixture(result)
        return result
    return chained

# Example usage (to be removed or adapted in tests):
# def fixture1(x):
#     return x + 1
# def fixture2(x):
#     return x * 2
# chained = chain_fixtures(fixture1, fixture2)
# assert chained(3) == 8
