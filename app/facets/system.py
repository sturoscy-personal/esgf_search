from datetime import datetime
from fastapi import Query
from typing import Annotated, Literal


def system_facets(
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
        Query(
            description="the geospatial search box [west, south, east, north]"),
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
    # offset: Annotated[
    #     int,
    #     Query(ge=0, description="the number of records to skip"),
    # ] = 0,
    # limit: Annotated[
    #     int,
    #     Query(ge=0, description="the number of records to return"),
    # ] = 10,
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
