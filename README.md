# Python Harvest API Client

### Installation

```
pip install python-harvest-redux
```

### Usage

```python
import harvest
client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", "EMAIL", "PASSWORD")
client.who_am_i
```

### How to use OAuth2

Token must look like this:

```python
token = {
  'token_type': 'bearer',
  'access_token': 'your access token',
  'refresh_token': 'your refresh token',
  'expires_in': 64799,
}
```

For information on how to get intial tokens see: https://github.com/harvesthq/api/blob/master/Authentication/OAuth%202.0.md

```python
import harvest
client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", client_id=client_id, token=token)
client.who_am_i
```

### License

See [LICENSE](LICENSE).

### Authors

See [AUTHORS](AUTHORS.md).
