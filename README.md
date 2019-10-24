# ov-prometheus-grafana

This repo contains code for HPE hardware monitoring solution designed using:
 - HPE oneview
 - prometheus
 - grafana

today, customers are able to monitor their existing virtualization and container apps using Prometheus connectors 
but hardware alerts are not presented on their dashboard. Customers are looking for unified end-to-end monitoring 
dashboard (like Grafana) that shows hardware alerts too in the same dashboard which helps in troubleshooting 
the outages that might have come from infrastructure failures.  

Also, this helps to co-relate alerts coming from applications/VMs/containers mapping it to the 
underlying hardware infrastructure

The solution is deployed on kubernetes platform.

Each of the components are deployed using helm charts

Go to respective components directory and read through REAMME to install, config and start the services


At high level you need to do following to stand up this solution:

 - working kubernetes cluster
 - generate alerts logs using oneview-syslog-lib ( k8s service )
 - export the alerts to prometheus using grok exporter
 - run prometheus ( using helm chart )
 - run grafana ( using helm chart )

Note that log generatori container and exporting logs  container are part of the same pod. These containers
same the volume and hence they are put into same pod 
