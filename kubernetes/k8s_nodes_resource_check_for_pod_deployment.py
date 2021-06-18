#################################################################################################################
#Name:          k8s_nodes_resource_check_for_pod_deployment.py
#Description:   Script to check the resource availablity of kubernetes worker nodes to deploy Pods(with replicas)
#Created by:    R Mathagi Arun
#Version:       1.0.0
#Created:       18/07/2021 
##################################################################################################################

## Import required modules
from optparse import OptionParser
import getopt, sys, re, os, subprocess, json
from kubernetes import client, config
from kubernetes.client.rest import ApiException

#Filter Worker Nodes and validate if they don't have taints - No Schedule and No Execute
def ready_worker_nodes():
    global available_worker_nodes
    available_worker_nodes=[]
    worker_label_selector="role=worker"

    try:
        list_worker_nodes = v1.list_node(label_selector=worker_label_selector)
    except ApiException as e:
        print("Exception when listing nodes for cluster")
        sys.exit(1)
    
    for worker_node in list_worker_nodes.items:
        if worker_node.spec.taints is None:
            available_worker_nodes.append(worker_node.metadata.name)
        else:
            taint_node=False
            for taint_value in worker_node.spec.taints:
                if taint_value.effect in ['NoSchedule', 'NoExecute']:
                    taint_node=True
                    break
            if not taint_node:
                available_worker_nodes.append(worker_node.metadata.name)
                

# Fetch Available and Allocated CPU, Memory Metrics and Validate if it's available to schedule pod based on resource request.
def node_resource_check():
    global pod_ready_worker_node, skip_metricchk_worker_node
    pod_ready_worker_node=[]
    skip_metricchk_worker_node=[]
    for worker_node in available_worker_nodes:
        cpu_units_mismatch=False
        mem_units_mismatch=False
        fetch_node_metric=subprocess.Popen(["/bin/bash", "-c", 'kubectl describe node '+worker_node +"| grep -E 'Allocatable|Allocated' -A 5 | grep -E 'cpu|memory'"], stdout=subprocess.PIPE)
        node_metrics_list=fetch_node_metric.stdout.read().decode("utf-8").split("\n")
        node_metrics_list=[node_metrics.strip() for node_metrics in node_metrics_list]
        total_cpu=(node_metrics_list[0].split(":")[1].strip())
        total_memory=(node_metrics_list[1].split(":")[1].strip())
        allocated_cpu=re.split(r'\s+', node_metrics_list[2])[1]
        allocated_memory=re.split(r'\s+', node_metrics_list[3])[1]

        if total_cpu.endswith('m') and allocated_cpu.endswith('m'):
            available_cpu=int(total_cpu[:-1]) - int(allocated_cpu[:-1])
            required_cpu_init=int(required_cpu[:-1])
        else:
            cpu_units_mismatch=True
        
        if total_memory.endswith('Mi') or total_memory.endswith('Ki'):
            if allocated_memory.endswith('Mi'):
                if total_memory.endswith('Ki'):
                    total_memory=str(int((int(total_memory[:-2])/1024)))+"Mi"
                available_memory=int(total_memory[:-2]) - int(allocated_memory[:-2])
                required_memory_init=int(required_memory[:-2])
            elif allocated_memory.endswith('Ki'):
                if total_memory.endswith('Mi'):
                    total_memory=str(int((int(total_memory[:-2])*1024)))+"Ki"
                available_memory=int(total_memory[:-2]) - int(allocated_memory[:-2])
                required_memory_init=(int(required_memory[:-2])*1024)
            else:
                mem_units_mismatch=True
        else:
            mem_units_mismatch=True

        if not cpu_units_mismatch and not mem_units_mismatch:
            if required_cpu_init  < available_cpu and required_memory_init < available_memory:
                pod_ready_worker_node.append(worker_node)
        else:
            skip_metricchk_worker_node.append(worker_node)


def Main():
    global o, Opt, kubeconfig, required_cpu, required_memory, replicas, v1

    ScriptName = os.path.basename(sys.argv[0])
    if len(sys.argv) == 1:
        print("Run %s --help to know the usage." %ScriptName)
        sys.exit(1)

    Usage = "%s [-k] [-c] [-m] [-r]" % ScriptName
    o = OptionParser(usage = Usage, add_help_option=True)
    o.add_option('--kubeconfig', '-k', metavar='Kubeconfig Filename with absolute path', help="Kubeconfig File with Path")
    o.add_option('--cpu', '-c', metavar='Integer Value ending with millicpu(Example - 100m)', help="Required CPU resource for the POD")
    o.add_option('--memory', '-m', metavar='Integer Value ending with Mi(Example - 1Mi)', help="Required Memory resource for POD")
    o.add_option('--replicas', '-r', metavar='Integer Value', help="Number of replicas to be deployed")
    (Opt, args) = o.parse_args()

    if Opt.kubeconfig is None:
        print("Provide a valid Cloud Environment Type")
        print("Run %s --help to know the usage." %ScriptName)
        sys.exit(1) 
    else:
        kubeconfig=Opt.kubeconfig
        if os.path.isfile(kubeconfig):
            # Loading Kubeconfig
            config.load_kube_config(kubeconfig)
            os.environ["KUBECONFIG"] = kubeconfig
        else:
            print("Kubeconfig "+kubeconfig+" doesn't exist, provide a valid path")
            sys.exit(1)

    if Opt.cpu is None or not Opt.cpu.endswith('m') or not Opt.cpu[:-1].isdigit():
        print("Provide a valid CPU value")
        print("Run %s --help to know the usage." %ScriptName)
        sys.exit(1) 
    else:
        required_cpu=Opt.cpu

    if Opt.memory is None or not Opt.memory.endswith('Mi') or not Opt.memory[:-2].isdigit():
        print("Provide a valid Memory value")
        print("Run %s --help to know the usage." %ScriptName)
        sys.exit(1) 
    else:
        required_memory=Opt.memory

    if Opt.replicas is None or not Opt.replicas.isdigit():
        print("Provide a valid replica count")
        print("Run %s --help to know the usage." %ScriptName)
        sys.exit(1)
    else:
        replicas=Opt.replicas

    v1 = client.CoreV1Api()
    ready_worker_nodes()
    if len(available_worker_nodes) >= int(replicas):
        node_resource_check()
        if len(pod_ready_worker_node) >= int(replicas):
            print(str(len(pod_ready_worker_node)) + " Worker Nodes are eligible for Scheduling this POD(with replicas)")
            sys.exit(0)
        else:
            if len(skip_metricchk_worker_node) > 0:
                print("Error: Inadequate resources - Only "  + str(len(pod_ready_worker_node)) + " Worker Nodes are available for Scheduling this POD(with replicas). Resource Check skipped in " + str(len(skip_metricchk_worker_node))+" Nodes due to Metrics Unit Mismatch")
                sys.exit(1)
            else:
                print("Error: Inadequate resources - Only "  + str(len(pod_ready_worker_node)) + " Worker Nodes are available for Scheduling this POD(with replicas)")
                sys.exit(1)
    else:
        print("Error: Inadequate resources - Only "  + str(len(available_worker_nodes)) + " Worker Nodes are available for Scheduling this POD(with replicas)")
        sys.exit(1)

if __name__ == '__main__':
  Main() 
