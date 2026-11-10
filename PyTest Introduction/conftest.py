import pytest


# hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)