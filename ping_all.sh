#!/bin/bash
for i in $(seq 177 255);
do
	for j in $(seq 0 255);
	do
		ip="138.73.${i}.${j}"
		ping -c 1 ${ip}
	done
done
