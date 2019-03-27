import unittest
from plumber import 9p


class Test9pParser(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse(self):
        raw_msg = ...
        parsed_msg = 9p.loadb(raw_msg)
        serialized_msg = 9p.dumpb(parsed_msg)
        self.assertEqual(raw_msg, serialized_msg)
