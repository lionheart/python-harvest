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

import json
import requests
from requests_oauthlib import OAuth2Session

from dacite import from_dict

from .dataclasses import *

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from base64 import b64encode as enc64
from collections import OrderedDict

HARVEST_STATUS_URL = 'http://www.harveststatus.com/api/v2/status.json'

class HarvestError(Exception):
    pass


class Harvest(object):
    def __init__(self, uri, email=None, password=None, refresh_token=None, client_id=None, token=None,
                 put_auth_in_header=True, personal_token=None, account_id=None):
        self.__uri = uri.rstrip('/')
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError('Invalid harvest uri "{0}".'.format(uri))

        if refresh_token:
            self.__headers = {
                "Content-Type": 'application/x-www-form-urlencoded',
                "Accept": 'application/json',
            }
        else:
            self.__headers = {
                'Content-Type'  : 'application/json',
                'Accept'        : 'application/json',
                'User-Agent'    : 'Mozilla/5.0',  # 'TimeTracker for Linux' -- ++ << >>
            }
        if email and password:
            self.__auth     = 'Basic'
            self.__email    = email.strip()
            self.__password = password
            if put_auth_in_header:
                self.__headers['Authorization'] = 'Basic {0}'.format(enc64("{self.email}:{self.password}".format(self=self).encode("utf8")).decode("utf8"))
        elif client_id and token:
            self.__auth         = 'OAuth2'
            self.__client_id    = client_id
            self.__token        = token
        elif account_id and personal_token:
            self.__auth = 'Bearer'
            self.__account_id = account_id

            if ('Bearer' in personal_token):
                self.__personal_token = personal_token[personal_token.index('Bearer ') + len('Bearer'):]
            else:
                self.__personal_token = personal_token

            if put_auth_in_header:
                self.__headers['Authorization'] = 'Bearer {0}'.format("{self.personal_token}".format(self=self))
                self.__headers['Harvest-Account-Id'] = "{self.account_id}".format(self=self)
    @property
    def uri(self):
        return self.__uri

    @property
    def auth(self):
        return self.__auth

    @property
    def email(self):
        return self.__email

    @property
    def password(self):
        return self.__password

    @property
    def client_id(self):
        return self.__client_id

    @property
    def token(self):
        return self.__token

    @property
    def personal_token(self):
        return self.__personal_token

    @property
    def account_id(self):
        return self.__account_id

    @property
    def status(self):
        return status()

    ## Client Contacts

    def client_contacts(self, page=1, per_page=100, client_id=None, updated_since=None):
        url = '/contacts?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)
        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=ClientContacts, data=self._get(url))

    def get_client_contact(self, contact_id):
        return from_dict(data_class=ClientContact, data=self._get('/contacts/{0}'.format(contact_id)))

    def create_client_contact(self, client_id, first_name, **kwargs):
        url  = '/contacts'
        kwargs.update({'client_id' : client_id, 'first_name':first_name})
        return from_dict(data_class=ClientContact, data=self._post(url, data=kwargs))

    def update_client_contact(self, contact_id, **kwargs):
        url = '/contacts/{0}'.format(contact_id)
        return from_dict(data_class=ClientContact, data=self._patch(url, data=kwargs))

    def delete_client_contact(self, contact_id):
        self._delete('/contacts/{0}'.format(contact_id))

    ## Clients

    def clients(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/clients?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)
        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=Clients, data=self._get(url))

    def get_client(self, client_id):
        return from_dict(data_class=Client, data=self._get('/clients/{0}'.format(client_id)))

    def create_client(self, **kwargs):
        url = '/clients/'
        # client.create_client(client={"name":"jo"})
        return self._post(url, data=kwargs)

    def update_client(self, client_id, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return self._patch(url, data=kwargs)

    def delete_client(self, client_id):
        return self._delete('/clients/{0}'.format(client_id))

    ## Company

    def company(self, page=1, per_page=100, is_active=None, updated_since_datetime=None):
        url = '/company'
        return from_dict(data_class=Company, data=self._get(url))

    ## Invoices

    def invoice_messages(self, invoice_id, page=1, per_page=100, updated_since=None):
        url = '/invoices/{0}/messages'.format(invoice_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoiceMessages, data=self._get(url))

        # TODO: need to come back and manage all the ways of interacting with ain invoice message

    def invoice_payments(self, invoice_id, page=1, per_page=100, updated_since=None):
        url = '/invoices/{0}/payments'.format(invoice_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoicePayments, data=self._get(url))

    # TODO: need to come back and manage all the ways of paying an invoice

    def invoices(self, page=1, per_page=100, client_id=None, project_id=None, updated_since=None, from_date=None, to_date=None, state=None):
        url = '/invoices?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if project_id is not None:
            url = '{0}&project_id={1}'.format(url, project_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to={1}'.format(url, to_date)
        if state is not None:
            url = '{0}&state={1}'.format(url, state)

        return from_dict(data_class=Invoices, data=self._get(url))

    def get_invoice(self, invoice_id):
        return from_dict(data_class=Invoice, data=self._get('/invoices/{0}'.format(invoice_id)))

    def update_invoice(self, invoice_id, **kwargs):
        url = '/invoices/{0}'.format(invoice_id)
        return self._patch(url, data=kwargs)

    def delete_invoice(self, invoice_id):
        return self._delete('/invoices/{0}'.format(invoice_id))

    def invoice_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/invoice_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoiceItemCategories, data=self._get(url))

     ## Estimates

    def estimate_messages(self, estimate_id, page=1, per_page=100, updated_since=None):
        url = '/estimates/{0}/messages'.format(estimate_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateMessages, data=self._get(url))

    def estimates(self, page=1, per_page=100, client_id=None, updated_since=None, from_date=None, to_date=None, state=None):
        url = '/estimates?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from_date={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to_date={1}'.format(url, to_date)

        return from_dict(data_class=Estimates, data=self._get(url))

    def estimate_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/estimate_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateItemCategories, data=self._get(url))

    ## Expenses

    def expenses(self, page=1, per_page=100, user_id=None, client_id=None, project_id=None, is_billed=None, updated_since=None, from_date=None, to_date=None):
        url = '/expenses?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if user_id is not None:
            url = '{0}&user_id={1}'.format(url, user_id)
        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if project_id is not None:
            url = '{0}&project_id={1}'.format(url, project_id)
        if is_billed is not None:
            url = '{0}&is_billed={1}'.format(url, is_billed)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to_date={1}'.format(url, to_date)

        return from_dict(data_class=Expenses, data=self._get(url))

    def get_expense(self, invoice_id):
        return from_dict(data_class=Expense, data=self._get('/expenses/{0}'.format(invoice_id)))

    def update_expense(self, invoice_id, **kwargs):
        url = '/expenses/{0}'.format(invoice_id)
        return self._patch(url, data=kwargs)

    def delete_expense(self, invoice_id):
        return self._delete('/expenses/{0}'.format(invoice_id))

    def expense_categories(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/expense_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=ExpenseCategories, data=self._get(url))

    def get_expense_category(self, expense_category_id):
        return from_dict(data_class=ExpenseCategory, data=self._get('/expense_categories/{0}'.format(expense_category_id)))

    def create_expense_category(self, new_expense_category_id, **kwargs):
        return self._post('/expense_categories/{0}'.format(new_expense_category_id), data=kwargs)

    def update_expense_category(self, expense_category_id, **kwargs):
        return self._patch('/expense_categories/{0}'.format(expense_category_id), data=kwargs)

    def delete_expense_category(self, expense_category_id):
        return self._delete('/expense_categories/{0}'.format(expense_category_id))

    ## Tasks

    def tasks(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/tasks?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=Tasks, data=self._get(url))

    def get_task(self, task_id):
        return from_dict(data_class=Task, data=self._get('/tasks/{0}'.format(task_id)))

    def create_task(self, **kwargs):
        return self._post('/tasks/', data=kwargs)

    def update_task(self, tasks_id, **kwargs):
        url = '/tasks/{0}'.format(tasks_id)
        return self._patch(url, data=kwargs)

    def delete_task(self, tasks_id):
        return self._delete('/tasks/{0}'.format(tasks_id))

    ## Time Entries

    def time_entries(self, page=1, per_page=100, user_id=None, client_id=None, project_id=None, is_billed=None, is_running=None, updated_since=None, from_date=None, to_date=None):
        url = '/time_entries?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if user_id is not None:
            url = '{0}&user_id={1}'.format(url, user_id)
        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if project_id is not None:
            url = '{0}&project_id={1}'.format(url, project_id)
        if is_billed is not None:
            url = '{0}&is_billed={1}'.format(url, is_billed)
        if is_running is not None:
            url = '{0}&is_running={1}'.format(url, is_running)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to_date={1}'.format(url, to_date)

        return from_dict(data_class=TimeEntries, data=self._get(url))

    def get_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._get('/time_entries/{0}'.format(time_entry_id)))

    def delete(self, entry_id):
        return self._delete('/daily/delete/{0}'.format(entry_id))

    def update(self, entry_id, data):
        return self._post('/daily/update/{0}'.format(entry_id), data)

    ## Projects

    def user_assignments(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/user_assignments?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=UserAssignments, data=self._get(url))

    def project_user_assignments(self, project_id, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/projects/{0}/user_assignments'.format(project_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=UserAssignments, data=self._get(url))

    def user_assignment(self, project_id, user_assignment_id):
        return from_dict(data_class=UserAssignment, data=self._get('/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id)))

    def task_assignments(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/task_assignments?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=TaskAssignments, data=self._get(url))

    def project_task_assignments(self, project_id, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/projects/{0}/task_assignments'.format(project_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=TaskAssignments, data=self._get(url))

    def task_assignment(self, project_id, task_assignment_id):
        return from_dict(data_class=TaskAssignment, data=self._get('/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id)))


    def projects(self, page=1, per_page=100, client_id=None, is_active=None, updated_since=None):
        url = '/projects?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=Projects, data=self._get(url))

    def get_project(self, project_id):
        return from_dict(data_class=Project, data=self._get('/projects/{0}'.format(project_id)))

    def create_project(self, **kwargs):
        # Example: client.create_project(project={"name": title, "client_id": client_id})
        return self._post('/projects', data=kwargs)

    def update_project(self, project_id, **kwargs):
        url = '/projects/{0}'.format(project_id)
        return self._put(url, data=kwargs)

    def delete_project(self, project_id):
        return self._delete('/projects/{0}'.format(project_id))


     ## Roles

    def roles(self, page=1, per_page=100):
        url = '/roles?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=Roles, data=self._get(url))

    def get_role(self, project_id):
        return from_dict(data_class=Role, data=self._get('/roles/{0}'.format(project_id)))

     ## Users

    def user_cost_rates(self, user_id, page=1, per_page=100):
        url = '/users/{0}/cost_rates'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=UserCostRates, data=self._get(url))

    def user_cost_rate(self, user_id, cost_rate_id):
        url = '/users/{0}/cost_rates/{1}'.format(user_id, cost_rate_id)

        return from_dict(data_class=CostRate, data=self._get(url))

    def project_assignments(self, user_id, page=1, per_page=100, updated_since=None):
        url = '/users/{0}/project_assignments'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=ProjectAssignments, data=self._get(url))

    def my_project_assignments(self, page=1, per_page=100):
        url = '/users/me/project_assignments?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=ProjectAssignments, data=self._get(url))

    def users(self, page=1, per_page=100, is_active=None, updated_since=None):
        url = '/users?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if is_active is not None:
            url = '{0}&is_active={1}'.format(url, is_active)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=Users, data=self._get(url))

    def get_user(self, user_id):
        return from_dict(data_class=User, data=self._get('/users/{0}'.format(user_id)))

    def currently_authenticated_user(self):
        return from_dict(data_class=User, data=self._get('/users/me'))


    def _get(self, path='/', data=None):
        return self._request('GET', path, data)

    def _post(self, path='/', data=None):
        return self._request('POST', path, data)

    def _put(self, path='/', data=None):
        return self._request('PUT', path, data)

    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)

    def _patch(self, path='/', data=None):
        return self._request('PATCH', path, data)

    def _request(self, method='GET', path='/', data=None):
        url = '{self.uri}{path}'.format(self=self, path=path)
        kwargs = {
            'method'  : method,
            'url'     : '{self.uri}{path}'.format(self=self, path=path),
            'headers' : self.__headers,
            'data'   : json.dumps(data),
        }
        if self.auth == 'Basic':
            requestor = requests
            if 'Authorization' not in self.__headers:
                kwargs['auth'] = (self.email, self.password)
        elif self.auth == 'Bearer':
            requestor = requests
            if 'Authorization' not in self.__headers:
                kwargs['access_token'] = self.personal_token
                kwargs['account_id'] = self.account_id
        elif self.auth == 'OAuth2':
            requestor = OAuth2Session(client_id=self.client_id, token=self.token)

        try:
            resp = requestor.request(**kwargs)
            if 'DELETE' not in method:
                try:
                    return resp.json(object_pairs_hook=OrderedDict)
                except:
                    return resp
            return resp
        except Exception as e:
            raise HarvestError(e)

def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get('status', {})
    except:
        status = {}
    return status
