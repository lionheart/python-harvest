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

sys.path.insert(0, sys.path[0]+"/..")

import harvest

"""
There is a sample test config.

Copy it, name it test_config.txt and fill it out with your test details.

tests/test_config.txt is already in .gitignore

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

    def test_company(self):
        company = self.harvest.company()

    def test_company(self):
        company = self.harvest.company()

    def test_client_contacts(self):
        client_contacts = self.harvest.client_contacts()

    def test_clients(self):
        clients = self.harvest.clients()

    def test_invoice_messages(self):
        invoice_messages = self.harvest.invoice_messages(18321917) # an invoice_id _MUST_ be filled

    def test_invoice_payments(self):
        invoice_payments = self.harvest.invoice_payments(18321917) # an invoice_id _MUST_ be filled

    def test_all_invoices(self):
        invoices = self.harvest.invoices()

    def test_all_invoice_item_categories(self):
        invoice_item_categories = self.harvest.invoice_item_categories()

    def test_all_estimate_messages(self):
        estimate_messages = self.harvest.estimate_messages(1961420) # an estimate id _MUST_ be filled

    def test_all_estimate_messages(self):
        estimate_messages = self.harvest.estimate_messages(1961420) # an estimate id _MUST_ be filled

    def test_all_estimates(self):
        estimates = self.harvest.estimates()

    def test_all_estimate_item_categories(self):
        estimate_item_categories = self.harvest.estimate_item_categories()

    def test_all_estimate_item_categories(self):
        estimate_item_categories = self.harvest.estimate_item_categories()

    def test_all_expense_categories(self):
        #self.assertEqual("none", self.harvest.status['indicator'], "Harvest API is having problems")
        expense_categories = self.harvest.expense_categories()

    def test_two_expense_categories(self):
        expense_categories = self.harvest.expense_categories(per_page=2)

    def test_all_expenses(self):
        expenses = self.harvest.expenses()

    def test_all_tasks(self):
        tasks = self.harvest.tasks()

    def test_task(self):
        task = self.harvest.get_task(10997931)

    def test_all_time_entries(self):
        time_entries = self.harvest.time_entries()

    def test_all_user_assignments(self):
        user_assignments = self.harvest.user_assignments()

    def test_all_task_assignments(self):
        task_assignments = self.harvest.task_assignments()

    def test_all_projects(self):
        projects = self.harvest.projects()

    def test_all_roles(self):
        roles = self.harvest.roles()

    def test_all_user_cost_rates(self):
        user_cost_rates = self.harvest.user_cost_rates(2438626) # user Id

    def test_all_user_cost_rate(self):
        user_cost_rate = self.harvest.user_cost_rate(2438626, 353253) # user Id, cost rate

    def test_all_project_assignments(self):
        project_assignments = self.harvest.project_assignments(2438626) # user Id

    def test_my_project_assignments(self):
        my_project_assignments = self.harvest.my_project_assignments()

    def test_users(self):
        users = self.harvest.users()

    def test_currently_authenticated_user(self):
        currently_authenticated_user = self.harvest.currently_authenticated_user()

    def test_user(self):
        user = self.harvest.get_user(2438626)


if __name__ == '__main__':
    unittest.main()
