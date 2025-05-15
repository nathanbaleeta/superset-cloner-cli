import click
import random
import string
import yaml
import re
import json
import copy

from io import BytesIO
from zipfile import ZipFile


from api_request_handler import APIRequestHandler
from endpoints import DASHBOARD_ENDPOINT, DATASET_ENDPOINT
from duplicate_chart import create_chart
from create_derived_dashboard import (
    create_empty_dashboard, 
    _create_chart_name_to_id_map, 
    _create_dataset_info_map,
    _retain_chart_positions
    )
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
        response = request_handler.get_request(endpoint, verify=False)
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
    
     # unzip the content
    f = ZipFile(BytesIO(dashboard_response.content))
    print(f.namelist())

    with f.open(f.namelist()[3], 'r') as g:
        # Read YAML file
        dashboard_data = yaml.safe_load(g)
       
        print('\n')
        print('#' * 100)

        if not dashboard_data:
            raise SystemExit(f"Dashboard data not found in {g}!")

    # private local function
    source_dashboard_name = _get_source_dashboard_name(dashboard_data)

    # private local function
    slice_config_map = _create_slice_config_map(dashboard_data, output_file)

    # import as module
    #dashboard_id = create_empty_dashboard(source_dashboard_name, 'RapidPro 2022 Messages duplicate')
    dashboard_id = create_empty_dashboard(source_dashboard_name, 'INVENT Data Analytics duplicate')

    # private local function
    chart_name_to_id_map = _create_chart_name_to_id_map(dashboard_data, output_file)

    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    dataset_info_map = _create_dataset_info_map(request_handler)

    chart_id_to_chart_info_map = _create_chart_id_to_chart_info_map(chart_name_to_id_map, dataset_info_map, slice_config_map)

    old_chart_id_to_dup_id_map = {}
    for chart_id in chart_id_to_chart_info_map:
        dataset_id = chart_id_to_chart_info_map[chart_id]["id"]
        dataset_type = chart_id_to_chart_info_map[chart_id]["type"]
        new_chart_name = chart_id_to_chart_info_map[chart_id]["new_chart_name"]

        print(f"Creating chart '{new_chart_name}'...")
        new_chart_id = create_chart(
            chart_id, dashboard_id, dataset_id, dataset_type, new_chart_name
        )
        #print(f"Chart '{new_chart_name}' created!\n")

        old_chart_id_to_dup_id_map[chart_id] = new_chart_id

        _retain_chart_positions(request_handler, dashboard_id, old_chart_id_to_dup_id_map)
    #print(f"Dashboard '{new_dashboard_name}' successfully created!")

def _get_source_dashboard_name(dashboard_data):
    dashboard_name = dashboard_data.get('dashboard_title')

    if not dashboard_name:
        raise SystemExit(f"Dashboard name not found in {dashboard_data}!")
    
    return dashboard_name

def _create_chart_id_to_chart_info_map(chart_name_to_id_map, dataset_info_map, slice_config_map):

    chart_id_to_chart_info_map = dict()
    for chart_name, chart_info in slice_config_map.items():
        chart_id = chart_name_to_id_map[chart_name]
        dataset_name = chart_info["dataset"]

        if dataset_info_map.get(dataset_name):
            chart_id_to_chart_info_map[chart_id] = copy.deepcopy(
                dataset_info_map[dataset_name]
            )
        else:
            raise SystemExit(
                f"Cannot find dataset '{dataset_name}' for chart '{chart_name}'\n"
                f"Please check if the dataset name provided in the config file '{slice_config_map}' is correct."
            )

        new_chart_name = chart_info.get("new_chart_name", f"chart-{chart_id}")
        chart_id_to_chart_info_map[chart_id]["new_chart_name"] = new_chart_name

    return chart_id_to_chart_info_map

def _create_slice_config_map(dashboard_data, output_file):
    chart_list = dashboard_data.get("position")

    if not chart_list:
        raise SystemExit(f"List of charts not found in {output_file}!")
    
    # regex pattern
    pattern = "CHART-"

    # Using pattern matching & list comprehension to extract charts info
    chart_filtered_keys = [x for x in chart_list if re.match(pattern, x)]

    # apply selective filtering to chart list dictionary to drop non chart info
    result = [chart_list[i] for i in chart_filtered_keys if i in chart_list]

    # convert filtered chart list back to dictionary for parsing
    chart_filtered_dict = dict(zip(range(len(result)), result))

    chart_filtered_list = list(chart_filtered_dict.keys())

    slice_list = []
    for chart in chart_filtered_list:
        chart_name = chart_filtered_dict[chart]['meta']['sliceName']
        slice_list.append(chart_name)

    slice_config_map = {}

    for i in slice_list:
        slice_config_map[i] = {}
        slice_config_map[i] = {}
        slice_config_map[i]['dataset'] = 'invent_initiatives_transformed.parquet' #'2022_combined_channel_stats_tall' #'invent_initiatives_transformed.parquet' 
        slice_config_map[i]['new_chart_name'] = f'{i} duplicate'


    #print(json.dumps(slice_config_map, indent=2))
    return slice_config_map


def _create_chart_name_to_id_map(dashboard_data, output_file):
    # with open(dashboard_file) as input_file:
    #     dashboard_data = yaml.load(input_file, Loader=SafeLoader) or {}

    if not dashboard_data:
        raise SystemExit(f"Dashboard data not found in {output_file}!")

    chart_list = dashboard_data.get("position")

    if not chart_list:
        raise SystemExit(f"List of charts not found in {output_file}!")

    # regex pattern
    pattern = "CHART-"

    # Using pattern matching & list comprehension to extract charts info
    chart_filtered_keys = [x for x in chart_list if re.match(pattern, x)]

    # apply selective filtering to chart list dictionary to drop non chart info
    result = [chart_list[i] for i in chart_filtered_keys if i in chart_list]
 
    # convert filtered chart list back to dictionary for parsing
    chart_filtered_dict = dict(zip(range(len(result)), result))

    chart_filtered_list = list(chart_filtered_dict.keys())

    chart_name_to_id_map = {}

    # Iterate through nested dictionary to extract useful chart values
    for chart in chart_filtered_list:
        chart_name = chart_filtered_dict[chart]['meta']['sliceName']
        chart_name_to_id_map[chart_name] = chart_filtered_dict[chart]['meta']['chartId']

    return chart_name_to_id_map

        
            
if __name__ == "__main__":
    export_dashboard()
