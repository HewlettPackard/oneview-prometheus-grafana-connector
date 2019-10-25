# oneview-prometheus-grafana-connector


## Overview
This repo contains code and configuration for connector between HPE hardware and prometheus/grafana.
The goal of the connector is monitor hardware alerts using prometheus and grafana. 

## Components of connector
The solution is designed using following compoents

 - HPE oneview
 - prometheus
 - grafana

## Background
today, customers are able to monitor their existing virtualization and container apps using Prometheus connectors 
but hardware alerts are not presented on their dashboard. Customers are looking for unified end-to-end monitoring 
dashboard (like Grafana) that shows hardware alerts too in the same dashboard which helps in troubleshooting 
the outages that might have come from infrastructure failures.  

Also, this helps to co-relate alerts coming from applications/VMs/containers mapping it to the 
underlying hardware infrastructure

## How to deploy the connector
The solution is deployed on kubernetes platform.

Each of the components are deployed using helm charts

Go to respective components directory and read through REAMME to install, config and start the services

At high level you need to do following to stand up this solution:

 - working kubernetes cluster
 - generate alerts logs using oneview-syslog-lib ( k8s service )
 - export the alerts to prometheus using grok exporter
 - run prometheus ( using helm chart )
 - run grafana ( using helm chart )

Note that log generator container and log exporter container are part of the same pod. These containers
share the volume and hence they are put into same pod.

Also you are free to use your existing prometheus and grafana instance and export the log data using log generator and log exporter pod.
