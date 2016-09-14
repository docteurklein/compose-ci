#!/bin/sh

set -euxo pipefail

function finish {
    docker rm -fv ci-test
}
trap finish EXIT

docker run -d \
    -e GITHUB_REPO=docteurklein/compose-ci -e GITHUB_TOKEN \
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

uuid=$(curl -X POST "localhost:$port/?token=$GITHUB_TOKEN" -d "{\"after\": \"$commit\"}")

content=$(docker logs -f $uuid)

expected="OK (skipped=1)"

test "${content#*$expected}" != "$content"

