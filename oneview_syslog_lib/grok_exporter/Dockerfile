FROM registry-ilm.prod.spock.bmwgroup.net/spock_rockylinux:8.5-1
LABEL Maintainer="um"
LABEL Name="grok_exporter"
LABEL Version="v1.0.0.RC5"

ENV GROK_ARCH="grok_exporter-1.0.0.RC5.linux-amd64"
ENV GROK_VERSION="v1.0.0.RC5"

RUN dnf install -qy unzip
RUN curl -s -O -L https://github.com/fstab/grok_exporter/releases/download/$GROK_VERSION/$GROK_ARCH.zip \
    && unzip $GROK_ARCH.zip \
    && mkdir -p /etc/grok_exporter/patterns \
    && mv $GROK_ARCH/patterns/* /etc/grok_exporter/patterns/ \
    && mv $GROK_ARCH/grok_exporter /usr/local/bin \
    && rm $GROK_ARCH.zip

COPY supervisord-grok-exporter.service /etc/supervisord.d/
COPY config.yml /etc/grok_exporter/config.yml
COPY oneview /etc/grok_exporter/patterns/oneview
