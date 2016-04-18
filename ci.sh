#!/bin/bash

set -exuo pipefail

commit=$1
uuid=$2

function export_env {
    export commit
    export short_commit="${commit:0:7}"

    export COMPOSE_PROJECT_NAME=$(
        echo "${uuid}" | tr -cd '[[:alnum:]]' | tr '[:upper:]' '[:lower:]'
    )
    export COMPOSE_HTTP_TIMEOUT=600
}

function run {
    exitCode=1
    export_env
    init_logs
    trap finish EXIT

    gh_status "pending" || true

    env
    docker version
    docker-compose version

    download
    eval ${HOOK} &> >(tee /logs)
    exitCode=$?
}

function gh_status {
    curl -X POST "https://api.github.com/repos/${GITHUB_REPO}/statuses/$commit" \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -d@- <<JSON
            {"state": "$1", "context": "[${GITHUB_REPO} ci]"}"
JSON
}

function download {
    url="https://api.github.com/repos/${GITHUB_REPO}/tarball/$commit"
    mkdir -p /tarball
    curl -H "Authorization: token ${GITHUB_TOKEN}" -kL $url | tar xz -C /tarball
    cd /tarball/*
}

function init_logs {
    cat > /logs <<EOF

    Oops! The hook didn't even run.
    Look at the logs at the given build uuid.

EOF
}

function notify {
    cat >> /logs <<EOF

    ------------------------------------------------
    exit status code: $exitCode
    build uuid: ${uuid}
    ------------------------------------------------

EOF
    docker version &>> /logs
    docker-compose version &>> /logs

    state=$([ $exitCode == 0 ] && echo 'passed' || echo "failed (exit $exitCode)")
    cat /logs | aha -b | python /mail.py "[${GITHUB_REPO} ci] ${short_commit} ${state}!"
}

function finish {
    set +e

    gh_status "$([ $exitCode == 0 ] && echo 'success' || echo 'failure')"
    if [ -n ${SMTP_TO-} ]; then
        notify
    fi

    docker-compose stop
    docker-compose rm -fv --all
    docker network rm "${COMPOSE_PROJECT_NAME}_default"

    if [ "${GARBAGE_COLLECT}" = 1 ] ; then
        docker rm -fv ${uuid} # remove myself!
    fi
}

run
