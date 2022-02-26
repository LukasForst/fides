from unittest import TestCase

from tests.load_fides import get_fides


class TestIntelligenceRequest(TestCase):

    def test_request_intell(self):
        fides = get_fides()
        self.assertIsNotNone(fides)
