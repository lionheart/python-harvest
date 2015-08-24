#Python Harvest API Client

###How to use:
    >>> import harvest
    >>> harvest.HarvestStatus().get()
    u'up'
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", "EMAIL", "PASSWORD")
    >>> data = {"notes":"test note", "project_id":"PROJECT_ID","hours":"1.0", "task_id": "TASK_ID"}
    >>> client.add(data)
    >>> data['notes'] = "another test"
    >>> client.update("ENTRY_ID", data)
    >>> client.get_today()


###How to use OAuth2:
    >>> import harvest
    >>> harvest.HarvestStatus().get()
    u'up'
    client_id = 'YOUR HARVEST CLIENT ID'
    token = {
        'token_type': 'bearer'
        'access_token': 'YOUR ACCESS TOKEN',
        'refresh_token': 'YOUR REFRESH TOKEN',
        'expires_at': 'UNIX TIMESTAMP WHEN TOKEN EXPIRES',
    }
    >>> client = harvest.Harvest("https://COMPANYNAME.harvestapp.com", client_id=client_id token=token)
    >>> data = {"notes":"test note", "project_id":"PROJECT_ID","hours":"1.0", "task_id": "TASK_ID"}
    >>> client.add(data)
    >>> data['notes'] = "another test"
    >>> client.update("ENTRY_ID", data)
    >>> client.get_today()
