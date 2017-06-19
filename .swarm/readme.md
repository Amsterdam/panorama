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

Start het cluster - uitgaande van 32 nodes:

```
docker service create --replicas 32 --name worker --constraint 'node.hostname != master.swarm.datapunt.amsterdam.nl' master.swarm.datapunt.amsterdam.nl:5000/worker:latest
```

En als het cluster succesvol is opgestart - uitgaande van 5cpu's, en > 16GB memory per node:

```
docker service scale worker=160
```


Stop swarm:

```
docker service stop worker
```

Clear stopped containers in swarm

```
docker service rm worker
```

