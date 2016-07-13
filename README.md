Datapunt panorama API
======================

Project om beelden gemaakt in equirectangulaire projectie te importeren, en te ontsluiten via een API.

De API-laag bestaat uit twee componenten:

* Een OGC (WMS/WFS)-server die de opnamelocatieas en de metadata serveert, 
* Een REST-API die aanvullende functionaliteiten biedt.


Requirements
------------

* Docker-Compose (required)


Developing
----------

Use `docker-compose` to start a local database.

	(sudo) docker-compose start

or

	docker-compose up

test