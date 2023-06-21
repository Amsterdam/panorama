# Panoramaverwerking

Project om beelden gemaakt in equirectangulaire projectie te importeren en
prepareren.

De bijbehorende API woont op https://github.com/Amsterdam/panorama-api.

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

Roep de Django-applicatie expliciet aan, en zorg dat ``OBJECTSTORE_PASSWORD``
als omgevingsvariabele is ingesteld:

    export OBJECTSTORE_PASSWORD=XXXXXX
    web/panorama/manage.py test datapunt_api

## Gedistribueerd beeldbewerking en beeldherkenning

Zie `.swarm/readme.md` in dit project voor meer informatie
