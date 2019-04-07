![](meta/repo-banner.png)
[![](meta/repo-banner-bottom.png)][lionheart-url]

[![Tests](https://img.shields.io/travis/lionheart/python-harvest.svg?style=flat)](https://travis-ci.org/lionheart/python-harvest)
![Version](https://img.shields.io/pypi/v/python-harvest-redux.svg?style=flat)
![License](https://img.shields.io/pypi/l/python-harvest-redux.svg?style=flat)
![Versions](https://img.shields.io/pypi/pyversions/python-harvest-redux.svg?style=flat)

### Installation

Python 3.5 and above:

```
pip install "python-harvest-redux>=3.5"
```

### Usage

#### Personal Access Token

Create a Personal Access Token in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

```python
import harvest
from harvest.dataclasses import *

personal_access_token = PersonalAccessToken("ACCOUNT ID", "PERSONAL TOKEN")
client = harvest.Harvest("https://api.harvestapp.com/api/v2", personal_access_token)

client.get_currently_authenticated_user()
```

#### For Server Side Applications

Create an OAuth2 application in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

Authentication needs to occur before you make your Harvest client.

```python
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
from dacite import from_dict

import harvest
from harvest.dataclasses import *

webclient = WebApplicationClient(client_id="CLIENT ID")
oauth = OAuth2Session(client=webclient)

authorization_url, state = oauth.authorization_url("https://id.getharvest.com/oauth2/authorize")
print("Browse to here in your web browser and authenticate: ", authorization_url)
response_uri = input("Please copy the resulting URL from your browser and paste here:")

harv = OAuth2Session("CLIENT ID", state=state)
token = harv.fetch_token("https://id.getharvest.com/api/v2/oauth2/token", client_secret="CLIENT SECRET", authorization_response=response_uri, state=state)
oauth2_serverside_token = from_dict(data_class=OAuth2_ServerSide_Token, data=token)
oauth2_serverside = OAuth2_ServerSide(client_id="CLIENT ID", client_secret="CLIENT SECRET", token=oauth2_serverside_token, refresh_url="https://id.getharvest.com/api/v2/oauth2/token")

client = harvest.Harvest("https://api.harvestapp.com/api/v2", oauth2_serverside)

client.get_currently_authenticated_user()
```

#### For Client Side Applications

Create an OAuth2 application in the Developers page on Harvest as documented in the Harvest documentation https://help.getharvest.com/api-v2/authentication-api/authentication/authentication/

Authentication needs to occur before you make your Harvest client.

```python
from oauthlib.oauth2 import MobileApplicationClient
from dacite import from_dict

import harvest
from harvest.dataclasses import *

mobileclient = MobileApplicationClient(client_id="CLIENT ID")

url = mobileclient.prepare_request_uri("https://id.getharvest.com/oauth2/authorize")
print("Browse to here in your web browser and authenticate: ", url)
response_uri = input("Please copy the resulting URL from your browser and paste here:")

response_uri = response_uri.replace('callback?', 'callback#')
token = mobileclient.parse_request_uri_response(response_uri)
oauth2_clientside_token = from_dict(data_class=OAuth2_ClientSide_Token, data=token)

client = harvest.Harvest("https://api.harvestapp.com/api/v2", oauth2_clientside_token)

client.get_currently_authenticated_user()
```

### How to use Personal Access Tokens

You must create a Personal Access Token in Harvest first. https://id.getharvest.com/developers

The PersonalAccessToken class is found in the dataclass module:

```python
from harvest.dataclasses import *

personal_access_token = PersonalAccessToken(account_id="ACCOUNT ID", access_token="ACCESS TOKEN")
```

### How to use OAuth2 for Server Side Applications

You must create an OAuth2 Application in Harvest first. https://id.getharvest.com/developers

Then you need to authenticate against Harvest to get your token.

Token must look like this:

```python
from harvest.dataclasses import *

authorization_code_flow_token = OAuth2_ServerSide_Token(access_token="ACCESS TOKEN", refresh_token="REFRESH TOKEN", expires_in="EXPIRES IN", expires_at="EXPIRES AT")
authorization_code_flow = OAuth2_ServerSide(client_id="CLIENT ID", client_secret="CLIENT SECRET", token=authorization_code_flow_token, refresh_url="REFRESH URL")
```

### How to use OAuth2 for Client Side Applications

You must create an OAuth2 Application in Harvest first. https://id.getharvest.com/developers

Then you need to authenticate against Harvest to get your token.

Token must look like this:

```python
from harvest.dataclasses import *

implicit_code_flow_token = OAuth2_ClientSide_Token(access_token="ACCESS TOKEN", expires_in="EXPIRES IN", token_type="Bearer", scope=["Harvest:ACCOUNTID", "Forecast:ACCOUNTID"])
```

### Contributions

Contributions are welcome. Please submit a pull request and make sure you adhere to PEP-8 coding guidelines. I'll review your patch and will accept if it looks good.

### TODOs
* [ ] OAuth workflow refinement
* [ ] Improve exception and error handling
* [ ] More documentation
* [ ] Refine tests

### License

python-harvest is licensed under Apache 2.0. See [LICENSE](LICENSE) for more details.

### Authors

See [AUTHORS](AUTHORS).

[lionheart-url]: https://lionheartsw.com/
