from tests.load_config import find_config


def test_load_configuration():
    assert find_config() is not None
