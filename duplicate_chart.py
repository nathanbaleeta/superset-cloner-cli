import click

from api_request_handler import APIRequestHandler
from endpoints import CHART_ENDPOINT 
from superset_constants import (
    SUPERSET_INSTANCE_URL,
    SUPERSET_USERNAME,
    SUPERSET_PASSWORD
) 

@click.command()
@click.option(
    "-oid",
    "--origin_chart_id",
    required=True,
    type=int,
    help="Chart ID of the original chart.",
)
@click.option(
    "-db",
    "--dashboard_id",
    required=True,
    type=int,
    help="Dashboard ID of the new dashboard.",
)
@click.option(
    "-ds",
    "--datasource_id",
    required=True,
    type=int,
    help="Datasource ID of the dataset.",
)
@click.option(
    "-dt",
    "--datasource_type",
    required=True,
    type=str,
    help="Datasource type of the dataset.",
)
@click.option(
    "-sn",
    "--slice_name",
    required=True,
    type=str,
    help="Name of the new chart.",
)
def create_chart_command(origin_chart_id,
                dashboard_id,
                datasource_id,
                datasource_type,
                slice_name
                ):

    create_chart(origin_chart_id, dashboard_id, datasource_id, datasource_type, slice_name)

def create_chart(origin_chart_id,
                dashboard_id,
                datasource_id,
                datasource_type,
                slice_name
                ):

    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    chart_details = _get_chart_details(origin_chart_id, request_handler)
    new_chart_details = _change_chart_details(chart_details,
                                            dashboard_id,
                                            datasource_id, 
                                            datasource_type, 
                                            slice_name)

    create_chart_request = request_handler.post_request(CHART_ENDPOINT, json=new_chart_details)
    chart_id = create_chart_request.json().get('id')

    if not chart_id:
        raise SystemExit(f"Chart ID not found upon creation. Check if the Superset API has been changed.")

    return chart_id

def _get_chart_details(origin_chart_id, request_handler):
    chart_details_endpoint = f"{CHART_ENDPOINT}{origin_chart_id}" 
    chart_details_request = request_handler.get_request(chart_details_endpoint)
    chart_details = chart_details_request.json().get('result')

    if not chart_details:
        raise SystemExit(f"Chart details missing from response. Check if the Superset API has been changed.")
    
    keys_to_remove = [
        'thumbnail_url', 
        'url', 
        'id', 
        'changed_on_delta_humanized', 
        'owners', 
        'tags' # This field was added in Superset 3.0.2
    ]

    for key in keys_to_remove:
        chart_details.pop(key, None)

    return chart_details


def _change_chart_details(chart_details, 
                        dashboard_id, 
                        datasource_id, 
                        datasource_type, 
                        slice_name):

    chart_details["dashboards"][0] = dashboard_id 
    chart_details["datasource_id"] = datasource_id
    chart_details["datasource_type"] = datasource_type
    chart_details["slice_name"] = slice_name
    #chart_details['owners'] = [owner['id'] for owner in chart_details['owners']]

    return chart_details

if __name__ == "__main__":
    # Example: create_chart(129, 11, 15, "How do you prefer to work? DUPLICATE")
    create_chart_command()
