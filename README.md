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

