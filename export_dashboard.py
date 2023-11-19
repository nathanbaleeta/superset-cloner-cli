import click
import json
import random
import string


from api_request_handler import APIRequestHandler
from endpoints import DASHBOARD_ENDPOINT
from superset_constants import (
    SUPERSET_INSTANCE_URL,
    SUPERSET_USERNAME,
    SUPERSET_PASSWORD
) 

def _get_random_string(size=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

@click.command()
@click.option(
    "-d",
    "--dashboard_title",
    required=True,
    type=str,
    help="Name of dashboard to be exported",
)
@click.option(
    "-o",
    "--output_file",
    default=f"dashboard_{_get_random_string()}.json",
    type=str,
    help="Name of output file, defaults to dashboard_<random_string>.json",
)
def export_dashboard(dashboard_title, output_file):
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    dashboard_id = _get_dashboard_id(dashboard_title, request_handler)

    if dashboard_id >= 0:
        endpoint = f"{DASHBOARD_ENDPOINT}export/?q=!({dashboard_id})"
        response = request_handler.get_request(endpoint)
        _write_to_file(response, output_file)

        print(f"Dashboard details of '{dashboard_title}' written to {output_file}")
    else:
        print(f"Error: No dashboard with title '{dashboard_title}' found.")

def _get_dashboard_id(dashboard_title, request_handler):
    dashboard_request = request_handler.get_request(DASHBOARD_ENDPOINT)
    resp_dashboard = dashboard_request.json()

    for result in resp_dashboard["result"]:
        if result["dashboard_title"].lower() == dashboard_title.lower():
            return result["id"]

    return -1

def _write_to_file(dashboard_response, output_file):
    with open(f"{output_file}.zip", 'wb') as dashboard_file:
        dashboard_file.write(dashboard_response.content)

if __name__ == "__main__":
    export_dashboard()
