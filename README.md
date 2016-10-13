Datapunt panorama API
======================

Project om beelden gemaakt in equirectangulaire projectie te importeren, en te ontsluiten via een API.

De API-laag bestaat uit twee componenten:

* Een OGC (WMS/WFS)-server die de opnamelocatieas en de metadata serveert,
* Een REST-API die aanvullende functionaliteiten biedt.


Vereisten
---------

* docker en docker-compose (required)


Ontwikkelen
-----------

Gebruik `docker-compose` om een lokale versie op te starten

	(sudo) docker-compose start

of

	docker-compose up
	
Je kunt ook het project lokaal op poort 8000 draaien, maar dat vereist op zijn minst de database-container:

	docker-compose up database
	
Unit tests lokaal draaien
-------------------------

Roep de django app expliciet aan, en zorg dat OBJECTSTORE_PASSWORD als omgevingsvariabele is gezet:

	export OBJECTSTORE_PASSWORD=XXXXXX
    web/panorama/manage.py test datapunt_api

Panorama demo lokaal
--------------------

Op [http://localhost:8088/demo](http://localhost:8088/demo) draaien de equidistante panorama's in Marzipano viewer.
Op [http://localhost:8088/demo/cubic.html](http://localhost:8088/demo/cubic.html) draaien de kubische projecties van de panorama's in Marzipano viewer.


Docker Job voor gedistribueerd rekenwerk
----------------------------------------

Zorg dat je een docker swarm tot je beschikking hebt :-) en dat het OBJECTSTORE_PASSWORD in een environment file staat (bijvoorbeeld ~/.docker/env/object_store.env)

	docker build ./web -f web/JobDockerfile -t job
	docker run --env-file ~/.docker/env/object_store.env job 2016/03/17/TMX7315120208-000020/pano_0000_000000.jpg 359.75457352539 -0.467467454247501 -0.446629825528845
	
Vervolgens kun je een shell-script maken met alle entries om gedistribueerd uit te laten rekenen.
Een to-do voor ons is om dit te automatiseren en te integreren met Jenkins.
