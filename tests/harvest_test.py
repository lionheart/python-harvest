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
import configparser
from dataclasses import asdict

sys.path.insert(0, sys.path[0]+"/..")

import harvest

"""
There is a sample test config.

Copy it, name it test_config.ini and fill it out with your test details.

tests/test_config.ini is already in .gitignore

Just in case, the test config file looks like this:

[PERSONAL ACCESS TOKEN]
url = 'https://api.harvestapp.com/api/v2'
put_auth_in_header = True
personal_token = 'Bearer 1234567.pt.somebunchoflettersandnumbers'
account_id = '1234567'
"""

class TestHarvest(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read('test_config.ini')
        self.harvest = harvest.Harvest(config['PERSONAL ACCESS TOKEN']['uri'], put_auth_in_header=config['PERSONAL ACCESS TOKEN']['put_auth_in_header'], personal_token=config['PERSONAL ACCESS TOKEN']['personal_token'], account_id=config['PERSONAL ACCESS TOKEN']['account_id'])

    def tearDown(self):
        pass

    def test_status_not_down(self):
        self.assertEqual("none", self.harvest.status['indicator'], "Harvest API is having problems")

    # def test_client(self):
    #     original_clients = self.harvest.clients()
    #     original_client_count = original_clients.total_entries
    #
    #     client = {'name':'Pinky', 'currency':'USD', 'is_active':True, 'address':'ACME Labs'}
    #     new_client = self.harvest.create_client(**client)
    #
    #     clients = self.harvest.clients()
    #
    #     client_count = clients.total_entries
    #
    #     self.assertTrue(client_count > original_client_count, "We didn't add a client.")
    #
    #     client_record = self.harvest.get_client(new_client.id)
    #
    #     self.assertTrue(client['name'] == client_record.name, "No such client as the one we tried to make.")
    #
    #     self.harvest.update_client(new_client.id, name='The Brain')
    #
    #     updated_client_record = self.harvest.get_client(new_client.id)
    #
    #     self.assertFalse(updated_client_record.name == client['name'], "The updated client record retained the original name.")
    #     self.assertTrue(updated_client_record.name == 'The Brain', "The updated client record does not have the name we tried to set.")
    #
    #     self.harvest.delete_client(new_client.id)

    # def test_client_contact(self):
    #     sample_client_a = 7439772
    #
    #     client = asdict(self.harvest.get_client(sample_client_a))
    #
    #     contact_dict = {'client': client, 'title': 'Mr', 'first_name': 'S', 'last_name': 'quiggle', 'email': 'mr.squiggle@example.com', 'phone_office': '555 Whilloghby', 'phone_mobile': '04123456789', 'fax': 'beep squeel'}
    #
    #     original_client_contacts = self.harvest.client_contacts()
    #     original_client_contacts_count = original_client_contacts.total_entries
    #
    #     new_client_contact = self.harvest.create_client_contact(sample_client_a, **contact_dict)
    #
    #     updated_client_contacts = self.harvest.client_contacts()
    #     updated_client_contacts_count = updated_client_contacts.total_entries
    #
    #     client_contact = self.harvest.get_client_contact(new_client_contact.id)
    #
    #     self.harvest.update_client_contact(client_contact.id, fax='Not connected')
    #
    #     delete_client_contact(client_contact.id)

if __name__ == '__main__':
    unittest.main()
