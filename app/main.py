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


def globus_search_metagrid_conversion(search):
    INDEX_ID = "d927e2d9-ccdb-48e4-b05d-adbc3d97bbc5"

    limit = int(search.pop("limit")[0]) if "limit" in search else 10
    offset = int(search.pop("offset")[0]) if "offset" in search else 0

    query = SearchQuery(q="*").set_limit(limit).set_offset(offset)

    # Add default facets
    query.add_facet("Activity ID", "activity_id")
    query.add_facet("Data Node", "data_node")
    query.add_facet("Experiment ID", "experiment_id")
    query.add_facet("Frequency", "frequency")
    query.add_facet("Grid Label", "grid_label")
    query.add_facet("Institution ID", "institution_id")
    query.add_facet("Nominal Resolution", "nominal_resolution")
    query.add_facet("Realm", "realm")
    query.add_facet("Result Type", "result_type")
    query.add_facet("Source ID", "source_id")
    query.add_facet("Source Type", "source_type")
    query.add_facet("Table ID", "table_id")
    query.add_facet("Variable ID", "variable_id")
    query.add_facet("Variant Label", "variant_label")
    query.add_facet("Version Type", "version_type")

    # from_field = search.pop("from") if "from" in search else ""
    # to_field = search.pop("to") if "to" in search else ""

    # Clean up facets that don't fit:
    if "format" in search:
        del search["format"]
    if "query" in search:
        del search["query"]

    # File or Dataset filter
    if "type" not in search:
        query.add_filter("type", ["Dataset"], type="match_any")
    else:
        query.add_filter("type", [search["type"]], type="match_any")
        if search["type"] == ["File"]:
            if "dataset_id" in search:
                id_parm = search["dataset_id"]
                query = (
                    SearchQuery()
                    .add_filter("dataset_id", id_parm)
                    .set_limit(1)
                )
                resp = SearchClient().post_search(INDEX_ID, query, limit=1)

                x = resp["gmeta"]
                rec = x[0]['entries'][0]['content']
                rec['id'] = x[0]['subject']
                docs = [].append(rec)

                ret = {"response": {"numFound": resp["total"], "docs": docs}}
                return ret
            else:
                # This is a free file query
                pass

    # Filters from query params
    for param in search:
        value = search[param]
        if value:
            value = value.split(',') if ',' in value else [value]
            query.add_filter(param, value, type="match_any")

    # Handle Additional Facets
    if "facets" in search:
        facets = search.pop('facets')
        for ff in facets[0].split(', '):
            query.add_facet(ff, ff)

    response = SearchClient().post_search(
        INDEX_ID,
        query,
        limit=limit,
        offset=offset,
    )

    # Unpack the response: facets and records (gmeta/docs)
    facet_map = {}
    if "facet_results" in response:
        fr = response["facet_results"]
        for x in fr:
            arr = []
            for y in x["buckets"]:
                arr.append(y['value'])
                arr.append(y['count'])
            facet_map[x['name']] = arr

    # Unpack the dataset Records
    docs = []
    for x in response["gmeta"]:
        rec = x['entries'][0]['content']
        rec['id'] = x['subject']
        docs.append(rec)

    # Package the response
    ret = {"response": {"numFound": response["total"], "docs": docs}}
    if len(facet_map) > 0:
        ret["facet_counts"] = {"facet_fields": facet_map}

    return ret


def globus_search(search):
    filters = [
        {"type": "match_any", "field_name": f"{key}", "values": val.split(",")}
        for key, val in search.items()
        if val is not None
    ]
    response = SearchClient().post_search(
        "d927e2d9-ccdb-48e4-b05d-adbc3d97bbc5",  # ALCF globus index uuid
        {
            "q": "",
            "filters": filters,
            "facets": [],
            "sort": [],
        },
        limit=10,
    )
    return response["gmeta"]


@app.get("/")
async def read_root(
    activity_id: str | None = None,
    experiment_id: str | None = None,
    source_id: str | None = None,
    variable_id: str | None = None,
):
    """
    The parameters of this function become the things you can query in the url
    and they get automatically type-checked.
    """
    return globus_search_metagrid_conversion(locals())


handler = Mangum(app)
