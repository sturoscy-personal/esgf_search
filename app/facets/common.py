from fastapi import Query
from typing import Annotated


def common_facets(
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
