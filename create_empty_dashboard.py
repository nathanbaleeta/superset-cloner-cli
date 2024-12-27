import click
import json

from api_request_handler import APIRequestHandler
from endpoints import DASHBOARD_ENDPOINT 
from superset_constants import (
    SUPERSET_INSTANCE_URL,
    SUPERSET_USERNAME,
    SUPERSET_PASSWORD
) 

@click.command()
@click.option(
    "-s",
    "--source_dashboard_name",
    required=True,
    type=str,
    help="Name of the template dashboard",
)
@click.option(
    "-d",
    "--destination_dashboard_name",
    required=True,
    type=str,
    help="Name of the derivative dashboard",
)
def create_empty_dashboard_command(source_dashboard_name, destination_dashboard_name):
    create_empty_dashboard(source_dashboard_name, destination_dashboard_name)

def create_empty_dashboard(source_dashboard_name, destination_dashboard_name):
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    print(f"Creating empty dashboard '{destination_dashboard_name}' from '{source_dashboard_name}'...")
    dashboard_id = _create_dashboard(request_handler, source_dashboard_name, destination_dashboard_name)
    print(f"Created empty dashboard '{destination_dashboard_name}' with id: {dashboard_id}.\n")

    return dashboard_id


def _create_dashboard(request_handler, source_dashboard_name, new_dashboard_name):
    dashboard_get_response = request_handler.get_request(DASHBOARD_ENDPOINT)
    dashboards = json.loads(dashboard_get_response.text)['result']
    dashboard_data = {}

    for dashboard in dashboards:
        if dashboard['dashboard_title'].lower() == source_dashboard_name.lower():
            dashboard_data = dashboard

    if not dashboard_data:
        raise SystemExit(f"Source dashboard name '{source_dashboard_name}' not found!")

    keys_to_remove = [
        'changed_by',
        'changed_by_name',
        'changed_by_url',
        'changed_on_delta_humanized',
        'created_on_delta_humanized', # This field was missing in the earlier API when orginal script created
        'changed_on_utc',
        'created_by',
        'id',
        'status',
        'thumbnail_url',
        'url',
        'tags' # This field was added in Superset 3.0.2
    ]

    for key in keys_to_remove:
        dashboard_data.pop(key, None)

    dashboard_data['dashboard_title'] = new_dashboard_name
    dashboard_data['slug'] = new_dashboard_name.lower().replace(" ", "-")
    if not dashboard_data.get('css'):
        dashboard_data['css'] = ""

    dashboard_data['owners'] = [owner['id'] for owner in dashboard_data['owners']]

    dashboard_post_response = request_handler.post_request(DASHBOARD_ENDPOINT, json=dashboard_data, verify=False)
    dashboard_id = dashboard_post_response.json().get('id')

    if not dashboard_id:
        raise SystemExit(f"Dashboard ID missing from response. Check if the Superset API has been changed.")

    return dashboard_id

if __name__ == "__main__":
    create_empty_dashboard_command()
