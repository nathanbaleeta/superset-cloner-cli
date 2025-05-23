## Magasin Superset Dashboard Cloner
#### Launch Superset Through Docker Compose (Non development/ Production setup)

For Apple M1/M2 chips, it may be useful to set the environment variable globally before proceeding:
```
export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

### Quick Superset setup
```
git clone https://github.com/apache/superset.git

cd superset

git checkout 3.1.0
```
Edit the file ```docker-compose-non-dev.yml``` and update the key ```x-superset-image``` to use a specific image tag as below:

```
x-superset-image: &superset-image apache/superset:3.1.0
```
Then switch to the ```docker``` directory and update the environment variables in ```.env-non-dev``` file as below:

```
cd docker
```

To generate a unique ```SUPERSET_SECRET_KEY``` environment variable use command below:
```
openssl rand -base64 42
```
```
SUPERSET_ENV=production
SUPERSET_LOAD_EXAMPLES=yes
SUPERSET_SECRET_KEY='TEXT_SUPERSET_SECRET_KEY'
CYPRESS_CONFIG=false
SUPERSET_PORT=8088
MAPBOX_API_KEY=''

CSRF_ENABLED=True
TALISMAN_ENABLED=False
WTF_CSRF_ENABLED=True

#SESSION_COOKIE_SAMESITE='None'
#SESSION_COOKIE_SECURE=false 
#SESSION_COOKIE_HTTPONLY=false
```



Navigate back to the superset root directory and run the docker compose commands as below:
```
cd ../
TAG=3.1.0 docker compose -f docker-compose-non-dev.yml pull
TAG=3.1.0 docker compose -f docker-compose-non-dev.yml up
```

#### Swagger API endpoint
```
http://localhost:8088/swagger/v1
```

