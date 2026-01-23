import pytest
from unittest.mock import patch, MagicMock

class Scenario:
    def _init_(self):
        self.state = {}
        self.patches = []

    def given(self, key, value):
        self.state[key] = value
        return self

    def mock_api(self, target, return_value=None, side_effect=None):
        patcher = patch(target, return_value=return_value, sideeffect=side_effect)
        mocked = patcher.start()
        self.patches.append(patcher)
        self.state[target] = mocked
        return self
    
    def when(self, key, func):
        self.state[key] = func(self.state[key])
        return self
    
    def then(self, key, expected):
        self.state[key] = expected
        return self

    def cleanup(self):
        for patcher in self.patches:
            patcher.stop()

@pytest.fixture
def scenario(request):
    s = Scenario()
    request.addfinalizer(s.cleanup)
    return s