#Python Harvest API Client

###How to use:
    >>> import harvest
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", "EMAIL", "PASSWORD")
    >>> client.today


###How to use OAuth2:
    >>> import harvest
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", client_id=client_id, token=token)
    >>> client.today
