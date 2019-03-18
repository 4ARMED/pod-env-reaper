#!/usr/bin/env python3

from kubernetes import client, config
import json
import requests

config.load_kube_config()

v1 = client.CoreV1Api()
nodes = v1.list_node()
kubelet_readonly_port = "10255"

internalIPs = []

for node in nodes.items:
    for s in node.status.addresses:
        if (s.type == 'InternalIP'):
            internalIPs.append(s.address)


for ip in internalIPs:
    r = requests.get("http://" + ip + ":" + kubelet_readonly_port + "/pods")
    pods = r.json()['items']
    for pod in pods:
        prefix = "%s:%s" % (ip, pod['metadata']['name'])
        for c in pod['spec']['containers']:
            if 'env' in c.keys():
                for e in c['env']:
                    if 'value' in e.keys():
                        print("%s:%s:%s" % (prefix, e['name'], e['value']))
                    elif 'valueFrom' in e.keys():
                        if 'configMapKeyRef' in e['valueFrom'].keys():
                            print("%s:%s:configMap:%s/%s" % (
                                prefix, e['name'], e['valueFrom']['configMapKeyRef']['name'], e['valueFrom']['configMapKeyRef']['key']))
                        elif 'secretKeyRef' in e['valueFrom'].keys():
                            print("%s:%s:secret:%s/%s" % (prefix, e['name'], e['valueFrom']
                                                          ['secretKeyRef']['name'], e['valueFrom']['secretKeyRef']['key']))
                    else:
                        print(e)
