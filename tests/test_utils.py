import unittest
import biovis_report.utils as utils

class TestUtils(unittest.TestCase):
    def test_check_plugin(self):
        self.assertEqual(utils.check_plugin(), True)

    def test_process(self):
        process = utils.Process()
        self.assertEqual(process.get_process(1000000), None)

if __name__ == '__main__':
    unittest.main()
