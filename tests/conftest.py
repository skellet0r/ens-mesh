import pytest

pytest_plugins = ["fixtures.accounts", "fixtures.deployments"]


@pytest.fixture(scope="module", autouse=True)
def isolate_module(chain):
    chain.snapshot()
    yield
    chain.revert()


@pytest.fixture(autouse=True)
def isolate_function(chain, history):
    start = len(history)
    yield
    end = len(history)
    if (undo_count := end - start) > 0:
        chain.undo(undo_count)
