#Python Harvest API Client

###How to use:
    >>> import harvest
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", "EMAIL", "PASSWORD")
    >>> client.who_am_i


###How to use OAuth2:
token must look like this:
token = { 
	'token_type': 'bearer', 
	'access_token': 'your access token', 
	'refresh_token': 'your refresh token',
	'expires_in': 64799,
}

    >>> import harvest
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", client_id=client_id, token=token)
    >>> client.who_am_i
