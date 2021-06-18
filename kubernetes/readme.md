## PURPOSE
Used to check if the POD(with replicas) can be deployed in Kubernetes cluster.

## DESCRIPTION

https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

As mentioned in the above article, A pod fails to be scheduled due to insufficient CPU or memory resource on the node. This script will help check if the POD(with Replicas) can be scheduled on the Cluster

## PRE-REQUISITES

Tested using Python 3.8.2 and requires the installation of following pip library:

pip install kubernetes

## USAGE

$ python3 k8s_nodes_resource_check_for_pod_deployment.py \--help

Usage: k8s_nodes_resource_check_for_pod_deployment.py [\-e] [\-r] [\-c] [\-d]

Options:

  \--help            show this help message and exit

  \--kubeconfig=Kubeconfig Filename with absolute path
                        Kubeconfig File with Path
                        
  \--cpu=Integer Value ending with millicpu(Example - 100m)
                        Required CPU resource for the POD
                        
  \--memory=Integer Value ending with Mi(Example - 1Mi)
                        Required Memory resource for POD
                        
  \--replicas=Integer Value
                        Number of replicas to be deployed


Example Usage:

$ python3 k8s_nodes_resource_check_for_pod_deployment.py -k /home/rmathagi/.kube/kubeconfig-aws-preprod -c 5000m -m 2048Mi -r 2

2 Worker Nodes are eligible for Scheduling this POD(with replicas)


$ python3 k8s_nodes_resource_check_for_pod_deployment.py -k /home/rmathagi/.kube/kubeconfig-aws-preprod -c 5000m -m 2048Mi -r 2

Error: Inadequate resources - Only 0 Worker Nodes are available for Scheduling this POD(with replicas)
