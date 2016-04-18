FROM alpine:edge

COPY repositories /etc/apk/repositories

RUN apk add --no-cache \
    docker \
    py-pip \
    curl \
    unzip \
    aha@testing \
    bash \
    && pip install docker-compose awscli \
    && rm -rf \
        /tmp/* \
        /root/.cache \
        /var/cache/apk \
        $(find / -regex '.*\.py[co]')

EXPOSE 80

ENV DOCKER_HOST=unix:///var/run/docker.sock
ENV BUILD_IMAGE=docteurklein/compose-ci
ENV BUILD_CMD=/ci.sh
ENV GARBAGE_COLLECT=1
ENV HOOK='/hook "docker-compose run --rm tests"'

CMD ["python", "/httpd.py"]

COPY . /
