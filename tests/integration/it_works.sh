#!/bin/sh

set -euo pipefail

uuid=$(curl -X POST "ci/?token=$GITHUB_TOKEN" -d@- <<JSON
    { "after": "$commit", "repository": { "full_name": "docteurklein/compose-ci"} }
JSON
)

content=$(docker logs -f $uuid)

expected="Result(code=0"
test "${content#*$expected}" != "$content"

expected="OK (skipped=1)"
test "${content#*$expected}" != "$content"

