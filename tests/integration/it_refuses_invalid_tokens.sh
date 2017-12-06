#!/bin/sh

set -euxo pipefail

code=$(curl -sLw '%{http_code}' -X POST "ci/?token=NOPE" -o /dev/null -d@- <<JSON
    { "after": "$commit", "repository": { "full_name": "docteurklein/compose-ci"} }
JSON
)

test $code -eq '401'

