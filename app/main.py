from app.facets.cmip6 import cmip6_facets
from app.facets.common import common_facets
from app.facets.system import system_facets

from fastapi import Depends, FastAPI
from globus_sdk import SearchClient, SearchQuery
from mangum import Mangum
from typing import Annotated


app = FastAPI(root_path="/develop")


def globus_search_metagrid_conversion(search):
    INDEX_ID = "d927e2d9-ccdb-48e4-b05d-adbc3d97bbc5"

    query = SearchQuery(q=search.get("q", "*"))

    # Limit and offset
    limit = int(search.pop("limit")[0]) if "limit" in search else 10
    offset = int(search.pop("offset")[0]) if "offset" in search else 0

    # Facets from pydantic models
    common = search.pop("common")
    system = search.pop("system")
    if "cmip6" in search:
        cmip6 = search.pop("cmip6")
        for facet in cmip6:
            pass

    # Add default facets
    # query.add_facet("Activity ID", "activity_id")
    # query.add_facet("Data Node", "data_node")
    # query.add_facet("Experiment ID", "experiment_id")
    # query.add_facet("Frequency", "frequency")
    # query.add_facet("Grid Label", "grid_label")
    # query.add_facet("Institution ID", "institution_id")
    # query.add_facet("Nominal Resolution", "nominal_resolution")
    # query.add_facet("Realm", "realm")
    # query.add_facet("Result Type", "result_type")
    # query.add_facet("Source ID", "source_id")
    # query.add_facet("Source Type", "source_type")
    # query.add_facet("Table ID", "table_id")
    # query.add_facet("Variable ID", "variable_id")
    # query.add_facet("Variant Label", "variant_label")
    # query.add_facet("Version Type", "version_type")

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
                query.add_filter("dataset_id", id_parm).set_limit(1)
                resp = SearchClient().post_search(INDEX_ID, query, limit=1)

                x = resp["gmeta"]
                rec = x[0]["entries"][0]["content"]
                rec["id"] = x[0]["subject"]
                docs = [].append(rec)

                ret = {"response": {"numFound": resp["total"], "docs": docs}}
                return ret
            else:
                pass

    # Filters from query params
    for param in search:
        value = search[param]
        if value:
            value = value.split(",") if "," in value else [value]
            query.add_filter(param, value, type="match_any")

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
                arr.append(y["value"])
                arr.append(y["count"])
            facet_map[x["name"]] = arr

    # Unpack the dataset Records
    docs = []
    for x in response["gmeta"]:
        rec = x["entries"][0]["content"]
        rec["id"] = x["subject"]
        docs.append(rec)

    # Package the response
    ret = {"response": {"numFound": response["total"], "docs": docs}}
    if len(facet_map) > 0:
        ret["facet_counts"] = {"facet_fields": facet_map}

    return ret


@app.get("/cmip6")
async def query_cmip6(
    cmip6: Annotated[dict, Depends(cmip6_facets)],
    common: Annotated[dict, Depends(common_facets)],
    system: Annotated[dict, Depends(system_facets)],
):
    return globus_search_metagrid_conversion(locals())


handler = Mangum(app)
