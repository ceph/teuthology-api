# Teuthology API

A REST API to execute [teuthology commands](https://docs.ceph.com/projects/teuthology/en/latest/commands/list.html). 

## Setup

#### Option 1: (teuthology docker setup)

1. Clone [teuthology](https://github.com/ceph/teuthology) and [teuthology-api](https://github.com/VallariAg/teuthology-api).
2. Rename `.env.dev` file to `.env`. 
3. Configure secrets:
    
   3.1. Create a Github OAuth Application by following [these](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) instructions. Set "Homepage URL" as `http://localhost:8082/` and "Authorization callback URL" as `http://localhost:8082/login/callback/`. 

   3.2. Ensure [ceph](https://github.com/ceph) belongs in your public list of organizations[[ref](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-membership-in-organizations/about-organization-membership)]. By default your membership is set private, change that to public by following [these](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-membership-in-organizations/publicizing-or-hiding-organization-membership) steps.

   3.3. Save `CLIENT_ID` and `CLIENT_SECRET` from your Github OAuth App to your local `.env` file as `GH_CLIENT_ID` and `GH_CLIENT_SECRET`.

4. Add the following to [teuthology's docker-compose](https://github.com/ceph/teuthology/blob/main/docs/docker-compose/docker-compose.yml) services.
    ```
    teuthology_api:
        build:
          context: ../../../teuthology-api
        ports:
            - 8082:8080
        environment: 
            TEUTHOLOGY_API_SERVER_HOST: 0.0.0.0
            TEUTHOLOGY_API_SERVER_PORT: 8080
            PADDLES_URL: http://localhost:8080
            TEUTHOLOGY_API_SQLALCHEMY_URL: postgresql+psycopg2://admin:password@tapi_db:5432/tapi_db
        depends_on:
            - teuthology
            - paddles
            - tapi_db
        links:
            - teuthology
            - paddles
             - tapi_db
        healthcheck:
          test: [ "CMD", "curl", "-f", "http://0.0.0.0:8082" ]
    tapi_db:
        image: postgres:14
        healthcheck:
            test: [ "CMD", "pg_isready", "-q", "-d", "tapi_db", "-U", "admin" ]
            timeout: 5s
            interval: 10s
            retries: 2
        environment:
            - POSTGRES_USER=root
            - POSTGRES_PASSWORD=password
            - APP_DB_USER=admin
            - APP_DB_PASS=password
            - APP_DB_NAME=tapi_db
        volumes:
            - ./db:/docker-entrypoint-initdb.d/
        ports:
            - 5433:5432
    ```

    [optional] For developement use:
    Add following things in `teuthology_api` container:
    ```
    teuthology_api:
        environment: 
            DEPLOYMENT: development
        volumes: 
            - ../../../teuthology-api:/teuthology_api/:rw
    ```
    `DEPLOYMENT: development` would run the server in `--reload` mode (server would restart when changes are made in `/src` dir) and `volumes` would mount host directory to docker's directory (local changes would reflect in docker container). 
3. Follow teuthology development setup instructions from [here](https://github.com/ceph/teuthology/tree/main/docs/docker-compose).

## Documentation

The documentation can be accessed at http://localhost:8082/docs after running the application.

Note: To run commands, authenticate by visiting `http://localhost:8082/login` through browser and follow the github authentication steps (this stores the auth token in browser cookies). 

### Route `/`

```
curl http://localhost:8082/
```
Returns `{"root": "success", "session": { <authentication details> }}`.

### Route `/suite`

POST `/suite/`: schedules a run.

Two query parameters: 
- `dry_run` (boolean) - Do a dry run; do not schedule anything.
- `logs` (boolean) - Send scheduling logs in response.

Example:
```
curl --location --request POST 'http://localhost:8082/suite?dry_run=false&logs=true' \
--header 'Content-Type: application/json' \
--data-raw '{
         "--ceph": "wip-dis-testing-2",
         "--ceph-repo": "https://github.com/ceph/ceph-ci.git",
         "--kernel": "distro",
         "--limit": "2",
         "--newest": "0",
         "--machine-type": "testnode",
         "--num": "1",
         "--priority": "70",
         "--suite": "teuthology:no-ceph",
         "--suite-branch": "wip-dis-testing-2",
         "--suite-repo": "https://github.com/ceph/ceph-ci.git",
         "--teuthology-branch": "main",
         "--verbose": "1",
         "--user": "vallariag"
 }'
```
