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

    sample_client_a = 7439772

    def setUp(self):
        config = configparser.ConfigParser()
        config.read('test_config.ini')
        self.harvest = harvest.Harvest(config['PERSONAL ACCESS TOKEN']['uri'], put_auth_in_header=config['PERSONAL ACCESS TOKEN']['put_auth_in_header'], personal_token=config['PERSONAL ACCESS TOKEN']['personal_token'], account_id=config['PERSONAL ACCESS TOKEN']['account_id'])

    def tearDown(self):
        pass

    def test_status_not_down(self):
        self.assertEqual("none", self.harvest.status['indicator'], "Harvest API is having problems")

    def test_project(self):
        pass

    # def test_expense_categories(self):
    #     expense_categories = self.harvest.expense_categories()
    #     expense_category = self.harvest.create_expense_category('Pass Through 00', unit_name='kilograms', unit_price=10.00)
    #     updated_expense_category = self.harvest.update_expense_category(expense_category.id, unit_price=100.00)
    #     expense_category = self.harvest.get_expense_category(updated_expense_category.id)
    #     self.harvest.delete_expense_category(expense_category.id)

    # def test_expenses(self):
    #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
    #     expense_category = self.harvest.create_expense_category('Pass Through 00', unit_name='kilograms', unit_price=10.00)
    #
    #     expenses = self.harvest.expenses()
    #
    #     new_expense = self.harvest.create_expense(project.id, expense_category.id, '2019-01-01')
    #
    #     expense = self.harvest.get_expense(new_expense.id)
    #
    #     updated_expense = self.harvest.update_expense(new_expense.id, notes="This is a note on an expense.")
    #
    #     self.harvest.delete_expense(updated_expense.id)
    #
    #     self.harvest.delete_project(project.id)
    #     self.harvest.delete_expense_category(expense_category.id)

    # def test_estimate_item_category(self):
    #     estimate_item_categories = self.harvest.estimate_item_categories()
    #
    #     category = self.harvest.create_estimate_item_category('Tabasco')
    #     self.harvest.update_estimate_item_category(category.id, 'Pass through')
    #     self.harvest.delete_estimate_item_category(category.id)

    # def test_estimates_messages(self):
    #     estimate_parameters = {"subject":"ABC Project Quote","line_items":[{"kind":"Service","description":"ABC Project Quote","unit_price":5000.0}]}
    #     estimate = self.harvest.create_estimate(self.sample_client_a, **estimate_parameters)
    #     self.harvest.create_estimate_message(estimate.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}])
    #
    #     message_parameters = {"subject":"Estimate #1001","body":"Here is our estimate.","send_me_a_copy":True}
    #     new_estimate_message = self.harvest.create_estimate_message(estimate.id, [{"name":"Richard Roe","email":"richardroe@example.com"}], **message_parameters)
    #     estimate_messages = self.harvest.estimate_messages(estimate.id)
    #     self.harvest.delete_estimate_message(estimate.id, new_estimate_message.id)
    #
    #     self.harvest.mark_open_estimate_as_declined(estimate.id)
    #
    # def test_estimates(self):
    #     estimates = self.harvest.estimates()
    #
    #     estimate_parameters = {"subject":"ABC Project Quote","line_items":[{"kind":"Service","description":"ABC Project Quote","unit_price":5000.0}]}
    #
    #     new_estimate = self.harvest.create_estimate(self.sample_client_a, **estimate_parameters)
    #     new_estimate = self.harvest.get_estimte(new_estimate.id)
    #
    #     updated_estimate = self.harvest.update_estimate(new_estimate.id, purchase_order="2345")
    #
    #     new_estimate_line_item = [{"kind":"Service","description":"Another Project","unit_price":1000.0}]
    #
    #     estimate_with_new_line_item = self.harvest.create_estimate_line_item(updated_estimate.id, new_estimate_line_item)
    #
    #     for item in estimate_with_new_line_item.line_items:
    #         updated_item = {'id':item.id, 'unit_price': 1.0}
    #         self.harvest.update_estimate_line_item(estimate_with_new_line_item.id, updated_item)
    #
    #     self.harvest.delete_estimate_line_items(estimate_with_new_line_item.id, estimate_with_new_line_item.line_items)
    #
    #     self.harvest.delete_estimate(estimate_with_new_line_item.id)
    #
    # def test_invoice_categories(self):
    #     categories = self.harvest.invoice_item_categories()
    #     invoice_item_category = self.harvest.create_invoice_item_category('Tabasco')
    #     invoice_item_category = self.harvest.get_invoice_item_category(invoice_item_category.id)
    #     self.harvest.update_invoice_item_category(invoice_item_category.id, 'Pass through')
    #     self.harvest.delete_invoice_item_category(invoice_item_category.id)
    #
    # def test_invoice_payments(self):
    #     invoice_config = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
    #     invoice = self.harvest.create_invoice(self.sample_client_a, **invoice_config)
    #     self.harvest.mark_draft_invoice_as_sent(invoice.id)
    #
    #     payment = self.harvest.create_invoice_payment(invoice.id, 500.00, paid_date='2019-02-17', notes='This is a note')
    #     payments = self.harvest.invoice_payments(invoice.id)
    #
    #     self.harvest.delete_invoice_payment(invoice.id, payment.id)
    #     payments = self.harvest.invoice_payments(invoice.id)
    #     self.harvest.delete_invoice(invoice.id)
    #
    # def test_invoice_messages(self):
    #
    #     invoice_config = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
    #     invoice = self.harvest.create_invoice(self.sample_client_a, **invoice_config)
    #
    #     new_invoice_message = self.harvest.create_invoice_message(invoice.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}], event_type='send')
    #
    #     invoice_messages = self.harvest.invoice_messages(invoice.id)
    #
    #     self.harvest.delete_invoice_message(invoice.id, new_invoice_message.id)
    #
    #     new_invoice_message = self.harvest.create_invoice_message(invoice.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}])
    #
    #     self.harvest.mark_open_invoice_as_closed(invoice.id)
    #     self.harvest.reopen_closed_invoice(invoice.id)
    #     self.harvest.mark_open_invoice_as_draft(invoice.id)
    #     self.harvest.mark_draft_invoice_as_sent(invoice.id)
    #
    #     self.harvest.delete_invoice(invoice.id)
    #
    # def test_invoices(self):
    #     original_invoices = self.harvest.invoices()
    #     original_invoice_count = original_invoices.total_entries
    #
    #     invoice = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
    #     new_invoice = self.harvest.create_invoice(self.sample_client_a, **invoice)
    #
    #     invoices = self.harvest.invoices()
    #     invoice_count = invoices.total_entries
    #
    #
    #     line_items = [{"kind":"Service","description":"CBA Project","unit_price":10000.0}, {"kind":"Product","description":"CBA Project","unit_price":10000.0}]
    #
    #     self.harvest.update_invoice(new_invoice.id, subject = "CBA Project Quote")
    #     updated_invoice = self.harvest.update_invoice(new_invoice.id, line_items = line_items)
    #
    #     for item in updated_invoice.line_items:
    #         updated_item = {'id':item.id, 'unit_price': 1.0}
    #         self.harvest.update_invoice_line_item(updated_invoice.id, updated_item)
    #
    #     self.harvest.create_invoice_line_item(new_invoice.id, line_items)
    #
    #     error = self.harvest.create_invoice_line_item(new_invoice.id, "")
    #
    #     invoice_record = self.harvest.get_invoice(new_invoice.id)
    #
    #     self.harvest.delete_invoice_line_items(invoice_record.id, invoice_record.line_items)
    #
    #     self.harvest.delete_invoice(invoice_record.id)
    #
    # def test_client(self):
    #     original_clients = self.harvest.clients()
    #     original_client_count = original_clients.total_entries
    #
    #     client = {'name':'Pinky', 'currency':'USD', 'is_active':True, 'address':'ACME Labs'}
    #     new_client = self.harvest.create_client(**client)
    #
    #     clients = self.harvest.clients()
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
    #
    # def test_client_contact(self):
    #     client = asdict(self.harvest.get_client(self.sample_client_a))
    #
    #     contact_dict = {'client': client, 'title': 'Mr', 'first_name': 'S', 'last_name': 'quiggle', 'email': 'mr.squiggle@example.com', 'phone_office': '555 Whilloghby', 'phone_mobile': '04123456789', 'fax': 'beep squeel'}
    #
    #     original_client_contacts = self.harvest.client_contacts()
    #     original_client_contacts_count = original_client_contacts.total_entries
    #
    #     new_client_contact = self.harvest.create_client_contact(self.sample_client_a, **contact_dict)
    #
    #     updated_client_contacts = self.harvest.client_contacts()
    #     updated_client_contacts_count = updated_client_contacts.total_entries
    #
    #     client_contact = self.harvest.get_client_contact(new_client_contact.id)
    #
    #     self.harvest.update_client_contact(client_contact.id, fax='Not connected')
    #
    #     self.harvest.delete_client_contact(client_contact.id)



if __name__ == '__main__':
    unittest.main()
