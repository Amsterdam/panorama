#!/usr/bin/env bash

for f in parameterfile.par
do
  echo "Processing $f"
  while read p; do
    (docker -H :4000 run -d -m 3600m master.swarm.datapunt.amsterdam.nl:5000/panojob $p)
    until [ $? == 0 ]
    do
	  sleep 1
      echo "cleaning exited containers"
	  for container_id in $(docker -H :4000 ps -a --filter status=exited -q);do docker -H :4000 rm $container_id;done
	  echo "retry $p"
	  (docker -H :4000 run -d -m 4G master.swarm.datapunt.amsterdam.nl:5000/panojob $p)
    done
  done <$f
done

sleep 300
for container_id in $(docker -H :4000 ps -a --filter status=exited -q);do docker -H :4000 rm $container_id;done