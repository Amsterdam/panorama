Op de swarm
===========

Uitgaande van een gecloned git-project in /home/user/panorama


```
cd /home/user/panorama
git pull
```

als sudo su - 

```
export OBJECTSTORE_PASSWORD=<OBJECT_STORE_PASSWORD>
```

en in dezelfde sudo sessie:

```
cd /home/user/panorama
cd .swarm
docker-compose up -d --build scheduler # requires OBJECTSTORE_PASSWORD to be set
cd ..
docker build --build-arg OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD --build-arg AMPQ_HOST=10.10.10.3 ./web -f web/WorkerDockerfile -t master.swarm.datapunt.amsterdam.nl:5000/worker
docker push master.swarm.datapunt.amsterdam.nl:5000/worker
```


Dan als gewone user, uitgaande van een cluster met 295 cpu's:

```
docker -H :4000 pull master.swarm.datapunt.amsterdam.nl:5000/worker:latest
for ((i=1;i<=295;i++)); do docker -H :4000 run -d master.swarm.datapunt.amsterdam.nl:5000/worker; done
```


Stop swarm:
```
for container_id in $(docker -H :4000 ps -q);do nohup docker -H :4000 stop $container_id & done;
```

Clear stopped containers in swarm
```
for container_id in $(docker -H :4000 ps -a --filter status=exited -q);do docker -H :4000 rm $container_id;done
```
