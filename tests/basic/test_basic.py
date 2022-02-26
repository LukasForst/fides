from tests.load_config import find_config
from tests.load_fides import get_fides


def test_get_fides():
    fides = get_fides()
    assert fides is not None


def test_find_config():
    conf = find_config()
    assert conf is not None


class A:
    def __init__(self, a):
        self.__a = a


class B(A):
    def __init__(self, a):
        super().__init__(a)

    def c(self):
        return self.__a


def test_inheritence():
    assert B(1).c() == 1
