
from os.path import normpath, join, abspath
import json

from harvest import Harvest


def get_client_credentials():
    """
    Need to place a json file with client credentials in the test directory.
    This file is excluded by .gitignore

    Should look like this:

    {
        base_url: "https://account.harvestapp.com",
        client_id: "123123123",
        client_secret: "123123123123"
    }

    """
    # Contains base_url, client id, and client secret
    client_file = normpath(join(abspath(__file__), '../client.json'))
    with open(client_file, 'r') as f:
        client_data = json.load(f)
    return client_data


def get_token():
    # This is a token dictionary, the same type passed into harvest for OAuth2
    token_file = normpath(join(abspath(__file__), '../token.json'))
    with open(token_file, 'r') as f:
        token = json.load(f)
    return token


def test_auto_refresh():
    client_data = get_client_credentials()
    token = get_token()
    # Make sure it's an invalid access token
    token['access_token'] = 'not_a_real_token'
    base_url = client_data['base_url']
    client_id = client_data['client_id']
    client_secret = client_data['client_secret']
    harv = Harvest(base_url, client_id=client_id, client_secret=client_secret, token=token)
    r = harv.who_am_i
    assert r.get('error') is None
