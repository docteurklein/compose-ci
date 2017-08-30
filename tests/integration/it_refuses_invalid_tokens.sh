#!/bin/sh

set -euxo pipefail

function finish {
    docker rm -fv ci-test
}
trap finish EXIT

docker run -d \
    -e YEAH \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 80 \
    -P \
    --name ci-test \
    -e LOG_LEVEL=DEBUG \
    docteurklein/compose-ci

commit=$(git log -1 --format=%H)
port=$(docker port ci-test 80/tcp)
port=${port##*:}

sleep 2

code=$(curl -sLw '%{http_code}' -X POST "localhost:$port/?token=NOPE" -o /dev/null -d@- <<JSON
    { "after": "$commit", "repository": { "full_name": "docteurklein/compose-ci"} }
JSON
)

test $code -eq '401'

