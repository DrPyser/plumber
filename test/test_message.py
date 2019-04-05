from plumber import message

import unittest


class TestMessage(unittest.TestCase):
    def setUp(self):
        print("Hello")
        pass

    def test_encode(self):
        msg = message.PlumbMsg(
            src="test",
            dst="test",
            type="text",
            attrs=dict(),
            ndata=10,
            data=b"012345678"
        )
        encoded = message.encode(msg)
        print("encoded=",encoded)
        deencoded = message.decode(encoded)
        print("deencoded=", repr(deencoded))
        self.assertEqual(deencoded, msg)
        
