#Python Harvest API Client

###How to use:
    >>> import Harvest
    >>> Harvest.HarvestStatus().get()
    u'up'
    >>> harvest = Harvest.Harvest("https://COMPANYNAME.harvestapp.com", "EMAIL", "PASSWORD")
    >>> data = {"notes":"test note", "project_id":"PROJECT_ID","hours":"1.0", "task_id": "TASK_ID"}
    >>> harvest.add(data)
    >>> data['notes'] = "another test"
    >>> harvest.update("ENTRY_ID", data)
    >>> harvest.get_today()

