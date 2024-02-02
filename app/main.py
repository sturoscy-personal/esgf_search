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
from globus_sdk import SearchClient
from mangum import Mangum

app = FastAPI()

def globus_search(search):

#    print(search)
    limit = 10
    offset = 0
    if "limit" in search:
        limit = int(search.pop("limit")[0])
    if "offset" in search:
        offset = int(search.pop("offset")[0])

    if "from" in search:
        from_field = search.pop("from")

    if "to" in search:
        to_field = search.pop("to")

    # remove facets that don't fit:
    if "format" in search:
        del search["format"]
    if "query" in search:
        del search["query"]

    if "type" not in search: # or search["type"] == ["Dataset"]:
        search["type"] = "Dataset" 
    elif search["type"] == ["File"]:
        #  File Search
        search["type"] = "File"
        if "dataset_id" in search:
            id_parm = search["dataset_id"]
            query = ( 
                SearchQuery()
                .add_filter("dataset_id", id_parm)
            )
            resp = SearchClient().post_search(INDEX_ID, query, limit=1)
            docs = []
            x = resp["gmeta"]
            rec = x[0]['entries'][0]['content']
            rec['id'] = x[0]['subject']
            docs.append(rec)       

            ret = { "response" : { "numFound" : resp["total"], "docs" : docs } }
            return ret
        else:
            #   this is a free file query
            pass

    facets = [""]
    if "facets" in search:
        facets = search.pop('facets')

    query = SearchQuery()

    for x in search:
        y = search[x]
        if ',' in y[0]:
            y = y[0].split(',')
        query.add_filter(x, y, type="match_any" )

    # handle the facets
    for ff in facets[0].split(', '):
       query.add_facet(ff, ff)

    response = SearchClient().post_search(INDEX_ID, query, limit=limit, offset=offset)
    # unpack the response: facets and records (gmeta/docs)
    facet_map = {}
    if "facet_results" in response:
        fr=response["facet_results"]
        for x in fr:
            arr = []
            for y in x["buckets"]:
                arr.append(y['value'])
                arr.append(y['count'])
            facet_map[x['name']] = arr

    # unpack the dataset Records
    docs = []
    for x in response["gmeta"]:
        rec = x['entries'][0]['content']
        rec['id'] = x['subject']
        docs.append(rec)

    # package the response
    ret = { "response" : { "numFound" : response["total"], "docs" : docs } }
    if len(facet_map) > 0:
           ret["facet_counts"] = { "facet_fields" : facet_map } 

    return ret

@app.get("/")
def read_root(
    experiment_id: str | None = None,
    source_id: str | None = None,
    variable_id: str | None = None,
    facets: str | None = None
):
    """
    the parameters of this function become the things you can query in the url
    and they get automatically type-checked.

    """
    kwargs = locals()  # all the function arguments as keywords
    return globus_search(kwargs)


handler = Mangum(app)
