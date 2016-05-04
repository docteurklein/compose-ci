FROM alpine:edge

RUN apk add --no-cache \
    docker \
    python3 \
    && pip3 install docker-compose ansi2html \
    && rm -rf /tmp /root/.cache /var/cache/apk $(find / -regex '.*\.py[co]')

EXPOSE 80

ENV DOCKER_HOST=unix:///var/run/docker.sock
ENV BUILD_IMAGE=docteurklein/compose-ci
ENV BUILD_CMD='python3 -m compose_ci.ci'
ENV GARBAGE_COLLECT=1

WORKDIR /ci

CMD ["python3", "-m", "compose_ci.httpd"]

COPY . /ci
