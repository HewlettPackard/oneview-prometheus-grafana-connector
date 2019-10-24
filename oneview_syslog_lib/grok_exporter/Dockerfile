FROM ubuntu:16.04
LABEL Maintainer="HPE GSE"
LABEL Name="grok_exporter"
LABEL Version="0.2.5"

ENV GROK_ARCH="grok_exporter-0.2.5.linux-amd64"
ENV GROK_VERSION="v0.2.5"

RUN apt-get update -qqy \
    && apt-get upgrade -qqy \
    && apt-get install --no-install-recommends -qqy \
       wget unzip ca-certificates \
    && update-ca-certificates \
    && wget https://github.com/fstab/grok_exporter/releases/download/$GROK_VERSION/$GROK_ARCH.zip \
    && unzip $GROK_ARCH.zip \
    && mv $GROK_ARCH /grok \
    && rm $GROK_ARCH.zip \
    && apt-get --autoremove purge -qqy \
       wget unzip ca-certificates \
    && rm -fr /var/lib/apt/lists/*


RUN mkdir -p /etc/grok_exporter
COPY config.yml /etc/grok_exporter/config.yml
COPY oneview /etc/grok_exporter/patterns/oneview
RUN ln -sf /etc/grok_exporter/config.yml /grok/
RUN ln -sf /etc/grok_exporter/patterns/oneview /grok/patterns/
WORKDIR /grok

CMD ["./grok_exporter", "-config", "/grok/config.yml"]
