from datetime import datetime
from fastapi import Query
from typing import Annotated


def cmip6_facets(
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
        # Q: data does not look accurate, same and system `end`?
        Query(description=""),
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
    return locals()
