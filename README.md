# compose-ci

## TL;DR

``` bash
# docker-machine create --driver <driver> my_ci
eval (docker-machine env my_ci)
docker run -d \
    -e HOOK="docker-compose run tests" \
    -e GITHUB_TOKEN -e GITHUB_REPO \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 8080:80 \
    docteurklein/compose-ci

curl -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    "https://api.github.com/repos/${GITHUB_REPO}/hooks" \
    -d@- <<JSON
      { "name": "web", "active": true, "events": [ "push" ], "config": {
        "url": "http://$(docker-machine ip my_ci):8080/?token=${GITHUB_TOKEN}",
        "content_type": "json",
        "insecure_ssl": "1"
      }}
JSON
```

## What ?

A simple, docker(-compose) enabled, alpine-based container, listening for github webhooks.

It will:
 - [notify](https://developer.github.com/v3/repos/statuses/) github of the build status
 - download and extract the corresponding tarball, then `cd` inside it
 - export some environment variables (`$COMPOSE_PROJECT_NAME`, `$commit`, `$short_commit`, …)
 - execute the `$HOOK` command inside a separate container
 - send a mail containing the `$HOOK` command output
 - cleanup running containers and networks afterwards

## Why ?

SaaS CIs are cool and all, but you clearly don't have the same flexibility as this \o/  
This also prepares the environment with latest versions of docker and compose,  
making it a breeze to run your tests.

It's self hosted. It can be used wherever docker is running.

## How to customize ?

 > Note: This is optional.

You can extend the base image and provide a `server.pem` certificate.  
In order to use it, you can `COPY` it in the image, or mount it using:

    docker run \
        -v my-cert.pem:/certs/my-cert.pem \
        -e CERT_PATH=/certs/my-cert.pem

### Create the `server.pem` file

    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes

> Note: the certificate must match the public IP (or hostname) that will be used for the webhook.

### Create a `Dockerfile`

``` Dockerfile
FROM docteurklein/compose-ci

COPY server.pem /certs/server.pem
COPY hook /hook # optional, to embed a hook file

# add extra packages
# RUN apk add --update <packages>
```

> Note: don't forget to add the `-e CERT_PATH=/certs/server.pem` env variable.

### Embed a `hook` file

> Note: this is optional. Run this with the appropriate `$HOOK` config.  
> You have access to the `docker`, `aws`, and `docker-compose` commands, plus all what alpine proposes.  
> All the output (stderr included) of this script will be sent to you by mail.  

``` bash
#!/bin/bash

set -exuo pipefail # stop on failure

# auth for private registry
eval $(aws ecr get-login)

docker-compose pull

# build latest images
docker-compose build

# run containers
docker-compose up -d

docker-compose run tests
# or ./bin/ci
# or ./bin/test

# push latest images in ECR only if tests pass
images=( "my" "images" "names" )
for image in "${images[@]}"
do
    docker push ${DOCKER_REGISTRY}/${image}:latest # (latest or $short_commit)
done
```

> Note: Don't forget to `chmod +x hook`.

### Run it

In order to listen to github webhooks, you'll need to define some environment variables.

> Note: All these variables will also be passed to the `hook` command.

Some variables are mandatory:

 - `$HOOK` the command to execute
 - `$GITHUB_TOKEN` a valid o-auth token
 - `$GITHUB_REPO` to know which tarball to download

Some are optional:

 - `$BUILD_IMAGE` the image to use for separate containers (default: docteurklein/compose-ci)
 - `$SMTP_*` if you want to receive emails
 - `$CERT_PATH` the absolute path to your https certificate
 - `$GARBAGE_COLLECT` set to 0 to keep the containers running (default 1)
 - whatever else that is required by your command

``` bash
docker build -t my_ci .

docker run -it --rm \
    -p 8080:80 \
    -e HOOK="/hook" \
    -e GITHUB_TOKEN -e GITHUB_REPO \
    -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
    -e SMTP_FROM -e SMTP_TO -e SMTP_HOST -e SMTP_PORT -e SMTP_USER -e SMTP_PASS \
    -v /var/run/docker.sock:/var/run/docker.sock \
    my_ci
```

> Note: We mount `docker.sock` inside the container.  
> /!\ This means that any docker command executed by the `hook` will be made against the **host** docker engine.


*Tadaaa!* You now have a service waiting for web hooks on port 8080.  
Grab the IP address of your host and configure a [github web hook](https://developer.github.com/webhooks/).

The url **MUST** contain [`?token=<my-oauth-token>`](https://github.com/settings/tokens/new).  
This token **MUST** match `$GITHUB_TOKEN`.

> Note: Depending wether your certificate (`server.pem`) is correctly signed, you might have to disable SSL verification.

## Manually trigger a build:

You can simulate a github webhook request using:

    curl -X POST "$(docker-machine ip my_ci):8080/?token=$GITHUB_TOKEN" -d '{"after": "<commit>"}'

## Logs and artifacts

Each build is executed inside a separate container, 
which means we can leverage the docker capabilities to retrieve logs and data.

> Note: These separate containers are removed if `$GARBAGE_COLLECT=1`.

### see what happened

    docker logs <uuid>

### re-execute a build

    docker start -a <uuid>

### get files

    docker cp <uuid>/tarball .

> Note: The uuid is visible at the end of every email and in the response of the webhook http request.


## A note about security

It is SSL-ready, but not enabled by default. You need to generate a certificate and enable it,
by using the `CERT_PATH` variable.

The only verification that is made is the `$GITHUB_TOKEN` comparison...
That same token is used to authenticate against the github API.

This is **not** intended to replace a multi-tenant SaaS.  
This is however not really important since you can launch one instance per project.

If you mount the docker socket, **anyone** can do **anything** to your host.  
If you don't want that, take a look at [--userns-remap](https://docs.docker.com/engine/reference/commandline/daemon/#starting-the-daemon-with-user-namespaces-enabled).  
But even then, the same docker engine is shared for every build.


