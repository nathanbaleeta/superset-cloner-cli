## Magasin Superset Dashboard Cloner

## Derivative-dashboard
This repository should include scripts related to creating derivative dashboards for UNICEF's country offices

### Pre-requisites
- Python 3.8+
- Docker
- Superset 2.1.0+ - Follow instructions [here](https://github.com/nathanbaleeta/magasin-superset-dashboard-cloner/blob/main/SUPERSET_SETUP.md) on how to install & configure the API for consuming

### Quick Setup
The project uses [Poetry](https://python-poetry.org/) to keep track of its dependencies. To install it, you can follow the instructions [here](https://python-poetry.org/docs/#installing-with-pipx).

Once Poetry has been installed, you can run the following commands to set up the project in your local:
```
git clone git@github.com:nathanbaleeta/magasin-superset-dashboard-cloner.git

python3 -m venv venv

source venv/bin/activate

poetry install
```

You'lll also need to set three environment variables before running the script: ```SUPERSET_INSTANCE_URL```, ```SUPERSET_USERNAME```, and ```SUPERSET_PASSWORD```. If any of these are not set, the scripts would fail to run. If you have a local Superset instance set up, sourcing the following .env file should work:

```
export SUPERSET_INSTANCE_URL='http://localhost:8088/'
export SUPERSET_USERNAME='admin'
export SUPERSET_PASSWORD='admin'
```

If you're going to test on staging, you'll need to change these three variables. Take note of the last / in the instance URL, as it's needed for the API endpoint concatenates to work properly.

## Running the scripts

### create_empty_dashboard.py
The script accepts 2 options:

- s - name of the template dashboard
- d - name of the derivative dashboard

```
python create_empty_dashboard.py -s "<source_dashboard_name>" -d "destination_dashboard_name"
```

Using an example, command would look like so:

```
python create_empty_dashboard.py -s "Sales Dashboard" -d "Sales Dashboard - Duplicate"
```
Once the script is run, you should be able to see the new empty dashboard in the Superset instance.

### duplicate_chart.py
The script accepts 5 options:
- oid - Chart ID of the original chart
- db - dashboard ID of the new dashboard
- ds - datasource ID of the dataset
- dt - datasource type of the dataset
- sn - name of the new chart (a.k.a slide_name in Superset API)

```
python duplicate_chart.py -oid 101 -db 24 -ds 10 -dt "table" -sn "Total Revenue - Duplicate"
```

### export_dashboard.py
The script accepts 2 options:
- d - Name of dashboard to be exported
- o - Name of output file, defaults to dashboard_<random_string>

```
python export_dashboard.py -d "COVID Vaccine Dashboard" -o "covid_vaccine_dashboard"
```
If the output_filename isn't specified, the script will default the filename to dashboard.json.


