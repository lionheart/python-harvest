# Copyright 2012-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
