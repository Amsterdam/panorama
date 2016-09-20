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

Unit tests run locally
----------------------

name the django app explicitly.

    web/panorama/manage.py test datapunt_api

Running panorama demo
---------------------

Use http:/<server>:8088/demo in url
