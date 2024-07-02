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
            TEUTHOLOGY_API_SQLITE_URI: sqlite:////teuthology_api/teuthology.db
        depends_on:
            - teuthology
            - paddles
        links:
            - teuthology
            - paddles
        healthcheck:
          test: [ "CMD", "curl", "-f", "http://0.0.0.0:8082" ]
    " >> teuthology/docs/docker-compose/docker-compose.yml
fi
cd teuthology/docs/docker-compose
./start.sh
