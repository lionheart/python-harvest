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
import configparser
from dataclasses import asdict
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient, WebApplicationClient
import httpretty
import warnings
from dacite import from_dict
import json

sys.path.insert(0, sys.path[0]+"/..")

import harvest
from harvest.harvestdataclasses import *
from harvest.helpers import *

"""
There is a sample test config.

Copy it, name it test_config.ini and fill it out with your test details.

tests/test_config.ini is already in .gitignore

Just in case, the test config file looks like this:

[PERSONAL ACCESS TOKEN]
url = https://api.harvestapp.com/api/v2
put_auth_in_header = True
personal_token = Bearer 1234567.pt.somebunchoflettersandnumbers
account_id = 1234567

[OAuth2 Implicit Code Grant]
uri = https://api.harvestapp.com/api/v2
client_id = aclientid
auth_url = https://id.getharvest.com/oauth2/authorize

[OAuth2 Authorization Code Grant]
uri = https://api.harvestapp.com/api/v2
client_id = aclientid
client_secret = itsmysecret
auth_url = https://id.getharvest.com/oauth2/authorize
token_url = https://id.getharvest.com/api/v2/oauth2/token
account_id = 1234567
"""

"""
Those who tread this path:-

These tests currently really only test that the default URL has been formed
correctly and that the datatype that gets returned can be typed into the dataclass.
Probably enough but a long way from "comprehensive".

TODO:
- in most cases the dataclass casting from int to float doesn't work. I think it's dacite but remains open for investigation
- create and update tests don't check to see if the parameters are being packaged correctly for the request. Would be good if they did
- have python-harvest check the HTTP status (essentially exception and error handling) and write tests esercising that
"""

