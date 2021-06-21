#!/bin/bash

[[ "$1" == "l" ]] && kubectl get pods --all-namespaces || eval $(kubectl get pods --all-namespaces |grep $1 |awk '{ print "kubectl logs -f -n "$1" "$2}')
