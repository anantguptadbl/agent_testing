
import glob
import pytest
from agent_test.src.fixture.data_loader.json_feature_loader import JSONFeatureLoader
import pytest

class FeatureLoader:
    """Unified feature loader that dispatches to the correct loader based on type."""
    def __init__(self, loader_type, root_path=None, file_list=None):
        self.loader_type = loader_type
        self.root_path = root_path
        self.file_list = file_list
        if loader_type == "json":
            self.loader = JSONFeatureLoader()
        else:
            raise ValueError(f"Unsupported loader type: {loader_type}")

    def load_all(self, file_list=None):
        if file_list is None:
            file_list = self.file_list
        all_scenarios = []
        for file in file_list or []:
            for scenario in self.loader.parse(file):
                if self.root_path:
                    scenario["root_path"] = self.root_path
                all_scenarios.append(scenario)
        return all_scenarios

# Pytest fixture for FeatureLoader
@pytest.fixture
def file_feature_loader(request):
    params = getattr(request, 'param', {})
    loader_type = params.get('loader_type', 'json')
    root_path = params.get('root_path')
    file_list = params.get('file_list')
    return FeatureLoader(loader_type, root_path, file_list)