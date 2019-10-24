# Introduction

Prometheus deployment using  helm chart

## steps to deploy prometheus service
Note: you may use your own version of prometheus instance.

The helm chart given here the one we used for testing the solution. The configuration/settings
may not represent your org standards. You are free to change the configuration present in this
helm chart

run below command to install/deploy prometheus
```
helm install helm/prometheus
```

By default prometheus service type is NodePort. You are free to change it as per your requirement
However, we recommend using ingress with LB.

To access the prometheus through browser, you can run below command to get the host port

```
kubectl get svc
```

In the above command output, look for the prometheus service host port it is listening on.
You can go to your browser and access it using
http://<node ip>:<host port> 

