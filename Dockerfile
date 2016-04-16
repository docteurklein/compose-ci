FROM alpine:edge

COPY repositories /etc/apk/repositories

RUN apk add --no-cache \
    docker \
    py-pip \
    curl \
    unzip \
    aha@testing \
    mutt \
    bash \
    && pip install docker-compose awscli \
    && rm -rf \
        /tmp/* \
        /root/.cache \
        /var/cache/apk \
        $(find / -regex '.*\.py[co]')

EXPOSE 80

CMD ["python", "/httpd.py"]

VOLUME "/tmp/builds"
VOLUME "/tmp/logs"

COPY . /
