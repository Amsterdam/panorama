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
cd /home/panorama
cd .swarm
docker-compose build --pull --build-arg OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD worker
docker-compose build --pull database
docker-compose push
docker stack deploy --compose-file docker-compose.yml panoswarm
```

Let op! De naam van het cluster is belangrijk (wordt gebruikt in `save-db.sh`)

Op het cluster 

En als het cluster succesvol is opgestart - uitgaande van 5cpu's, en > 16GB memory per node:

```
docker service scale panoswarm_worker=160
```

Stel de gegevens in de database veilig, wannneer de swarm klaar is:

```
./save-db.sh
```

Stop swarm - zorg ervoor dat de gegevens uit de database zijn veiliggesteld! zie stap hierboven - met het volgende commando:

```
docker stack rm panoswarm
```

Lokaal
======

Bijvoorbeeld voor ontwikkelen kun je de stack ook lokaal opstarten
 (zie [https://docs.docker.com/engine/swarm/stack-deploy/](https://docs.docker.com/engine/swarm/stack-deploy/) ):

```bash
docker swarm init
docker service create --name registry --publish 5000:5000 registry:2
```

Ga dan naar het panorama project en voer de volgende commando's uit:

```bash
cd .swarm
export OBJECTSTORE_PASSWORD=<OBJECT_STORE_PASSWORD>
docker-compose -f docker-compose-local.yml build --pull --build-arg OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD worker
docker-compose -f docker-compose-local.yml build --pull database
docker-compose -f docker-compose-local.yml push
docker stack deploy --compose-file docker-compose-local.yml panoslocal
```

Om de swarm op te starten, lokaal.

Wil je gebruik maken van de volledige database gebruik dan onderstaande - uit `dl_and_load_data.sh` gekopieerde commando's om de database op te halen

```bash
_db_docker=`docker ps -q -f "name=panoslocal_database"`

docker exec $_db_docker /bin/download-db.sh panorama <username>
docker exec $_db_docker /bin/update-table.sh panorama panoramas_region public panorama
docker exec $_db_docker psql -U panorama -c 'create sequence panoramas_region_id_seq'
docker exec $_db_docker psql -U panorama -c "alter table panoramas_region alter id set default nextval('panoramas_region_id_seq')"
docker exec $_db_docker /bin/update-table.sh panorama panoramas_panorama public panorama
```


Lokaal stoppen kan met:

```bash
docker stack rm panoslocal
```

en

```bash
docker swarm leave --force
```
