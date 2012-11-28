import os, sys
import unittest

sys.path.insert(0, sys.path[0]+"/..")

import harvest

class TestLogic(unittest.TestCase):
    def setUp(self):
        self.harvest = harvest.Harvest("https://goretoytest.harvestapp.com", "tester@goretoy.com", "tester account")

    def tearDown(self):
        pass

    def test_status_up(self):
        self.assertEqual("up", harvest.HarvestStatus().get(), "Harvest must be down?")

    def test_status_not_down(self):
        self.assertNotEqual("down", harvest.HarvestStatus().get(), "Harvest must be down?")

if __name__ == '__main__':
    unittest.main()
