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
    init_logs
    export_env
    trap finish EXIT
    gh_status "pending" || true
    download
    ${HOOK} &> >(tee /logs)
    exitCode=$?
}

function gh_status {
    curl -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/repos/${GITHUB_REPO}/statuses/$commit" \
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
    if [ -z ${SMTP_TO-} ]; then
        return
    fi
    cat >> /logs <<EOF

    ----------------------------------------------
    build uuid: ${uuid}
    ----------------------------------------------

EOF
    docker version &>> /logs
    docker-compose version &>> /logs

    state=$([ $exitCode == 0 ] && echo 'passed' || echo 'failed')
    cat /logs | aha -b | mutt \
        -s "[${GITHUB_REPO} ci] commit ${short_commit} ${state}!" \
        -e "set content_type=text/html" \
        -e "set smtp_url=smtp://${SMTP_USER}@${SMTP_HOST}:${SMTP_PORT}" \
        -e "set smtp_pass=${SMTP_PASS}" \
        -e "set from=${SMTP_FROM}" \
        $SMTP_TO
}

function finish {
    set +e
    gh_status "$([ $exitCode == 0 ] && echo 'success' || echo 'failure')"
    notify
    if [ "${GARBAGE_COLLECT-1}" = 1 ] ; then
        docker-compose stop
        docker-compose rm -fv --all
        docker network rm "${COMPOSE_PROJECT_NAME}_default"
        docker rm -fv ${uuid} # remove myself!
    fi
}

run
