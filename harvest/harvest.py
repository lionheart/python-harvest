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
from dataclasses import asdict
from collections import deque
from datetime import timedelta, datetime
import time

import requests
from requests_oauthlib import OAuth2Session
from dacite import from_dict

from .dataclasses import *

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

class HarvestError(Exception):
    pass

class Harvest(object):

    # 15 is from the Harvest API doco https://help.getharvest.com/api-v2/introduction/overview/general/
    RATE_LIMIT_DURATION_SECONDS = 15

    def __init__(self, uri, auth):
        self.__uri = uri.rstrip('/')
        parsed = urlparse(uri)

        self.__headers = {'User-Agent': 'Lionheart/python-harvest'}

        if not (parsed.scheme and parsed.netloc):
            raise HarvestError('Invalid harvest uri "{0}".'.format(uri))

        if isinstance(auth, PersonalAccessToken):
            self.__headers['Authorization'] = auth.access_token
            self.__headers['Harvest-Account-ID'] = auth.account_id

        elif isinstance(auth, OAuth2_ClientSide_Token):
            self.__headers['Authorization'] = auth.access_token

        elif isinstance(auth, OAuth2_ServerSide):
            self.__headers['Authorization'] = auth.token.access_token

        else:
            raise HarvestError('Invalid authorization type "{0}".'.format(type(auth)))

        self.__auth = auth
        self.request_throttle = deque()
        self.time_limit = timedelta(seconds=self.RATE_LIMIT_DURATION_SECONDS)

    @property
    def uri(self):
        return self.__uri

    @property
    def headers(self):
        return self.__headers

    @property
    def auth(self):
        return self.__auth

    ## Client Contacts

    def client_contacts(self, page=1, per_page=100, client_id=None, updated_since=None):
        url = '/contacts?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)
        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return ClientContacts.from_json(self._get(url))

    def get_client_contact(self, contact_id):
        return from_dict(data_class=ClientContact, data=self._get('/contacts/{0}'.format(contact_id)))

    def create_client_contact(self, client_id, first_name, **kwargs):
        url  = '/contacts'
        kwargs.update({'client_id': client_id, 'first_name': first_name})
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

    def create_client(self, name, **kwargs):
        url  = '/clients'
        kwargs.update({'name': name})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Client, data=response)

    def update_client(self, client_id, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return from_dict(data_class=Client, data=self._patch(url, data=kwargs))

    def delete_client(self, client_id):
        self._delete('/clients/{0}'.format(client_id))

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

    def create_invoice_message(self, invoice_id, recipients, **kwargs):
        url  = '/invoices/{0}/messages'.format(invoice_id)
        kwargs.update({'recipients': recipients})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=InvoiceMessage, data=response)

    def mark_draft_invoice(self, invoice_id, event_type):
        url = '/invoices/{0}/messages'.format(invoice_id)
        return from_dict(data_class=InvoiceMessage, data=self._post(url, data={'event_type': event_type}))

    def mark_draft_invoice_as_sent(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'send')

    def mark_open_invoice_as_closed(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'close')

    def reopen_closed_invoice(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 're-open')

    def mark_open_invoice_as_draft(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'draft')

    def delete_invoice_message(self, invoice_id, message_id):
        self._delete('/invoices/{0}/messages/{1}'.format(invoice_id, message_id))


    def invoice_payments(self, invoice_id, page=1, per_page=100, updated_since=None):
        url = '/invoices/{0}/payments'.format(invoice_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoicePayments, data=self._get(url))

    def create_invoice_payment(self, invoice_id, amount, **kwargs):
        url  = '/invoices/{0}/payments'.format(invoice_id)
        kwargs.update({'amount': amount})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=InvoicePayment, data=response)

    def delete_invoice_payment(self, invoice_id, payment_id):
        self._delete('/invoices/{0}/payments/{1}'.format(invoice_id, payment_id))


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

    def get_invoices(self, invoice_ids):
        returnable = []
        for invoice_id in invoice_ids:
            returnable.append(self.get_invoice(invoice_id))
        return returnable

    def create_invoice(self, client_id, **kwargs):
        url = '/invoices'
        kwargs.update({'client_id': client_id})
        return from_dict(data_class=Invoice, data=self._post(url, data=kwargs))

    # invoice is a dataclass invoice
    def create_free_form_invoice(self, client_id, free_form_invoice):
        return self.create_invoice(client_id, free_form_invoice)

    def create_invoice_based_on_tracked_time_and_expenses(self, client_id, invoice_import):
        return self.create_free_form_invoice(client_id, invoice_import)

    # line_items is a list of LineItem
    def update_invoice(self, invoice_id, **kwargs):
        url = '/invoices/{0}'.format(invoice_id)
        response = self._patch(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Invoice, data=response)

    def create_invoice_line_item(self, invoice_id, line_items):
        if not isinstance(line_items, list):
            return ErrorMessage(message="line_items is not a list")
        return self.update_invoice(invoice_id, line_items=line_items)


    def update_invoice_line_item(self, invoice_id, line_item):
        if not isinstance(line_item, dict):
            return ErrorMessage(message="line_items is not a dictionary")
        return self.update_invoice(invoice_id, line_items = [line_item])

    # line_items is a list of LineItems
    def delete_invoice_line_items(self, invoice_id, line_items):
        url = '/invoices/{0}'.format(invoice_id)

        delete_line_item = []
        for item in line_items:
            delete_line_item.append({'id':item.id, '_destroy':True})

        return from_dict(data_class=Invoice, data=self._patch(url, data={'line_items': delete_line_item}))

    def delete_invoice(self, invoice_id):
        return self._delete('/invoices/{0}'.format(invoice_id))

    def invoice_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/invoice_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoiceItemCategories, data=self._get(url))

    def get_invoice_item_category(self, category_id):
        url = '/invoice_item_categories/{0}'.format(category_id)
        return from_dict(data_class=InvoiceItemCategory, data=self._get(url))

    def create_invoice_item_category(self, name):
        url = '/invoice_item_categories'
        return from_dict(data_class=InvoiceItemCategory, data=self._post(url, data={'name': name}))

    def update_invoice_item_category(self, category_id, name):
        url = '/invoice_item_categories/{0}'.format(category_id)
        return from_dict(data_class=InvoiceItemCategory, data=self._patch(url, data={'name': name}))

    def delete_invoice_item_category(self, invoice_category_id):
        return self._delete('/invoice_item_categories/{0}'.format(invoice_category_id))

     ## Estimates

    def estimate_messages(self, estimate_id, page=1, per_page=100, updated_since=None):
        url = '/estimates/{0}/messages'.format(estimate_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateMessages, data=self._get(url))

    # recipients is a list of Recipient
    def create_estimate_message(self, estimate_id, recipients, **kwargs):
        url  = '/estimates/{0}/messages'.format(estimate_id)
        kwargs.update({'recipients': recipients})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=EstimateMessage, data=response)

    def delete_estimate_message(self, estimate_id, message_id):
        self._delete('/estimates/{0}/messages/{1}'.format(estimate_id, message_id))

    def mark_draft_estimate(self, estimate_id, event_type):
        url  = '/estimates/{0}/messages'.format(estimate_id)
        return from_dict(data_class=EstimateMessage, data=self._post(url, data={'event_type': event_type}))

    def mark_draft_estimate_as_sent(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'send')

    def mark_open_estimate_as_accepted(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'accept')

    def mark_open_estimate_as_declined(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'decline')

    def reopen_a_closed_estimate(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 're-open')

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

    def get_estimte(self, estimate_id):
        url = '/estimates/{0}'.format(estimate_id)
        return from_dict(data_class=Estimate, data=self._get(url))

    def create_estimate(self, client_id, **kwargs):
        url  = '/estimates'
        kwargs.update({'client_id': client_id})

        return from_dict(data_class=Estimate, data=self._post(url, data=kwargs))

    def update_estimate(self, estimate_id, **kwargs):
        url = '/estimates/{0}'.format(estimate_id)
        return from_dict(data_class=Estimate, data=self._patch(url, data=kwargs))

    def create_estimate_line_item(self, estimate_id, line_items):
        if not isinstance(line_items, list):
            return ErrorMessage(message="line_items is not a list")
        return self.update_estimate(estimate_id, line_items=line_items)

    def update_estimate_line_item(self, estimate_id, line_item):
        if not isinstance(line_item, dict):
            return ErrorMessage(message="line_items is not a dictionary")
        return self.update_estimate(estimate_id, line_items=[line_item])

    # line_items is a list of LineItem.id's
    def delete_estimate_line_items(self, estimate_id, line_items):
        url = '/estimates/{0}'.format(estimate_id)

        delete_line_item = []
        for item in line_items:
            delete_line_item.append({'id':item.id, '_destroy':True})

        return from_dict(data_class=Estimate, data=self._patch(url, data={'line_items': delete_line_item}))

    def delete_estimate(self, estimate_id):
        return self._delete('/estimates/{0}'.format(estimate_id))

    def estimate_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/estimate_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateItemCategories, data=self._get(url))

    def get_estimate_item_category(self, estimate_item_category_id):
        url = '/estimate_item_categories/{0}'.format(estimate_item_category_id)
        return from_dict(data_class=EstimateItemCategory, data=self._get(url))

    def create_estimate_item_category(self, name):
        url = '/estimate_item_categories'
        return from_dict(data_class=EstimateItemCategory, data=self._post(url, data={'name': name}))

    def update_estimate_item_category(self, estimate_item_category_id, name):
        url = '/estimate_item_categories/{0}'.format(estimate_item_category_id)
        return from_dict(data_class=EstimateItemCategory, data=self._patch(url, data={'name': name}))

    def delete_estimate_item_category(self, estimate_item_id):
        return self._delete('/estimate_item_categories/{0}'.format(estimate_item_id))

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

    def get_expense(self, expense_id):
        return from_dict(data_class=Expense, data=self._get('/expenses/{0}'.format(expense_id)))

    def create_expense(self, project_id, expense_category_id, spent_date, **kwargs):
        url = '/expenses'
        kwargs.update({'project_id': project_id, 'expense_category_id': expense_category_id, 'spent_date': spent_date})

        if 'receipt' in kwargs.keys():
            receipt = kwargs.pop('receipt')
            response = self._post(url, data=kwargs, files=receipt['files'])
        else:
            response = self._post(url, data=kwargs)

            if 'message' in response.keys():
                return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Expense, data=response)

    def update_expense(self, expense_id, **kwargs):
        url = '/expenses/{0}'.format(expense_id)

        if 'receipt' in kwargs.keys():
            receipt = kwargs.pop('receipt')
            response = self._patch(url, data=kwargs, files=receipt['files'])
        else:
            response = self._patch(url, data=kwargs)

        return from_dict(data_class=Expense, data=response)

    def delete_expense(self, expense_id):
        return self._delete('/expenses/{0}'.format(expense_id))

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

    def create_expense_category(self, name, **kwargs):
        url = '/expense_categories'
        kwargs.update({'name': name})
        return from_dict(data_class=ExpenseCategory, data=self._post(url, data=kwargs))

    def update_expense_category(self, expense_category_id, **kwargs):
        url = '/expense_categories/{0}'.format(expense_category_id)
        return from_dict(data_class=ExpenseCategory, data=self._patch(url, data=kwargs))

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

    def create_task(self, name, **kwargs):
        url = '/tasks'
        kwargs.update({'name': name})
        return from_dict(data_class=Task, data=self._post(url, data=kwargs))

    def update_task(self, task_id, **kwargs):
        url = '/tasks/{0}'.format(task_id)
        return from_dict(data_class=Task, data=self._patch(url, data=kwargs))

    def delete_task(self, task_id):
        return self._delete('/tasks/{0}'.format(task_id))

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

    def create_time_entry(self, project_id, task_id, spent_date, **kwargs):
        url = '/time_entries'
        kwargs.update({'project_id': project_id, 'task_id': task_id, 'spent_date': spent_date})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=TimeEntry, data=response)

    def create_time_entry_via_start_and_end_time(self, project_id, task_id, spent_date, **kwargs):
        return self.create_time_entry(project_id, task_id, spent_date, kwargs)

    def create_time_entry_via_duration(self, project_id, task_id, spent_date, **kwargs):
        return self.create_time_entry(project_id, task_id, spent_date, **kwargs)

    def update_time_entry(self, time_entry_id, **kwargs):
        url = '/time_entries/{0}'.format(time_entry_id)
        return from_dict(data_class=TimeEntry, data=self._patch(url, data=kwargs))

    def delete_time_entry_external_reference(self, time_entry_id):
        return self._delete('/time_entries/{0}/external_reference'.format(time_entry_id))

    def delete_time_entry(self, time_entry_id):
        return self._delete('/time_entries/{0}'.format(time_entry_id))

    def restart_a_stopped_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._patch('/time_entries/{0}/restart'.format(time_entry_id)))

    def stop_a_running_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._patch('/time_entries/{0}/stop'.format(time_entry_id)))

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

    def get_user_assignment(self, project_id, user_assignment_id):
        return from_dict(data_class=UserAssignment, data=self._get('/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id)))

    def create_user_assignment(self, project_id, user_id, **kwargs):
        url = '/projects/{0}/user_assignments'.format(project_id)
        kwargs.update({'user_id': user_id})
        return from_dict(data_class=UserAssignment, data=self._post(url, data=kwargs))

    def update_user_assignment(self, project_id, user_assignment_id, **kwargs):
        url = '/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id)
        return from_dict(data_class=UserAssignment, data=self._patch(url, data=kwargs))

    def delete_user_assignment(self, project_id, user_assignment_id):
        return self._delete('/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id))

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

    def get_task_assignment(self, project_id, task_assignment_id):
        return from_dict(data_class=TaskAssignment, data=self._get('/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id)))

    def create_task_assignment(self, project_id, task_id, **kwargs):
        url = '/projects/{0}/task_assignments'.format(project_id)
        kwargs.update({'task_id': task_id})

        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=TaskAssignment, data=response)

    def update_task_assignment(self, project_id, task_assignment_id, **kwargs):
        url = '/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id)
        return from_dict(data_class=TaskAssignment, data=self._patch(url, data=kwargs))

    def delete_task_assignment(self, project_id, task_assignment_id):
        return self._delete('/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id))

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

    def create_project(self, client_id, name, is_billable, bill_by, budget_by, **kwargs):
        url = '/projects'
        kwargs.update({'client_id': client_id, 'name': name, 'is_billable': is_billable, 'bill_by': bill_by, 'budget_by': budget_by})
        return from_dict(data_class=Project, data=self._post(url, data=kwargs))

    def update_project(self, project_id, **kwargs):
        url = '/projects/{0}'.format(project_id)
        return from_dict(data_class=Project, data=self._patch(url, data=kwargs))

    def delete_project(self, project_id):
        return self._delete('/projects/{0}'.format(project_id))

     ## Roles

    def roles(self, page=1, per_page=100):
        url = '/roles?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=Roles, data=self._get(url))

    def get_role(self, role_id):
        return from_dict(data_class=Role, data=self._get('/roles/{0}'.format(role_id)))

    def create_role(self, name, **kwargs):
        url = '/roles'
        kwargs.update({'name': name})
        return from_dict(data_class=Role, data=self._post(url, data=kwargs))

    def update_role(self, role_id, name, **kwargs):
        url = '/roles/{0}'.format(role_id)
        kwargs.update({'name': name})
        return from_dict(data_class=Role, data=self._patch(url, data=kwargs))

    def delete_role(self, role_id):
        return self._delete('/roles/{0}'.format(role_id))

     ## Users

    def user_cost_rates(self, user_id, page=1, per_page=100):
        url = '/users/{0}/cost_rates'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=UserCostRates, data=self._get(url))

    def get_user_cost_rate(self, user_id, cost_rate_id):
        url = '/users/{0}/cost_rates/{1}'.format(user_id, cost_rate_id)
        return from_dict(data_class=CostRate, data=self._get(url))

    def create_user_cost_rate(self, user_id, amount, **kwargs):
        url = '/users/{0}/cost_rates'.format(user_id)
        kwargs.update({'amount': amount})
        return from_dict(data_class=CostRate, data=self._post(url, data=kwargs))

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

    def get_currently_authenticated_user(self):
        return from_dict(data_class=User, data=self._get('/users/me'))

    def create_user(self, first_name, last_name, email, **kwargs):
        url = '/users'
        kwargs.update({'first_name': first_name, 'last_name': last_name, 'email': email})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=User, data=response)

    def update_user(self, user_id, **kwargs):
        url = '/users/{0}'.format(user_id)
        return from_dict(data_class=User, data=self._patch(url, data=kwargs))

    def delete_user(self, user_id):
        return self._delete('/users/{0}'.format(user_id))

    def _get(self, path='/', data=None):
        return self._request('GET', path, data)

    def _post(self, path='/', data=None, files=None):
        return self._request('POST', path, data, files)

    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)

    def _patch(self, path='/', data=None, files=None):
        return self._request('PATCH', path, data, files)

    def _request(self, method='GET', path='/', data=None, files=None):
        url = '{self.uri}{path}'.format(self=self, path=path)

        kwargs = {
            'method': method,
            'url': '{self.uri}{path}'.format(self=self, path=path),
            'headers': self.__headers
        }

        if files is not None:
            kwargs['files'] = files

        if data is not None:
            kwargs['data'] = json.dumps(data)

        requestor = requests

        # request throttling
        now = datetime.now()
        self.request_throttle.append(now)
        oldest_time = self.request_throttle.popleft()
        aged_delta = now - oldest_time

        if aged_delta <= self.time_limit:
            self.request_throttle.appendleft(oldest_time)

            # 15 is from the Harvest API doco https://help.getharvest.com/api-v2/introduction/overview/general/
            if (len(self.request_throttle) > 100):
                time.sleep(self.RATE_LIMIT_DURATION_SECONDS * (aged_delta / self.time_limit))

        # "auto" refresh_token. Currently only works on Authorization Code flow
        if isinstance(self.__auth, OAuth2_ServerSide) and (datetime.utcfromtimestamp(self.__auth.token.expires_at) <= datetime.now()):
            new_session = OAuth2Session(client_id=self.__auth.client_id, token=asdict(self.__auth.token))
            oauth_token = new_session.refresh_token(self.__auth.refresh_url, client_id=self.__auth.client_id, client_secret=self.__auth.client_secret)
            self.__auth = from_dict(data_class=OAuth2_ServerSide_Token, data=oauth_token)

        try:
            resp = requestor.request(**kwargs)
            if 'DELETE' not in method:
                try:
                    return resp.json()
                except:
                    return resp
            return resp
        except Exception as e:
            raise HarvestError(e)

def remove_nones(obj):
  if isinstance(obj, (list, tuple, set)):
    return type(obj)(remove_nones(x) for x in obj if x is not None)
  elif isinstance(obj, dict):
    return type(obj)((remove_nones(k), remove_nones(v))
      for k, v in obj.items() if k is not None and v is not None)
  else:
    return obj
