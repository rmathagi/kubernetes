#!/usr/bin/python3
#################################################################################################################################
#Name:          watch_endpoints.py
#Description:   Script to monitor endpoints and trigger action/alerts whenever there are any changes on the Services
#Created by:    R Mathagi Arun
Version="1.0.0"
#Created:       01/04/2021
#################################################################################################################################
from optparse import OptionParser
import os, sys, time, yaml, logging
from kubernetes import client, config, watch

# Setting Log Fromat
def Setup_Custom_Logger():
    logging.basicConfig(format='%(asctime)s %(levelname)-s : %(message)s',level=logging.INFO,datefmt='%d-%b-%Y %I:%M:%S %p')

# Watch DB End Points and trigger Envoy Config Update whenever any events are traced.
def Trigger_Watch_Endpoints():
    stream = watch.Watch().stream(v1.list_endpoints_for_all_namespaces)
    for event in stream:
        Resource_Version = event['object'].metadata.resource_version
        if Resource_Version not in Resource_Version_All:
            Resource_Version_All.append(Resource_Version)
            Event_Type = event['type']
            Endpoint_Name = event['object'].metadata.name
            logging.info("Triggering Action Script due to Event %s triggred on Endpoint %s" % (Event_Type, Endpoint_Name))
            try:
                logging.info("Trigger action/alerts due to change in End Points")
            except Exception as e:
                logging.critical("Exception while executing Trigger Script - %s" % (e))
            time.sleep(5)

#main
def Main():
    global o, Opt, ScriptName, v1, v2, Resource_Version_All

    Setup_Custom_Logger()

    ScriptName = os.path.basename(sys.argv[0])

    Usage = "%s [-f]" % ScriptName
    o = OptionParser(usage = Usage, version = Version, add_help_option=True)
    o.add_option('--file', '-f', metavar='<Kubeconfig file>', help="Enter the Kubeconfig file with location")

    (Opt, args) = o.parse_args()

    if Opt.file is None:
        try:
            config.load_incluster_config()
        except config.config_exception.ConfigException:
            logging.error("Provide a valid Kubeconfig file")
            logging.error("Run %s --help to know the usage." %ScriptName)
            sys.exit(1)
    else:  
        KubeConfig=Opt.file  
        if os.path.isfile(KubeConfig):
            # Loading Kubeconfig
            config.load_kube_config(KubeConfig)
        else:
            logging.info("Kubeconfig "+KubeConfig+" doesn't exist, provide a valid path")
            sys.exit(1)
    v1 = client.CoreV1Api()
    v2 = client.AppsV1Api()
    Resource_Version_All=[]
    logging.info("Container initiated to monitor DB End Points..!!")
    # This will handle exceptions arising due to watch timeout.
    while True:
        try:
            Trigger_Watch_Endpoints()
        except Exception:
            if len(Resource_Version_All) > 30:
                Resource_Version_All = Resource_Version_All[-30:]
            #logging.error("Exception when watching DB Endpoint's changes - %s" % (e))

if __name__ == '__main__':
    Main()