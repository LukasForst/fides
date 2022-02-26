from unittest import TestCase

from tests.load_config import find_config


class ConfigurationTests(TestCase):

    def test_load_configuration(self):
        self.assertIsNotNone(find_config())
