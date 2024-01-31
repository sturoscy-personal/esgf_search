"""
A REST API for Globus-based searches that mimics esg-search.
This API is so that community tools that are based on the esg-search
RESTful API need not change to be compatible with the new Globus indices.
If you are designing a new project, you should look to use the globus-sdk
directly and this is only a small wrapper around the `post_search`
functionality. The standalone script does not need installed. You will
need FastAPI on which it is based and the Globus sdk.

python -m pip install fastapi[all] globus_sdk

This will also install Uvicorn (an ASGI web server implementation for Python).
This allows you to test this locally with:

uvicorn concept:app --reload
"""

from fastapi import FastAPI
from globus_sdk import SearchClient, SearchQuery
from mangum import Mangum

app = FastAPI()

# the parameters of this function become the things you can query in the url
# and they get automatically type-checked.


@app.get("/")
def read_root(**search):
    kwargs = locals()  # all the function arguments as keywords
    # the filters can be much more complex, here we are just matching
    # any and splitting the argument strings with a comma

    # Handle the non-facet esg-search keys, remove from the basic query
    limit = 10
    offset = 0
    if "limit" in search:
        limit = search.pop("limit")
    if "offset" in search:
        offset = search.pop("offset")

    if "from" in search:
        from_field = search.pop("from")

    if "to" in search:
        to_field = search.pop("to")

    del search["format"]

    if "type" not in search:
        search["type"] = "Dataset"
    elif search["type"] = "File":
        if "dataset_id" in search:
            id_parm = search["dataset_id"]
        else:
            #   this is a free file query
            pass
    facets = search.pop['facets']

    #  iterate through the remaining keys to be used as search filters
    query = SearchQuery()
    for x in search:
        y = search[x]
        if ',' in y:
            y = split(',')
        else:
            y = [y]
        query.add_filter(x, y, type="match_any" )

    # handle the facets
    for ff in facets.split(','):
        query.add_facet(ff, ff)

    sc = SearchClient()
    response = sc.post_search(
        "d927e2d9-ccdb-48e4-b05d-adbc3d97bbc5",  # ALCF globus index uuid
        query,
        limit=limit, 
        offset=offset
    )

    # unpack the response: facets and records (gmeta/docs)
    fr=response["facet_results"]
    facet_map = {}
    for x in fr:
        arr = []
        for y in x["buckets"]:
            arr.append(y['value'])
            arr.append(y['count'])
        facet_map[x['name']] = arr

    docs = []
    for x in response["gmeta"]:
        rec = x['entries'][0]['content']
        rec['id'] = x['subject']

    ret = { "response" : { "num_found" : response["total"], "docs" : docs } ,
           "facet_counts" : { "facet_field" : facet_map } }

    return ret


handler = Mangum(app)
