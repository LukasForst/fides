from tests.load_config import find_config
from tests.load_fides import get_fides


def test_get_fides():
    fides = get_fides()
    assert fides is not None


def test_find_config():
    conf = find_config()
    assert conf is not None
