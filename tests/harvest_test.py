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
                body=json.dumps(contact_4706510_dict),
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

        httpretty.register_uri(httpretty.GET, "https://api.harvestapp.com/api/v2/company", body=json.dumps(company_dict))
        requested_company = self.harvest.company()

        # httpretty.last_request().body.should.equal( json.dumps(contacts_dict) )

        self.assertEqual(requested_company, company)

        httpretty.reset()


        # company = self.harvest.company()

# class TestHarvest(unittest.TestCase):
#
#     sample_client_a = 7439772
#
#     def setUp(self):
#         config = configparser.ConfigParser()
#         config.read('test_config.ini')
#         #--- PERSONAL ACCESS TOKEN ---
#         personal_access_token = PersonalAccessToken(config['PERSONAL ACCESS TOKEN']['account_id'], config['PERSONAL ACCESS TOKEN']['personal_token'])
#         self.harvest = Helpers(config['PERSONAL ACCESS TOKEN']['uri'], personal_access_token)
#
#         # #--- PERSONAL ACCESS TOKEN ---
#         # personal_access_token = PersonalAccessToken(config['PERSONAL ACCESS TOKEN']['account_id'], config['PERSONAL ACCESS TOKEN']['personal_token'])
#         # self.harvest = harvest.Harvest(config['PERSONAL ACCESS TOKEN']['uri'], personal_access_token)
#         # # oauth2 = OAuth2_ClientSide(config['OAuth2_Implicit_Code_Grant']['client_id'], config['OAuth2_Implicit_Code_Grant']['auth_url'])
#
#         # #--- CLIENT SIDE APPLICATIONS ---
#         # mobileclient = MobileApplicationClient(client_id=config['OAuth2 Implicit Code Grant']['client_id'])
#         #
#         # url = mobileclient.prepare_request_uri(config['OAuth2 Implicit Code Grant']['auth_url'])
#         # print("Browse to here and authenticate: ", url)
#         # response_uri = input("Please put the resulting URL in here:")
#         # # response_uri = "https://127.0.0.1:5000/callback?access_token=1387424.at.ckrsmRcPq2p7bunoRhTjmMx_bgFUslDgy-2jjfodpKXxeuXESktpZBogQBnNtO5lGBdWxnomYOfL7PLvsHQO-Q&expires_in=1209599&scope=harvest%3A1062659&token_type=bearer"
#         # response_uri = response_uri.replace('callback?', 'callback#')
#         # token = mobileclient.parse_request_uri_response(response_uri)
#         # oauth2_clientside_token = from_dict(data_class=OAuth2_ClientSide_Token, data=token)
#         #
#         # self.harvest = harvest.Harvest(config['OAuth2 Implicit Code Grant']['uri'], oauth2_clientside_token)
#
#         # #--- Server SIDE APPLICATIONS ---
#         # webclient = WebApplicationClient(client_id=config['OAuth2 Authorization Code Grant']['client_id'])
#         # oauth = OAuth2Session(client=webclient)
#         #
#         # authorization_url, state = oauth.authorization_url(config['OAuth2 Authorization Code Grant']['auth_url'])
#         # print("Browse to here and authenticate: ", authorization_url)
#         # response_uri = input("Please put the resulting URL in here:")
#         #
#         # harv = OAuth2Session(config['OAuth2 Authorization Code Grant']['client_id'], state=state)
#         # token = harv.fetch_token(config['OAuth2 Authorization Code Grant']['token_url'], client_secret=config['OAuth2 Authorization Code Grant']['client_secret'], authorization_response=response_uri, state=state)
#         # oauth2_serverside_token = from_dict(data_class=OAuth2_ServerSide_Token, data=token)
#         # oauth2_serverside = OAuth2_ServerSide(client_id= config['OAuth2 Authorization Code Grant']['client_id'], client_secret= config['OAuth2 Authorization Code Grant']['client_secret'], token= oauth2_serverside_token, refresh_url= config['OAuth2 Authorization Code Grant']['token_url'])
#         #
#         # self.harvest = harvest.Harvest(config['OAuth2 Authorization Code Grant']['uri'], oauth2_serverside)
#
#
#     #
#     # def tearDown(self):
#     #     pass
#     #
#     # def test_status_not_down(self):
#     #     self.assertEqual("none", self.harvest.status['indicator'], "Harvest API is having problems")
#
#
#     # def test_OAuth2(self):
#         # harvestapp = OAuth2Service(
#         #     client_id='SGyrhXtLAYy0WKqtAucHKdP_',
#         #     client_secret='JRrw_9u1MpsTxsvuQJh76TW59fjSaLnqJNu3kCXRamHpcbvtUuNXQ7MqHKB3SRaZXnfPDIBkXGaLW2vuIYGn2Q',
#         #     name='harvetapp',
#         #     authorize_url='https://id.getharvest.com/oauth2/authorize',
#         #     access_token_url='https://id.getharvest.com/oauth/authorize',
#         #     base_url='https://id.getharvest.com/')
#         #
#         # # https://localhost/?access_token=1387424.at.03VOq-K2U79kPJMuoU3IgdWYWN4DCqg9yZgw7Qm2WYbQuTVaJlnF6vW5Ftsian6rOBoKXNtLFaQeE29CxKpt2g&expires_in=1209599&scope=harvest%3A1062659&token_type=bearer
#         #
#         # access_token = 'Bearer 1387424.at.03VOq-K2U79kPJMuoU3IgdWYWN4DCqg9yZgw7Qm2WYbQuTVaJlnF6vW5Ftsian6rOBoKXNtLFaQeE29CxKpt2g'
#         #
#         # # return an authenticated session
#         # session = harvestapp.get_session(access_token)
#         # print("session", session)
#         #
#         # # make a request using the authenticated session
#         # user = session.get('me')
#         # print("user", user)
#         #
#         # print('Currently logged in as: {user}'.format(user=user['username']))
#
#     # def test_user_project_assignments(self):
#     #     user = self.harvest.create_user('George', 'Frank', 'george@example.com')
#     #
#     #     user_project_assignments = self.harvest.project_assignments(user.id)
#     #     my_project_assignments = self.harvest.my_project_assignments()
#     #
#     #     self.harvest.delete_user(user.id)
#     #
#     # def test_cost_rates(self):
#     #     user = self.harvest.create_user('George', 'Frank', 'george@example.com')
#     #
#     #     user_cost_rate = self.harvest.create_user_cost_rate(user.id, 10.00)
#     #     user_cost_rate = self.harvest.get_user_cost_rate(user.id, user_cost_rate.id)
#     #
#     #     cost_rates = self.harvest.user_cost_rates(user.id)
#     #
#     #     self.harvest.delete_user(user.id)
#     #
#     # def test_users(self):
#     #     users = self.harvest.users()
#     #
#     #     user = self.harvest.create_user('George', 'Frank', 'george@example.com')
#     #     self.harvest.update_user(user.id, telephone='04123456789')
#     #     updated_user = self.harvest.get_user(user.id)
#     #     myself = self.harvest.get_currently_authenticated_user()
#     #
#     #     self.harvest.delete_user(updated_user.id)
#     #
#     # def test_roles(self):
#     #     user1 = self.harvest.create_user('George','Frank','george@example.com')
#     #     user2 = self.harvest.create_user('Your','Name','yourname@example.com')
#     #     roles = self.harvest.roles()
#     #     new_role = self.harvest.create_role('Interface Developer', user_ids=[user1.id])
#     #     self.harvest.update_role(new_role.id, 'Interface Developer', user_ids=[user2.id])
#     #     updated_role = self.harvest.get_role(new_role.id)
#     #
#     #     self.harvest.delete_role(updated_role.id)
#     #
#     #     self.harvest.delete_user(user1.id)
#     #     self.harvest.delete_user(user2.id)
#     #
#     # def test_project_user_assignments(self):
#     #     user_assignments = self.harvest.user_assignments()
#     #
#     #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
#     #     user = self.harvest.create_user('George','Frank','george@example.com')
#     #
#     #     user_assignment = self.harvest.create_user_assignment(project.id, user.id)
#     #     self.harvest.update_user_assignment(project.id, user_assignment.id, hourly_rate=200.00)
#     #     updated_user_assignment = self.harvest.get_user_assignment(project.id, user_assignment.id)
#     #
#     #     project_user_assignments = self.harvest.project_user_assignments(project.id)
#     #
#     #     self.harvest.delete_user_assignment(project.id, user_assignment.id)
#     #     self.harvest.delete_user(user.id)
#     #     self.harvest.delete_project(project.id)
#     #
#     # def test_project_task_assignments(self):
#     #     task_assignments = self.harvest.task_assignments()
#     #
#     #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
#     #     projects = self.harvest.project_task_assignments(project.id)
#     #     new_task = self.harvest.create_task('Integrate With Harvest')
#     #
#     #     project_task_assignment = self.harvest.create_task_assignment(project.id, new_task.id, hourly_rate=150.00)
#     #     task_assignment = self.harvest.get_task_assignment(project.id, project_task_assignment.id)
#     #     updated_task_assignment = self.harvest.update_task_assignment(project.id, project_task_assignment.id, hourly_rate=100.00)
#     #
#     #     self.harvest.delete_task_assignment(project.id, new_task.id)
#     #     self.harvest.delete_task(new_task.id)
#     #     self.harvest.delete_project(project.id)
#     #
#     # def test_projects(self):
#     #     projects = self.harvest.projects()
#     #
#     #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
#     #     self.harvest.update_project(project.id, budget_by='none')
#     #     updated_project = self.harvest.get_project(project.id)
#     #
#     #     self.harvest.delete_project(project.id)
#     #
#     # def test_timesheets(self):
#     #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
#     #     new_task = self.harvest.create_task('Integrate With Harvest')
#     #     project_task_assignment = self.harvest.create_task_assignment(project.id, new_task.id, hourly_rate=150.00)
#     #
#     #     time_entries = self.harvest.time_entries()
#     #
#     #     new_time_entry = self.harvest.create_time_entry_via_duration(project.id, new_task.id, '2019-02-01', hours=7.5)
#     #     updated_time_entry = self.harvest.update_time_entry(new_time_entry.id, hours=8.0)
#     #     time_entry = self.harvest.get_time_entry(updated_time_entry.id)
#     #
#     #     # external reference currently un-tested
#     #     # updated_time_entry = self.harvest.update_time_entry(time_entry.id, external_reference={'id': '', 'group_id': '', 'permalink': ''})
#     #     # updated_time_entry = self.harvest.delete_time_entry_external_reference(time_entry.id)
#     #
#     #     self.harvest.delete_time_entry(time_entry.id)
#     #
#     #     running_time_entry = self.harvest.create_time_entry(project.id, new_task.id, '2019-02-01')
#     #     running_time_entry = self.harvest.stop_a_running_time_entry(running_time_entry.id)
#     #     running_time_entry = self.harvest.restart_a_stopped_time_entry(running_time_entry.id)
#     #     running_time_entry = self.harvest.stop_a_running_time_entry(running_time_entry.id)
#     #     self.harvest.delete_time_entry(running_time_entry.id)
#     #
#     #     self.harvest.delete_task_assignment(project.id, new_task.id)
#     #     self.harvest.delete_project(project.id)
#     #     self.harvest.delete_task(new_task.id)
#     #
#     # def test_tasks(self):
#     #     tasks = self.harvest.tasks()
#     #     new_task = self.harvest.create_task('Integrate With Harvest')
#     #     task = self.harvest.get_task(new_task.id)
#     #     updated_task = self.harvest.update_task(task.id, default_hourly_rate=100.00)
#     #     self.harvest.delete_task(updated_task.id)
#     #
#     # def test_expense_categories(self):
#     #     expense_categories = self.harvest.expense_categories()
#     #     expense_category = self.harvest.create_expense_category('Pass Through 00', unit_name='kilograms', unit_price=10.00)
#     #     updated_expense_category = self.harvest.update_expense_category(expense_category.id, unit_price=100.00)
#     #     expense_category = self.harvest.get_expense_category(updated_expense_category.id)
#     #     self.harvest.delete_expense_category(expense_category.id)
#     #
#     # def test_expenses(self):
#     #     project = self.harvest.create_project(self.sample_client_a, "Your New Project", True, "Project", "project")
#     #     expense_category = self.harvest.create_expense_category('Pass Through 00', unit_name='kilograms', unit_price=10.00)
#     #
#     #     expenses = self.harvest.expenses()
#     #
#     #     new_expense = self.harvest.create_expense(project.id, expense_category.id, '2019-01-01')
#     #     expense = self.harvest.get_expense(new_expense.id)
#     #     updated_expense = self.harvest.update_expense(new_expense.id, notes="This is a note on an expense.")
#     #     self.harvest.delete_expense(updated_expense.id)
#     #
#     #     my_first_receipt = {'file_name':'repo-banner.png', 'content_type': 'image/png', 'files': {'receipt': ('repo-banner.png', open('repo-banner.png', 'rb'), 'image/png', {'Expires': '0'})}}
#     #     new_expense = self.harvest.create_expense(project.id, expense_category.id, '2019-01-02', receipt=my_first_receipt)
#     #     my_second_receipt = {'file_name':'repo-banner-bottom.png', 'content_type': 'image/png', 'files': {'receipt': ('repo-banner-bottom.png', open('repo-banner-bottom.png', 'rb'), 'image/png', {'Expires': '0'})}}
#     #     updated_expense = self.harvest.update_expense(new_expense.id, notes="This is a note on an expense.", receipt=my_second_receipt)
#     #
#     #     self.harvest.delete_expense(updated_expense.id)
#     #
#     #     self.harvest.delete_project(project.id)
#     #     self.harvest.delete_expense_category(expense_category.id)
#     #
#     # def test_estimate_item_category(self):
#     #     estimate_item_categories = self.harvest.estimate_item_categories()
#     #
#     #     category = self.harvest.create_estimate_item_category('Tabasco')
#     #     self.harvest.update_estimate_item_category(category.id, 'Pass through')
#     #     self.harvest.delete_estimate_item_category(category.id)
#     #
#     # def test_estimates_messages(self):
#     #     estimate_parameters = {"subject":"ABC Project Quote","line_items":[{"kind":"Service","description":"ABC Project Quote","unit_price":5000.0}]}
#     #     estimate = self.harvest.create_estimate(self.sample_client_a, **estimate_parameters)
#     #     self.harvest.create_estimate_message(estimate.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}])
#     #
#     #     message_parameters = {"subject":"Estimate #1001","body":"Here is our estimate.","send_me_a_copy":True}
#     #     new_estimate_message = self.harvest.create_estimate_message(estimate.id, [{"name":"Richard Roe","email":"richardroe@example.com"}], **message_parameters)
#     #     estimate_messages = self.harvest.estimate_messages(estimate.id)
#     #     self.harvest.delete_estimate_message(estimate.id, new_estimate_message.id)
#     #
#     #     self.harvest.mark_open_estimate_as_declined(estimate.id)
#     #
#     # def test_estimates(self):
#     #     estimates = self.harvest.estimates()
#     #
#     #     estimate_parameters = {"subject":"ABC Project Quote","line_items":[{"kind":"Service","description":"ABC Project Quote","unit_price":5000.0}]}
#     #
#     #     new_estimate = self.harvest.create_estimate(self.sample_client_a, **estimate_parameters)
#     #     new_estimate = self.harvest.get_estimte(new_estimate.id)
#     #
#     #     updated_estimate = self.harvest.update_estimate(new_estimate.id, purchase_order="2345")
#     #
#     #     new_estimate_line_item = [{"kind":"Service","description":"Another Project","unit_price":1000.0}]
#     #
#     #     estimate_with_new_line_item = self.harvest.create_estimate_line_item(updated_estimate.id, new_estimate_line_item)
#     #
#     #     for item in estimate_with_new_line_item.line_items:
#     #         updated_item = {'id':item.id, 'unit_price': 1.0}
#     #         self.harvest.update_estimate_line_item(estimate_with_new_line_item.id, updated_item)
#     #
#     #     self.harvest.delete_estimate_line_items(estimate_with_new_line_item.id, estimate_with_new_line_item.line_items)
#     #
#     #     self.harvest.delete_estimate(estimate_with_new_line_item.id)
#     #
#     # def test_invoice_categories(self):
#     #     categories = self.harvest.invoice_item_categories()
#     #     invoice_item_category = self.harvest.create_invoice_item_category('Tabasco')
#     #     invoice_item_category = self.harvest.get_invoice_item_category(invoice_item_category.id)
#     #     self.harvest.update_invoice_item_category(invoice_item_category.id, 'Pass through')
#     #     self.harvest.delete_invoice_item_category(invoice_item_category.id)
#     #
#     # def test_invoice_payments(self):
#     #     invoice_config = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
#     #     invoice = self.harvest.create_invoice(self.sample_client_a, **invoice_config)
#     #     self.harvest.mark_draft_invoice_as_sent(invoice.id)
#     #
#     #     payment = self.harvest.create_invoice_payment(invoice.id, 500.00, paid_date='2019-02-17', notes='This is a note')
#     #     payments = self.harvest.invoice_payments(invoice.id)
#     #
#     #     self.harvest.delete_invoice_payment(invoice.id, payment.id)
#     #     payments = self.harvest.invoice_payments(invoice.id)
#     #     self.harvest.delete_invoice(invoice.id)
#     #
#     # def test_invoice_messages(self):
#     #
#     #     invoice_config = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
#     #     invoice = self.harvest.create_invoice(self.sample_client_a, **invoice_config)
#     #
#     #     new_invoice_message = self.harvest.create_invoice_message(invoice.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}], event_type='send')
#     #
#     #     invoice_messages = self.harvest.invoice_messages(invoice.id)
#     #
#     #     self.harvest.delete_invoice_message(invoice.id, new_invoice_message.id)
#     #
#     #     new_invoice_message = self.harvest.create_invoice_message(invoice.id, [{'name': 'S quiggle', 'email': 'mr.squiggle@example.com'}])
#     #
#     #     self.harvest.mark_open_invoice_as_closed(invoice.id)
#     #     self.harvest.reopen_closed_invoice(invoice.id)
#     #     self.harvest.mark_open_invoice_as_draft(invoice.id)
#     #     self.harvest.mark_draft_invoice_as_sent(invoice.id)
#     #
#     #     self.harvest.delete_invoice(invoice.id)
#     #
#     # def test_invoices(self):
#     #     original_invoices = self.harvest.invoices()
#     #     original_invoice_count = original_invoices.total_entries
#     #
#     #     invoice = {"subject": "ABC Project Quote", "due_date":"2017-07-27", "line_items":[{"kind":"Service","description":"ABC Project","unit_price":5000.0}]}
#     #     new_invoice = self.harvest.create_invoice(self.sample_client_a, **invoice)
#     #
#     #     invoices = self.harvest.invoices()
#     #     invoice_count = invoices.total_entries
#     #
#     #
#     #     line_items = [{"kind":"Service","description":"CBA Project","unit_price":10000.0}, {"kind":"Product","description":"CBA Project","unit_price":10000.0}]
#     #
#     #     self.harvest.update_invoice(new_invoice.id, subject = "CBA Project Quote")
#     #     updated_invoice = self.harvest.update_invoice(new_invoice.id, line_items = line_items)
#     #
#     #     for item in updated_invoice.line_items:
#     #         updated_item = {'id':item.id, 'unit_price': 1.0}
#     #         self.harvest.update_invoice_line_item(updated_invoice.id, updated_item)
#     #
#     #     self.harvest.create_invoice_line_item(new_invoice.id, line_items)
#     #
#     #     error = self.harvest.create_invoice_line_item(new_invoice.id, "")
#     #
#     #     invoice_record = self.harvest.get_invoice(new_invoice.id)
#     #
#     #     self.harvest.delete_invoice_line_items(invoice_record.id, invoice_record.line_items)
#     #
#     #     # self.harvest.delete_invoice(invoice_record.id)


if __name__ == '__main__':
    unittest.main()
