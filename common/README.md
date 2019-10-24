## common services

Deploy these services onto your k8s cluster before deploying oneview-syslog-lib service, prometheus and grafan services
These services create pv, pvc

### Note:
Following yaml resources are provided as an example, in the current release these below resources are not used. So you don't need to install
 - ingress-service.yaml
 - default-storage-class.yaml
 - namespace.yaml
 
TODO:
  - deploy ingress, LB
