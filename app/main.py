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

# the parameters of this function become the things you can query in the url
# and they get automatically type-checked.


@app.get("/")
def read_root(
    experiment_id: str | None = None,
    source_id: str | None = None,
    variable_id: str | None = None,
):
    kwargs = locals()  # all the function arguments as keywords
    # the filters can be much more complex, here we are just matching
    # any and splitting the argument strings with a comma
    filters = [
        {"type": "match_any", "field_name": f"{key}", "values": val.split(",")}
        for key, val in kwargs.items()
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


handler = Mangum(app)
