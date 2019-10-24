## Overview
Repo for deploying grafana container and custome dashboard for hpe oneview

There are two parts:
  - custom grafana dashboard to view hardware alerts coming from oneview
  - helm charts for grafana

The grafana dashboard data contains list of json files with pre-built graphs of Oneiew through prometheus
Before importing these json data files, prometheus should be added to grafana Datasources

### steps to import custom dashboards

Follow the below steps to import these json files to grafana

- Add prometheus Datasource in the Configuration section

-  Import JSON
    -  Manage Dashboards
    -  Import json file
    -  Use the prometheus as Datasource

   Repeat the same steps for all the other json files


### steps to deploy grafana service
Note: you may use your own version of grafana instance.

The helm chart given here the one we used for testing the solution. The configuration/settings
may not represent your org standards. You are free to change the configuration present in this
helm chart

run below command to install/deploy grafana
```
helm install helm/grafana
```

By default grafana service type is NodePort. You are free to change it as per your requirement
However, we recommend using ingress with LB.

To access the grafana through browser, you can run below command to get the host port

```
kubectl get svc
```

In the above command output, look for the grafana service host port it is listening on.
You can go to your browser and access it using
http://<node ip>:<host port> 

