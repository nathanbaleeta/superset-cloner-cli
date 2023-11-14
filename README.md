## Magasin Superset Dashboard Cloner

## Derivative-dashboard
This repository should include scripts related to creating derivative dashboards for UNICEF's country offices

### Quick Setup
The project uses [Poetry](https://python-poetry.org/) to keep track of its dependencies. To install it, you can follow the instructions [here](https://python-poetry.org/docs/#installing-with-pipx).

Once Poetry has been installed, you can run the following commands to set up the project in your local:
```
git clone git@github.com:nathanbaleeta/magasin-superset-dashboard-cloner.git

python3 -m venv venv

source <name_of_virtual_env>/bin/activate

poetry install
```

You'lll also need to set three environment variables before running the script: SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, and SUPERSET_PASSWORD. If any of these are not set, the scripts would fail to run. If you have a local Superset instance set up, sourcing the following .env file should work:

```
export SUPERSET_INSTANCE_URL='http://localhost:8088/'
export SUPERSET_USERNAME='admin'
export SUPERSET_PASSWORD='admin'
```

If you're going to test on staging, you'll need to change these three variables. Take note of the last / in the instance URL, as it's needed for the API endpoint concatenates to work properly.

## Running the scripts
