## Magasin Superset Dashboard Cloner
#### Launch Superset Through Docker Compose (Non development/ Production setup)

For Apple M1/M2 chips, it may be useful to set the environmental variable globally before proceeding:
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

### Quick setup
```
git clone https://github.com/apache/superset.git

cd superset

git checkout 2.1.0

TAG=2.1.0 docker compose -f docker-compose-non-dev.yml up
```
Edit the file ```docker-compose-non-dev.yml``` and update the key ```x-superset-image``` to use a specific image tag as below:

```
x-superset-image: &superset-image apache/superset:2.1.0
```
Then switch to the docker directory and update the environment variables in ```.env-non-dev``` file as below:

```
cd docker
```

```
SUPERSET_ENV=production
SUPERSET_LOAD_EXAMPLES=yes
SUPERSET_SECRET_KEY='TEXT_SUPERSET_SECRET_KEY'
CYPRESS_CONFIG=false
SUPERSET_PORT=8088
MAPBOX_API_KEY=''

CSRF_ENABLED=False
TALISMAN_ENABLED=False
WTF_CSRF_ENABLED=False

SESSION_COOKIE_SAMESITE='None'
SESSION_COOKIE_SECURE=false 
SESSION_COOKIE_HTTPONLY=false
```
