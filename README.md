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
