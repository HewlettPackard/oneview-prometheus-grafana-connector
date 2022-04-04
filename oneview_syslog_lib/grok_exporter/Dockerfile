ARG REGISTRY= 
FROM ${REGISTRY}/spock_rockylinux:8.5-1
LABEL Maintainer="um"
LABEL Name="grok_exporter"
LABEL Version="v1.0.0.RC5"

RUN groupadd -g 2000 grok && \
    useradd -r -u 2000 -g grok grok

ENV GROK_ARCH="grok_exporter-1.0.0.RC5.linux-amd64"
ENV GROK_VERSION="v1.0.0.RC5"

RUN dnf install -qy unzip
RUN curl -s -O -L https://github.com/fstab/grok_exporter/releases/download/$GROK_VERSION/$GROK_ARCH.zip \
    && unzip $GROK_ARCH.zip \
    && mkdir -p /etc/grok_exporter/patterns \
    && mv $GROK_ARCH/patterns/* /etc/grok_exporter/patterns/ \
    && mv $GROK_ARCH/grok_exporter /usr/local/bin \
    && rm $GROK_ARCH.zip

COPY supervisord.conf /etc/
COPY supervisord-grok-exporter.service /etc/supervisord.d/
COPY config.yml /etc/grok_exporter/config.yml
COPY patterns/oneview /etc/grok_exporter/patterns/oneview

RUN chown -R grok:grok /etc/grok_exporter \
    && mkdir -p /var/log/supervisord \
    && chown grok:grok /usr/local/bin/grok_exporter /var/log/supervisord

USER grok
