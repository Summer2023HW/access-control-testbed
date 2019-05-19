#!/bin/bash
cat /home/pi/network_ip.txt | while read output
do
	ping -c 1 $output
	if [ $? -eq 0 ]; then
		echo "node $output is up"
	else
		echo "node $output is down"
	fi
done
