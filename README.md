# Teuthology API

A REST API to execute [teuthology commands](https://docs.ceph.com/projects/teuthology/en/latest/commands/list.html).

## Setup

### Option 1: Teuthology Docker Setup

1. Clone [teuthology](https://github.com/ceph/teuthology) and [teuthology-api](https://github.com/ceph/teuthology-api).
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
        env_file: ../../../teuthology-api/.env
        ports:
            - 8082:8080
        environment:
            TEUTHOLOGY_API_SERVER_HOST: 0.0.0.0
            TEUTHOLOGY_API_SERVER_PORT: 8080
            PADDLES_URL: http://localhost:8080
        depends_on:
            - teuthology
            - paddles
        links:
            - teuthology
            - paddles
        healthcheck:
          test: [ "CMD", "curl", "-f", "http://0.0.0.0:8082" ]
    ```
    [optional] For developement use:
    Add following things in `teuthology_api` container:
    ```
    teuthology_api:
        environment:
            DEPLOYMENT: development
        volumes:
            - ../../../teuthology-api/src:/teuthology_api/src:rw
    ```
    `DEPLOYMENT: development` would run the server in `--reload` mode (server would restart when changes are made in `/src` dir) and `volumes` would mount host directory to docker's directory (local changes would reflect in docker container).

5. Follow teuthology development setup instructions from [here](https://github.com/ceph/teuthology/tree/main/docs/docker-compose).

### Option 2: Non-containerized with venv and pip

1. Clone [teuthology-api](https://github.com/ceph/teuthology-api) and `cd` into it.

2. Rename `.env.dev` file to `.env`.

3. Configure secrets as described in Option 1 above.

4. Create a virtualenv: `python3 -m venv venv`

5. Activate the virtualenv: `source ./venv/bin/activate`

6. Build the project: `pip install -e .`

7. Start the server: `gunicorn -c gunicorn_config.py teuthology_api.main:app`

## Documentation

The documentation can be accessed at http://localhost:8082/docs after running the application.

Once you have teuthology-api running, authenticate by visiting `http://localhost:8082/login` through browser and follow the github authentication steps (this stores the auth token in browser cookies).

> Note: To test below endpoints locally, recommended flow is to login through browser (as mentioned above) and then send requests (and receive response) through interactive docs at `/docs`.

### Route `/`

```
curl http://localhost:8082/
```
Returns `{"root": "success", "session": { <authentication details> }}`.

### Route `/suite`

POST `/suite/`: schedules a run.

Query parameters:
- `logs` (boolean) - Send scheduling logs in response.

Example

    curl --location --request POST 'http://localhost:8082/suite&logs=true' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "--ceph": "main",
        "--ceph-repo": "https://github.com/ceph/ceph-ci.git",
        "--machine-type": "testnode",
        "--num": "1",
        "--priority": "70",
        "--suite": "teuthology:no-ceph",
        "--suite-branch": "main",
        "--suite-repo": "https://github.com/ceph/ceph-ci.git",
        "--teuthology-branch": "", // necessary for docker setup
        "--verbose": "1",
        "<config_yaml>": ["/teuthology/containerized_node.yaml"],
        "--owner": "example"
     }'

Note: "--owner" in data body should be same as your github username (case sensitive). Otherwise, you wouldn't have permission to kill jobs/run.

xxx
