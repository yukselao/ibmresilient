#!/bin/bash

splitcounter=7000
parallelcount=10

function processit() {
	f=$1
	echo "$(date "+%F %T") INFO processing $f ($(wc -l $f| awk '{print $1}') rows)"
	sleep 15
	# curl blablabla
}

/bin/rm -fr ./tmp*
split -l $splitcounter $1 tmp
i=0
for f in $(ls -1 tmp* |sort); do
	processit $f &
	export i=$(expr $i + 1)
	if [[ "$(expr $i % $parallelcount)" == "0" ]]; then
		wait
	fi
done