class TestClientContacts(unittest.TestCase):

    def setUp(self):
        personal_access_token = PersonalAccessToken('ACCOUNT_NUMBER', 'PERSONAL_ACCESS_TOKEN')
        self.harvest = Harvest('https://api.harvestapp.com/api/v2', personal_access_token)
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*") # There's a bug in httpretty ATM.
        httpretty.enable()

    def teardown(self):
        httpretty.reset()
        httpretty.disable()


    def test_client_contacts(self):
        contact_4706479_dict = {
                "id":4706479,
                "title":"Owner",
                "first_name":"Jane",
                "last_name":"Doe",
                "email":"janedoe@example.com",
                "phone_office":"(203) 697-8885",
                "phone_mobile":"(203) 697-8886",
                "fax":"(203) 697-8887",
                "created_at":"2017-06-26T21:20:07Z",
                "updated_at":"2017-06-26T21:27:07Z",
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    }
            }

        contact_4706453_dict = {
                "id":4706453,
                "title":"Manager",
                "first_name":"Richard",
                "last_name":"Roe",
                "email":"richardroe@example.com",
                "phone_office":"(318) 515-5905",
                "phone_mobile":"(318) 515-5906",
                "fax":"(318) 515-5907",
                "created_at":"2017-06-26T21:06:55Z",
                "updated_at":"2017-06-26T21:27:20Z",
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    }
            }

        contact_4706510_dict = {
                "id":4706510,
                "title":None,
                "first_name":"George",
                "last_name":"Frank",
                "email":"georgefrank@example.com",
                "phone_office":"",
                "phone_mobile":"",
                "fax":"",
                "created_at":"2017-06-26T21:44:57Z",
                "updated_at":"2017-06-26T21:44:57Z",
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    }
            }

        contacts_dict = {
                "contacts":[contact_4706479_dict, contact_4706453_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/contacts?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/contacts?page=1&per_page=100"
                    }
            }

        # client_contacts
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/contacts?page=1&per_page=100",
                body=json.dumps(contacts_dict),
                status=200
            )
        client_contacts = from_dict(data_class=ClientContacts, data=contacts_dict)
        requested_client_contacts = self.harvest.client_contacts()
        self.assertEqual(requested_client_contacts, client_contacts)

        # get_client_contact
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/contacts/4706479",
                body=json.dumps(contact_4706479_dict),
                status=200
            )
        client_contact = from_dict(data_class=ClientContact, data=contact_4706479_dict)
        requested_client_contact = self.harvest.get_client_contact(contact_id= 4706479)
        self.assertEqual(requested_client_contact, client_contact)

        # create_client_contact
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/contacts",
                body=json.dumps(contact_4706510_dict),
                status=200
            )
        new_client_contact = from_dict(data_class=ClientContact, data=contact_4706510_dict)
        requested_new_client_contact = self.harvest.create_client_contact(client_id= 5735776, first_name= "George", last_name= "Frank", email= "georgefrank@example.com")
        self.assertEqual(requested_new_client_contact, new_client_contact)

        # update_client_contact
        contact_4706510_dict["title"] = "Owner"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/contacts/4706510",
                body=json.dumps(contact_4706510_dict),
                status=200
            )
        updated_client_contact = from_dict(data_class=ClientContact, data=contact_4706510_dict)
        requested_updated_client_contact = self.harvest.update_client_contact(contact_id=4706510, title= "Owner")
        self.assertEqual(requested_updated_client_contact, updated_client_contact)

        # delete_client_contact
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/contacts/4706510",
                status=200
            )
        requested_deleted_client_contact = self.harvest.delete_client_contact(contact_id=4706510)
        self.assertEqual(requested_deleted_client_contact, None)

        httpretty.reset()


    def test_clients(self):

        client_5735776_dict = {
                "id":5735776,
                "name":"123 Industries",
                "is_active":True,
                "address":"123 Main St.\r\nAnytown, LA 71223",
                "created_at":"2017-06-26T21:02:12Z",
                "updated_at":"2017-06-26T21:34:11Z",
                "currency":"EUR"
            }

        client_5735774_dict = {
                "id":5735774,
                "name":"ABC Corp",
                "is_active":True,
                "address":"456 Main St.\r\nAnytown, CT 06467",
                "created_at":"2017-06-26T21:01:52Z",
                "updated_at":"2017-06-26T21:27:07Z",
                "currency":"USD"
            }

        client_5737336_dict = {
                "id":5737336,
                "name":"Your New Client",
                "is_active":True,
                "address":None,
                "created_at":"2017-06-26T21:39:35Z",
                "updated_at":"2017-06-26T21:39:35Z",
                "currency":"EUR"
            }

        clients_dict = {
                "clients":[client_5735776_dict, client_5735774_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                    "first":"https://api.harvestapp.com/v2/clients?page=1&per_page=100",
                    "next":None,
                    "previous":None,
                    "last":"https://api.harvestapp.com/v2/clients?page=1&per_page=100"
                }
            }

        # clients
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/clients?page=1&per_page=100",
                body=json.dumps(clients_dict),
                status=200
            )
        clients = from_dict(data_class=Clients, data=clients_dict)
        requested_clients = self.harvest.clients()
        self.assertEqual(requested_clients, clients)

        # get_client
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/clients/5735776",
                body=json.dumps(client_5735776_dict),
                status=200
            )
        client = from_dict(data_class=Client, data=client_5735776_dict)
        requested_client = self.harvest.get_client(client_id= 5735776)
        self.assertEqual(requested_client, client)

        # create_client
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/clients",
                body=json.dumps(client_5737336_dict),
                status=200
            )
        new_client = from_dict(data_class=Client, data=client_5737336_dict)
        requested_new_client = self.harvest.create_client(name= "Your New Client", currency= "EUR")
        self.assertEqual(requested_new_client, new_client)

        # update_client
        client_5737336_dict["is_active"] = False
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/clients/5737336",
                body=json.dumps(client_5737336_dict),
                status=200
            )
        updated_client = from_dict(data_class=Client, data=client_5737336_dict)
        requested_updated_client = self.harvest.update_client(client_id= 5737336, is_active= False)
        self.assertEqual(requested_updated_client, updated_client)

        # delete_client
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/clients/5737336",
                status=200
            )
        requested_deleted_client = self.harvest.delete_client(client_id= 5737336)
        self.assertEqual(requested_deleted_client, None)


        httpretty.reset()


    def test_company(self):
        company_dict = {
                "base_uri":"https://{ACCOUNT_SUBDOMAIN}.harvestapp.com",
                "full_domain":"{ACCOUNT_SUBDOMAIN}.harvestapp.com",
                "name":"API Examples",
                "is_active":True,
                "week_start_day":"Monday",
                "wants_timestamp_timers":True,
                "time_format":"hours_minutes",
                "plan_type":"sponsored",
                "expense_feature":True,
                "invoice_feature":True,
                "estimate_feature":True,
                "approval_required":True,
                "clock":"12h",
                "decimal_symbol":".",
                "thousands_separator":",",
                "color_scheme":"orange"
            }
        company = from_dict(data_class=Company, data=company_dict)

        httpretty.register_uri(httpretty.GET, "https://api.harvestapp.com/api/v2/company", body=json.dumps(company_dict), status=200)
        requested_company = self.harvest.company()

        self.assertEqual(requested_company, company)

        httpretty.reset()


    def test_invoice_messages(self):
        invoice_message_27835209_dict = {
                "id":27835209,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":False,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:15:06Z",
                "updated_at":"2017-08-23T22:15:06Z",
                "attach_pdf":True,
                "event_type":None,
                "recipients":[
                    {
                        "name":"Richard Roe",
                        "email":"richardroe@example.com"
                    }
                ],
                "subject":"Past due invoice reminder: #1001 from API Examples",
                "body":"Dear Customer,\r\n\r\nThis is a friendly reminder to let you know that Invoice 1001 is 144 days past due. If you have already sent the payment, please disregard this message. If not, we would appreciate your prompt attention to this matter.\r\n\r\nThank you for your business.\r\n\r\nCheers,\r\nAPI Examples"
            }

        invoice_message_27835207_dict = {
                "id":27835207,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":True,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:14:49Z",
                "updated_at":"2017-08-23T22:14:49Z",
                "attach_pdf":True,
                "event_type":None,
                "recipients":[
                {
                    "name":"Richard Roe",
                    "email":"richardroe@example.com"
                },
                {
                    "name":"Bob Powell",
                    "email":"bobpowell@example.com"
                }
                ],
                "subject":"Invoice #1001 from API Examples",
                "body":"---------------------------------------------\r\nInvoice Summary\r\n---------------------------------------------\r\nInvoice ID: 1001\r\nIssue Date: 04/01/2017\r\nClient: 123 Industries\r\nP.O. Number: \r\nAmount: €288.90\r\nDue: 04/01/2017 (upon receipt)\r\n\r\nThe detailed invoice is attached as a PDF.\r\n\r\nThank you!\r\n---------------------------------------------"
            }

        invoice_message_27835324_dict = {
                "id":27835324,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":True,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "attach_pdf":True,
                "event_type":None,
                "recipients":[
                {
                    "name":"Richard Roe",
                    "email":"richardroe@example.com"
                },
                {
                    "name":"Bob Powell",
                    "email":"bobpowell@example.com"
                }
                ],
                "subject":"Invoice #1001",
                "body":"The invoice is attached below."
            }

        invoice_message_27835325_dict = {
                "id":27835325,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":False,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "attach_pdf":False,
                "event_type":"send",
                "recipients":[],
                "subject":None,
                "body":None
            }

        invoice_message_27835326_dict = {
                "id":27835326,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":False,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "attach_pdf":False,
                "event_type":"close",
                "recipients":[],
                "subject":None,
                "body":None
            }

        invoice_message_27835327_dict = {
                "id":27835327,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":False,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "attach_pdf":False,
                "event_type":"re-open",
                "recipients":[],
                "subject":None,
                "body":None
            }

        invoice_message_27835328_dict = {
                "id":27835328,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "include_link_to_client_invoice":False,
                "send_me_a_copy":False,
                "thank_you":False,
                "reminder":False,
                "send_reminder_on":None,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "attach_pdf":False,
                "event_type":"draft",
                "recipients":[],
                "subject":None,
                "body":None
            }

        invoice_messages_dict = {
                "invoice_messages":[invoice_message_27835209_dict, invoice_message_27835207_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                    "first":"https://api.harvestapp.com/api/v2/invoices/13150403/messages?page=1&per_page=100",
                    "next":None,
                    "previous":None,
                    "last":"https://api.harvestapp.com/v2/invoices/13150403/messages?page=1&per_page=100"
                }
            }

        # invoice_messages
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages?page=1&per_page=100",
                body=json.dumps(invoice_messages_dict),
                status=200
            )
        invoice_messages = from_dict(data_class=InvoiceMessages, data=invoice_messages_dict)
        requested_invoice_messages = self.harvest.invoice_messages(invoice_id= 13150403)
        self.assertEqual(requested_invoice_messages, invoice_messages)

        # create_invoice_message
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/27835324/messages",
                body=json.dumps(invoice_message_27835324_dict),
                status=201
            )
        created_invoice_message = from_dict(data_class=InvoiceMessage, data=invoice_message_27835324_dict)
        requested_created_invoice_message = self.harvest.create_invoice_message(invoice_id= 27835324, recipients= [{"name":"Richard Roe", "email":"richardroe@example.com"}], subject= "Invoice #1001", body= "The invoice is attached below.", attach_pdf= True, send_me_a_copy= True)
        self.assertEqual(requested_created_invoice_message, created_invoice_message)

        # delete_client
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages/27835324",
                status=200
            )
        requested_deleted_invoice_message = self.harvest.delete_invoice_message(invoice_id= 13150403, message_id= 27835324)
        self.assertEqual(requested_deleted_invoice_message, None)

        # mark_draft_invoice_as_sent
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages",
                body=json.dumps(invoice_message_27835325_dict),
                status=201
            )
        sent_invoice_message = from_dict(data_class=InvoiceMessage, data=invoice_message_27835325_dict)
        requested_sent_invoice_message = self.harvest.mark_draft_invoice(invoice_id= 13150403, event_type= "send")
        self.assertEqual(requested_sent_invoice_message, sent_invoice_message)

        # mark_open_invoice_as_closed
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages",
                body=json.dumps(invoice_message_27835326_dict),
                status=201
            )
        closed_invoice_message = from_dict(data_class=InvoiceMessage, data=invoice_message_27835326_dict)
        requested_closed_invoice_message = self.harvest.mark_draft_invoice(invoice_id= 13150403, event_type= "close")
        self.assertEqual(requested_closed_invoice_message, closed_invoice_message)

        # reopen_closed_invoice
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages",
                body=json.dumps(invoice_message_27835327_dict),
                status=201
            )
        reopened_invoice_message = from_dict(data_class=InvoiceMessage, data=invoice_message_27835327_dict)
        requested_reopened_invoice_message = self.harvest.mark_draft_invoice(invoice_id= 13150403, event_type= "re-open")
        self.assertEqual(requested_reopened_invoice_message, reopened_invoice_message)

        # mark_open_invoice_as_draft
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/13150403/messages",
                body=json.dumps(invoice_message_27835328_dict),
                status=201
            )
        draft_invoice_message = from_dict(data_class=InvoiceMessage, data=invoice_message_27835328_dict)
        requested_draft_invoice_message = self.harvest.mark_draft_invoice(invoice_id= 13150403, event_type= "draft")
        self.assertEqual(requested_draft_invoice_message, draft_invoice_message)

        httpretty.reset()


    def test_invoice_payments(self):
        invoice_payment_10112854_dict = {
                "id": 10112854,
                "amount": 10700.00, # TODO: this needs to be an int and have python-harvest cast it. For some reason dcite isn't listening to the cast in the constructor
                "paid_at": "2017-02-21T00:00:00Z",
                "paid_date": "2017-02-21",
                "recorded_by": "Alice Doe",
                "recorded_by_email": "alice@example.com",
                "notes": "Paid via check #4321",
                "transaction_id": None,
                "created_at": "2017-06-27T16:24:57Z",
                "updated_at": "2017-06-27T16:24:57Z",
                "payment_gateway": {
                        "id": 1234,
                        "name": "Linkpoint International"
                    }
            }

        invoice_payment_10336386_dict = {
                "id": 10336386,
                "amount": 1575.86,
                "paid_at": "2017-07-24T13:32:18Z",
                "paid_date": "2017-07-24",
                "recorded_by": "Jane Bar",
                "recorded_by_email": "jane@example.com",
                "notes": "Paid by phone",
                "transaction_id": None,
                "created_at": "2017-07-28T14:42:44Z",
                "updated_at": "2017-07-28T14:42:44Z",
                "payment_gateway": {
                        "id": None,
                        "name": None
                    }
            }

        invoice_payments_dict = {
        "invoice_payments": [invoice_payment_10112854_dict],
        "per_page": 100,
        "total_pages": 1,
        "total_entries": 1,
        "next_page": None,
        "previous_page": None,
        "page": 1,
        "links": {
                "first": "https://api.harvestapp.com/v2/invoices/13150378/payments?page=1&per_page=100",
                "next": None,
                "previous": None,
                "last": "https://api.harvestapp.com/v2/invoices/13150378/payments?page=1&per_page=100"
            }
        }

        # invoice_payments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoices/13150403/payments?page=1&per_page=100",
                body=json.dumps(invoice_payments_dict),
                status=200
            )
        invoice_messages = from_dict(data_class=InvoicePayments, data=invoice_payments_dict)
        requested_invoice_messages = self.harvest.invoice_payments(invoice_id= 13150403)
        self.assertEqual(requested_invoice_messages, invoice_messages)

        # create_invoice_payment
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices/13150378/payments",
                body=json.dumps(invoice_payment_10336386_dict),
                status=200
            )
        created_invoice_payment = from_dict(data_class=InvoicePayment, data=invoice_payment_10336386_dict)
        requested_created_invoice_payment = self.harvest.create_invoice_payment(invoice_id= 13150378, amount= 1575.86, paid_at= "2017-07-24T13:32:18Z", notes= "Paid by phone")
        self.assertEqual(requested_created_invoice_payment, created_invoice_payment)

        # delete_invoice_payment
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/invoices/13150403/payments/10336386",
                status=200
            )
        requested_deleted_invoice_message = self.harvest.delete_invoice_payment(invoice_id= 13150403, payment_id= 10336386)
        self.assertEqual(requested_deleted_invoice_message, None)

        httpretty.reset()


    def test_invoices(self):
        invoice_13150403_dict = {
                "id":13150403,
                "client_key":"21312da13d457947a217da6775477afee8c2eba8",
                "number":"1001",
                "purchase_order":"",
                "amount":288.9,
                "due_amount":288.9,
                "tax":5.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "tax_amount":13.5,
                "tax2":2.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "tax2_amount":5.4,
                "discount":10.0 , # TODO: this is supposed to be an int. Something isn't casting int to float.
                "discount_amount":30.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "subject":"Online Store - Phase 1",
                "notes":"Some notes about the invoice.",
                "state":"open",
                "period_start":"2017-03-01",
                "period_end":"2017-03-01",
                "issue_date":"2017-04-01",
                "due_date":"2017-04-01",
                "payment_term":"upon receipt",
                "sent_at":"2017-08-23T22:25:59Z",
                "paid_at":None,
                "paid_date":None,
                "closed_at":None,
                "created_at":"2017-06-27T16:27:16Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "currency":"EUR",
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "estimate":None,
                "retainer":None,
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                    {
                        "id":53341602,
                        "kind":"Service",
                        "description":"03/01/2017 - Project Management: [9:00am - 11:00am] Planning meetings",
                        "quantity":2.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "unit_price":100.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "amount":200.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "taxed":True,
                        "taxed2":True,
                        "project":{
                                "id":14308069,
                                "name":"Online Store - Phase 1",
                                "code":"OS1"
                            }
                    },
                    {
                    "id":53341603,
                    "kind":"Service",
                    "description":"03/01/2017 - Programming: [1:00pm - 2:00pm] Importing products",
                    "quantity":1.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                    "unit_price":100.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                    "amount":100.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                    "taxed":True,
                    "taxed2":True,
                    "project":{
                            "id":14308069,
                            "name":"Online Store - Phase 1",
                            "code":"OS1"
                        }
                    }
                ]
            }

        invoice_13150378_dict = {
                "id":13150378,
                "client_key":"9e97f4a65c5b83b1fc02f54e5a41c9dc7d458542",
                "number":"1000",
                "purchase_order":"1234",
                "amount":10700.0,
                "due_amount":0.0,
                "tax":5.0,
                "tax_amount":500.0,
                "tax2":2.0,
                "tax2_amount":200.0,
                # "discount":None, # TODO: this is supposed to be a None. Something isn't casting int to float.
                "discount_amount":0.0,
                "subject":"Online Store - Phase 1",
                "notes":"Some notes about the invoice.",
                "state":"paid",
                "period_start":None,
                "period_end":None,
                "issue_date":"2017-02-01",
                "due_date":"2017-03-03",
                "payment_term":"custom",
                "sent_at":"2017-02-01T07:00:00Z",
                "paid_at":"2017-02-21T00:00:00Z",
                "paid_date":"2017-02-21",
                "closed_at":None,
                "created_at":"2017-06-27T16:24:30Z",
                "updated_at":"2017-06-27T16:24:57Z",
                "currency":"USD",
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "estimate":{
                        "id":1439814
                    },
                "retainer":None,
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                    {
                        "id":53341450,
                        "kind":"Service",
                        "description":"50% of Phase 1 of the Online Store",
                        "quantity":100.0,
                        "unit_price":100.0,
                        "amount":10000.0,
                        "taxed":True,
                        "taxed2":True,
                        "project":{
                                "id":14308069,
                                "name":"Online Store - Phase 1",
                                "code":"OS1"
                            }
                    }
                ]
            }

        invoice_13150453_dict = {
                "id":13150453,
                "client_key":"8b86437630b6c260c1bfa289f0154960f83b606d",
                "number":"1002",
                "purchase_order":None,
                "amount":5000.0,
                "due_amount":5000.0,
                "tax":None,
                "tax_amount":0.0,
                "tax2":None,
                "tax2_amount":0.0,
                "discount":None,
                "discount_amount":0.0,
                "subject":"ABC Project Quote",
                "notes":None,
                "state":"draft",
                "period_start":None,
                "period_end":None,
                "issue_date":"2017-06-27",
                "due_date":"2017-07-27",
                "payment_term":"custom",
                "sent_at":None,
                "paid_at":None,
                "paid_date":None,
                "closed_at":None,
                "created_at":"2017-06-27T16:34:24Z",
                "updated_at":"2017-06-27T16:34:24Z",
                "currency":"USD",
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "estimate":None,
                "retainer":None,
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                    {
                        "id":53341928,
                        "kind":"Service",
                        "description":"ABC Project",
                        "quantity":1.0,
                        "unit_price":5000.0,
                        "amount":5000.0,
                        "taxed":False,
                        "taxed2":False,
                        "project":None
                    }
                ]
            }

        invoice_15340591_dict = {
                "id":15340591,
                "client_key":"16173155e0a01542b8c7f689888cb3eaeda0dc94",
                "number":"1002",
                "purchase_order":"",
                "amount":333.35,
                "due_amount":333.35,
                "tax":None,
                "tax_amount":0.0,
                "tax2":None,
                "tax2_amount":0.0,
                "discount":None,
                "discount_amount":0.0,
                "subject":"ABC Project Quote",
                "notes":"",
                "state":"draft",
                "period_start":"2017-03-01",
                "period_end":"2017-03-31",
                "issue_date":"2018-02-12",
                "due_date":"2018-02-12",
                "payment_term":"upon receipt",
                "sent_at":None,
                "paid_at":None,
                "closed_at":None,
                "created_at":"2018-02-12T21:02:37Z",
                "updated_at":"2018-02-12T21:02:37Z",
                "paid_date":None,
                "currency":"USD",
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "estimate":None,
                "retainer":None,
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                    {
                        "id":64957723,
                        "kind":"Service",
                        "description":"[MW] Marketing Website: Graphic Design (03/01/2017 - 03/31/2017)",
                        "quantity":2.0,
                        "unit_price":100.0,
                        "amount":200.0,
                        "taxed":False,
                        "taxed2":False,
                        "project":{
                                "id":14307913,
                                "name":"Marketing Website",
                                "code":"MW"
                            }
                    },
                        {
                        "id":64957724,
                        "kind":"Product",
                        "description":"[MW] Marketing Website: Meals ",
                        "quantity":1.0,
                        "unit_price":133.35,
                        "amount":133.35,
                        "taxed":False,
                        "taxed2":False,
                        "project":{
                                "id":14307913,
                                "name":"Marketing Website",
                                "code":"MW"
                            }
                    }
                ]
            }

        invoices_dict = {
                "invoices":[invoice_13150403_dict, invoice_13150378_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/invoices?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/invoices?page=1&per_page=100"
                    }
            }

        # invoices
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoices?page=1&per_page=100",
                body=json.dumps(invoices_dict),
                status=200
            )
        invoices = from_dict(data_class=Invoices, data=invoices_dict)
        requested_invoices = self.harvest.invoices()
        self.assertEqual(requested_invoices, invoices)

        # get_invoice
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoices/13150378",
                body=json.dumps(invoice_13150378_dict),
                status=200
            )
        invoice = from_dict(data_class=Invoice, data=invoice_13150378_dict)
        requested_invoice = self.harvest.get_invoice(invoice_id= 13150378)
        self.assertEqual(requested_invoice, invoice)

        # create_invoice
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoices",
                body=json.dumps(invoice_15340591_dict),
                status=200
            )
        created_invoice = from_dict(data_class=Invoice, data=invoice_15340591_dict)
        requested_created_invoice = self.harvest.create_invoice(client_id= 5735774, subject= "ABC Project Quote", due_date= "2017-07-27", line_items= [{"kind" : "Service", "description" : "ABC Project", "unit_price" : 5000.0}])
        self.assertEqual(requested_created_invoice, created_invoice)

        # update_invoice
        invoice_13150453_dict['purchase_order'] = "2345"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/invoices/13150453",
                body=json.dumps(invoice_13150453_dict),
                status=200
            )
        updated_invoice = from_dict(data_class=Invoice, data=invoice_13150453_dict)
        requested_updated_invoice = self.harvest.update_invoice(invoice_id= 13150453, purchase_order="2345")
        self.assertEqual(requested_created_invoice, created_invoice)


        # create_invoice_line_item  invoice_13150453_dict
        # https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/ has an error in the doco...
        invoice_13150453_dict['line_items'].append(
                {
                    "id":53341929,
                    "kind":"Service",
                    "description":"DEF Project",
                    "quantity":1.0,
                    "unit_price":1000.0,
                    "amount":1000.0,
                    "taxed":False,
                    "taxed2":False,
                    "project":None
                }
            )
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/invoices/13150453",
                body=json.dumps(invoice_13150453_dict),
                status=200
            )
        updated_invoice = from_dict(data_class=Invoice, data=invoice_13150453_dict)
        requested_updated_invoice = self.harvest.create_invoice_line_item(invoice_id= 13150453, line_items = [{"kind" : "Service", "description" : "DEF Project"," unit_price" : 1000.0}])
        self.assertEqual(requested_created_invoice, created_invoice)

        # update_invoice_line_item  invoice_13150453_dict
        # https://help.getharvest.com/api-v2/invoices-api/invoices/invoices/ has an error in the doco...
        invoice_13150453_dict['line_items'][1]['description'] = "ABC Project Phase 2"
        invoice_13150453_dict['line_items'][1]['unit_price'] = 500.00
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/invoices/13150453",
                body=json.dumps(invoice_13150453_dict),
                status=200
            )
        updated_invoice = from_dict(data_class=Invoice, data=invoice_13150453_dict)
        requested_updated_invoice = self.harvest.update_invoice_line_item(invoice_id= 13150453, line_item = {"id":53341928,"description":"ABC Project Phase 2","unit_price":5000.0})
        self.assertEqual(requested_created_invoice, created_invoice)

        # delete_invoice_line_items
        del(invoice_13150453_dict['line_items'][1])
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/invoices/13150453",
                body=json.dumps(invoice_13150453_dict),
                status=200
            )
        deleted_invoice_line_items = from_dict(data_class=Invoice, data=invoice_13150453_dict)
        requested_deleted_invoice_line_items = self.harvest.delete_invoice_line_items(invoice_id= 13150453, line_items = [{"id" : 53341928, "_destroy" : True}])
        self.assertEqual(requested_deleted_invoice_line_items, deleted_invoice_line_items)

        # delete_invoice
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/invoices/13150453",
                status=200
            )
        requested_deleted_invoice = self.harvest.delete_invoice(invoice_id= 13150453)
        self.assertEqual(requested_deleted_invoice, None)

        httpretty.reset()


    def test_invoice_item_categories(self):
        invoice_item_category_1466293_dict = {
                "id":1466293,
                "name":"Product",
                "use_as_service":False,
                "use_as_expense":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        invoice_item_category_1466292_dict = {
                "id":1466292,
                "name":"Service",
                "use_as_service":True,
                "use_as_expense":False,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        invoice_item_category_1467098_dict = {
                "id":1467098,
                "name":"Hosting",
                "use_as_service":False,
                "use_as_expense":False,
                "created_at":"2017-06-27T16:20:59Z",
                "updated_at":"2017-06-27T16:20:59Z"
            }

        invoice_item_categories_dict = {
        "invoice_item_categories":[invoice_item_category_1466293_dict, invoice_item_category_1466292_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/invoice_item_categories?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/invoice_item_categories?page=1&per_page=100"
                    }
            }

        # invoice_categories
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoice_item_categories?page=1&per_page=100",
                body=json.dumps(invoice_item_categories_dict),
                status=200
            )
        invoice_item_categories = from_dict(data_class=InvoiceItemCategories, data=invoice_item_categories_dict)
        requested_invoice_item_categories = self.harvest.invoice_item_categories()
        self.assertEqual(invoice_item_categories, invoice_item_categories)

        # get_invoice_item_categories
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/invoice_item_categories/1466293",
                body=json.dumps(invoice_item_category_1466293_dict),
                status=200
            )
        invoice_item_categories = from_dict(data_class=InvoiceItemCategory, data=invoice_item_category_1466293_dict)
        requested_invoice_item_categories = self.harvest.get_invoice_item_category(category_id= 1466293)
        self.assertEqual(requested_invoice_item_categories, invoice_item_categories)

        # create_invoice_item_category
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/invoice_item_categories",
                body=json.dumps(invoice_item_category_1467098_dict),
                status=200
            )
        created_invoice_item_category = from_dict(data_class=InvoiceItemCategory, data=invoice_item_category_1467098_dict)
        requested_created_invoice_item_category = self.harvest.create_invoice_item_category(name= "Hosting")
        self.assertEqual(requested_created_invoice_item_category, created_invoice_item_category)

        # update_invoice_item_category
        invoice_item_category_1467098_dict['name'] = "Expense"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/invoice_item_categories/1467098",
                body=json.dumps(invoice_item_category_1467098_dict),
                status=200
            )
        update_invoice_item_category = from_dict(data_class=InvoiceItemCategory, data=invoice_item_category_1467098_dict)
        requested_update_invoice_item_category = self.harvest.update_invoice_item_category(category_id= 1467098, name= "Expense")
        self.assertEqual(requested_update_invoice_item_category, update_invoice_item_category)

        # delete_invoice_item_category
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/invoice_item_categories/1467098",
                status=200
            )
        requested_deleted_invoice_item_category = self.harvest.delete_invoice_item_category(invoice_category_id= 1467098)
        self.assertEqual(requested_deleted_invoice_item_category, None)

        httpretty.reset()


    def test_estimate_messages(self):
        estimate_message_2666236_dict = {
                "id":2666236,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":True,
                "created_at":"2017-08-25T21:23:40Z",
                "updated_at":"2017-08-25T21:23:40Z",
                "recipients":[
                    {
                        "name":"Richard Roe",
                        "email":"richardroe@example.com"
                    },
                    {
                        "name":"Bob Powell",
                        "email":"bobpowell@example.com"
                    }
                ],
                "event_type":None,
                "subject":"Estimate #1001 from API Examples",
                "body":"---------------------------------------------\r\nEstimate Summary\r\n---------------------------------------------\r\nEstimate ID: 1001\r\nEstimate Date: 06/01/2017\r\nClient: 123 Industries\r\nP.O. Number: 5678\r\nAmount: $9,630.00\r\n\r\nYou can view the estimate here:\r\n\r\n%estimate_url%\r\n\r\nThank you!\r\n---------------------------------------------"
            }

        estimate_message_2666240_dict = {
                "id":2666240,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":True,
                "created_at":"2017-08-25T21:27:52Z",
                "updated_at":"2017-08-25T21:27:52Z",
                "recipients":[
                    {
                        "name":"Richard Roe",
                        "email":"richardroe@example.com"
                    },
                    {
                        "name":"Bob Powell",
                        "email":"bobpowell@example.com"
                    }
                ],
                "event_type":None,
                "subject":"Estimate #1001",
                "body":"Here is our estimate."
            }

        estimate_message_2666241_dict = {
                "id":2666241,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":False,
                "created_at":"2017-08-23T22:25:59Z",
                "updated_at":"2017-08-23T22:25:59Z",
                "event_type":"send",
                "recipients":[],
                "subject":None,
                "body":None
            }

        estimate_message_2666244_dict = {
                "id":2666244,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":False,
                "created_at":"2017-08-25T21:31:55Z",
                "updated_at":"2017-08-25T21:31:55Z",
                "recipients":[],
                "event_type":"accept",
                "subject":None,
                "body":None
            }

        estimate_message_2666245_dict = {
                "id":2666245,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":False,
                "created_at":"2017-08-25T21:31:55Z",
                "updated_at":"2017-08-25T21:31:55Z",
                "recipients":[],
                "event_type":"decline",
                "subject":None,
                "body":None
            }

        estimate_message_2666246_dict = {
                "id":2666246,
                "sent_by":"Bob Powell",
                "sent_by_email":"bobpowell@example.com",
                "sent_from":"Bob Powell",
                "sent_from_email":"bobpowell@example.com",
                "send_me_a_copy":False,
                "created_at":"2017-08-25T21:31:55Z",
                "updated_at":"2017-08-25T21:31:55Z",
                "recipients":[],
                "event_type":"re-open",
                "subject":None,
                "body":None
            }

        estimate_messages_dict = {
        "estimate_messages":[estimate_message_2666236_dict],
            "per_page":100,
            "total_pages":1,
            "total_entries":1,
            "next_page":None,
            "previous_page":None,
            "page":1,
            "links":{
                    "first":"https://api.harvestapp.com/v2/estimates/1439818/messages?page=1&per_page=100",
                    "next":None,
                    "previous":None,
                    "last":"https://api.harvestapp.com/v2/estimates/1439818/messages?page=1&per_page=100"
                }
        }

        # estimate_messages
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages?page=1&per_page=100",
                body=json.dumps(estimate_messages_dict),
                status=200
            )
        estimate_messages = from_dict(data_class=EstimateMessages, data=estimate_messages_dict)
        requested_estimate_messages = self.harvest.estimate_messages(estimate_id= 1439818)
        self.assertEqual(requested_estimate_messages, estimate_messages)

        # estimate_message
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages",
                body=json.dumps(estimate_message_2666240_dict),
                status=200
            )
        new_estimate_message = from_dict(data_class=EstimateMessage, data=estimate_message_2666240_dict)
        requested_new_estimate_message = self.harvest.create_estimate_message(estimate_id= 1439818, recipients= [{"name" : "Richard Roe", "email" : "richardroe@example.com"}], subject= "Estimate #1001", body= "Here is our estimate.", send_me_a_copy= True)
        self.assertEqual(requested_new_estimate_message, new_estimate_message)

        # mark estimate as sent
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages",
                body=json.dumps(estimate_message_2666241_dict),
                status=201
            )
        mark_draft_estimate = from_dict(data_class=EstimateMessage, data=estimate_message_2666241_dict)
        requested_mark_draft_estimate = self.harvest.mark_draft_estimate(estimate_id= 1439818, event_type= "send")
        self.assertEqual(requested_mark_draft_estimate, mark_draft_estimate)

        # mark estimate as accepted
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages",
                body=json.dumps(estimate_message_2666244_dict),
                status=201
            )
        mark_draft_estimate = from_dict(data_class=EstimateMessage, data=estimate_message_2666244_dict)
        requested_mark_draft_estimate = self.harvest.mark_draft_estimate(estimate_id= 1439818, event_type= "accept")
        self.assertEqual(requested_mark_draft_estimate, mark_draft_estimate)

        # mark estimate as declined
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages",
                body=json.dumps(estimate_message_2666245_dict),
                status=201
            )
        mark_draft_estimate = from_dict(data_class=EstimateMessage, data=estimate_message_2666245_dict)
        requested_mark_draft_estimate = self.harvest.mark_draft_estimate(estimate_id= 1439818, event_type= "decline")
        self.assertEqual(requested_mark_draft_estimate, mark_draft_estimate)

        # mark estimate as re-opened
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates/1439818/messages",
                body=json.dumps(estimate_message_2666246_dict),
                status=201
            )
        mark_draft_estimate = from_dict(data_class=EstimateMessage, data=estimate_message_2666246_dict)
        requested_mark_draft_estimate = self.harvest.mark_draft_estimate(estimate_id= 1439818, event_type= "re-open")
        self.assertEqual(requested_mark_draft_estimate, mark_draft_estimate)

        httpretty.reset()


    def test_estimates(self):
        estimate_1439818_dict = {
                "id":1439818,
                "client_key":"13dc088aa7d51ec687f186b146730c3c75dc7423",
                "number":"1001",
                "purchase_order":"5678",
                "amount":9630.0,
                "tax":5.0,
                "tax_amount":450.0,
                "tax2":2.0,
                "tax2_amount":180.0,
                "discount":10.0,
                "discount_amount":1000.0,
                "subject":"Online Store - Phase 2",
                "notes":"Some notes about the estimate",
                "state":"sent",
                "issue_date":"2017-06-01",
                "sent_at":"2017-06-27T16:11:33Z",
                "created_at":"2017-06-27T16:11:24Z",
                "updated_at":"2017-06-27T16:13:56Z",
                "accepted_at":None,
                "declined_at":None,
                "currency":"USD",
                "client":{
                    "id":5735776,
                    "name":"123 Industries"
                    },
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                        {
                            "id":53334195,
                            "kind":"Service",
                            "description":"Phase 2 of the Online Store",
                            "quantity":100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                            "unit_price":100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                            "amount":10000.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                            "taxed":True,
                            "taxed2":True
                        }
                    ]
            }

        estimate_1439814_dict = {
                "id":1439814,
                "client_key":"a5ffaeb30c55776270fcd3992b70332d769f97e7",
                "number":"1000",
                "purchase_order":"1234",
                "amount":21000.0,
                "tax":5.0,
                "tax_amount":1000.0,
                "tax2":None,
                "tax2_amount":0.0,
                "discount":None,
                "discount_amount":0.0,
                "subject":"Online Store - Phase 1",
                "notes":"Some notes about the estimate",
                "state":"accepted",
                "issue_date":"2017-01-01",
                "sent_at":"2017-06-27T16:10:30Z",
                "created_at":"2017-06-27T16:09:33Z",
                "updated_at":"2017-06-27T16:12:00Z",
                "accepted_at":"2017-06-27T16:10:32Z",
                "declined_at":None,
                "currency":"USD",
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                    {
                        "id":57531966,
                        "kind":"Service",
                        "description":"Phase 1 of the Online Store",
                        "quantity":1.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "unit_price":20000.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "amount":20000.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "taxed":True,
                        "taxed2":False
                    }
                ]
            }

        estimate_1439827_dict = {
                "id":1439827,
                "client_key":"ddd4504a68fb7339138d0c2ea89ba05a3cf12aa8",
                "number":"1002",
                "purchase_order":None,
                "amount":5000.0,
                "tax":None,
                "tax_amount":0.0,
                "tax2":None,
                "tax2_amount":0.0,
                "discount":None,
                "discount_amount":0.0,
                "subject":"Project Quote",
                "notes":None,
                "state":"draft",
                "issue_date":None,
                "sent_at":None,
                "created_at":"2017-06-27T16:16:24Z",
                "updated_at":"2017-06-27T16:16:24Z",
                "accepted_at":None,
                "declined_at":None,
                "currency":"USD",
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "creator":{
                        "id":1782884,
                        "name":"Bob Powell"
                    },
                "line_items":[
                        {
                            "id":53339199,
                            "kind":"Service",
                            "description":"Project Description",
                            "quantity":1.0,
                            "unit_price":5000.0,
                            "amount":5000.0,
                            "taxed":False,
                            "taxed2":False
                        }
                    ]
            }

        estimates_dict = {
                "estimates":[estimate_1439818_dict, estimate_1439814_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/estimates?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/estimates?page=1&per_page=100"
                    }
            }

        # estimates
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/estimates?page=1&per_page=100",
                body=json.dumps(estimates_dict),
                status=200
            )
        estimates = from_dict(data_class=Estimates, data=estimates_dict)
        requested_estimates = self.harvest.estimates()
        self.assertEqual(requested_estimates, estimates)

        # get_estimte
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/estimates/1439818",
                body=json.dumps(estimate_1439818_dict),
                status=200
            )
        estimate = from_dict(data_class=Estimate, data=estimate_1439818_dict)
        requested_estimate = self.harvest.get_estimte(estimate_id= 1439818)
        self.assertEqual(requested_estimate, estimate)

        # create_estimate
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimates",
                body=json.dumps(estimate_1439827_dict),
                status=201
            )
        new_estimate = from_dict(data_class=Estimate, data=estimate_1439827_dict)
        requested_new_estimate = self.harvest.create_estimate(client_id= 5735774, subject= "ABC Project Quote", line_items= [{"kind" : "Service", "description" : "ABC Project Quote", "unit_price" : 5000.0}])
        self.assertEqual(requested_new_estimate, new_estimate)

        # update_estimate
        estimate_1439827_dict["purchase_order"] = "2345"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/estimates/1439827",
                body=json.dumps(estimate_1439827_dict),
                status=200
            )
        new_estimate = from_dict(data_class=Estimate, data=estimate_1439827_dict)
        requested_new_estimate = self.harvest.update_estimate(estimate_id= 1439827, purchase_order= "2345")
        self.assertEqual(requested_new_estimate, new_estimate)

        # create_estimate_line_item
        estimate_1439827_dict["line_items"].append(
                {
                    "id":53339200,
                    "kind":"Service",
                    "description":"Another Project",
                    "quantity":1.0,
                    "unit_price":1000.0,
                    "amount":1000.0,
                    "taxed":False,
                    "taxed2":False
                }
            )
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/estimates/1439827",
                body=json.dumps(estimate_1439827_dict),
                status=200
            )
        new_estimate_line_item = from_dict(data_class=Estimate, data=estimate_1439827_dict)
        requested_new_estimate_line_item = self.harvest.create_estimate_line_item(estimate_id= 1439827, line_items= [{"kind" : "Service", "description" : "Another Project", "unit_price" : 1000.0}])
        self.assertEqual(requested_new_estimate_line_item, new_estimate_line_item)

        # delete_estimate_line_items
        del(estimate_1439827_dict["line_items"][0])
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/estimates/1439827",
                body=json.dumps(estimate_1439827_dict),
                status=200
            )
        new_estimate_line_item = from_dict(data_class=Estimate, data=estimate_1439827_dict)
        requested_new_estimate_line_item = self.harvest.create_estimate_line_item(estimate_id= 1439827, line_items= [{"id" : 53339199, "_destroy" : True}])
        self.assertEqual(requested_new_estimate_line_item, new_estimate_line_item)

        # delete_estimate
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/estimates/1439827",
                status=200
            )
        requested_deleted_estimate = self.harvest.delete_estimate(estimate_id= 1439827)
        self.assertEqual(requested_deleted_estimate, None)

        httpretty.reset()


    def test_estimate_item_categories(self):
        estimate_item_category_1378704_dict = {
                "id":1378704,
                "name":"Product",
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        estimate_item_category_1378703_dict = {
                "id":1378703,
                "name":"Service",
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        estimate_item_category_1379244_dict = {
                "id":1379244,
                "name":"Hosting",
                "created_at":"2017-06-27T16:06:35Z",
                "updated_at":"2017-06-27T16:06:35Z"
            }

        estimate_item_categories_dict = {
                "estimate_item_categories":[estimate_item_category_1378704_dict, estimate_item_category_1378703_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/estimate_item_categories?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/estimate_item_categories?page=1&per_page=100"
                    }
            }

        # estimate_item_categories
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/estimate_item_categories?page=1&per_page=100",
                body=json.dumps(estimate_item_categories_dict),
                status=200
            )
        estimate_item_categories = from_dict(data_class=EstimateItemCategories, data=estimate_item_categories_dict)
        requested_estimate_item_categories = self.harvest.estimate_item_categories()
        self.assertEqual(requested_estimate_item_categories, estimate_item_categories)

        # get_estimate_item_category
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/estimate_item_categories/1378704",
                body=json.dumps(estimate_item_category_1378704_dict),
                status=200
            )
        estimate_item_category = from_dict(data_class=EstimateItemCategory, data=estimate_item_category_1378704_dict)
        requested_estimate_item_category = self.harvest.get_estimate_item_category(estimate_item_category_id=1378704)
        self.assertEqual(requested_estimate_item_category, estimate_item_category)

        # create_estimate_item_category
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/estimate_item_categories",
                body=json.dumps(estimate_item_category_1379244_dict),
                status=201
            )
        new_estimate_item_category = from_dict(data_class=EstimateItemCategory, data=estimate_item_category_1379244_dict)
        requested_new_estimate_item_category = self.harvest.create_estimate_item_category(name= "Hosting")
        self.assertEqual(requested_new_estimate_item_category, new_estimate_item_category)

        # update_estimate_item_category
        estimate_item_category_1379244_dict["name"] = "Transportation"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/estimate_item_categories/1379244",
                body=json.dumps(estimate_item_category_1379244_dict),
                status=200
            )
        updated_estimate_item_category = from_dict(data_class=EstimateItemCategory, data=estimate_item_category_1379244_dict)
        requested_updated_estimate_item_category = self.harvest.update_estimate_item_category(estimate_item_category_id= 1379244, name= "Transportation")
        self.assertEqual(requested_updated_estimate_item_category, updated_estimate_item_category)

        # delete_estimate_item_category
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/estimate_item_categories/1379244",
                status=200
            )
        requested_deleted_estimate_item_category = self.harvest.delete_estimate_item_category(estimate_item_id= 1379244)
        self.assertEqual(requested_deleted_estimate_item_category, None)

        httpretty.reset()


    def test_expenses(self):
        expense_15296442_dict = {
                "id":15296442,
                "notes":"Lunch with client",
                "total_cost":33.35,
                "units":1.0,
                "is_closed":False,
                "is_locked":True,
                "is_billed":True,
                "locked_reason":"Expense is invoiced.",
                "spent_date":"2017-03-03",
                "created_at":"2017-06-27T15:09:54Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "billable":True,
                "receipt":{
                        "url":"https://{ACCOUNT_SUBDOMAIN}.harvestapp.com/expenses/15296442/receipt",
                        "file_name":"lunch_receipt.gif",
                        "file_size":39410,
                        "content_type":"image/gif"
                    },
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "user_assignment":{
                        "id":125068553,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "expense_category":{
                        "id":4195926,
                        "name":"Meals",
                        "unit_price":None,
                        "unit_name":None
                    },
                "client":{
                        "id":5735774,
                        "name":"ABC Corp",
                        "currency":"USD"
                    },
                "invoice":{
                        "id":13150403,
                        "number":"1001"
                    }
            }

        expense_15296423_dict = {
                "id":15296423,
                "notes":"Hotel stay for meeting",
                "total_cost":100.0,
                "units":1.0,
                "is_closed":True,
                "is_locked":True,
                "is_billed":False,
                "locked_reason":"The project is locked for this time period.",
                "spent_date":"2017-03-01",
                "created_at":"2017-06-27T15:09:17Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "billable":True,
                "receipt":None,
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "user_assignment":{
                        "id":125068554,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "expense_category":{
                        "id":4197501,
                        "name":"Lodging",
                        "unit_price":None,
                        "unit_name":None
                    },
                "client":{
                        "id":5735776,
                        "name":"123 Industries",
                        "currency":"EUR"
                    },
                "invoice":None
            }

        expense_15297032_dict = {
                "id":15297032,
                "notes":None,
                "total_cost":13.59,
                "units":1.0,
                "is_closed":False,
                "is_locked":False,
                "is_billed":False,
                "locked_reason":None,
                "spent_date":"2017-03-01",
                "created_at":"2017-06-27T15:42:27Z",
                "updated_at":"2017-06-27T15:42:27Z",
                "billable":True,
                "receipt":None,
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "user_assignment":{
                        "id":125068553,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "expense_category":{
                        "id":4195926,
                        "name":"Meals",
                        "unit_price":None,
                        "unit_name":None
                    },
                "client":{
                    "id":5735776,
                        "name":"123 Industries",
                        "currency":"EUR"
                    },
                "invoice":None
            }

        expenses_dict = {
        "expenses":[expense_15296442_dict, expense_15296423_dict],
        "per_page":100,
        "total_pages":1,
        "total_entries":2,
        "next_page":None,
        "previous_page":None,
        "page":1,
        "links":{
                "first":"https://api.harvestapp.com/v2/expenses?page=1&per_page=100",
                "next":None,
                "previous":None,
                "last":"https://api.harvestapp.com/v2/expenses?page=1&per_page=100"
            }
        }

        # expenses
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/expenses?page=1&per_page=100",
                body=json.dumps(expenses_dict),
                status=200
            )
        expenses = from_dict(data_class=Expenses, data=expenses_dict)
        requested_expenses = self.harvest.expenses()
        self.assertEqual(requested_expenses, expenses)

        # get_expense
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/expenses/15296442",
                body=json.dumps(expense_15296442_dict),
                status=200
            )
        expense = from_dict(data_class=Expense, data=expense_15296442_dict)
        requested_expense = self.harvest.get_expense(expense_id=15296442)
        self.assertEqual(requested_expense, expense)

        # create_expense
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/expenses",
                body=json.dumps(expense_15297032_dict),
                status=201
            )
        new_expense = from_dict(data_class=Expense, data=expense_15297032_dict)
        requested_new_expense = self.harvest.create_expense(project_id= 14308069, expense_category_id= 4195926, spent_date= "2017-03-01", user_id= 1782959, total_cost= 13.59)
        self.assertEqual(requested_new_expense, new_expense)

        # update_expense
        receipt = {'file_name':'dinner_receipt.gif', 'content_type': 'image/gif', 'files': {'receipt': ('dinner_receipt.gif', 'open(filename, "rb")', 'image/png', {'Expires': '0'})}, "url": "https://{ACCOUNT_SUBDOMAIN}.harvestapp.com/expenses/15297032/receipt", "file_size": 39410 }
        expense_15297032_dict['notes'] = "Dinner"
        expense_15297032_dict['receipt'] = receipt
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/expenses/15297032",
                body=json.dumps(expense_15297032_dict),
                status=200
            )
        updated_expense = from_dict(data_class=Expense, data=expense_15297032_dict)
        requested_updated_expense = self.harvest.update_expense(expense_id= 15297032, notes= "Dinner", receipt= receipt)
        self.assertEqual(requested_updated_expense, updated_expense)

        # delete_expense
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/expenses/15297032",
                status=200
            )
        requested_deleted_expense = self.harvest.delete_expense(expense_id= 15297032)
        self.assertEqual(requested_deleted_expense, None)

        httpretty.reset()


    def test_expense_categories(self):
        expense_category_4197501_dict = {
                "id":4197501,
                "name":"Lodging",
                "unit_name":None,
                "unit_price":None,
                "is_active":True,
                "created_at":"2017-06-27T15:01:32Z",
                "updated_at":"2017-06-27T15:01:32Z"
            }

        expense_category_4195930_dict = {
                "id":4195930,
                "name":"Mileage",
                "unit_name":"mile",
                "unit_price":0.535,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        expense_category_4195928_dict = {
                "id":4195928,
                "name":"Transportation",
                "unit_name":None,
                "unit_price":None,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        expense_category_4195926_dict = {
                "id":4195926,
                "name":"Meals",
                "unit_name":None,
                "unit_price":None,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:41:00Z"
            }

        expense_category_4197514_dict = {
                "id":4197514,
                "name":"Other",
                "unit_name":None,
                "unit_price":None,
                "is_active":True,
                "created_at":"2017-06-27T15:04:23Z",
                "updated_at":"2017-06-27T15:04:23Z"
            }

        expense_categories_dict = {
                "expense_categories":[expense_category_4197501_dict, expense_category_4195930_dict, expense_category_4195928_dict, expense_category_4195926_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":4,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/expense_categories?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/expense_categories?page=1&per_page=100"
                    }
            }

        # expense_categories
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/expense_categories?page=1&per_page=100",
                body=json.dumps(expense_categories_dict),
                status=200
            )
        expense_categories = from_dict(data_class=ExpenseCategories, data=expense_categories_dict)
        requested_expense_categories = self.harvest.expense_categories()
        self.assertEqual(requested_expense_categories, expense_categories)

        # get_expense_category
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/expense_categories/4197501",
                body=json.dumps(expense_category_4197501_dict),
                status=200
            )
        expense_category = from_dict(data_class=ExpenseCategory, data=expense_category_4197501_dict)
        requested_expense_category = self.harvest.get_expense_category(expense_category_id= 4197501)
        self.assertEqual(requested_expense_category, expense_category)

        # create_expense_category
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/expense_categories",
                body=json.dumps(expense_category_4197514_dict),
                status=201
            )
        new_expense_category = from_dict(data_class=ExpenseCategory, data=expense_category_4197514_dict)
        requested_new_expense_category = self.harvest.create_expense_category(name= "Other")
        self.assertEqual(requested_new_expense_category, new_expense_category)

        # update_expense_category
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/expense_categories/4197514",
                body=json.dumps(expense_category_4197514_dict),
                status=201
            )
        updated_expense_category = from_dict(data_class=ExpenseCategory, data=expense_category_4197514_dict)
        requested_updated_expense_category = self.harvest.update_expense_category(expense_category_id= 4197514)
        self.assertEqual(requested_updated_expense_category, updated_expense_category)

        # delete_expense_category
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/expense_categories/4197514",
                status=200
            )
        requested_deleted_expense_category = self.harvest.delete_expense_category(expense_category_id= 4197514)
        self.assertEqual(requested_deleted_expense_category, None)

        httpretty.reset()


    def test_tasks(self):
        task_8083800_dict = {
                "id":8083800,
                "name":"Business Development",
                "billable_by_default":False,
                "default_hourly_rate":0.0,
                "is_default":False,
                "is_active":True,
                "created_at":"2017-06-26T22:08:25Z",
                "updated_at":"2017-06-26T22:08:25Z"
            }

        task_8083369_dict = {
                "id":8083369,
                "name":"Research",
                "billable_by_default":False,
                "default_hourly_rate":0.0,
                "is_default":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T21:53:34Z"
            }

        task_8083368_dict = {
                "id":8083368,
                "name":"Project Management",
                "billable_by_default":True,
                "default_hourly_rate":100.0,
                "is_default":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T21:14:10Z"
            }

        task_8083366_dict = {
                "id":8083366,
                "name":"Programming",
                "billable_by_default":True,
                "default_hourly_rate":100.0,
                "is_default":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T21:14:07Z"
            }

        task_8083365_dict = {
                "id":8083365,
                "name":"Graphic Design",
                "billable_by_default":True,
                "default_hourly_rate":100.0,
                "is_default":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T21:14:02Z"
            }

        task_8083782_dict = {
                "id":8083782,
                "name":"New Task Name",
                "billable_by_default":True,
                "default_hourly_rate":0.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "is_default":False,
                "is_active":True,
                "created_at":"2017-06-26T22:04:31Z",
                "updated_at":"2017-06-26T22:04:31Z"
            }

        tasks_dict = {
                "tasks":[task_8083800_dict, task_8083369_dict, task_8083368_dict, task_8083366_dict, task_8083365_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":5,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/tasks?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/tasks?page=1&per_page=100"
                    }
            }

        # tasks
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/tasks?page=1&per_page=100",
                body=json.dumps(tasks_dict),
                status=200
            )
        tasks = from_dict(data_class=Tasks, data=tasks_dict)
        requested_tasks = self.harvest.tasks()
        self.assertEqual(requested_tasks, tasks)

        # get_task
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/tasks/8083800",
                body=json.dumps(task_8083800_dict),
                status=200
            )
        task = from_dict(data_class=Task, data=task_8083800_dict)
        requested_task = self.harvest.get_task(task_id= 8083800)
        self.assertEqual(requested_task, task)

        # create_task
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/tasks",
                body=json.dumps(task_8083782_dict),
                status=201
            )
        new_task = from_dict(data_class=Task, data=task_8083782_dict)
        requested_new_task = self.harvest.create_task(name= "New Task Name", default_hourly_rate= 120.0) # Harvest doco is wrong. they use hourly_rate not default_hourly_rate
        self.assertEqual(requested_new_task, new_task)

        # update_task
        task_8083782_dict["is_default"] = True
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/tasks/8083782",
                body=json.dumps(task_8083782_dict),
                status=200
            )
        updated_task = from_dict(data_class=Task, data=task_8083782_dict)
        requested_updated_task = self.harvest.update_task(task_id=8083782, is_default=True)
        self.assertEqual(requested_updated_task, updated_task)

        # delete_task
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/tasks/8083782",
                status=200
            )
        requested_deleted_task = self.harvest.delete_task(task_id=8083782)
        self.assertEqual(requested_deleted_task, None)

        httpretty.reset()


    def test_time_entries(self):
        time_entry_636709355_dict = {
                "id":636709355,
                "spent_date":"2017-03-02",
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "project":{
                        "id":14307913,
                        "name":"Marketing Website"
                    },
                "task":{
                        "id":8083365,
                        "name":"Graphic Design"
                    },
                "user_assignment":{
                        "id":125068553,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "task_assignment":{
                    "id":155502709,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:36:23Z",
                        "updated_at":"2017-06-26T21:36:23Z",
                        "hourly_rate":100.0,
                        "budget":None
                    },
                "hours":2.0,
                "notes":"Adding CSS styling",
                "created_at":"2017-06-27T15:50:15Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "is_locked":True,
                "locked_reason":"Item Approved and Locked for this Time Period",
                "is_closed":True,
                "is_billed":False,
                "timer_started_at":None,
                "started_time":"3:00pm",
                "ended_time":"5:00pm",
                "is_running":False,
                "invoice":None,
                "external_reference":None,
                "billable":True,
                "budgeted":True,
                "billable_rate":100.0,
                "cost_rate":50.0
            }

        time_entry_636708723_dict = {
                "id":636708723,
                "spent_date":"2017-03-01",
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1"
                    },
                "task":{
                        "id":8083366,
                        "name":"Programming"
                    },
                "user_assignment":{
                        "id":125068554,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "task_assignment":{
                        "id":155505014,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None
                    },
                "hours":1.0,
                "notes":"Importing products",
                "created_at":"2017-06-27T15:49:28Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "is_locked":True,
                "locked_reason":"Item Invoiced and Approved and Locked for this Time Period",
                "is_closed":True,
                "is_billed":True,
                "timer_started_at":None,
                "started_time":"1:00pm",
                "ended_time":"2:00pm",
                "is_running":False,
                "invoice":{
                        "id":13150403,
                        "number":"1001"
                    },
                "external_reference":None,
                "billable":True,
                "budgeted":True,
                "billable_rate":100.0,
                "cost_rate":50.0
            }

        time_entry_636708574_dict = {
                "id":636708574,
                "spent_date":"2017-03-01",
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1"
                    },
                "task":{
                        "id":8083369,
                        "name":"Research"
                    },
                "user_assignment":{
                        "id":125068554,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "task_assignment":{
                        "id":155505016,
                        "billable":False,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:54:06Z",
                        "hourly_rate":100.0,
                        "budget":None
                    },
                "hours":1.0,
                "notes":"Evaluating 3rd party libraries",
                "created_at":"2017-06-27T15:49:17Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "is_locked":True,
                "locked_reason":"Item Approved and Locked for this Time Period",
                "is_closed":True,
                "is_billed":False,
                "timer_started_at":None,
                "started_time":"11:00am",
                "ended_time":"12:00pm",
                "is_running":False,
                "invoice":None,
                "external_reference":None,
                "billable":False,
                "budgeted":True,
                "billable_rate":None,
                "cost_rate":50.0
            }

        time_entry_636707831_dict = {
                "id":636707831,
                "spent_date":"2017-03-01",
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "client":{
                        "id":5735776,
                        "name":"123 Industries"
                    },
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1"
                    },
                "task":{
                        "id":8083368,
                        "name":"Project Management"
                    },
                "user_assignment":{
                        "id":125068554,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "task_assignment":{
                        "id":155505015,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None
                    },
                "hours":2.0,
                "notes":"Planning meetings",
                "created_at":"2017-06-27T15:48:24Z",
                "updated_at":"2017-06-27T16:47:14Z",
                "is_locked":True,
                "locked_reason":"Item Invoiced and Approved and Locked for this Time Period",
                "is_closed":True,
                "is_billed":True,
                "timer_started_at":None,
                "started_time":"9:00am",
                "ended_time":"11:00am",
                "is_running":False,
                "invoice":{
                        "id":13150403,
                        "number":"1001"
                    },
                "external_reference":None,
                "billable":True,
                "budgeted":True,
                "billable_rate":100.0,
                "cost_rate":50.0
            }

        time_entry_636718192_dict = {
                "id":636718192,
                "spent_date":"2017-03-21",
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    },
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "project":{
                        "id":14307913,
                        "name":"Marketing Website"
                    },
                "task":{
                        "id":8083365,
                        "name":"Graphic Design"
                    },
                "user_assignment":{
                        "id":125068553,
                        "is_project_manager":True,
                        "is_active":True,
                        "budget":None,
                        "created_at":"2017-06-26T22:32:52Z",
                        "updated_at":"2017-06-26T22:32:52Z",
                        "hourly_rate":100.0
                    },
                "task_assignment":{
                        "id":155502709,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:36:23Z",
                        "updated_at":"2017-06-26T21:36:23Z",
                        "hourly_rate":100.0,
                        "budget":None
                    },
                "hours":1.0,
                "notes":None,
                "created_at":"2017-06-27T16:01:23Z",
                "updated_at":"2017-06-27T16:01:23Z",
                "is_locked":False,
                "locked_reason":None,
                "is_closed":False,
                "is_billed":False,
                "timer_started_at":None,
                "started_time":None,
                "ended_time":None,
                "is_running":False,
                "invoice":None,
                "external_reference": None,
                "billable":True,
                "budgeted":True,
                "billable_rate":100.0,
                "cost_rate":50.0
            }

        time_entry_662204379_dict = {
                "id": 662204379,
                "spent_date": "2017-03-21",
                "user": {
                        "id": 1795925,
                        "name": "Jane Smith"
                    },
                "client": {
                        "id": 5735776,
                        "name": "123 Industries"
                    },
                "project": {
                        "id": 14808188,
                        "name": "Task Force"
                    },
                "task": {
                        "id": 8083366,
                        "name": "Programming"
                    },
                "user_assignment": {
                        "id": 130403296,
                        "is_project_manager": True,
                        "is_active": True,
                        "budget": None,
                        "created_at": "2017-08-22T17:36:54Z",
                        "updated_at": "2017-08-22T17:36:54Z",
                        "hourly_rate": 100.00 # TODO: this is supposed to be an int. Something isn't casting int to float.
                    },
                "task_assignment": {
                        "id": 160726645,
                        "billable": True,
                        "is_active": True,
                        "created_at": "2017-08-22T17:36:54Z",
                        "updated_at": "2017-08-22T17:36:54Z",
                        "hourly_rate": 100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "budget": None
                    },
                "hours": 0.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "notes": None,
                "created_at": "2017-08-22T17:40:24Z",
                "updated_at": "2017-08-22T17:40:24Z",
                "is_locked": False,
                "locked_reason": None,
                "is_closed": False,
                "is_billed": False,
                "timer_started_at": "2017-08-22T17:40:24Z",
                "started_time": "11:40am",
                "ended_time": None,
                "is_running": True,
                "invoice": None,
                "external_reference": None,
                "billable": True,
                "budgeted": False,
                "billable_rate": 100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "cost_rate": 75.00 # TODO: this is supposed to be an int. Something isn't casting int to float.
            }

        time_entry_662202797_dict = {
                "id": 662202797,
                "spent_date": "2017-03-21",
                "user": {
                        "id": 1795925,
                        "name": "Jane Smith"
                    },
                "client": {
                        "id": 5735776,
                        "name": "123 Industries"
                    },
                "project": {
                        "id": 14808188,
                        "name": "Task Force"
                    },
                "task": {
                        "id": 8083366,
                        "name": "Programming"
                    },
                "user_assignment": {
                        "id": 130403296,
                        "is_project_manager": True,
                        "is_active": True,
                        "budget": None,
                        "created_at": "2017-08-22T17:36:54Z",
                        "updated_at": "2017-08-22T17:36:54Z",
                        "hourly_rate": 100.00 # TODO: this is supposed to be an int. Something isn't casting int to float.
                    },
                "task_assignment": {
                        "id": 160726645,
                        "billable": True,
                        "is_active": True,
                        "created_at": "2017-08-22T17:36:54Z",
                        "updated_at": "2017-08-22T17:36:54Z",
                        "hourly_rate": 100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                        "budget": None
                    },
                "hours": 0.02,
                "notes": None,
                "created_at": "2017-08-22T17:37:13Z",
                "updated_at": "2017-08-22T17:38:31Z",
                "is_locked": False,
                "locked_reason": None,
                "is_closed": False,
                "is_billed": False,
                "timer_started_at": None,
                "started_time": "11:37am",
                "ended_time": "11:38am",
                "is_running": False,
                "invoice": None,
                "external_reference": None,
                "billable": True,
                "budgeted": False,
                "billable_rate": 100.00, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "cost_rate": 75.00 # TODO: this is supposed to be an int. Something isn't casting int to float.
            }

        time_entries_dict = {
                "time_entries":[time_entry_636709355_dict, time_entry_636708723_dict, time_entry_636708574_dict, time_entry_636707831_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":4,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/time_entries?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/time_entries?page=1&per_page=100"
                    }
            }

        company_dict = {
                "base_uri":"https://{ACCOUNT_SUBDOMAIN}.harvestapp.com",
                "full_domain":"{ACCOUNT_SUBDOMAIN}.harvestapp.com",
                "name":"API Examples",
                "is_active":False,
                "week_start_day":"Monday",
                "wants_timestamp_timers":False,
                "time_format":"hours_minutes",
                "plan_type":"sponsored",
                "expense_feature":True,
                "invoice_feature":True,
                "estimate_feature":True,
                "approval_required":True,
                "clock":"12h",
                "decimal_symbol":".",
                "thousands_separator":",",
                "color_scheme":"orange"
            }

        # time_entries
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/time_entries?page=1&per_page=100",
                body=json.dumps(time_entries_dict),
                status=200
            )
        time_entries = from_dict(data_class=TimeEntries, data=time_entries_dict)
        requested_time_entries = self.harvest.time_entries()
        self.assertEqual(requested_time_entries, time_entries)

        # get_time_entry
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/time_entries/636708723",
                body=json.dumps(time_entry_636708723_dict),
                status=200
            )
        time_entry = from_dict(data_class=TimeEntry, data=time_entry_636708723_dict)
        requested_time_entry = self.harvest.get_time_entry(time_entry_id=636708723)
        self.assertEqual(requested_time_entries, time_entries)

        # create_time_entry via duration
        company_dict['wants_timestamp_timers'] = False
        httpretty.register_uri(httpretty.GET, "https://api.harvestapp.com/api/v2/company", body=json.dumps(company_dict), status=200)
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/time_entries",
                body=json.dumps(time_entry_636718192_dict),
                status=201
            )
        new_time_entry0 = from_dict(data_class=TimeEntry, data=time_entry_636718192_dict)
        requested_new_time_entry0 = self.harvest.create_time_entry_via_duration(project_id= 14307913, task_id= 8083365, spent_date= "2017-03-21", user_id= 1782959, hours= 1.0)
        self.assertEqual(requested_new_time_entry0, new_time_entry0)

        # create_time_entry via start and end time
        company_dict['wants_timestamp_timers'] = True
        httpretty.register_uri(httpretty.GET, "https://api.harvestapp.com/api/v2/company", body=json.dumps(company_dict), status=200)
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/time_entries",
                body=json.dumps(time_entry_636718192_dict),
                status=201
            )
        new_time_entry1 = from_dict(data_class=TimeEntry, data=time_entry_636718192_dict)
        requested_new_time_entry1 = self.harvest.create_time_entry_via_start_and_end_time(project_id= 14307913, task_id= 8083365, spent_date= "2017-03-21", user_id= 1782959, started_time= "8:00am", ended_time= "9:00am")
        self.assertEqual(requested_new_time_entry1, new_time_entry1)

        # update_time_entry
        time_entry_636718192_dict['notes'] = "Updated notes"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/time_entries/636718192",
                body=json.dumps(time_entry_636718192_dict),
                status=200
            )
        updated_time_entry = from_dict(data_class=TimeEntry, data=time_entry_636718192_dict)
        requested_updated_time_entry = self.harvest.update_time_entry(time_entry_id= 636718192, notes= "Updated notes")
        self.assertEqual(requested_updated_time_entry, updated_time_entry)

        # delete_time_entry_external_reference
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/time_entries/636718192/external_reference",
                status=200
            )
        requested_deleted_time_entry_external_reference = self.harvest.delete_time_entry_external_reference(time_entry_id= 636718192)
        self.assertEqual(requested_deleted_time_entry_external_reference, None)

        # delete_time_entry
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/time_entries/636718192",
                status=200
            )
        requested_deleted_time_entry = self.harvest.delete_time_entry(time_entry_id= 636718192)
        self.assertEqual(requested_deleted_time_entry, None)

        # restart_a_stopped_time_entry
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/time_entries/662204379/restart", # harvest have the wrong time entry id in their doco
                body=json.dumps(time_entry_662204379_dict),
                status=200
            )
        restarted_time_entry = from_dict(data_class=TimeEntry, data=time_entry_662204379_dict)
        requested_restarted_time_entry = self.harvest.restart_a_stopped_time_entry(time_entry_id= 662204379)
        self.assertEqual(requested_restarted_time_entry, restarted_time_entry)

        # stop_a_running_time_entry
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/time_entries/662202797/stop",
                body=json.dumps(time_entry_662202797_dict),
                status=200
            )
        stopped_time_entry = from_dict(data_class=TimeEntry, data=time_entry_662202797_dict)
        requested_stopped_time_entry = self.harvest.stop_a_running_time_entry(time_entry_id= 662202797)
        self.assertEqual(requested_stopped_time_entry, stopped_time_entry)


        httpretty.reset()

    def test_project_user_assignments(self):
        user_assignment_130403297_dict = {
                "id":130403297,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":False,
                "budget":None,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    }
            }

        user_assignment_130403296_dict = {
                "id":130403296,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":True,
                "budget":None,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "user":{
                        "id":1795925,
                        "name":"Jason Dew"
                    }
            }

        user_assignment_125068554_dict = {
                "id":125068554,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":True,
                "budget":None,
                "created_at":"2017-06-26T22:32:52Z",
                "updated_at":"2017-06-26T22:32:52Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    }
            }


        user_assignment_125068553_dict = {
                "id":125068553,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":True,
                "budget":None,
                "created_at":"2017-06-26T22:32:52Z",
                "updated_at":"2017-06-26T22:32:52Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "user":{
                        "id":1782959,
                        "name":"Kim Allen"
                    }
            }

        user_assignment_125066109_dict = {
                "id":125066109,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":False,
                "budget":None,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:52:18Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "user":{
                        "id":1782884,
                        "name":"Jeremy Israelsen"
                    }
            }

        user_assignment_125063975_dict = {
                "id":125063975,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":True,
                "budget":None,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:36:23Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "user":{
                        "id":1782884,
                        "name":"Jeremy Israelsen"
                    }
            }

        user_assignment_125068758_dict = {
                "id":125068758,
                "is_project_manager":False,
                "is_active":True,
                "use_default_rates":False,
                "budget":None,
                "created_at":"2017-06-26T22:36:01Z",
                "updated_at":"2017-06-26T22:36:01Z",
                "hourly_rate":75.5,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "user":{
                        "id":1782974,
                        "name":"Jim Allen"
                    }
            }

        user_assignments_dict = {
                "user_assignments":[user_assignment_130403297_dict, user_assignment_130403296_dict, user_assignment_125068554_dict, user_assignment_125068553_dict, user_assignment_125066109_dict, user_assignment_125063975_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":6,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/user_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/user_assignments?page=1&per_page=100"
                    }
            }

        project_user_assignments_dict = {
                "user_assignments":[user_assignment_125068554_dict, user_assignment_125066109_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/projects/14308069/user_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/projects/14308069/user_assignments?page=1&per_page=100"
                    }
            }

        # user_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/user_assignments?page=1&per_page=100",
                body=json.dumps(user_assignments_dict),
                status=200
            )
        user_assignments = from_dict(data_class=UserAssignments, data=user_assignments_dict)
        requested_user_assignments = self.harvest.user_assignments()
        self.assertEqual(requested_user_assignments, user_assignments)

        # project_user_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects/14308069/user_assignments",
                body=json.dumps(project_user_assignments_dict),
                status=200
            )
        project_user_assignments = from_dict(data_class=UserAssignments, data=project_user_assignments_dict)
        requested_project_user_assignments = self.harvest.project_user_assignments(project_id= 14308069)
        self.assertEqual(requested_project_user_assignments, project_user_assignments)

        # get_user_assignment
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects/14308069/user_assignments/125068554",
                body=json.dumps(user_assignment_125068554_dict),
                status=200
            )
        user_assignment = from_dict(data_class=UserAssignment, data=user_assignment_125068554_dict)
        requested_user_assignment = self.harvest.get_user_assignment(project_id= 14308069, user_assignment_id= 125068554)
        self.assertEqual(requested_user_assignment, user_assignment)

        # create_user_assignment
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/projects/14308069/user_assignments",
                body=json.dumps(user_assignment_125068758_dict),
                status=201
            )
        created_user_assignment = from_dict(data_class=UserAssignment, data=user_assignment_125068758_dict)
        requested_created_user_assignment = self.harvest.create_user_assignment(project_id= 14308069, user_id= 1782974, use_default_rates= False, hourly_rate= 75.50)
        self.assertEqual(requested_created_user_assignment, created_user_assignment)

        # update_user_assignment
        user_assignment_125068758_dict['budget'] = 120.0 # TODO: this is supposed to be an int. Something isn't casting int to float.
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/projects/14308069/user_assignments/125068758",
                body=json.dumps(user_assignment_125068758_dict),
                status=200
            )
        updated_user_assignment = from_dict(data_class=UserAssignment, data=user_assignment_125068758_dict)
        requested_updated_user_assignment = self.harvest.update_user_assignment(project_id= 14308069, user_assignment_id= 125068758, budget= 120)
        self.assertEqual(requested_updated_user_assignment, updated_user_assignment)

        # delete_user_assignment
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/projects/14308069/user_assignments/125068758",
                status=200
            )
        requested_deleted_user_assignment = self.harvest.delete_user_assignment(project_id= 14308069, user_assignment_id= 125068758)
        self.assertEqual(requested_deleted_user_assignment, None)

        httpretty.reset()


    def test_project_task_assignments(self):
        task_assignment_160726647_dict = {
                "id":160726647,
                "billable":False,
                "is_active":True,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "task":{
                        "id":8083369,
                        "name":"Research"
                    }
            }

        task_assignment_160726646_dict = {
                "id":160726646,
                "billable":True,
                "is_active":True,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "task":{
                        "id":8083368,
                        "name":"Project Management"
                    }
            }

        task_assignment_160726645_dict = {
                "id":160726645,
                "billable":True,
                "is_active":True,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "task":{
                        "id":8083366,
                        "name":"Programming"
                    }
            }

        task_assignment_160726644_dict = {
                "id":160726644,
                "billable":True,
                "is_active":True,
                "created_at":"2017-08-22T17:36:54Z",
                "updated_at":"2017-08-22T17:36:54Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14808188,
                        "name":"Task Force",
                        "code":"TF"
                    },
                "task":{
                        "id":8083365,
                        "name":"Graphic Design"
                    }
            }

        task_assignment_155505153_dict = {
                "id":155505153,
                "billable":False,
                "is_active":True,
                "created_at":"2017-06-26T21:53:20Z",
                "updated_at":"2017-06-26T21:54:31Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "task":{
                        "id":8083369,
                        "name":"Research"
                    }
            }

        task_assignment_155505016_dict = {
                "id":155505016,
                "billable":False,
                "is_active":True,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:54:06Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "task":{
                        "id":8083369,
                        "name":"Research"
                    }
            }

        task_assignment_155505015_dict = {
                "id":155505015,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:52:18Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "task":{
                        "id":8083368,
                        "name":"Project Management"
                    }
            }

        task_assignment_155505014_dict = {
                "id":155505014,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:52:18Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                    "id":14308069,
                    "name":"Online Store - Phase 1",
                    "code":"OS1"
                    },
                "task":{
                    "id":8083366,
                    "name":"Programming"
                    }
            }

        task_assignment_155505013_dict = {
                "id":155505013,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:52:18Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "task":{
                        "id":8083365,
                        "name":"Graphic Design"
                    }
            }

        task_assignment_155502711_dict = {
                "id":155502711,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:36:23Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "task":{
                        "id":8083368,
                        "name":"Project Management"
                    }
            }

        task_assignment_155502710_dict = {
                "id":155502710,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:36:23Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "task":{
                        "id":8083366,
                        "name":"Programming"
                    }
            }

        task_assignment_155502709_dict = {
                "id":155502709,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:36:23Z",
                "hourly_rate":100.0,
                "budget":None,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "task":{
                        "id":8083365,
                        "name":"Graphic Design"
                    }
            }

        task_assignment_155506339_dict = {
                "id":155506339,
                "billable":True,
                "is_active":True,
                "created_at":"2017-06-26T22:10:43Z",
                "updated_at":"2017-06-26T22:10:43Z",
                "hourly_rate":75.5,
                "budget":None,
                "project":{
                        "id":14308069,
                        "name":"Online Store - Phase 1",
                        "code":"OS1"
                    },
                "task":{
                        "id":8083800,
                        "name":"Business Development"
                    }
            }

        task_assignments_dict = {
                "task_assignments": [task_assignment_160726647_dict, task_assignment_160726646_dict, task_assignment_160726645_dict, task_assignment_160726644_dict, task_assignment_155505153_dict, task_assignment_155505016_dict, task_assignment_155505015_dict, task_assignment_155505014_dict, task_assignment_155505013_dict, task_assignment_155502711_dict, task_assignment_155502710_dict, task_assignment_155502709_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":12,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/task_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/task_assignments?page=1&per_page=100"
                    }
            }

        task_assignments_project_14308069_dict = {
                "task_assignments":[task_assignment_155505016_dict, task_assignment_155505015_dict, task_assignment_155505014_dict, task_assignment_155505013_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":4,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/projects/14308069/task_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/projects/14308069/task_assignments?page=1&per_page=100"
                    }
            }

        # task_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/task_assignments?page=1&per_page=100",
                body=json.dumps(task_assignments_dict),
                status=200
            )
        task_assignments = from_dict(data_class=TaskAssignments, data=task_assignments_dict)
        requested_task_assignments = self.harvest.task_assignments()
        self.assertEqual(requested_task_assignments, task_assignments)

        # project_task_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects/14308069/task_assignments?page=1&per_page=100",
                body=json.dumps(task_assignments_project_14308069_dict),
                status=200
            )
        project_task_assignments = from_dict(data_class=TaskAssignments, data=task_assignments_project_14308069_dict)
        requested_project_task_assignments = self.harvest.project_task_assignments(project_id= 14308069)
        self.assertEqual(requested_project_task_assignments, project_task_assignments)

        # get_task_assignment
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects/14308069/task_assignments/155505016",
                body=json.dumps(task_assignment_155505016_dict),
                status=200
            )
        task_assignment = from_dict(data_class=TaskAssignment, data=task_assignment_155505016_dict)
        requested_task_assignment = self.harvest.get_task_assignment(project_id= 14308069, task_assignment_id= 155505016)
        self.assertEqual(requested_task_assignment, task_assignment)

        # create_task_assignment
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/projects/14308069/task_assignments",
                body=json.dumps(task_assignment_155506339_dict),
                status=201
            )
        new_task_assignment = from_dict(data_class=TaskAssignment, data=task_assignment_155506339_dict)
        requested_new_task_assignment = self.harvest.create_task_assignment(project_id= 14308069, task_id= 8083800, is_active= True, billable= True, hourly_rate= 75.50)
        self.assertEqual(requested_new_task_assignment, new_task_assignment)

        # update_task_assignment
        task_assignment_155506339_dict['budget'] = 120.0  # TODO: this is supposed to be an int. Something isn't casting int to float.
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/projects/14308069/task_assignments/155506339",
                body=json.dumps(task_assignment_155506339_dict),
                status=200
            )
        updated_task_assignment = from_dict(data_class=TaskAssignment, data=task_assignment_155506339_dict)
        requested_updated_task_assignment = self.harvest.update_task_assignment(project_id= 14308069, task_assignment_id= 155506339, budget= 120)
        self.assertEqual(requested_updated_task_assignment, updated_task_assignment)

        # delete_task_assignment
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/projects/14308069/task_assignments/155506339",
                status=200
            )
        requested_deleted_task_assignment = self.harvest.delete_task_assignment(project_id= 14308069, task_assignment_id= 155506339)
        self.assertEqual(requested_deleted_task_assignment, None)

        httpretty.reset()

    def test_projects(self):
        project_14308069_dict = {
                "id":14308069,
                "name":"Online Store - Phase 1",
                "code":"OS1",
                "is_active":True,
                "bill_by":"Project",
                "budget":200.0,
                "budget_by":"project",
                "budget_is_monthly":False,
                "notify_when_over_budget":True,
                "over_budget_notification_percentage":80.0,
                "over_budget_notification_date":None,
                "show_budget_to_all":False,
                "created_at":"2017-06-26T21:52:18Z",
                "updated_at":"2017-06-26T21:54:06Z",
                "starts_on":"2017-06-01",
                "ends_on":None,
                "is_billable":True,
                "is_fixed_fee":False,
                "notes":"",
                "client":{
                        "id":5735776,
                        "name":"123 Industries",
                        "currency":"EUR"
                    },
                "cost_budget":None,
                "cost_budget_include_expenses":False,
                "hourly_rate":100.0,
                "fee":None
            }

        project_14307913_dict = {
                "id":14307913,
                "name":"Marketing Website",
                "code":"MW",
                "is_active":True,
                "bill_by":"Project",
                "budget":50.0,
                "budget_by":"project",
                "budget_is_monthly":False,
                "notify_when_over_budget":True,
                "over_budget_notification_percentage":80.0,
                "over_budget_notification_date":None,
                "show_budget_to_all":False,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:54:46Z",
                "starts_on":"2017-01-01",
                "ends_on":"2017-03-31",
                "is_billable":True,
                "is_fixed_fee":False,
                "notes":"",
                "client":{
                        "id":5735774,
                        "name":"ABC Corp",
                        "currency":"USD"
                    },
                "cost_budget":None,
                "cost_budget_include_expenses":False,
                "hourly_rate":100.0,
                "fee":None
            }

        project_14308112_dict = {
                "id":14308112,
                "name":"Your New Project",
                "code":None,
                "is_active":True,
                "bill_by":"Project",
                "budget":10000.0,
                "budget_by":"project",
                "budget_is_monthly":False,
                "notify_when_over_budget":False,
                "over_budget_notification_percentage":80.0,
                "over_budget_notification_date":None,
                "show_budget_to_all":False,
                "created_at":"2017-06-26T21:56:52Z",
                "updated_at":"2017-06-26T21:56:52Z",
                "starts_on":None,
                "ends_on":None,
                "is_billable":True,
                "is_fixed_fee":False,
                "notes":"",
                "client":{
                        "id":5735776,
                        "name":"123 Industries",
                        "currency":"EUR"
                    },
                "cost_budget":None,
                "cost_budget_include_expenses":False,
                "hourly_rate":100.0,
                "fee":None
            }

        project_dict = {
                "projects":[project_14308069_dict, project_14307913_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/projects?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/projects?page=1&per_page=100"
                    }
            }

        # projects
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects?page=1&per_page=100",
                body=json.dumps(project_dict),
                status=200
            )
        projects = from_dict(data_class=Projects, data=project_dict)
        requested_projects = self.harvest.projects()
        self.assertEqual(requested_projects, projects)

        # get_project
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/projects/14308069",
                body=json.dumps(project_14308069_dict),
                status=200
            )
        project = from_dict(data_class=Project, data=project_14308069_dict)
        requested_project = self.harvest.get_project(project_id= 14308069)
        self.assertEqual(requested_project, project)

        # create_project
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/projects",
                body=json.dumps(project_14308112_dict),
                status=201
            )
        new_project = from_dict(data_class=Project, data=project_14308112_dict)
        requested_new_project = self.harvest.create_project(client_id= 5735776, name= "Your New Project", is_billable= True, bill_by= "Project", hourly_rate= 100.0, budget_by= "project", budget= 10000)
        self.assertEqual(requested_new_project, new_project)

        # update_project
        project_14308112_dict["name"] = "New project name"
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/projects/14308112",
                body=json.dumps(project_14308112_dict),
                status=201
            )
        new_project = from_dict(data_class=Project, data=project_14308112_dict)
        requested_new_project = self.harvest.update_project(project_id= 14308112, name= "New project name")
        self.assertEqual(requested_new_project, new_project)

        # delete_project
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/projects/14308112",
                status=200
            )
        requested_deleted_project = self.harvest.delete_project(project_id= 14308112)
        self.assertEqual(requested_deleted_project, None)

        httpretty.reset()

    def test_roles(self):

        role_1782974_dict = {
                "id": 1782974,
                "name": "Founder",
                "user_ids": [8083365],
                "created_at": "2017-06-26T22:34:41Z",
                "updated_at": "2017-06-26T22:34:52Z"
            }

        role_1782959_dict = {
                "id": 1782959,
                "name": "Developer",
                "user_ids": [8083366],
                "created_at": "2017-06-26T22:15:45Z",
                "updated_at": "2017-06-26T22:32:52Z"
            }

        role_1782884_dict = {
                "id": 1782884,
                "name": "Designer",
                "user_ids": [8083367],
                "created_at": "2017-06-26T20:41:00Z",
                "updated_at": "2017-06-26T20:42:25Z"
            }

        role_2_dict = {
                "id": 2,
                "name": "Project Manager",
                "user_ids": [8083365, 8083366],
                "created_at": "2017-06-26T22:34:41Z",
                "updated_at": "2017-06-26T22:34:52Z"
            }

        roles_dict = {
                "roles": [role_1782974_dict, role_1782959_dict, role_1782884_dict],
                "per_page": 100,
                "total_pages": 1,
                "total_entries": 3,
                "next_page": None,
                "previous_page": None,
                "page": 1,
                "links": {
                        "first": "https://api.harvestapp.com/v2/roles?page=1&per_page=100",
                        "next": None,
                        "previous": None,
                        "last": "https://api.harvestapp.com/v2/roles?page=1&per_page=100"
                    }
            }

        # roles
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/roles?page=1&per_page=100",
                body=json.dumps(roles_dict),
                status=200
            )
        roles = from_dict(data_class=Roles, data=roles_dict)
        requested_roles = self.harvest.roles()
        self.assertEqual(requested_roles, roles)

        # get_role
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/roles/1782974",
                body=json.dumps(role_1782974_dict),
                status=200
            )
        role = from_dict(data_class=Role, data=role_1782974_dict)
        requested_role = self.harvest.get_role(role_id= 1782974)
        self.assertEqual(requested_role, role)

        # create_role
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/roles",
                body=json.dumps(role_2_dict),
                status=201
            )
        role = from_dict(data_class=Role, data=role_2_dict)
        requested_role = self.harvest.create_role(name= "Project Manager", user_ids= [8083365,8083366])
        self.assertEqual(requested_role, role)

        # update_role
        role_2_dict["name"] = "PM"
        role_2_dict["user_ids"] = [8083365,8083366,8083367]
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/roles/2",
                body=json.dumps(role_2_dict),
                status=200
            )
        new_role = from_dict(data_class=Role, data=role_2_dict)
        requested_new_role = self.harvest.update_role(role_id= 2, name= "PM", user_ids= [8083365,8083366,8083367])
        self.assertEqual(requested_new_role, new_role)

        # delete_project
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/roles/2",
                status=200
            )
        requested_deleted_role = self.harvest.delete_role(role_id= 2)
        self.assertEqual(requested_deleted_role, None)

        httpretty.reset()

    def test_user_cost_rates(self):
        cost_rate_125068554_dict = {
                "id":125068554,
                "amount":75.0,
                "start_date":None,
                "end_date":"2016-12-31",
                "created_at":"2019-06-26T22:32:52Z",
                "updated_at":"2019-06-26T22:32:52Z"
            }

        cost_rate_125066109_dict = {
                "id":125066109,
                "amount":100.0,
                "start_date":"2017-01-01",
                "end_date":"2017-12-31",
                "created_at":"2019-06-26T21:52:18Z",
                "updated_at":"2019-06-26T21:52:18Z"
            }

        cost_rate_125066110_dict = {
                "id":125066110,
                "amount":125.0,
                "start_date":"2018-01-01",
                "end_date":None,
                "created_at":"2019-06-26T21:52:18Z",
                "updated_at":"2019-06-26T21:52:18Z"
            }

        cost_rate_125068758_dict = {
                "id":125068758,
                "amount":150.0,
                "start_date":"2019-01-01",
                "end_date":None,
                "created_at":"2019-01-06T22:36:01Z",
                "updated_at":"2019-01-06T22:36:01Z"
            }

        cost_rates_dict = {
                "cost_rates":[cost_rate_125068554_dict, cost_rate_125066109_dict, cost_rate_125066110_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":3,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/users/1782974/cost_rates?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/users/1782974/cost_rates?page=1&per_page=100"
                    }
            }

        # user_cost_rates
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/1782974/cost_rates?page=1&per_page=100",
                body=json.dumps(cost_rates_dict),
                status=200
            )
        user_cost_rates = from_dict(data_class=UserCostRates, data=cost_rates_dict)
        requested_user_cost_rates = self.harvest.user_cost_rates(user_id= 1782974)
        self.assertEqual(requested_user_cost_rates, user_cost_rates)

        # get_user_cost_rate
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/1782974/cost_rates/125068554",
                body=json.dumps(cost_rate_125068554_dict),
                status=200
            )
        user_cost_rate = from_dict(data_class=CostRate, data=cost_rate_125068554_dict)
        requested_user_cost_rate = self.harvest.get_user_cost_rate(user_id= 1782974, cost_rate_id= 125068554)
        self.assertEqual(requested_user_cost_rate, user_cost_rate)

        # create_user_cost_rate
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/users/1782974/cost_rates",
                body=json.dumps(cost_rate_125068758_dict),
                status=201
            )
        created_user_cost_rate = from_dict(data_class=CostRate, data=cost_rate_125068758_dict)
        requested_created_user_cost_rate = self.harvest.create_user_cost_rate(user_id= 1782974, amount= 150.0, start_date= "2019-01-01")
        self.assertEqual(requested_created_user_cost_rate, created_user_cost_rate)

        httpretty.reset()

    def test_project_assignments(self):
        project_assignment_125068554_dict = {
                "id":125068554,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":True,
                "budget":None,
                "created_at":"2017-06-26T22:32:52Z",
                "updated_at":"2017-06-26T22:32:52Z",
                "hourly_rate":100.0,
                "project":{
                "id":14308069,
                "name":"Online Store - Phase 1",
                "code":"OS1"
                },
                "client":{
                "id":5735776,
                "name":"123 Industries"
                },
                "task_assignments":[
                    {
                        "id":155505013,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083365,
                                "name":"Graphic Design"
                            }
                    },
                    {
                        "id":155505014,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083366,
                                "name":"Programming"
                            }
                    },
                    {
                        "id":155505015,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083368,
                                "name":"Project Management"
                            }
                    },
                    {
                        "id":155505016,
                        "billable":False,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:54:06Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083369,
                                "name":"Research"
                            }
                    }
                ]
            }

        project_assignment_125068553_dict = {
                "id":125068553,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":False,
                "budget":None,
                "created_at":"2017-06-26T22:32:52Z",
                "updated_at":"2017-06-26T22:32:52Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "task_assignments":[
                        {
                            "id":155502709,
                            "billable":True,
                            "is_active":True,
                            "created_at":"2017-06-26T21:36:23Z",
                            "updated_at":"2017-06-26T21:36:23Z",
                            "hourly_rate":100.0,
                            "budget":None,
                            "task":{
                                    "id":8083365,
                                    "name":"Graphic Design"
                                }
                        },
                        {
                            "id":155502710,
                            "billable":True,
                            "is_active":True,
                            "created_at":"2017-06-26T21:36:23Z",
                            "updated_at":"2017-06-26T21:36:23Z",
                            "hourly_rate":100.0,
                            "budget":None,
                            "task":{
                                    "id":8083366,
                                    "name":"Programming"
                                }
                        },
                        {
                            "id":155502711,
                            "billable":True,
                            "is_active":True,
                            "created_at":"2017-06-26T21:36:23Z",
                            "updated_at":"2017-06-26T21:36:23Z",
                            "hourly_rate":100.0,
                            "budget":None,
                            "task":{
                                    "id":8083368,
                                    "name":"Project Management"
                                }
                        },
                        {
                            "id":155505153,
                            "billable":False,
                            "is_active":True,
                            "created_at":"2017-06-26T21:53:20Z",
                            "updated_at":"2017-06-26T21:54:31Z",
                            "hourly_rate":100.0,
                            "budget":None,
                            "task":{
                                    "id":8083369,
                                    "name":"Research"
                                }
                        }
                    ]
            }

        project_assignment_125066109_dict = {
            "id":125066109,
            "is_project_manager":True,
            "is_active":True,
            "use_default_rates":True,
            "budget":None,
            "created_at":"2017-06-26T21:52:18Z",
            "updated_at":"2017-06-26T21:52:18Z",
            "hourly_rate":100.0,
            "project":{
                    "id":14308069,
                    "name":"Online Store - Phase 1",
                    "code":"OS1"
                },
            "client":{
                    "id":5735776,
                    "name":"123 Industries"
                },
            "task_assignments":[
                {
                    "id":155505013,
                    "billable":True,
                    "is_active":True,
                    "created_at":"2017-06-26T21:52:18Z",
                    "updated_at":"2017-06-26T21:52:18Z",
                    "hourly_rate":100.0,
                    "budget":None,
                    "task":{
                            "id":8083365,
                            "name":"Graphic Design"
                        }
                },
                {
                    "id":155505014,
                    "billable":True,
                    "is_active":True,
                    "created_at":"2017-06-26T21:52:18Z",
                    "updated_at":"2017-06-26T21:52:18Z",
                    "hourly_rate":100.0,
                    "budget":None,
                    "task":{
                            "id":8083366,
                            "name":"Programming"
                        }
                },
                    {
                        "id":155505015,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:52:18Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083368,
                                "name":"Project Management"
                            }
                },
                    {
                        "id":155505016,
                        "billable":False,
                        "is_active":True,
                        "created_at":"2017-06-26T21:52:18Z",
                        "updated_at":"2017-06-26T21:54:06Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083369,
                                "name":"Research"
                            }
                    }
                ]
            }



        project_assignment_125063975_dict = {
                "id":125063975,
                "is_project_manager":True,
                "is_active":True,
                "use_default_rates":False,
                "budget":None,
                "created_at":"2017-06-26T21:36:23Z",
                "updated_at":"2017-06-26T21:36:23Z",
                "hourly_rate":100.0,
                "project":{
                        "id":14307913,
                        "name":"Marketing Website",
                        "code":"MW"
                    },
                "client":{
                        "id":5735774,
                        "name":"ABC Corp"
                    },
                "task_assignments":[
                    {
                        "id":155502709,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:36:23Z",
                        "updated_at":"2017-06-26T21:36:23Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083365,
                                "name":"Graphic Design"
                            }
                    },
                    {
                        "id":155502710,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:36:23Z",
                        "updated_at":"2017-06-26T21:36:23Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083366,
                                "name":"Programming"
                            }
                    },
                    {
                        "id":155502711,
                        "billable":True,
                        "is_active":True,
                        "created_at":"2017-06-26T21:36:23Z",
                        "updated_at":"2017-06-26T21:36:23Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083368,
                                "name":"Project Management"
                            }
                    },
                    {
                        "id":155505153,
                        "billable":False,
                        "is_active":True,
                        "created_at":"2017-06-26T21:53:20Z",
                        "updated_at":"2017-06-26T21:54:31Z",
                        "hourly_rate":100.0,
                        "budget":None,
                        "task":{
                                "id":8083369,
                                "name":"Research"
                            }
                    }
                ]
            }

        project_assignments_dict = {
                "project_assignments":[project_assignment_125068554_dict, project_assignment_125068553_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/users/1782959/project_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/users/1782959/project_assignments?page=1&per_page=100"
                    }
            }

        my_project_assignments_dict = {
                "project_assignments":[project_assignment_125066109_dict, project_assignment_125063975_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/users/1782884/project_assignments?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/users/1782884/project_assignments?page=1&per_page=100"
                    }
            }

        # project_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/1782959/project_assignments?page=1&per_page=100",
                body=json.dumps(project_assignments_dict),
                status=200
            )
        project_assignments = from_dict(data_class=ProjectAssignments, data=project_assignments_dict)
        requested_project_assignments = self.harvest.project_assignments(user_id= 1782959)
        self.assertEqual(requested_project_assignments, project_assignments)

        # my_project_assignments
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me/project_assignments?page=1&per_page=100",
                body=json.dumps(my_project_assignments_dict),
                status=200
            )
        my_project_assignments = from_dict(data_class=ProjectAssignments, data=my_project_assignments_dict)
        requested_my_project_assignments = self.harvest.my_project_assignments()
        self.assertEqual(requested_my_project_assignments, my_project_assignments)

        httpretty.reset()

    def test_users(self):

        user_1782974_dict = {
                "id":1782974,
                "first_name":"Jim",
                "last_name":"Allen",
                "email":"jimallen@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":False,
                "is_project_manager":False,
                "can_see_rates":False,
                "can_create_projects":False,
                "can_create_invoices":False,
                "is_active":True,
                "created_at":"2017-06-26T22:34:41Z",
                "updated_at":"2017-06-26T22:34:52Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":50.0,
                "roles":["Developer"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/abraj_albait_towers.png?1498516481"
            }

        user_1782959_dict = {
                "id":1782959,
                "first_name":"Kim",
                "last_name":"Allen",
                "email":"kimallen@example.com",
                "telephone":"",
                "timezone":"Eastern Time (US & Canada)",
                "has_access_to_all_future_projects":True,
                "is_contractor":False,
                "is_admin":False,
                "is_project_manager":True,
                "can_see_rates":False,
                "can_create_projects":False,
                "can_create_invoices":False,
                "is_active":True,
                "created_at":"2017-06-26T22:15:45Z",
                "updated_at":"2017-06-26T22:32:52Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":50.0,
                "roles":["Designer"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/cornell_clock_tower.png?1498515345"
            }

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }

        user_3_dict = {
                "id": 3,
                "first_name": "George",
                "last_name": "Frank",
                "email": "george@example.com",
                "telephone": "",
                "timezone": "Eastern Time (US & Canada)",
                "has_access_to_all_future_projects": False,
                "is_contractor": False,
                "is_admin": False,
                "is_project_manager": True,
                "can_see_rates": False,
                "can_create_projects": False,
                "can_create_invoices": False,
                "is_active": True,
                "weekly_capacity":126000,
                "default_hourly_rate": 0.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "cost_rate": 0.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "roles": ["Project Manager"],
                "avatar_url": "https://{ACCOUNT_SUBDOMAIN}.harvestapp.com/assets/profile_images/big_ben.png?1485372046",
                "created_at": "2017-01-25T19:20:46Z",
                "updated_at": "2017-01-25T19:20:57Z"
            }

        user_2_dict = {
                "id": 2,
                "first_name": "Project",
                "last_name": "Manager",
                "email": "pm@example.com",
                "telephone": "888-555-1212",
                "timezone": "Eastern Time (US & Canada)",
                "has_access_to_all_future_projects": True,
                "is_contractor": False,
                "is_admin": False,
                "is_project_manager": True,
                "can_see_rates": True,
                "can_create_projects": True,
                "can_create_invoices": True,
                "is_active": True,
                "weekly_capacity":126000,
                "default_hourly_rate": 120.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "cost_rate": 50.0, # TODO: this is supposed to be an int. Something isn't casting int to float.
                "roles": ["Project Manager"],
                "avatar_url": "https://{ACCOUNT_SUBDOMAIN}.harvestapp.com/assets/profile_images/big_ben.png?1485372046",
                "created_at": "2017-01-25T19:20:46Z",
                "updated_at": "2017-01-25T19:20:57Z"
            }

        users_dict = {
                "users":[user_1782974_dict, user_1782959_dict, user_1782884_dict],
                "per_page":100,
                "total_pages":1,
                "total_entries":3,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/v2/users?page=1&per_page=100",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/v2/users?page=1&per_page=100"
                    }
            }

        # users
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users?page=1&per_page=100",
                body=json.dumps(users_dict),
                status=200
            )
        users = from_dict(data_class=Users, data=users_dict)
        requested_users = self.harvest.users()
        self.assertEqual(requested_users, users)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=200
            )
        me = from_dict(data_class=User, data=user_1782884_dict)
        requested_me = self.harvest.get_currently_authenticated_user()
        self.assertEqual(requested_me, me)

        # get_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/1782974",
                body=json.dumps(user_1782974_dict),
                status=200
            )
        user = from_dict(data_class=User, data=user_1782974_dict)
        requested_user = self.harvest.get_user(user_id= 1782974)
        self.assertEqual(requested_user, user)

        # create_user
        httpretty.register_uri(httpretty.POST,
                "https://api.harvestapp.com/api/v2/users",
                body=json.dumps(user_3_dict),
                status=201
            )
        created_user = from_dict(data_class=User, data=user_3_dict)
        requested_created_user = self.harvest.create_user(email= "george@example.com", first_name= "George", last_name= "Frank", is_project_manager= True)
        self.assertEqual(requested_created_user, created_user)

        # update_user
        httpretty.register_uri(httpretty.PATCH,
                "https://api.harvestapp.com/api/v2/users/2",
                body=json.dumps(user_2_dict),
                status=200
            )
        updated_user = from_dict(data_class=User, data=user_2_dict)
        requested_updated_user = self.harvest.update_user(user_id= 2, telephone= "888-555-1212")
        self.assertEqual(requested_updated_user, updated_user)

        # delete_user
        httpretty.register_uri(httpretty.DELETE,
                "https://api.harvestapp.com/api/v2/users/2",
                status=200
            )
        requested_deleted_user = self.harvest.delete_user(user_id= 2)
        self.assertEqual(requested_deleted_user, None)

if __name__ == '__main__':
    unittest.main()
