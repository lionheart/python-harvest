import os, sys
import unittest
from time import time

sys.path.insert(0, sys.path[0]+"/..")

import harvest

class TestHarvest(unittest.TestCase):
    def setUp(self):
        self.harvest = harvest.Harvest("https://goretoytest.harvestapp.com", "tester@goretoy.com", "tester account")

    def tearDown(self):
        pass

    def test_status_not_down(self):
        self.assertNotEqual("down", harvest.status(), "Harvest must be down?")

if __name__ == '__main__':
    unittest.main()
