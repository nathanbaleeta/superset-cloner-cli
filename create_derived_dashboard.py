import copy
import json
import yaml
from yaml.loader import SafeLoader

import click

from api_request_handler import APIRequestHandler
from create_empty_dashboard import create_empty_dashboard
from duplicate_chart import create_chart
from endpoints import DASHBOARD_ENDPOINT, DATASET_ENDPOINT
from superset_constants import (
    SUPERSET_INSTANCE_URL,
    SUPERSET_USERNAME,
    SUPERSET_PASSWORD
) 


@click.command()
@click.option(
    "-f",
    "--dashboard_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the dashboard file exported through the API",
)
@click.option(
    "-c",
    "--config_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the JSON file containing <chart_name>:<dataset_name> pairs",
)
@click.option(
    "-n",
    "--new_dashboard_name",
    required=True,
    type=str,
    help="The name of the new derivative dashboard",
)
def create_derived_dashboard(dashboard_file, config_file, new_dashboard_name):
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    source_dashboard_name = _get_source_dashboard_name(dashboard_file)
    dashboard_id = create_empty_dashboard(source_dashboard_name, new_dashboard_name)

    chart_name_to_id_map = _create_chart_name_to_id_map(dashboard_file)
    dataset_info_map = _create_dataset_info_map(request_handler)
    chart_id_to_chart_info_map = _create_chart_id_to_chart_info_map(
        chart_name_to_id_map, dataset_info_map, config_file
    )

    old_chart_id_to_dup_id_map = {}
    for chart_id in chart_id_to_chart_info_map:
        dataset_id = chart_id_to_chart_info_map[chart_id]["id"]
        dataset_type = chart_id_to_chart_info_map[chart_id]["type"]
        new_chart_name = chart_id_to_chart_info_map[chart_id]["new_chart_name"]

        print(f"Creating chart '{new_chart_name}'...")
        new_chart_id = create_chart(
            chart_id, dashboard_id, dataset_id, dataset_type, new_chart_name
        )
        print(f"Chart '{new_chart_name}' created!\n")

        old_chart_id_to_dup_id_map[chart_id] = new_chart_id

    _retain_chart_positions(request_handler, dashboard_id, old_chart_id_to_dup_id_map)
    print(f"Dashboard '{new_dashboard_name}' successfully created!")


def _retain_chart_positions(request_handler, dashboard_id, chart_id_map):
    dashboard_endpoint = f"{DASHBOARD_ENDPOINT}{dashboard_id}"
    get_dashboard_response = request_handler.get_request(dashboard_endpoint)
    dashboard_info = get_dashboard_response.json().get("result")
    if not dashboard_info:
        raise SystemExit(f"Dashboard info for dashboard with id {dashboard_id} not found!")

    position_json_str = dashboard_info.get("position_json")
    if not position_json_str:
        raise SystemExit(f"position_json not found in response. Exiting.")

    position_json_dict = json.loads(position_json_str)

    for key, value in position_json_dict.items():
        if (
            type(value) is dict
            and "meta" in value.keys()
            and "chartId" in value["meta"].keys()
        ):
            old_chart_id = value["meta"]["chartId"]
            value["meta"]["chartId"] = chart_id_map[old_chart_id]

    altered_position_json = json.dumps(position_json_dict)
    put_request_payload = _change_position_json(dashboard_info, altered_position_json)
    put_request = request_handler.put_request(
        dashboard_endpoint, json=put_request_payload
    )

    return put_request


def _change_position_json(dashboard_info, altered_position_json):
    put_request_payload = {}
    put_request_payload["certification_details"] = dashboard_info[
        "certification_details"
    ]
    put_request_payload["certified_by"] = dashboard_info["certified_by"]
    put_request_payload["css"] = dashboard_info["css"]
    put_request_payload["dashboard_title"] = dashboard_info["dashboard_title"]
    put_request_payload["json_metadata"] = dashboard_info["json_metadata"]
    put_request_payload["owners"] = [owner["id"] for owner in dashboard_info["owners"]]
    put_request_payload["published"] = dashboard_info["published"]
    put_request_payload["roles"] = dashboard_info["roles"]
    put_request_payload["slug"] = dashboard_info["slug"]
    put_request_payload["position_json"] = altered_position_json

    return put_request_payload


def _get_source_dashboard_name(dashboard_file):
    with open(dashboard_file) as f:
        dashboard_data = yaml.load(f, Loader=SafeLoader) or {}

    if not dashboard_data:
        raise SystemExit(f"Dashboard data not found in {dashboard_file}!")

    dashboard_name = dashboard_data.get('dashboard_title')
    if not dashboard_name:
        raise SystemExit(f"Dashboard name not found in {dashboard_file}!")

    return dashboard_name


def _create_chart_name_to_id_map(dashboard_file):
    with open(dashboard_file, "r") as input_file:
        dashboard_dict = json.load(input_file)

    dashboard_data = dashboard_dict.get("dashboards")[0].get("__Dashboard__")
    if not dashboard_data:
        raise SystemExit(f"Dashboard data not found in {dashboard_file}!")

    chart_list = dashboard_data.get("slices")
    if not chart_list:
        raise SystemExit(f"List of charts not found in {dashboard_file}!")

    chart_name_to_id_map = {}
    for chart in chart_list:
        chart_info = chart["__Slice__"]
        chart_name = chart_info["slice_name"]
        chart_name_to_id_map[chart_name] = chart_info["id"]

    return chart_name_to_id_map


def _create_dataset_info_map(request_handler):
    params = (
        (
            "q",
            '{"columns": ["id", "table_name", "datasource_type"], "page": 0, "page_size": 1000}',
        ),
    )
    get_dataset_response = request_handler.get_request(DATASET_ENDPOINT, params=params)
    datasets = get_dataset_response.json().get("result")
    if not datasets:
        raise SystemExit(f"List of datasets not found! Check if Superset API has been changed.")

    dataset_info_map = {}
    for dataset in datasets:
        dataset_name = dataset["table_name"]
        dataset_info_map[dataset_name] = {
            "id": dataset["id"],
            "type": dataset["datasource_type"],
        }

    return dataset_info_map


def _create_chart_id_to_chart_info_map(
    chart_name_to_id_map, dataset_info_map, config_file
):
    with open(config_file, "r") as input_file:
        config_map = json.load(input_file)

    chart_id_to_chart_info_map = {}
    for chart_name, chart_info in config_map.items():
        chart_id = chart_name_to_id_map[chart_name]
        dataset_name = chart_info["dataset"]

        if dataset_info_map.get(dataset_name):
            chart_id_to_chart_info_map[chart_id] = copy.deepcopy(
                dataset_info_map[dataset_name]
            )
        else:
            raise SystemExit(
                f"Cannot find dataset '{dataset_name}' for chart '{chart_name}'\n"
                f"Please check if the dataset name provided in the config file '{config_file}' is correct."
            )

        new_chart_name = chart_info.get("new_chart_name", f"chart-{chart_id}")
        chart_id_to_chart_info_map[chart_id]["new_chart_name"] = new_chart_name

    return chart_id_to_chart_info_map


if __name__ == "__main__":
    create_derived_dashboard()