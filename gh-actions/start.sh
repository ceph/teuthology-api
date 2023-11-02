#!/bin/bash
set -e
folder="teuthology"
if [ ! -d "$folder" ] ; then
    git clone https://github.com/ceph/teuthology.git
    echo "  teuthology_api:
        build:
          context: ../../../../
        ports:
            - 8082:8080
        environment: 
            TEUTHOLOGY_API_SERVER_HOST: 0.0.0.0
            TEUTHOLOGY_API_SERVER_PORT: 8080
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
    " >> teuthology/docs/docker-compose/docker-compose.yml
fi
cd teuthology/docs/docker-compose
./start.sh
