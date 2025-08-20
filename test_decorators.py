import unittest
import datetime
from decorators import execute_only_at_night_time

class TestDecorators(unittest.TestCase):

    def test_execute_only_at_night_time(self):
        @execute_only_at_night_time
        def dummy():
            return True

        now = datetime.datetime.now().time()
        start = datetime.time(23, 0)
        end = datetime.time(6, 0)

        if (now >= start) or (now <= end):
            self.assertTrue(dummy())
        else:
            self.assertIsNone(dummy())

if __name__ == "__main__":
    unittest.main()
