#!/bin/bash
cat ../network_ip.txt | while read output
do
	sudo ping -q -c 1 -i 0.2 $output >> trash.txt
	if [ $? -eq 0 ]; then
		echo "node $output is up"
	else
		echo "node $output is down"
	fi
done
