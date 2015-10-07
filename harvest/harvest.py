"""
 harvest.py

 Author: Jonathan Hosmer (forked from https://github.com/lionheart/python-harvest.git)
 Date: Sat Jan 31 12:17:16 2015

"""

import requests
from requests_oauthlib import OAuth2Session
from urlparse import urlparse
from base64   import b64encode as enc64

HARVEST_STATUS_URL = 'http://www.harveststatus.com/api/v2/status.json'

class HarvestError(Exception):
    pass

class Harvest(object):
    def __init__(self, uri, email=None, password=None, client_id=None, token=None, put_auth_in_header=True):
        self.__uri      = uri.rstrip('/')
        parsed = urlparse(uri)
        if not (parsed.scheme and parsed.netloc):
            raise HarvestError('Invalid harvest uri "{0}".'.format(uri))

        self.__headers = {
            'Accept'        : 'application/json',
            'User-Agent'    : 'Mozilla/5.0',  # 'TimeTracker for Linux' -- ++ << >>
        }
        if email and password:
            self.__auth     = 'Basic'
            self.__email    = email.strip()
            self.__password = password
            if put_auth_in_header:
                self.__headers['Authorization'] = 'Basic {0}'.format(enc64('{self.email}:{self.password}'.format(self=self)))
        elif client_id and token:
            self.__auth         = 'OAuth2'
            self.__client_id    = client_id
            self.__token = token

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
    def status(self):
        return status()

    ## Accounts

    @property
    def who_am_i(self):
        return self._get('/account/who_am_i')

    ## Client Contacts

    def contacts(self, updated_since=None):
        url = '/contacts'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def get_contact(self, contact_id):
        return self._get('/contacts/{0}'.format(contact_id))

    def create_contact(self, new_contact_id, fname, lname, **kwargs):
        url  = '/contacts/{0}'.format(new_contact_id)
        kwargs.update({'first-name':fname, 'last-name':lname})
        return self._post(url, data=kwargs)

    def client_contacts(self, client_id, updated_since=None):
        url = '/clients/{0}/contacts'.format(client_id)
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def update_contact(self, contact_id, **kwargs):
        url = '/contacts/{0}'.format(contact_id)
        return self._put(url, data=kwargs)

    def delete_contact(self, contact_id):
        return self._delete('/contacts/{0}'.format(contact_id))

    ## Clients

    def clients(self, updated_since=None):
        url = '/clients'
        if updated_since is not None:
            url = '{0}?updated_since={1}'.format(url, updated_since)
        return self._get(url)

    def get_client(self, client_id):
        return self._get('/clients/{0}'.format(client_id))

    def create_client(self, new_client_id, name, **kwargs):
        url  = '/clients/{0}'.format(new_client_id)
        kwargs.update({'name':name})
        return self._post(url, data=kwargs)

    def update_client(self, client_id, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return self._put(url, data=kwargs)

    def toggle_client_active(self, client_id):
        return self._get('/clients/{0}/toggle'.format(client_id))

    def delete_client(self, client_id):
        return self._delete('/clients/{0}'.format(client_id))


     ## People

    def people(self):
        url = '/people'
        return self._get(url)

    def get_person(self, person_id):
        return self._get('/people/{0}'.format(person_id))

    def toggle_person_active(self, client_id):
        return self._get('/people/{0}/toggle'.format(people_id))

    def delete_person(self, client_id):
        return self._delete('/people/{0}'.format(person_id))

    ## Projects

    def projects(self):
        return self._get('/projects')

    def projects_for_client(self, client_id):
        return self._get('/projects?client={}'.format(client_id))

    def get_project(self, project_id):
        return self._get('/projects/{0}'.format(project_id))

    def create_project(self, **kwargs):
        return self._post('/projects', data=kwargs)

    def update_project(self, project_id, **kwargs):
        url = '/projects/{0}'.format(project_id)
        return self._put(url, data=kwargs)

    def toggle_project_active(self, project_id):
        return self._put('/projects/{0}/toggle'.format(project_id))

    def delete_project(self, project_id):
        return self._delete('/projects/{0}'.format(project_id))

    ## Expense Categories

    @property
    def expense_categories(self):
        return self._get('/expense_categories')

    def create_expense_category(self, new_expense_category_id, **kwargs):
        return self._post('/expense_categories/{0}'.format(new_expense_category_id), data=kwargs)

    def update_expense_category(self, expense_category_id, **kwargs):
        return self._put('/expense_categories/{0}'.format(expense_category_id), data=kwargs)

    def get_expense_category(self, expense_category_id):
        return self._get('/expense_categories/{0}'.format(expense_category_id))

    def delete_expense_category(self, expense_category_id):
        return self._delete('/expense_categories/{0}'.format(expense_category_id))

    def toggle_expense_category_active(self, expense_category_id):
        return self._get('/expense_categories/{0}/toggle'.format(expense_category_id))

    ## Time Tracking

    @property
    def today(self):
        return self._get('/daily')

    def get_day(self, day_of_the_year=1, year=2012):
        return self._get('/daily/{0}/{1}'.format(day_of_the_year, year))

    def get_entry(self, entry_id):
        return self._get('/daily/show/{0}'.format(entry_id))

    def toggle_timer(self, entry_id):
        return self._get('/daily/timer/{0}'.format(entry_id))

    def add(self, data):
        return self._post('/daily/add', data)

    def delete(self, entry_id):
        return self._delete('/daily/delete/{0}'.format(entry_id))

    def update(self, entry_id, data):
        return self._post('/daily/update/{0}'.format(entry_id), data)

    def _get(self, path='/', data=None):
        return self._request('GET', path, data)
    def _post(self, path='/', data=None):
        return self._request('POST', path, data)
    def _put(self, path='/', data=None):
        return self._request('PUT', path, data)
    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)
    def _request(self, method='GET', path='/', data=None):
        url = '{self.uri}{path}'.format(self=self, path=path)
        kwargs = {
            'method'  : method,
            'url'     : '{self.uri}{path}'.format(self=self, path=path),
            'headers' : self.__headers,
            'data'    : data,
        }
        if self.auth == 'Basic':
            requestor = requests
            if 'Authorization' not in self.__headers:
                kwargs['auth'] = (self.email, self.password)
        elif self.auth == 'OAuth2':
            requestor = OAuth2Session(client_id=self.client_id, token=self.token)

        try:
            resp = requestor.request(**kwargs)
            if 'DELETE' not in method:
                return resp.json()
            return resp
        except Exception, e:
            raise HarvestError(e)

def status():
    try:
        status = requests.get(HARVEST_STATUS_URL).json().get('status', {})
    except:
        status = {}
    return status
