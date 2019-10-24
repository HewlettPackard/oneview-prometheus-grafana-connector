## Introduction
grok-exporter reads the oneview alerts/statistics from the syslog and sends these metrics to prometheus

### Note
### How to setup
edit the config.yaml with right log path ( what is used in oneview-syslog-lib service )
build the docker iamges
edit the values.yaml with right docker images (name you used for building docker image )

### How to deploy
run below command
```
helm install --name grok helm/grok
```
