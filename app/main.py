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

from datetime import datetime
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query
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
                query = SearchQuery().add_filter("dataset_id", id_parm).set_limit(1)
                resp = SearchClient().post_search(INDEX_ID, query, limit=1)

                x = resp["gmeta"]
                rec = x[0]["entries"][0]["content"]
                rec["id"] = x[0]["subject"]
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
            value = value.split(",") if "," in value else [value]
            query.add_filter(param, value, type="match_any")

    # Handle Additional Facets
    if "facets" in search:
        facets = search.pop("facets")
        for ff in facets[0].split(", "):
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


async def system_facets(
    format: Annotated[
        Literal["application/solr+xml", "application/solr+json"],
        Query(description="the type of data returned in the response"),
    ] = "application/solr+xml",
    type: Annotated[
        Literal["Dataset", "File", "Aggregation"],
        Query(description="the type of database record"),
    ] = "Dataset",
    bbox: Annotated[
        str | None,
        Query(description="the geospatial search box [west, south, east, north]"),
    ] = None,
    start: Annotated[
        datetime | None,
        Query(description="beginning of the temporal coverage in the dataset"),
    ] = None,
    end: Annotated[
        datetime | None,
        Query(description="ending of the temporal coverage in the dataset"),
    ] = None,
    _from: Annotated[
        datetime | None,
        Query(
            alias="from",  # because you can't call a argument `from`
            description="return records last modified after this timestamp",
        ),
    ] = None,
    to: Annotated[
        datetime | None,
        Query(description="return records last modified before this timestamp"),
    ] = None,
    offset: Annotated[
        int,
        Query(ge=0, description="the number of records to skip"),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=0, description="the number of records to return"),
    ] = 10,
    replica: Annotated[
        bool,
        Query(description="enable to include replicas in the search results"),
    ] = True,
    latest: Annotated[
        bool,
        Query(description="enable to only return the latest versions"),
    ] = True,
    distrib: Annotated[
        bool,
        Query(description="enable to search across all federated nodes"),
    ] = True,
):
    return locals()


async def common_facets(
    access: Annotated[
        list[str] | None,
        Query(description="The method which the data may be accessed."),
    ] = None,
    data_node: Annotated[
        list[str] | None,
        Query(description="The hostname of where the results are located."),
    ] = None,
    index_node: Annotated[
        list[str] | None,
        Query(
            description="The hostname of where information describing the results is located."
        ),
    ] = None,
    version: Annotated[
        list[str] | None,
        Query(
            description="The version of the data, usually in the form of a timestamp"
        ),
    ] = None,
):
    return locals()


@app.get("/")
async def query_cmip6(
    system: Annotated[dict, Depends(system_facets)],
    common: Annotated[dict, Depends(common_facets)],
    activity_drs: Annotated[
        list[str] | None,
        Query(
            description="The activity identifier, which is a broad collection of experiments. Also known as `activity_id`"
        ),
    ] = None,
    activity_id: Annotated[
        list[str] | None,
        Query(
            description="The activity identifier, which is a broad collection of experiments. Also known as `activity_drs`"
        ),
    ] = None,
    branch_method: Annotated[
        list[str] | None,
        Query(
            description="A short description of how the experiment branched from the control."  # Q: correct?
        ),
    ] = None,
    cf_standard_name: Annotated[
        list[str] | None,
        Query(description="The Climate Forecast (CF) standard name of the variable."),
    ] = None,
    creation_date: Annotated[
        datetime | None,
        Query(
            description="The timestamp for when the dataset was created."
        ),  # Q: dataset or record?
    ] = None,
    data_specs_version: Annotated[
        list[str] | None,
        Query(description="The version of the data specifications used."),
    ] = None,
    datetime_end: Annotated[
        list[str] | None,
        Query(description=""),  # Q: data does not look accurate, same and system `end`?
    ] = None,
    directory_format_template_: Annotated[
        list[str] | None,
        Query(
            description="The template for how the path is formed from facet information."
        ),
    ] = None,
    experiment_id: Annotated[
        list[str] | None,
        Query(description="The experiment identifier."),
    ] = None,
    experiment_title: Annotated[
        list[str] | None,
        Query(description="The experiment title."),
    ] = None,
    frequency: Annotated[
        list[str] | None,
        Query(description="The temporal frequency of the search results."),
    ] = None,
    grid: Annotated[
        list[str] | None,
        Query(description="The short description for the grid used."),
    ] = None,
    grid_label: Annotated[
        list[str] | None,
        Query(
            description="The label for the grid used. Typical values are the natural grid `gn` or a regredding `gr`."
        ),
    ] = None,
    institution_id: Annotated[
        list[str] | None,
        Query(
            description="The institution identifier for the responsible entity for the submission."
        ),
    ] = None,
    member_id: Annotated[
        list[str] | None,
        Query(
            description="The variant identifier, also known as `variant_label`. Typical values are of the form `r1i1p1f1` where `r` is for the realization, `i` for the initialization, `p` for the physics parameterization, and `f` for the forcing."
        ),
    ] = None,
    mip_era: Annotated[
        list[str] | None,
        Query(description="The era of the model intercomparison project."),
    ] = None,
    model_cohort: Annotated[
        list[str] | None,
        Query(
            description="The cohort to which the model belongs, `Published` or `Registered`."
        ),
    ] = None,
    nominal_resolution: Annotated[
        list[str] | None,
        Query(description="The resolution of the search results."),
    ] = None,
    product: Annotated[
        list[str] | None,
        Query(description="The kind of data found in the database."),
    ] = None,
    realm: Annotated[
        list[str] | None,
        Query(description="The realm to which the search results belong."),
    ] = None,
    short_description: Annotated[
        list[str] | None,
        Query(
            description="A short description for the data submission, typically of the form `Model output prepared for CMIP6`."
        ),
    ] = None,
    source_id: Annotated[
        list[str] | None,
        Query(
            description="The source identifier, more commonly referred to as the model."
        ),
    ] = None,
    source_type: Annotated[
        list[str] | None,
        Query(description="The type of the source, or the type of model."),
    ] = None,
    sub_experiment_id: Annotated[
        list[str] | None,
        Query(
            description="The sub experiment identifier, if one is used for the given `experiment_id`."
        ),
    ] = None,
    table_id: Annotated[
        list[str] | None,
        Query(
            description="The table identifier for the variable, a broad collection of variables with a common problem domain."
        ),
    ] = None,
    variable: Annotated[
        list[str] | None,
        Query(description="The variable identifier, also known as `variable_id`."),
    ] = None,
    variable_id: Annotated[
        list[str] | None,
        Query(description="The variable identifier, also known as `variable`."),
    ] = None,
    variable_long_name: Annotated[
        list[str] | None,
        Query(description="The short description of the variable."),
    ] = None,
    variant_label: Annotated[
        list[str] | None,
        Query(
            description="The variant identifier, also known as `member_id`. Typical values are of the form `r1i1p1f1` where `r` is for the realization, `i` for the initialization, `p` for the physics parameterization, and `f` for the forcing."
        ),
    ] = None,
):
    return globus_search_metagrid_conversion(locals())


handler = Mangum(app)
