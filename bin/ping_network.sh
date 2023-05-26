#!/bin/bash
cat ../network_ip.txt | while read output
do
	ping -q -c 1 -i 0.3 $output >> trash.txt
	if [ $? -eq 0 ]; then
		echo "node $output is up"
	else
		echo "node $output is down"
	fi
done
