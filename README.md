## Datapunt Panorama-API

Project om beelden gemaakt in equirectangulaire projectie te importeren, en te ontsluiten via een API.

De API-laag bestaat uit twee componenten:

- Een OGC (WMS/WFS)-server die de opnamelocaties en de metadata serveert,
- Een REST-API die aanvullende functionaliteiten biedt.

## Vereisten

- Docker en Docker Compose

## Ontwikkelen

Gebruik `docker-compose` om een lokale versie op te starten
(Wanneer je gebruik maakt van Google Vision API is een bestand
`google-application-credentials.json` nodig in de web/panorama map
met daarin geldige credentials voor Google Vision API):

    (sudo) docker-compose start

Of:

    docker-compose up -d

Je kunt ook het project lokaal op poort 8000 draaien, maar dat vereist op zijn minst de database-container:

    docker-compose up -d database

Importeer de meest recente database van acceptatie:

    docker-compose exec database update-db.sh panorama <your_username>

## Unit tests lokaal draaien

Roep de Django-applicatie expliciet aan, en zorg dat OBJECTSTORE_PASSWORD als omgevingsvariabele is gezet:

    export OBJECTSTORE_PASSWORD=XXXXXX
    web/panorama/manage.py test datapunt_api

## Panorama demo lokaal

Op [http://localhost:8088/demo](http://localhost:8088/demo) draaien de equidistante panorama's in Marzipano viewer.
Op [http://localhost:8088/demo/cubic.html](http://localhost:8088/demo/cubic.html) draaien de kubische projecties van de panorama's in Marzipano viewer.

## Gedistribueerd beeldbewerking en beeldherkenning

Zie `.swarm/readme.md` in dit project voor meer informatie
