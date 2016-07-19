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

### Contributions

Contributions are welcome. Please submit a pull request and make sure you adhere to PEP-8 coding guidelines. I'll review your patch and will accept if it looks good.

### TODOs

* [ ] Tests
* [ ] Full OAuth workflow
* [ ] More documentation

### License

python-harvest is licensed under Apache 2.0. See [LICENSE](LICENSE) for more details.

### Authors

See [AUTHORS](AUTHORS).
